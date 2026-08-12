import os
os.environ["GOOGLE_CLOUD_PROJECT"] = "universal-trail-492014-n5"
os.environ["GOOGLE_CLOUD_LOCATION"] = "global"
os.environ["FIRESTORE_DATABASE_ID"] = "vinylvault-hk"
os.environ["GCS_BUCKET_NAME"] = "universal-trail-492014-n5-vinyl-vault-hk-data"


container_adc = "/root/.config/gcloud/application_default_credentials.json"
host_adc = os.path.expanduser("~/.config/gcloud/application_default_credentials.json")

if os.path.exists(container_adc):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = container_adc
elif os.path.exists(host_adc):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = host_adc


import uuid
import json
import re
import base64
import logging
import urllib.request
import asyncio
from datetime import datetime, timezone




from fastapi import FastAPI, UploadFile, File, Form, Query, HTTPException, BackgroundTasks



from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, StreamingResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from database import db
from gemini_service import gemini_service
from discogs_service import discogs_service
from deskew_service import deskew_service
from classical_service import classical_service
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

from starlette.exceptions import HTTPException as StarletteHTTPException

class RedirectingStaticFiles(StaticFiles):
    async def get_response(self, path: str, scope):
        try:
            return await super().get_response(path, scope)
        except (HTTPException, StarletteHTTPException) as exc:
            if exc.status_code == 404:
                clean_fn = os.path.basename(path)
                if clean_fn and ("extracted_covers" in path or "uploads" in path or clean_fn.endswith((".jpg", ".png", ".jpeg"))):
                    gcs_url = f"https://storage.googleapis.com/{gcs_service.bucket_name}/covers/{clean_fn}"
                    return RedirectResponse(url=gcs_url, status_code=307)
            raise exc


static_dir = os.path.join(os.path.dirname(__file__), "static")
covers_dir = os.path.join(static_dir, "extracted_covers")
os.makedirs(static_dir, exist_ok=True)
os.makedirs(covers_dir, exist_ok=True)
app.mount("/static", RedirectingStaticFiles(directory=static_dir), name="static")


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
    originalScannedCoverUrl: Optional[str] = None
    catalogNumber: Optional[str] = None
    label: Optional[str] = None
    country: Optional[str] = None
    formatDetails: Optional[str] = "Standard Black Vinyl"
    listeningGuide: Optional[Dict[str, Any]] = None
    pressings: Optional[List[Dict[str, Any]]] = None




class ListeningGuideRequest(BaseModel):
    artist: str
    albumTitle: str
    catalogNumber: Optional[str] = None
    label: Optional[str] = None
    country: Optional[str] = None
    recordId: Optional[str] = None
    forceRefresh: Optional[bool] = False

class PronounceRequest(BaseModel):

    text: str

class FetchCoverRequest(BaseModel):
    artist: str
    title: str
    coverUrl: Optional[str] = None
    catalogNumber: Optional[str] = None
    country: Optional[str] = None
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

class UpdateCoverPayload(BaseModel):
    coverUrl: str

@app.post("/api/records/{record_id}/rescan-cover")
async def rescan_record_cover_endpoint(record_id: str):
    rec = db.get_record_by_id(record_id)
    if not rec:
        raise HTTPException(status_code=404, detail="Record not found")

    artist = rec.get("artist", "")
    title = rec.get("title", "")
    catno = rec.get("catalogNumber", "")

    info = discogs_service.fetch_release_info(
        artist,
        title,
        cover_url=rec.get("coverUrl"),
        catalog_number=catno,
        country=rec.get("country", "Japan")
    )
    official_art = info.get("coverUrl")

    if official_art:
        rec["coverUrl"] = official_art
        if info.get("releaseYear") and info.get("releaseYear") > 1900:
            rec["releaseYear"] = info.get("releaseYear")
        if info.get("catalogNumber") and not rec.get("catalogNumber"):
            rec["catalogNumber"] = info.get("catalogNumber")
        if info.get("country") and not rec.get("country"):
            rec["country"] = info.get("country")

        db.update_record(rec)
        return {
            "status": "success",
            "message": f"Successfully fetched official cover art & metadata for '{title}'",
            "coverUrl": official_art,
            "record": rec
        }

    else:
        raise HTTPException(status_code=404, detail="No official cover art found for this record")



