# DEFINE

## [2026-07-30 20:22:15] TODO List

- [x] `[backend]` Preserve `extracted_metadata["coverUrl"] = uploaded_cover_url` in `/api/scan` in `main.py`.
- [x] `[backend]` Add `POST /api/upload-cover` route in `main.py` for direct GCS photo uploads.
- [x] `[frontend]` Update `rescanUploadPhoto()` in `static/index.html` to call `POST /api/upload-cover`.
- [x] `[testing]` Test `POST /api/upload-cover` locally.
- [x] `[deployment]` Stage, commit, push to GitHub, and restart local Docker container + trigger Cloud Run deploy.
