# DEFINE

## [2026-07-30 18:04:30] TODO List

- [x] `[backend]` Implement `GCSStorageManager` in `gcs_service.py` targeting bucket `gs://universal-trail-492014-n5-vinyl-vault-data/covers/`.
- [x] `[script]` Create `upload_catalog_covers_to_gcs.py` to upload all 48 catalog covers to GCS and update Firestore records.
- [x] `[backend]` Update `/api/scan`, `/api/crop-deskew`, and `/api/manual-deskew` in `main.py` to upload user scans directly to GCS.
- [x] `[backend]` Add `/api/covers/{filename}` image proxy/serving endpoint in `main.py`.
- [x] `[frontend]` Add `onerror` graceful image fallback handlers in `static/index.html`.
- [x] `[config]` Exclude static cover directories from Docker image context in `.dockerignore` and `.gitignore`.
- [x] `[testing]` Execute GCS migration script and run integration tests (`./test_local_integration.sh`).