@app.post("/api/records/{record_id}/reanalyze")
async def reanalyze_record_metadata_endpoint(record_id: str):
    rec = db.get_record_by_id(record_id)
    if not rec:
        raise HTTPException(status_code=404, detail="Record not found")

    # Re-analyze MUST always use the default scanned GCS cover art image
    scanned_gcs_url = rec.get("originalScannedCoverUrl")
    if not scanned_gcs_url or "storage.googleapis.com" not in scanned_gcs_url:
        if rec.get("coverUrl") and "storage.googleapis.com" in rec.get("coverUrl"):
            scanned_gcs_url = rec.get("coverUrl")
        else:
            for a in rec.get("assets", []):
                url = a.get("url", "")
                if "storage.googleapis.com" in url:
                    scanned_gcs_url = url
                    break

    if not scanned_gcs_url:
        scanned_gcs_url = rec.get("coverUrl", "")

    if not scanned_gcs_url or "placeholder" in scanned_gcs_url:
        raise HTTPException(status_code=400, detail="Record has no valid cover image stored on GCS to re-analyze")

    image_bytes = gcs_service.download_gcs_cover_bytes(scanned_gcs_url)

    if not image_bytes:
        raise HTTPException(status_code=400, detail="Failed to retrieve GCS cover image for re-analysis. Please upload or snap a new cover photo.")



    try:
        # 1. Run upgraded Gemini Vision AI with double-checked label & catalog grounding
        extracted = gemini_service.analyze_album_cover(image_bytes, filename=f"reanalyze_{record_id}.jpg")
    except Exception as err:
        logger.error(f"Error in Gemini Vision AI during re-analysis: {err}")
        raise HTTPException(status_code=500, detail=f"Gemini AI Vision error: {str(err)}")

    # 2. Query Discogs using double-checked catalog number & label
    artist = extracted.get("artist") or rec.get("artist")
    title = extracted.get("albumTitle") or rec.get("title")
    catno = extracted.get("catalogNumber") or rec.get("catalogNumber")
    country = extracted.get("country") or rec.get("country", "Japan")

    discogs_info = {}
    try:
        discogs_info = discogs_service.fetch_release_info(
            artist,
            title,
            cover_url=scanned_gcs_url,
            catalog_number=catno,
            country=country
        )
    except Exception as err:
        logger.warning(f"Discogs release info fetch warning during re-analysis: {err}")

    # 3. Update record fields with fresh double-checked metadata
    if extracted.get("artist"): rec["artist"] = extracted["artist"]
    if extracted.get("albumTitle"): rec["title"] = extracted["albumTitle"]
    if extracted.get("label"): rec["label"] = extracted["label"]
    if extracted.get("catalogNumber"): rec["catalogNumber"] = extracted["catalogNumber"]
    if extracted.get("country"): rec["country"] = extracted["country"]
    if extracted.get("genre"): rec["genre"] = extracted["genre"]

    if extracted.get("releaseYear"):
        rec["releaseYear"] = extracted["releaseYear"]
    elif discogs_info.get("releaseYear") and discogs_info.get("releaseYear") > 1900:
        rec["releaseYear"] = discogs_info["releaseYear"]

    if extracted.get("listeningGuide"):
        rec["listeningGuide"] = extracted["listeningGuide"]
        guide_key = f"{sanitize_cache_key(rec.get('artist', ''))}_{sanitize_cache_key(rec.get('title', ''))}"
        db.firestore.save_listening_guide(guide_key, extracted["listeningGuide"])



    if discogs_info.get("coverUrl") and "shopping_cover_2.jpg" not in discogs_info["coverUrl"]:
        rec["coverUrl"] = discogs_info["coverUrl"]

    db.update_record(rec)


    return {
        "status": "success",
        "message": f"Successfully re-analyzed metadata for '{rec.get('title')}'",
        "record": rec,
        "extracted": extracted
    }


@app.post("/api/admin/repair-covers")

async def repair_covers_admin_endpoint():
    recs = db.get_all_records(sync_if_needed=True)
    updated_count = 0

    for r in recs:
        old_url = r.get("coverUrl", "")
        rec_id = r.get("id", "")
        artist = r.get("artist", "")
        title = r.get("title", "")
        new_url = None

        if old_url.startswith("/static/extracted_covers/"):
            fname = os.path.basename(old_url)
            new_url = f"https://storage.googleapis.com/{gcs_service.bucket_name}/covers/{fname}"

        # Fetch unique high-res official artwork for user scans & records using duplicate fallback
        if "rec-user" in rec_id or "shopping_cover_2.jpg" in old_url or old_url.startswith("/static/uploads/") or not old_url:
            official_url = discogs_service.fetch_official_cover(artist, title)
            if official_url and "shopping_cover_2.jpg" not in official_url:
                new_url = official_url

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





_daily_poster_cache = {}

@app.get("/api/daily-poster")
async def get_daily_poster(date_str: Optional[str] = None):
    import hashlib
    if not date_str:
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    records = db.get_all_records()
    if not records:
        return {"error": "No records in vault"}

    if date_str in _daily_poster_cache:
        return _daily_poster_cache[date_str]

    # Deterministic selection based on date string hash
    hash_val = int(hashlib.md5(date_str.encode('utf-8')).hexdigest(), 16)
    selected_index = hash_val % len(records)
    selected_record = records[selected_index]

    # Generate insights via Gemini in thread
    insights = await asyncio.to_thread(gemini_service.generate_daily_poster_insights, selected_record)

    result = {
        "date": date_str,
        "record": selected_record,
        "headline": insights.get("headline", f"Featured Vinyl: {selected_record.get('title')}"),
        "listeningHighlight": insights.get("listeningHighlight", ""),
        "trivia": insights.get("trivia", ""),
        "pairingNote": insights.get("pairingNote", "")
    }

    _daily_poster_cache[date_str] = result
    return result


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

