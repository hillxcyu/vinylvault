# PLAN

## [2026-07-30 19:49:15] Switch Exclusively to Discogs for Cover Art (Remove iTunes) [COMPLETED]


### Goal
Completely remove iTunes Search API integration and rely exclusively on Discogs API for fetching official vinyl album cover art and release assets.

---

### Proposed Plan

1. **Update `discogs_service.py`**
   - Remove `fetch_itunes_cover` method.
   - Update `fetch_official_cover(artist, title)` to query Discogs API (`https://api.discogs.com/database/search?q={query}&type=release&format=vinyl`) exclusively with strict artist/title matching.

2. **Update Frontend UI in `static/index.html`**
   - Update modal text from `Auto-Fetch High-Res Official Cover (iTunes/Discogs)` to `Auto-Fetch Official Cover (Discogs)`.

3. **Verification & Deployment**
   - Test `discogs_service.fetch_official_cover()` via Python test script.
   - Commit and push to GitHub to deploy to Cloud Run.
