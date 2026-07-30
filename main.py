import os
import uuid
import json
import re
import logging
from datetime import datetime
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, StreamingResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from database import db
from duplicate_engine import DuplicateEngine
from gemini_service import gemini_service
from discogs_service import discogs_service
from deskew_service import deskew_service
from classical_service import classical_service
from batch_import_webarchive import run_batch_import
from gcs_service import gcs_service
from fastapi.responses import RedirectResponse

from fastapi.middleware.gzip import GZipMiddleware

logger = logging.getLogger("vinyl_vault")

app = FastAPI(title="Vinyl Vault - Collection & Anti-Duplicate Assistant")
app.add_middleware(GZipMiddleware, minimum_size=1000)

@app.middleware("http")
async def add_cache_control_header(request, call_next):
    response = await call_next(request)
    path = request.url.path.lower()
    if path == "/" or path.endswith(".html") or path.startswith("/api/"):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    elif path.startswith("/static/uploads/") or path.startswith("/static/extracted_covers/"):
        response.headers["Cache-Control"] = "public, max-age=86400"
    return response

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
    forceRefresh: Optional[bool] = False

class FetchCoverRequest(BaseModel):
    artist: str
    title: str
    coverUrl: Optional[str] = None
    forceRefresh: Optional[bool] = False

@app.get("/", response_class=HTMLResponse)
@app.get("/index.html", response_class=HTMLResponse)
async def serve_index():
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(
            index_path,
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate, max-age=0",
                "Pragma": "no-cache",
                "Expires": "0"
            }
        )
    return HTMLResponse("<h1>Vinyl Vault Server Running</h1>")

@app.get("/api/records")
async def get_records():
    return {"records": db.get_all_records(sync_if_needed=True)}

@app.get("/api/covers/{filename}")
async def serve_cover_image(filename: str):
    clean_fn = os.path.basename(filename)
    gcs_url = f"https://storage.googleapis.com/{gcs_service.bucket_name}/covers/{clean_fn}"
    return RedirectResponse(url=gcs_url)

@app.get("/static/extracted_covers/{filename}")
async def redirect_legacy_extracted_cover(filename: str):
    clean_fn = os.path.basename(filename)
    return RedirectResponse(
        url=f"https://storage.googleapis.com/{gcs_service.bucket_name}/covers/{clean_fn}"
    )

@app.get("/static/uploads/{filename}")
async def redirect_legacy_upload_cover(filename: str):
    clean_fn = os.path.basename(filename)
    return RedirectResponse(
        url=f"https://storage.googleapis.com/{gcs_service.bucket_name}/covers/{clean_fn}"
    )


@app.post("/api/admin/repair-covers")
async def repair_covers_admin_endpoint():
    recs = db.get_all_records(sync_if_needed=True)
    updated_count = 0

    for r in recs:
        old_url = r.get("coverUrl", "")
        rec_id = r.get("id")
        artist = r.get("artist", "")
        title = r.get("title", "")
        new_url = None

        if old_url.startswith("/static/extracted_covers/"):
            fname = os.path.basename(old_url)
            new_url = f"https://storage.googleapis.com/{gcs_service.bucket_name}/covers/{fname}"
        elif old_url.startswith("/static/uploads/") or not old_url or "shopping_cover" in old_url:
            discogs_url = discogs_service.fetch_official_cover(artist, title)
            if discogs_url and "shopping_cover" not in discogs_url:
                new_url = discogs_url
            else:
                new_url = f"https://storage.googleapis.com/{gcs_service.bucket_name}/covers/shopping_cover_2.jpg"

        if new_url and new_url != old_url:
            r["coverUrl"] = new_url
            updated_count += 1

    if updated_count > 0:
        db.save_records()
        if db.firestore.db:
            db.firestore.save_all_records_batch(recs)

    return {
        "status": "success",
        "updatedCount": updated_count,
        "totalRecords": len(recs)
    }




@app.get("/api/wishlist")
async def get_wishlist():
    return {"wishlist": db.get_wishlist()}

@app.get("/api/chronicle")
async def get_chronicle():
    data = classical_service.get_chronicle_data(db.get_all_records())
    data["isRebuilding"] = classical_service.is_rebuilding
    return data

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
    detected_corners = deskew_service.detect_corners(contents)
    deskewed_bytes, is_deskewed = deskew_service.auto_deskew_image(contents)
    final_bytes = deskewed_bytes if is_deskewed else contents

    # 1. Upload scan cover image to GCS bucket (covers/)
    ext = ".jpg" if is_deskewed else (os.path.splitext(file.filename)[1] or ".jpg")
    filename = f"scan_{uuid.uuid4().hex[:8]}{ext}"
    uploaded_cover_url = gcs_service.upload_cover(final_bytes, filename)

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
        "deskewed": is_deskewed,
        "detectedCorners": detected_corners
    }