@app.get("/api/spins")
async def get_spins_endpoint(limit: int = 10, offset: int = 0):
    spins = db.get_spins_log() or []
    
    def parse_time(s):
        ts = s.get("timestamp") or s.get("spunAt") or s.get("time") or ""
        return str(ts)

    sorted_spins = sorted(spins, key=parse_time, reverse=True)
    
    if not sorted_spins:
        records = db.get_all_records()
        fallback_spins = []
        for r in records:
            if r.get("spinsCount", 0) > 0 or r.get("lastSpunAt"):
                fallback_spins.append({
                    "id": f"spin_{r.get('id')}",
                    "recordId": r.get("id"),
                    "title": r.get("title", "Unknown Title"),
                    "artist": r.get("artist", "Unknown Artist"),
                    "coverUrl": r.get("coverUrl") or "",
                    "timestamp": r.get("lastSpunAt") or "2026-08-01T12:00:00Z",
                    "catalogNumber": r.get("catalogNumber") or "",
                    "notes": f"Spun {r.get('spinsCount', 1)} time(s) on turntable."
                })
        sorted_spins = sorted(fallback_spins, key=parse_time, reverse=True)

    paginated_spins = sorted_spins[offset : offset + limit]
    has_more = (offset + limit) < len(sorted_spins)
    
    return {
        "status": "success",
        "spins": paginated_spins,
        "total": len(sorted_spins),
        "offset": offset,
        "limit": limit,
        "hasMore": has_more
    }


def build_duplicate_result(metadata: dict, crate_records: list = None) -> dict:
    if crate_records is None:
        crate_records = db.get_all_records()

    is_in_crate = metadata.get("isAlreadyInCrate", False)
    match_id = metadata.get("crateMatchId")
    reason = metadata.get("crateMatchReason") or ""
    
    matching_rec = None
    if match_id and crate_records:
        matching_rec = next((r for r in crate_records if r.get("id") == match_id), None)
        
    if not matching_rec and crate_records:
        title = (metadata.get("albumTitle") or metadata.get("title") or "").lower().strip()
        artist = (metadata.get("artist") or "").lower().strip()
        catno = (metadata.get("catalogNumber") or "").lower().strip()
        catno_clean = "".join(c for c in catno if c.isalnum())
        
        for r in crate_records:
            r_cat = (r.get("catalogNumber") or "").lower().strip()
            r_cat_clean = "".join(c for c in r_cat if c.isalnum())
            if catno_clean and len(catno_clean) >= 3 and catno_clean == r_cat_clean:
                matching_rec = r
                break

            for p in r.get("pressings", []):
                p_cat = (p.get("catalogNumber") or "").lower().strip()
                p_cat_clean = "".join(c for c in p_cat if c.isalnum())
                if catno_clean and len(catno_clean) >= 3 and catno_clean == p_cat_clean:
                    matching_rec = r
                    break
            if matching_rec:
                break

            r_title = (r.get("title") or "").lower().strip()
            r_artist = (r.get("artist") or "").lower().strip()
            if title and artist and title == r_title and artist == r_artist:
                matching_rec = r
                break


    if is_in_crate or matching_rec:
        rec_title = matching_rec.get("title", "") if matching_rec else metadata.get("albumTitle", "")
        fallback_msg = f'Matches record "{rec_title}".' if rec_title else 'Matches existing album in collection.'
        return {
            "status": "EXACT_MATCH",
            "matchingRecord": matching_rec,
            "message": f"ALREADY IN YOUR COLLECTION! {reason if reason else fallback_msg}"
        }


    if metadata.get("isWishlistMatch"):
        return {
            "status": "WISHLIST_MATCH",
            "message": metadata.get("wishlistMatchReason") or "This album is currently on your wishlist!"
        }

    return {
        "status": "NEW_RECORD",
        "message": f"NEW ALBUM DISCOVERED! Clean copy verified: '{metadata.get('artist', '')} - {metadata.get('albumTitle', '')}'."
    }

@app.post("/api/check-duplicate")
async def check_duplicate(query: DuplicateCheckQuery):
    result = build_duplicate_result(query.dict(), db.get_all_records())
    return result

def is_missing_or_placeholder_cover(cover_url: Optional[str]) -> bool:
    if not cover_url or not isinstance(cover_url, str):
        return True
    cover_url_lower = cover_url.lower().strip()
    if not cover_url_lower:
        return True
    return (
        "placeholder" in cover_url_lower
        or "shopping_cover_2.jpg" in cover_url_lower
        or cover_url_lower.endswith(".svg")
        or "data:image/svg+xml" in cover_url_lower
    )

@app.post("/api/scan/corners")
async def scan_corners(file: UploadFile = File(...)):
    contents = await file.read()
    logger.info("Call A: Running fast album cover corner detection...")
    detected_corners = await asyncio.to_thread(deskew_service.detect_corners, contents, gemini_service)
    return {"corners": detected_corners}

