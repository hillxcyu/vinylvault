# PLAN

## [2026-07-30 20:21:30] Fix Uploaded Cover Image Preservation [COMPLETED]


### Goal
Ensure uploaded cover art images are ALWAYS preserved and used as the primary album cover, without being overwritten by online Discogs image lookups.

---

### Proposed Plan

1. **Fix `/api/scan` in `main.py`**
   - Preserve `extracted_metadata["coverUrl"] = uploaded_cover_url`.
   - Store optional Discogs cover URL in `extracted_metadata["officialCoverUrl"]` without overwriting the user's uploaded photo URL.

2. **Add Direct Upload Endpoint in `main.py`**
   - Add `POST /api/upload-cover`: Uploads user photo directly to GCS bucket (`covers/`) and returns the permanent GCS URL (`https://storage.googleapis.com/...`).

3. **Update Upload Handlers in `static/index.html`**
   - Update `rescanUploadPhoto(input)` to use `POST /api/upload-cover` and immediately update the record's `coverUrl` in Firestore with the newly uploaded image URL.

4. **Testing & Deployment**
   - Test photo upload via curl and verify image URL persistence.
   - Commit, push, and deploy to Cloud Run & local Docker.