@app.post("/api/detect-corners")
async def detect_corners_endpoint(file: UploadFile = File(...)):
    contents = await file.read()
    corners = deskew_service.detect_corners(contents)
    return {
        "status": "success",
        "corners": corners
    }

@app.post("/api/crop-deskew")
async def crop_deskew_endpoint(
    file: UploadFile = File(...),
    corners: str = Form(...)
):
    contents = await file.read()
    try:
        parsed_corners = json.loads(corners)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid corners format. Must be JSON array of 4 coordinate pairs.")

    deskewed_bytes, is_deskewed = deskew_service.manual_deskew_image(contents, parsed_corners)
    final_bytes = deskewed_bytes if is_deskewed else contents

    filename = f"manual_scan_{uuid.uuid4().hex[:8]}.jpg"
    uploaded_cover_url = gcs_service.upload_cover(final_bytes, filename)

    return {
        "status": "success",
        "coverUrl": uploaded_cover_url,
        "filename": filename
    }


@app.post("/api/analyze-deskewed")
async def analyze_deskewed_endpoint(coverUrl: str):
    rel_path = coverUrl.lstrip("/")
    if not os.path.exists(rel_path):
        raise HTTPException(status_code=404, detail="Deskewed image file not found.")

    with open(rel_path, "rb") as f:
        final_bytes = f.read()

    filename = os.path.basename(rel_path)
    extracted_metadata = gemini_service.analyze_album_cover(final_bytes, filename=filename)
    extracted_metadata["coverUrl"] = coverUrl
    extracted_metadata["deskewedCoverUrl"] = coverUrl
    extracted_metadata["deskewed"] = True

    artist = extracted_metadata.get("artist", "")
    title = extracted_metadata.get("albumTitle", "")
    if artist and title:
        asset_key = f"{sanitize_cache_key(artist)}_{sanitize_cache_key(title)}"
        assets = discogs_service.fetch_all_release_assets(artist, title, cover_url=coverUrl)
        if assets:
            db.firestore.save_release_assets(asset_key, assets)

    duplicate_result = DuplicateEngine.check_duplicate(
        extracted_metadata,
        db.get_all_records(),
        db.get_wishlist()
    )

    return {
        "status": "success",
        "metadata": extracted_metadata,
        "duplicateCheck": duplicate_result,
        "deskewed": True
    }

@app.post("/api/manual-deskew")
async def manual_deskew_endpoint(
    file: UploadFile = File(...),
    corners: str = Form(...)
):
    contents = await file.read()
    try:
        parsed_corners = json.loads(corners)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid corners format. Must be JSON array of 4 coordinate pairs.")

    deskewed_bytes, is_deskewed = deskew_service.manual_deskew_image(contents, parsed_corners)
    final_bytes = deskewed_bytes if is_deskewed else contents

    filename = f"manual_scan_{uuid.uuid4().hex[:8]}.jpg"
    uploaded_cover_url = gcs_service.upload_cover(final_bytes, filename)

    extracted_metadata = gemini_service.analyze_album_cover(final_bytes, filename=filename)
    extracted_metadata["coverUrl"] = uploaded_cover_url
    extracted_metadata["deskewedCoverUrl"] = uploaded_cover_url
    extracted_metadata["deskewed"] = True


    artist = extracted_metadata.get("artist", "")
    title = extracted_metadata.get("albumTitle", "")
    if artist and title:
        asset_key = f"{sanitize_cache_key(artist)}_{sanitize_cache_key(title)}"
        assets = discogs_service.fetch_all_release_assets(artist, title, cover_url=uploaded_cover_url)
        if assets:
            db.firestore.save_release_assets(asset_key, assets)

    duplicate_result = DuplicateEngine.check_duplicate(
        extracted_metadata,
        db.get_all_records(),
        db.get_wishlist()
    )

    return {
        "status": "success",
        "metadata": extracted_metadata,
        "duplicateCheck": duplicate_result,
        "deskewed": True
    }

@app.post("/api/spin")
async def log_spin(req: LogSpinRequest):
    spin_entry = db.log_spin(req.recordId, req.notes or "")
    rec = db.get_record_by_id(req.recordId)
    return {"status": "success", "spin": spin_entry, "record": rec}

@app.post("/api/records")
async def add_record(req: AddRecordRequest, background_tasks: BackgroundTasks):
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
    
    # Trigger AI Chronicle refresh asynchronously in the background so API responds instantly (< 50ms)
    background_tasks.add_task(classical_service.get_chronicle_data, db.get_all_records(), force_ai_refresh=True)

    return {"status": "success", "record": new_rec}

