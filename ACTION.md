# ACTION

## [2026-07-30 19:59:30] Discogs Exclusive Cover Art Execution Log

1. **[2026-07-30 19:59:43] Updated `discogs_service.py`**:
   - Completely removed `fetch_itunes_cover()`.
   - Updated `fetch_official_cover()` to query Discogs Search API exclusively for vinyl releases.
2. **[2026-07-30 19:59:47] Updated `static/index.html`**:
   - Updated rescan modal auto-fetch button text to `Auto-Fetch Official Cover (Discogs)`.

