# PLAN

## [2026-07-30 16:59:00] Cloud Run Fast Startup & Lazy On-Demand /api/records Firestore Sync [COMPLETED]


### Goal
Fix Cloud Run container startup failure (`PORT=8080` health check timeout) by removing all blocking startup event handlers from `main.py` and deferring Firestore synchronization to only when the `GET /api/records` endpoint is explicitly invoked by the client.

---

### Proposed Plan

1. **Remove Startup Event in `main.py`**
   - Remove `@app.on_event("startup")` in [main.py](file:///Users/hill/src/vinylvault/main.py) so FastAPI and Uvicorn start immediately (< 50ms) and bind to `0.0.0.0:${PORT}` without waiting for network I/O.

2. **Refactor Firestore Sync to On-Demand in `database.py` & `main.py`**
   - Add a lazy sync flag `_has_synced_firestore` to `VinylDatabase` in [database.py](file:///Users/hill/src/vinylvault/database.py).
   - In `get_records()`, if Firestore sync has not occurred yet, run `sync_firestore_on_startup()` on demand when `GET /api/records` is called.

3. **Verify Local & Docker Container Execution**
   - Run integration tests (`./test_local_integration.sh`).
   - Test Docker build & local container startup (`docker build` and `docker run -p 8080:8080`).