@app.delete("/api/records/{record_id}")
async def delete_record_endpoint(record_id: str, background_tasks: BackgroundTasks):
    success = db.delete_record(record_id)
    if success:
        background_tasks.add_task(classical_service.get_chronicle_data, db.get_all_records(), force_ai_refresh=True)
        return {"status": "success", "message": f"Record {record_id} deleted."}
    raise HTTPException(status_code=404, detail="Record not found.")

@app.post("/api/fetch-official-cover")
async def fetch_official_cover_endpoint(req: FetchCoverRequest):
    img_url = discogs_service.fetch_official_cover(req.artist, req.title, cover_url=req.coverUrl)
    return {"status": "success", "coverUrl": img_url}

@app.post("/api/fetch-release-assets")
async def fetch_release_assets_endpoint(req: FetchCoverRequest):
    asset_key = f"{sanitize_cache_key(req.artist)}_{sanitize_cache_key(req.title)}"
    
    # Check Firestore cache if forceRefresh is False
    if not req.forceRefresh:
        cached_assets = db.firestore.get_release_assets(asset_key)
        if cached_assets:
            return {"status": "success", "assets": cached_assets, "cached": True}

    target_cover = req.coverUrl
    if not target_cover:
        for r in db.get_all_records():
            if r.get("title") == req.title or r.get("artist") == req.artist:
                target_cover = r.get("coverUrl")
                break

    assets = discogs_service.fetch_all_release_assets(req.artist, req.title, cover_url=target_cover)
    if assets:
        db.firestore.save_release_assets(asset_key, assets)

    return {"status": "success", "assets": assets, "cached": False}

GUIDE_CACHE_DIR = os.path.join(os.path.dirname(__file__), "data_store", "listening_guides")
os.makedirs(GUIDE_CACHE_DIR, exist_ok=True)

def sanitize_cache_key(name: str) -> str:
    cleaned = re.sub(r'[^\w\s-]', '', name).strip().lower()
    return re.sub(r'[-\s]+', '_', cleaned)

@app.post("/api/listening-guide")
async def get_listening_guide(req: ListeningGuideRequest):
    guide_key = f"{sanitize_cache_key(req.artist)}_{sanitize_cache_key(req.albumTitle)}"
    
    # 1. Check Firestore cache if forceRefresh is False
    if not req.forceRefresh:
        cached_guide = db.firestore.get_listening_guide(guide_key)
        if cached_guide:
            return {"status": "success", "guide": cached_guide, "cached": True}

    # 2. Check local disk cache fallback
    cache_path = os.path.join(GUIDE_CACHE_DIR, f"{guide_key}.json")
    if not req.forceRefresh and os.path.exists(cache_path):
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                guide_data = json.load(f)
                db.firestore.save_listening_guide(guide_key, guide_data)
                return {"status": "success", "guide": guide_data, "cached": True}
        except Exception:
            pass

    # 3. Call Gemini 3.6 Flash to generate fresh guide
    guide = gemini_service.generate_listening_guide(req.artist, req.albumTitle)
    if guide:
        db.firestore.save_listening_guide(guide_key, guide)
        try:
            with open(cache_path, "w", encoding="utf-8") as f:
                json.dump(guide, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

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

@app.post("/api/chat/stream")
async def chat_stream_endpoint(req: ChatAlbumRequest):
    grounding_ctx = get_local_grounding_context(req.artist, req.albumTitle)
    record_ctx = grounding_ctx.get("recordDetails") if isinstance(grounding_ctx, dict) else None
    return StreamingResponse(
        gemini_service.stream_chat_response(req.message, record_ctx),
        media_type="text/event-stream"
    )

@app.post("/api/admin/seed-firestore")
async def seed_firestore_endpoint():
    all_recs = db.get_all_records()
    success, err_msg = db.firestore.save_all_records_batch(all_recs)
    return {
        "status": "success" if success else "failed",
        "recordsCount": len(all_recs),
        "errorDetails": err_msg,
        "databaseId": db.firestore.database_id,
        "projectId": db.firestore.project_id
    }

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

@app.get("/api/backup")
async def export_backup_endpoint():
    data = db.export_backup()
    return JSONResponse(
        content=data,
        headers={
            "Content-Disposition": f"attachment; filename=vinyl_vault_backup_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        }
    )

@app.post("/api/restore")
async def restore_backup_endpoint(file: UploadFile = File(...)):
    contents = await file.read()
    try:
        data = json.loads(contents)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON backup file.")

    res = db.restore_backup(data)
    return {"status": "success", "restored": res}

@app.post("/api/restore-sample-data")
async def restore_sample_data_endpoint():
    res = db.restore_sample_data()
    return {"status": "success", "restored": res}

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