@app.post("/api/scan/duplicate-check")
async def scan_duplicate_check(file: UploadFile = File(...)):
    contents = await file.read()
    crate_records = db.get_all_records()
    logger.info("Call B: Running fast duplicate check against crate inventory...")
    fast_dup = await asyncio.to_thread(gemini_service.check_album_duplicate, contents, crate_records)
    metadata = {
        "artist": fast_dup.get("artist", ""),
        "albumTitle": fast_dup.get("albumTitle", ""),
        "isAlreadyInCrate": fast_dup.get("isAlreadyInCrate", False),
        "crateMatchId": fast_dup.get("crateMatchId"),
        "crateMatchReason": fast_dup.get("crateMatchReason", "")
    }
    duplicate_result = build_duplicate_result(metadata, crate_records)
    return {
        "metadata": metadata,
        "duplicateCheck": duplicate_result
    }

@app.post("/api/scan/deep-metadata")
async def scan_deep_metadata(file: UploadFile = File(...)):
    contents = await file.read()
    logger.info("Call C: Running fast album release metadata extraction...")
    deep_meta = await asyncio.to_thread(gemini_service.extract_album_metadata, contents)
    artist = deep_meta.get("artist", "")
    title = deep_meta.get("albumTitle", "")
    catno = deep_meta.get("catalogNumber", "")
    country = deep_meta.get("country", "Japan")
    if artist and title:
        opt_raw_bytes = gemini_service.downsample_image_bytes(contents, max_dim=1024, quality=85)
        raw_b64 = f"data:image/jpeg;base64,{base64.b64encode(opt_raw_bytes).decode('utf-8')}"
        info = await asyncio.to_thread(
            discogs_service.fetch_release_info,
            artist,
            title,
            cover_url=raw_b64,
            catalog_number=catno,
            country=country
        )
        if info.get("coverUrl"):
            deep_meta["officialCoverUrl"] = info["coverUrl"]
        if not deep_meta.get("releaseYear") and info.get("releaseYear"):
            deep_meta["releaseYear"] = info["releaseYear"]
        if not deep_meta.get("catalogNumber") and info.get("catalogNumber"):
            deep_meta["catalogNumber"] = info["catalogNumber"]
    logger.info(f"Call C deep-metadata result: releaseYear={deep_meta.get('releaseYear')}, artist='{deep_meta.get('artist')}', title='{deep_meta.get('albumTitle')}', catno='{deep_meta.get('catalogNumber')}'")
    return {"metadata": deep_meta}

@app.post("/api/scan")
async def scan_cover(file: UploadFile = File(...), skip_deskew: bool = Query(False)):
    contents = await file.read()
    crate_records = db.get_all_records()

    logger.info("Launching 3 concurrent Gemini calls for scan analysis (Call A: Corners, Call B: Fast Duplicate, Call C: Fast Release Meta)...")

    # 1. Issue Call A (Corners), Call B (Fast Duplicate Check), and Call C (Fast Release Metadata) concurrently in parallel
    corners_task = asyncio.to_thread(deskew_service.detect_corners, contents, gemini_service)
    duplicate_task = asyncio.to_thread(gemini_service.check_album_duplicate, contents, crate_records)
    deep_meta_task = asyncio.to_thread(gemini_service.extract_album_metadata, contents)

    detected_corners_res, fast_dup_res, deep_meta_res = await asyncio.gather(
        corners_task, duplicate_task, deep_meta_task, return_exceptions=True
    )

    detected_corners = detected_corners_res if isinstance(detected_corners_res, list) else None
    fast_dup = fast_dup_res if isinstance(fast_dup_res, dict) else {}
    deep_meta = deep_meta_res if isinstance(deep_meta_res, dict) else {}

    # Combine fast duplicate findings with deep metadata
    extracted_metadata = {**deep_meta}
    if not extracted_metadata.get("artist") and fast_dup.get("artist"):
        extracted_metadata["artist"] = fast_dup.get("artist")
    if not extracted_metadata.get("albumTitle") and fast_dup.get("albumTitle"):
        extracted_metadata["albumTitle"] = fast_dup.get("albumTitle")

    extracted_metadata["isAlreadyInCrate"] = fast_dup.get("isAlreadyInCrate", False)
    extracted_metadata["crateMatchId"] = fast_dup.get("crateMatchId")
    extracted_metadata["crateMatchReason"] = fast_dup.get("crateMatchReason", "")

    # 2. Perspective-warp cover image using detected corners
    deskewed_bytes = deskew_service.warp_image_from_normalized_corners(contents, detected_corners)

    # Downsample preview base64 images to 1024px max dimension for fast transmission (<200KB vs 7MB)
    opt_raw_bytes = gemini_service.downsample_image_bytes(contents, max_dim=1024, quality=85)
    opt_deskewed_bytes = gemini_service.downsample_image_bytes(deskewed_bytes, max_dim=1024, quality=85)

    raw_b64 = f"data:image/jpeg;base64,{base64.b64encode(opt_raw_bytes).decode('utf-8')}"
    deskewed_b64 = f"data:image/jpeg;base64,{base64.b64encode(opt_deskewed_bytes).decode('utf-8')}"

    extracted_metadata["coverUrl"] = deskewed_b64
    extracted_metadata["rawCoverUrl"] = raw_b64
    extracted_metadata["deskewed"] = True

    # 3. Store optional Discogs official cover suggestion and fallback releaseYear asynchronously
    artist = extracted_metadata.get("artist", "")
    title = extracted_metadata.get("albumTitle", "")
    catno = extracted_metadata.get("catalogNumber", "")
    country = extracted_metadata.get("country", "Japan")
    if artist and title:
        discogs_info = await asyncio.to_thread(
            discogs_service.fetch_release_info,
            artist,
            title,
            cover_url=deskewed_b64,
            catalog_number=catno,
            country=country
        )
        if discogs_info.get("coverUrl"):
            extracted_metadata["officialCoverUrl"] = discogs_info["coverUrl"]
        if not extracted_metadata.get("releaseYear") and discogs_info.get("releaseYear"):
            extracted_metadata["releaseYear"] = discogs_info["releaseYear"]
        if not extracted_metadata.get("catalogNumber") and discogs_info.get("catalogNumber"):
            extracted_metadata["catalogNumber"] = discogs_info["catalogNumber"]

    logger.info(f"Scan analysis complete: releaseYear={extracted_metadata.get('releaseYear')}, artist='{extracted_metadata.get('artist')}', title='{extracted_metadata.get('albumTitle')}'")

    # 4. Automatically run duplicate check on extracted metadata using pre-fetched crate_records
    duplicate_result = build_duplicate_result(
        extracted_metadata,
        crate_records
    )

    return {
        "metadata": extracted_metadata,
        "duplicateCheck": duplicate_result,
        "rawCoverUrl": raw_b64,
        "coverUrl": deskewed_b64,
        "detectedCorners": detected_corners
    }



