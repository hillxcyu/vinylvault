# PLAN

## [2026-07-30 20:08:00] Discogs Precise Search with Region/CatNo & Top 10 Front Art Picker [COMPLETED]


### Goal
Enhance Discogs cover art search to prioritize catalog numbers (`catno`) and Japan region pressings (`country=Japan`), returning up to 10 top front artwork candidates for easy user selection in the Rescan Cover Art Modal.

---

### Proposed Plan

1. **Update `discogs_service.py`**
   - Update `fetch_all_release_assets(artist, title, cover_url=None, catalog_number=None, country="Japan")`:
     - Query Discogs with `catno={catalog_number}` if available.
     - Query Discogs with `country=Japan` (or user pressing country) for precise regional matching.
     - Collect up to **10 top distinct front cover artwork images** across matching vinyl releases.

2. **Update Backend Endpoint in `main.py`**
   - Update `GET /api/release-assets/{key}` / `GET /api/records/{record_id}/assets` to accept `catalog_number` and `country` parameters, pulling directly from record metadata.

3. **Update Rescan Modal in `static/index.html`**
   - Update `#rescanAssetsGrid` in `#rescanModal` to display up to 10 front artwork options with release details (e.g., "Japan Pressing [IMP-2026-001]").
   - 1-click selection updates the record's `coverUrl` live in Firestore.

4. **Testing & Deployment**
   - Test Discogs search with Japan pressings and catalog numbers via Python test script.
   - Commit, push, and verify Cloud Run deployment.
