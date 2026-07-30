# DEFINE

## [2026-07-30 17:03:00] TODO List

- [x] `[backend]` Remove `@app.on_event("startup")` hook from `main.py` so Uvicorn binds instantly to port 8080.
- [x] `[backend]` Refactor `database.py` to add `_has_synced_firestore` flag and perform lazy Firestore sync when requested.
- [x] `[backend]` Update `GET /api/records` in `main.py` to trigger on-demand Firestore sync.
- [x] `[testing]` Test Docker container build (`docker build -t vinyl-vault:test .`).
- [x] `[testing]` Test Docker container health check and instant startup on port 8080 via OrbStack.