@app.post("/api/upload-cover")
async def upload_cover_direct_endpoint(file: UploadFile = File(...)):
    contents = await file.read()
    raw_b64 = f"data:image/jpeg;base64,{base64.b64encode(contents).decode('utf-8')}"
    return {
        "status": "success",
        "coverUrl": raw_b64
    }

@app.post("/api/detect-corners")
async def detect_corners_endpoint(file: UploadFile = File(...)):
    contents = await file.read()
    corners = deskew_service.detect_corners(contents, gemini_service=gemini_service)
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
    deskewed_b64 = f"data:image/jpeg;base64,{base64.b64encode(final_bytes).decode('utf-8')}"

    return {
        "status": "success",
        "coverUrl": deskewed_b64
    }




@app.post("/api/analyze-deskewed")
async def analyze_deskewed_endpoint(coverUrl: str):
    final_bytes = None
    filename = os.path.basename(coverUrl)

    if coverUrl.startswith("http://") or coverUrl.startswith("https://"):
        def _fetch_url():
            req = urllib.request.Request(
                coverUrl,
                headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
            )
            with urllib.request.urlopen(req, timeout=12) as resp:
                return resp.read()
        try:
            final_bytes = await asyncio.to_thread(_fetch_url)
        except Exception as e:
            logger.warning(f"Error downloading coverUrl from HTTP/GCS: {e}")



    if not final_bytes:
        rel_path = coverUrl.lstrip("/")
        if os.path.exists(rel_path):
            with open(rel_path, "rb") as f:
                final_bytes = f.read()

    if not final_bytes:
        raise HTTPException(status_code=404, detail="Deskewed image file could not be retrieved.")

    extracted_metadata = gemini_service.analyze_album_cover(final_bytes, filename=filename)
    extracted_metadata["coverUrl"] = coverUrl
    extracted_metadata["deskewedCoverUrl"] = coverUrl
    extracted_metadata["deskewed"] = True

    artist = extracted_metadata.get("artist", "")
    title = extracted_metadata.get("albumTitle", "")
    catno = extracted_metadata.get("catalogNumber", "")
    country = extracted_metadata.get("country", "Japan")

    if artist and title:
        asset_key = f"{sanitize_cache_key(artist)}_{sanitize_cache_key(title)}"
        official_img = discogs_service.fetch_official_cover(
            artist,
            title,
            cover_url=coverUrl,
            catalog_number=catno,
            country=country
        )
        if official_img:
            extracted_metadata["officialCoverUrl"] = official_img

    duplicate_result = build_duplicate_result(
        extracted_metadata,
        db.get_all_records()
    )

    # Auto-fill missing cover art for existing record if scanned image exists
    if duplicate_result.get("status") in ["EXACT_MATCH", "VARIANT_MATCH"]:
        matching_rec = duplicate_result.get("matchingRecord")
        if matching_rec and is_missing_or_placeholder_cover(matching_rec.get("coverUrl")):
            scanned_cover = extracted_metadata.get("coverUrl")
            if scanned_cover and not is_missing_or_placeholder_cover(scanned_cover):
                matching_rec["coverUrl"] = scanned_cover
                db.save_records()
                if db.firestore.db:
                    db.firestore.save_record(matching_rec)
                logger.info(f"Updated missing cover art for existing record '{matching_rec.get('title')}' with scanned image: {scanned_cover}")

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

    duplicate_result = build_duplicate_result(
        extracted_metadata,
        db.get_all_records()
    )


    return {
        "status": "success",
        "metadata": extracted_metadata,
        "duplicateCheck": duplicate_result,
        "deskewed": True
    }

@app.get("/api/now_spinning")
async def get_now_spinning():
    ns = db.get_now_spinning()
    return {"status": "success", "nowSpinning": ns}

