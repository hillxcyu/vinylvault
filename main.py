import os
import uuid
import json
import re
import logging
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from database import db
from duplicate_engine import DuplicateEngine
from gemini_service import gemini_service
from discogs_service import discogs_service
from deskew_service import deskew_service
from classical_service import classical_service
from batch_import_webarchive import run_batch_import

logger = logging.getLogger("vinyl_vault")

app = FastAPI(title="Vinyl Vault - Collection & Anti-Duplicate Assistant")

# Mount static directory and subdirectories safely
static_dir = os.path.join(os.path.dirname(__file__), "static")
covers_dir = os.path.join(static_dir, "extracted_covers")
os.makedirs(static_dir, exist_ok=True)
os.makedirs(covers_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

class DuplicateCheckQuery(BaseModel):
    artist: str
    albumTitle: str
    catalogNumber: Optional[str] = None

class LogSpinRequest(BaseModel):
    recordId: str
    notes: Optional[str] = ""

class AddRecordRequest(BaseModel):
    artist: str
    title: str
    releaseYear: Optional[Any] = None
    genre: Optional[str] = None
    coverUrl: Optional[str] = None
    catalogNumber: Optional[str] = None
    formatDetails: Optional[str] = "Standard Black Vinyl"

class ListeningGuideRequest(BaseModel):
    artist: str
    albumTitle: str

class FetchCoverRequest(BaseModel):
    artist: str
    title: str
    coverUrl: Optional[str] = None

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return HTMLResponse("<h1>Vinyl Vault Server Running</h1>")

@app.get("/api/records")
async def get_records():
    return {"records": db.get_all_records()}

@app.get("/api/wishlist")
async def get_wishlist():
    return {"wishlist": db.get_wishlist()}

@app.get("/api/chronicle")
async def get_chronicle():
    return classical_service.get_chronicle_data(db.get_all_records())

@app.get("/api/stats")
async def get_stats():
    records = db.get_all_records()
    spins = db.get_spins_log()
    total_spins = sum(r.get("spinsCount", 0) for r in records)
    genres = {}
    for r in records:
        g = r.get("genre", "Unknown")
        genres[g] = genres.get(g, 0) + 1

    return {
        "totalRecords": len(records),
        "totalSpins": total_spins,
        "recentSpinsCount": len(spins),
        "genreBreakdown": genres
    }

@app.post("/api/check-duplicate")
async def check_duplicate(query: DuplicateCheckQuery):
    result = DuplicateEngine.check_duplicate(
        query.dict(),
        db.get_all_records(),
        db.get_wishlist()
    )
    return result

@app.post("/api/scan")
async def scan_cover(file: UploadFile = File(...)):
    contents = await file.read()
    
    # 0. Auto-deskew & perspective correct image
    deskewed_bytes, is_deskewed = deskew_service.auto_deskew_image(contents)
    final_bytes = deskewed_bytes if is_deskewed else contents

    # 1. Save uploaded/deskewed cover image to static/uploads/
    os.makedirs("static/uploads", exist_ok=True)
    ext = ".jpg" if is_deskewed else (os.path.splitext(file.filename)[1] or ".jpg")
    filename = f"scan_{uuid.uuid4().hex[:8]}{ext}"
    saved_path = os.path.join("static/uploads", filename)
    with open(saved_path, "wb") as f:
        f.write(final_bytes)

    uploaded_cover_url = f"/static/uploads/{filename}"

    # 2. Extract metadata via Gemini Vision API using deskewed image
    extracted_metadata = gemini_service.analyze_album_cover(final_bytes, filename=filename)
    extracted_metadata["coverUrl"] = uploaded_cover_url
    extracted_metadata["deskewed"] = is_deskewed

    # 3. Try fetching genuine Discogs release cover image
    artist = extracted_metadata.get("artist", "")
    title = extracted_metadata.get("albumTitle", "")
    if artist and title:
        official_img = discogs_service.fetch_official_cover(artist, title, cover_url=uploaded_cover_url)
        if official_img and "shopping_cover" not in official_img:
            extracted_metadata["coverUrl"] = official_img

    # 4. Automatically run duplicate check on extracted metadata
    duplicate_result = DuplicateEngine.check_duplicate(
        extracted_metadata,
        db.get_all_records(),
        db.get_wishlist()
    )

    return {
        "metadata": extracted_metadata,
        "duplicateCheck": duplicate_result,
        "deskewed": is_deskewed
    }

@app.post("/api/spin")
async def log_spin(req: LogSpinRequest):
    spin_entry = db.log_spin(req.recordId, req.notes or "")
    rec = db.get_record_by_id(req.recordId)
    return {"status": "success", "spin": spin_entry, "record": rec}

@app.post("/api/records")
async def add_record(req: AddRecordRequest):
    rec_dict = req.dict()
    
    # Sanitize releaseYear to 4-digit integer if possible
    ry = rec_dict.get("releaseYear")
    if ry is not None:
        if isinstance(ry, str):
            match = re.search(r'\b(19\d\d|20\d\d)\b', ry)
            if match:
                rec_dict["releaseYear"] = int(match.group(1))
            else:
                rec_dict["releaseYear"] = None
        elif isinstance(ry, (int, float)):
            rec_dict["releaseYear"] = int(ry)
        else:
            rec_dict["releaseYear"] = None

    # Try fetching official release cover art asset if current URL is fallback
    if not rec_dict.get("coverUrl") or "wikimedia" in rec_dict.get("coverUrl", ""):
        official_cover = discogs_service.fetch_official_cover(req.artist, req.title)
        if official_cover:
            rec_dict["coverUrl"] = official_cover

    new_rec = db.add_record(rec_dict)
    
    # Refresh AI Chronicle via Gemini 3.6 Flash and persist to DB/disk
    try:
        classical_service.get_chronicle_data(db.get_all_records(), force_ai_refresh=True)
    except Exception as err:
        logger.warning(f"AI Chronicle refresh warning: {err}")

    return {"status": "success", "record": new_rec}

@app.delete("/api/records/{record_id}")
async def delete_record_endpoint(record_id: str):
    success = db.delete_record(record_id)
    if success:
        try:
            classical_service.get_chronicle_data(db.get_all_records(), force_ai_refresh=True)
        except Exception as err:
            logger.warning(f"AI Chronicle refresh warning: {err}")
        return {"status": "success", "message": f"Record {record_id} deleted."}
    raise HTTPException(status_code=404, detail="Record not found.")

@app.post("/api/fetch-official-cover")
async def fetch_official_cover_endpoint(req: FetchCoverRequest):
    img_url = discogs_service.fetch_official_cover(req.artist, req.title, cover_url=req.coverUrl)
    return {"status": "success", "coverUrl": img_url}

@app.post("/api/fetch-release-assets")
async def fetch_release_assets_endpoint(req: FetchCoverRequest):
    target_cover = req.coverUrl
    if not target_cover:
        for r in db.get_all_records():
            if r.get("title") == req.title or r.get("artist") == req.artist:
                target_cover = r.get("coverUrl")
                break

    assets = discogs_service.fetch_all_release_assets(req.artist, req.title, cover_url=target_cover)
    return {"status": "success", "assets": assets}

GUIDE_CACHE_DIR = os.path.join(os.path.dirname(__file__), "data_store", "listening_guides")
os.makedirs(GUIDE_CACHE_DIR, exist_ok=True)

def sanitize_cache_key(name: str) -> str:
    cleaned = re.sub(r'[^\w\s-]', '', name).strip().lower()
    return re.sub(r'[-\s]+', '_', cleaned)

@app.post("/api/listening-guide")
async def get_listening_guide(req: ListeningGuideRequest):
    safe_key = f"{sanitize_cache_key(req.artist)}_{sanitize_cache_key(req.albumTitle)}.json"
    cache_path = os.path.join(GUIDE_CACHE_DIR, safe_key)

    if os.path.exists(cache_path):
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                guide_data = json.load(f)
                return {"status": "success", "guide": guide_data, "cached": True}
        except Exception as e:
            logger.warning(f"Failed to load cached listening guide: {e}")

    guide = gemini_service.generate_listening_guide(req.artist, req.albumTitle)

    try:
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(guide, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.warning(f"Failed to write listening guide cache: {e}")

    return {"status": "success", "guide": guide, "cached": False}

def get_local_grounding_context(artist: str, title: str) -> Dict[str, Any]:
    all_records = db.get_all_records()
    target_record = None

    clean_a = re.sub(r'[^\w\s]', '', artist.lower())
    clean_t = re.sub(r'[^\w\s]', '', title.lower())
    a_tokens = set(w for w in clean_a.split() if len(w) > 2)
    t_tokens = set(w for w in clean_t.split() if len(w) > 2)

    for r in all_records:
        r_a = re.sub(r'[^\w\s]', '', r.get("artist", "").lower())
        r_t = re.sub(r'[^\w\s]', '', r.get("title", "").lower())

        if clean_t and (clean_t in r_t or r_t in clean_t):
            target_record = r
            break
        
        r_t_tokens = set(r_t.split())
        if t_tokens and len(t_tokens.intersection(r_t_tokens)) >= 1:
            target_record = r
            break

    if not target_record and len(all_records) > 0:
        target_record = all_records[0]

    safe_key = f"{sanitize_cache_key(artist)}_{sanitize_cache_key(title)}.json"
    cache_path = os.path.join(GUIDE_CACHE_DIR, safe_key)
    guide_data = None
    if os.path.exists(cache_path):
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                guide_data = json.load(f)
        except Exception:
            pass

    crate_summary = {
        "totalRecordsInCrate": len(all_records),
        "ownedAlbums": [f"{r.get('artist', 'Unknown')} - {r.get('title', 'Unknown')}" for r in all_records[:30]]
    }

    return {
        "recordDetails": target_record or {},
        "guideMetadata": guide_data or {},
        "crateSummary": crate_summary
    }

class ChatAlbumRequest(BaseModel):
    artist: str
    albumTitle: str
    message: str
    history: Optional[List[Dict[str, str]]] = []

@app.post("/api/chat-album")
async def chat_album_endpoint(req: ChatAlbumRequest):
    grounding_ctx = get_local_grounding_context(req.artist, req.albumTitle)
    reply = gemini_service.chat_about_album(
        req.artist,
        req.albumTitle,
        req.message,
        req.history,
        grounding_context=grounding_ctx
    )
    return {"status": "success", "reply": reply}

class PronounceRequest(BaseModel):
    text: str

@app.post("/api/pronounce")
async def pronounce_endpoint(req: PronounceRequest):
    text = req.text.strip()
    clean_text = re.sub(r'\([\u4e00-\u9fff\w\s\.]+\)', '', text).strip()
    return {
        "status": "success",
        "originalText": text,
        "cleanText": clean_text or text
    }

@app.post("/api/batch-import-webarchive")
async def batch_import_route():
    try:
        res = run_batch_import()
        return res
    except Exception as e:
        logger.error(f"Error running batch import: {e}")
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
