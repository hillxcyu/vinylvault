# PLAN

## [2026-07-30 18:03:00] Unified Google Cloud Storage (GCS) for All Album Covers (Original 48 & Scans) [COMPLETED]


### Goal
Establish a single, consistent, persistent storage architecture using Google Cloud Storage (GCS) for **ALL album covers** (both the original 48 catalog covers and new user scans), removing heavy image assets from the Docker image while guaranteeing zero image loss across Cloud Run revisions.

---

### Proposed Plan

1. **Implement `GCSStorageManager` in `gcs_service.py`**
   - Create `gcs_service.py` with `GCSStorageManager`.
   - Read `GCS_BUCKET_NAME` (defaults to `$PROJECT_ID-vinyl-vault-data`).
   - Implement `upload_cover(file_bytes, filename)` returning public GCS URL (`https://storage.googleapis.com/{bucket_name}/covers/{filename}`).
   - Include local disk fallback (`data_store/covers/`) for offline local development.

2. **Migrate Original 48 Covers to GCS & Remove from Docker Context**
   - Create `upload_catalog_covers_to_gcs.py` to seed/upload all 48 original covers to GCS bucket `covers/`.
   - Update Firestore records so all 48 catalog covers point to permanent GCS URLs (`https://storage.googleapis.com/{bucket_name}/covers/shopping_cover_X.jpg`).
   - Add `static/extracted_covers/` and `static/uploads/` to `.gitignore` / `.dockerignore` so images are not baked into the Docker container image.

3. **Update Upload & Scan Workflows in `main.py`**
   - Update `/api/scan`, `/api/crop-deskew`, `/api/manual-deskew`, and `add_record` (`/api/records`) in [main.py](file:///Users/hill/src/vinylvault/main.py) to upload scanned images directly to GCS via `gcs_service.upload_cover()`.

4. **Add Endpoint Proxy / Fallback in `main.py`**
   - Add `/api/covers/{filename}` route in [main.py](file:///Users/hill/src/vinylvault/main.py) to serve cover images reliably with caching.

---

### Verification Plan
- Run `upload_catalog_covers_to_gcs.py` to seed GCS bucket and update Firestore records.
- Verify `docker build` image size is drastically reduced (no baked image files).
- Test image uploads and scans via `/api/scan` and `/api/records`.