class NowSpinningRequest(BaseModel):
    recordId: str

@app.post("/api/now_spinning")
async def set_now_spinning(req: NowSpinningRequest):
    rec = db.get_record_by_id(req.recordId)
    if not rec:
        raise HTTPException(status_code=404, detail="Record not found")
    db.log_spin(req.recordId, "Now spinning interactive update")
    ns = db.set_now_spinning(rec)
    return {"status": "success", "nowSpinning": ns}

@app.delete("/api/now_spinning")
@app.post("/api/stop_spinning")
async def stop_spinning():
    db.set_now_spinning(None)
    return {"status": "success", "nowSpinning": None}

@app.post("/api/spin")
async def log_spin(req: LogSpinRequest):
    spin_entry = db.log_spin(req.recordId, req.notes or "")
    rec = db.get_record_by_id(req.recordId)
    if rec:
        db.set_now_spinning(rec)
    return {"status": "success", "spin": spin_entry, "record": rec}


@app.post("/api/records")
async def add_record(req: AddRecordRequest, background_tasks: BackgroundTasks):
    rec_dict = req.dict()
    
    # Idempotency check: prevent duplicate insertions if user clicked 'Add' multiple times
    norm_art = (req.artist or "").strip().lower()
    norm_title = (req.title or "").strip().lower()
    norm_cat = (req.catalogNumber or "").strip().lower()

    if norm_art and norm_title:
        for existing in db.get_all_records():
            ex_art = (existing.get("artist") or "").strip().lower()
            ex_title = (existing.get("title") or "").strip().lower()
            ex_cat = (existing.get("catalogNumber") or "").strip().lower()

            if norm_art == ex_art and norm_title == ex_title:
                if not norm_cat or not ex_cat or norm_cat == ex_cat:
                    if req.coverUrl and "shopping_cover_2.jpg" not in req.coverUrl:
                        existing["coverUrl"] = req.coverUrl
                        existing["originalScannedCoverUrl"] = req.coverUrl
                        db.update_record(existing)

                    logger.info(f"Idempotency catch: Record '{req.title}' by {req.artist} updated with scanned coverUrl.")
                    return {"status": "success", "record": existing, "message": "Record updated in collection"}


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

    # Persist base64 cover image to GCS ONLY when user clicks Add to Crate
    cover_url = rec_dict.get("coverUrl")
    if cover_url and cover_url.startswith("data:image/"):
        try:
            header, encoded = cover_url.split(",", 1)
            img_data = base64.b64decode(encoded)
            ext = ".png" if "png" in header else ".jpg"
            filename = f"cover_{uuid.uuid4().hex[:8]}{ext}"
            persistent_gcs_url = gcs_service.upload_cover(img_data, filename)
            rec_dict["coverUrl"] = persistent_gcs_url
            rec_dict["originalScannedCoverUrl"] = persistent_gcs_url
        except Exception as e:
            logger.error(f"Error persisting base64 cover art to GCS: {e}")

    if req.listeningGuide:
        rec_dict["listeningGuide"] = req.listeningGuide
        guide_key = f"{sanitize_cache_key(req.artist)}_{sanitize_cache_key(req.title)}"
        db.firestore.save_listening_guide(guide_key, req.listeningGuide)

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


@app.post("/api/records/{record_id}/update-cover")
async def update_record_cover_endpoint(record_id: str, req: Dict[str, Any]):
    cover_url = req.get("coverUrl")
    rec = db.get_record_by_id(record_id)
    if not rec:
        raise HTTPException(status_code=404, detail="Record not found.")

    if cover_url and cover_url.startswith("data:image/"):
        try:
            header, encoded = cover_url.split(",", 1)
            img_data = base64.b64decode(encoded)
            ext = ".png" if "png" in header else ".jpg"
            filename = f"cover_{record_id[:8]}_{uuid.uuid4().hex[:4]}{ext}"
            persistent_gcs_url = gcs_service.upload_cover(img_data, filename)
            cover_url = persistent_gcs_url
        except Exception as e:
            logger.error(f"Error persisting base64 cover art to GCS: {e}")

    rec["coverUrl"] = cover_url
    rec["originalScannedCoverUrl"] = cover_url
    db.update_record(rec)

    if db.firestore.db:
        db.firestore.save_record(rec)
    return {"status": "success", "record": rec}


class FetchCoverRequest(BaseModel):
    artist: str
    title: str
    coverUrl: Optional[str] = None
    catalogNumber: Optional[str] = None
    country: Optional[str] = "Japan"
    forceRefresh: Optional[bool] = False

@app.post("/api/fetch-official-cover")
async def fetch_official_cover_endpoint(req: FetchCoverRequest):
    img_url = await asyncio.to_thread(discogs_service.fetch_official_cover, req.artist, req.title, cover_url=req.coverUrl)
    return {"status": "success", "coverUrl": img_url}


