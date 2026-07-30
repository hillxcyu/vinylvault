# ACTION

## [2026-07-30 20:22:20] Uploaded Cover Image Preservation Log

1. **[2026-07-30 20:22:37] Updated `main.py`**:
   - Fixed `/api/scan` to preserve `extracted_metadata["coverUrl"] = uploaded_cover_url` without overwriting with Discogs images.
   - Added `POST /api/upload-cover` endpoint for direct GCS photo uploads.
2. **[2026-07-30 20:22:47] Updated `static/index.html`**:
   - Updated `rescanUploadPhoto()` to invoke `POST /api/upload-cover` and set the record's `coverUrl` directly.
3. **[2026-07-30 20:22:57] Tested Upload Endpoint**:
   - Verified `POST /api/upload-cover` returns `HTTP 200 OK` with valid cover URL.