@app.post("/api/fetch-release-assets")
async def fetch_release_assets_endpoint(req: FetchCoverRequest):
    asset_key = f"{sanitize_cache_key(req.artist)}_{sanitize_cache_key(req.title)}"
    
    if not req.forceRefresh:
        cached_assets = db.firestore.get_release_assets(asset_key)
        if cached_assets:
            if req.coverUrl and "shopping_cover_2.jpg" not in req.coverUrl:
                has_orig = any(a.get("url") == req.coverUrl or a.get("type") == "📸 Original Jacket" for a in cached_assets)
                if not has_orig:
                    orig_asset = {
                        "type": "📸 Original Jacket",
                        "url": req.coverUrl,
                        "thumbnail": req.coverUrl,
                        "isPrimary": True,
                        "country": req.country or "Original",
                        "comment": "Original Scanned / Uploaded Album Cover"
                    }
                    cached_assets.insert(0, orig_asset)
                    db.firestore.save_release_assets(asset_key, cached_assets)
            return {"status": "success", "assets": cached_assets, "cached": True}


    target_cover = req.coverUrl
    catno = req.catalogNumber
    country = req.country or "Japan"

    norm_title = (req.title or "").strip().lower()
    norm_artist = (req.artist or "").strip().lower()

    if not target_cover or not catno:
        for r in db.get_all_records():
            r_title = (r.get("title") or "").strip().lower()
            r_artist = (r.get("artist") or "").strip().lower()
            if r_title and norm_title and r_artist and norm_artist and r_title == norm_title and r_artist == norm_artist:
                target_cover = target_cover or r.get("coverUrl")
                catno = catno or r.get("catalogNumber")
                country = req.country or r.get("country") or "Japan"
                break

    assets = await asyncio.to_thread(
        discogs_service.fetch_all_release_assets,
        req.artist,
        req.title,
        cover_url=target_cover,
        catalog_number=catno,
        country=country
    )

    if assets:
        db.firestore.save_release_assets(asset_key, assets)

    return {"status": "success", "assets": assets, "cached": False}

@app.get("/api/release-assets/{key}")
async def get_release_assets_by_key(key: str, catno: Optional[str] = None, country: Optional[str] = "Japan"):
    all_recs = db.get_all_records()
    rec = next((r for r in all_recs if r.get("id") == key), None)
    
    if rec:
        artist = rec.get("artist", "")
        title = rec.get("title", "")
        catalog_number = catno or rec.get("catalogNumber", "")
        assets = await asyncio.to_thread(
            discogs_service.fetch_all_release_assets,
            artist,
            title,
            cover_url=rec.get("coverUrl"),
            catalog_number=catalog_number,
            country=country
        )
        return {"status": "success", "assets": assets, "record": rec}

    parts = key.split("_")
    artist = parts[0] if parts else ""
    title = parts[1] if len(parts) > 1 else ""
    assets = await asyncio.to_thread(discogs_service.fetch_all_release_assets, artist, title, catalog_number=catno, country=country)
    return {"status": "success", "assets": assets}



GUIDE_CACHE_DIR = os.path.join(os.path.dirname(__file__), "data_store", "listening_guides")
os.makedirs(GUIDE_CACHE_DIR, exist_ok=True)

def sanitize_cache_key(name: str) -> str:
    cleaned = re.sub(r'[^\w\s-]', '', name).strip().lower()
    return re.sub(r'[-\s]+', '_', cleaned)

@app.post("/api/listening-guide")
async def get_listening_guide(req: ListeningGuideRequest):
    logger.info(f"Received /api/listening-guide request for '{req.artist}' - '{req.albumTitle}' (forceRefresh={req.forceRefresh}, recordId={req.recordId})")
    guide_key = f"{sanitize_cache_key(req.artist)}_{sanitize_cache_key(req.albumTitle)}"
    
    # 0. Check if target record in database already holds listeningGuide on the record object
    if not req.forceRefresh:
        if req.recordId:
            rec = db.get_record_by_id(req.recordId)
            if rec and rec.get("listeningGuide"):
                guide = rec.get("listeningGuide")
                db.firestore.save_listening_guide(guide_key, guide)
                return {"status": "success", "guide": guide, "cached": True}

        all_recs = db.get_all_records()
        norm_req_title = (req.albumTitle or "").strip().lower()
        norm_req_artist = (req.artist or "").strip().lower()
        for r in all_recs:
            r_t = (r.get("title") or "").strip().lower()
            r_a = (r.get("artist") or "").strip().lower()
            if (norm_req_title and (norm_req_title == r_t or norm_req_title in r_t or r_t in norm_req_title)) or (norm_req_artist and (norm_req_artist == r_a or norm_req_artist in r_a or r_a in norm_req_artist)):
                if r.get("listeningGuide"):
                    guide = r.get("listeningGuide")
                    db.firestore.save_listening_guide(guide_key, guide)
                    return {"status": "success", "guide": guide, "cached": True}


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

    # Extract release details (catalog number, label, country) if available
    cat_no = req.catalogNumber
    lbl = req.label
    cntry = req.country

    if req.recordId:
        rec = db.get_record_by_id(req.recordId)
        if rec:
            if not cat_no:
                cat_no = rec.get("catalogNumber") or rec.get("catno")
            if not lbl:
                lbl = rec.get("label")
            if not cntry:
                cntry = rec.get("country")

    # 3. Call Gemini 3.6 Flash to generate fresh guide
    logger.info(f"Invoking Gemini 3.6 Flash + Grounding for listening guide generation: '{req.artist}' - '{req.albumTitle}' (catNo={cat_no}, label={lbl}, country={cntry})")
    guide = gemini_service.generate_listening_guide(
        artist=req.artist, 
        title=req.albumTitle,
        catalog_number=cat_no,
        label=lbl,
        country=cntry
    )
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

    # Priority 1: Check active backend now_spinning state first
    active_ns = db.get_now_spinning()
    if active_ns and isinstance(active_ns, dict) and active_ns.get("record"):
        target_record = active_ns.get("record")

    # Priority 2: Match by exact or strong artist/title if no record is currently spinning
    if not target_record and (artist or title):
        clean_a = re.sub(r'[^\w\s]', '', (artist or "").lower())
        clean_t = re.sub(r'[^\w\s]', '', (title or "").lower())

        for r in all_records:
            r_a = re.sub(r'[^\w\s]', '', r.get("artist", "").lower())
            r_t = re.sub(r'[^\w\s]', '', r.get("title", "").lower())

            if clean_a and clean_t and (clean_a in r_a or r_a in clean_a) and (clean_t in r_t or r_t in clean_t):
                target_record = r
                break

        if not target_record and clean_t and len(clean_t) > 3:
            for r in all_records:
                r_t = re.sub(r'[^\w\s]', '', r.get("title", "").lower())
                if clean_t in r_t or r_t in clean_t:
                    target_record = r
                    break



    safe_key = f"{sanitize_cache_key(artist)}_{sanitize_cache_key(title)}.json"
    cache_path = os.path.join(GUIDE_CACHE_DIR, safe_key)
    guide_data = None
    if os.path.exists(cache_path):
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                guide_data = json.load(f)
        except Exception:
            pass

    # Build complete crate catalog with full metadata for AI collection awareness
    crate_catalog = []
    for r in all_records:
        r_artist = r.get("artist", "Unknown Artist")
        r_title = r.get("title", "Unknown Title")
        label = r.get("label") or (r.get("pressings", [{}])[0].get("label") if r.get("pressings") else None)
        cat_no = r.get("catalogNumber") or (r.get("pressings", [{}])[0].get("catalogNumber") if r.get("pressings") else None)
        year = r.get("releaseYear")
        country = r.get("country")
        
        info = f"{r_artist} - {r_title}"
        details = []
        if label: details.append(f"Label: {label}")
        if cat_no: details.append(f"Cat#: {cat_no}")
        if year: details.append(f"Year: {year}")
        if country: details.append(f"Country: {country}")
        
        if details:
            info += f" [{', '.join(details)}]"
        crate_catalog.append(info)

    return {
        "recordDetails": target_record or {},
        "guideMetadata": guide_data or {},
        "crateCatalog": crate_catalog
    }

class ChatAlbumRequest(BaseModel):
    artist: Optional[str] = ""
    albumTitle: Optional[str] = ""
    message: Optional[str] = ""
    images: Optional[List[str]] = []
    history: Optional[List[Dict[str, str]]] = []

@app.post("/api/chat-album")
async def chat_album_endpoint(req: ChatAlbumRequest):
    grounding_ctx = get_local_grounding_context(req.artist or "", req.albumTitle or "")
    msg = req.message or "Analyze the attached image(s) for this vinyl album."
    reply = gemini_service.chat_about_album(
        req.artist or "",
        req.albumTitle or "",
        msg,
        req.history,
        grounding_context=grounding_ctx,
        images=req.images
    )
    return {"status": "success", "reply": reply}

@app.post("/api/chat/stream")
async def chat_stream_endpoint(req: ChatAlbumRequest):
    grounding_ctx = get_local_grounding_context(req.artist or "", req.albumTitle or "")
    record_ctx = grounding_ctx.get("recordDetails") if isinstance(grounding_ctx, dict) else None
    crate_cat = grounding_ctx.get("crateCatalog") if isinstance(grounding_ctx, dict) else None
    msg = req.message or "Analyze the attached image(s) for this vinyl album."
    return StreamingResponse(
        gemini_service.stream_chat_response(
            message=msg,
            record_context=record_ctx,
            crate_catalog=crate_cat,
            images=req.images
        ),
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

@app.post("/api/pronounce")
async def pronounce_endpoint(req: PronounceRequest):
    if not req.text or not req.text.strip():
        raise HTTPException(status_code=400, detail="Text is required")
    
    clean_text = req.text.strip()
    result = gemini_service.generate_pronunciation(clean_text)
    if result and isinstance(result, dict) and result.get("audio_b64"):
        return {
            "status": "success",
            "audioB64": result["audio_b64"],
            "mimeType": result.get("mime_type", "audio/wav"),
            "model": result.get("model", "gemini-3.1-flash-tts-preview"),
            "voice": result.get("voice", "Aoede")

        }
    else:
        err_msg = result.get("error") if (result and isinstance(result, dict) and result.get("error")) else "Failed to generate audio via gemini-3.1-flash-tts-preview"
        return {"status": "error", "detail": err_msg}



if __name__ == "__main__":

    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
