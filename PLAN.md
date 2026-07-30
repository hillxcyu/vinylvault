# PLAN

## [2026-07-30 20:28:30] Extract & Pass Catalog Number and Country in Vision Scan Engine [COMPLETED]


### Goal
Enhance Gemini Vision scanning to explicitly extract Catalog Numbers (`catalogNumber`) and Pressing Country (`country`) from cover art, spines, and obi strips, and pass them to Discogs for precise release matching.

---

### Proposed Plan

1. **Update Gemini Vision Prompt in `gemini_service.py`**
   - Instruct Gemini Vision to explicitly extract `catalogNumber` (from spine, obi strip, top/bottom cover corners) and `country` (e.g. "Japan", "US", "UK").

2. **Update `discogs_service.py`**
   - Update `fetch_official_cover(artist, title, cover_url=None, catalog_number=None, country="Japan")` to accept `catalog_number` and `country` and pass them to Discogs search.

3. **Update `/api/scan` in `main.py`**
   - Pass `catalog_number = extracted_metadata.get("catalogNumber")` and `country = extracted_metadata.get("country")` from Gemini Vision to Discogs search queries.

4. **Testing & Deployment**
   - Test Gemini Vision extraction with catalog number prompt locally.
   - Commit, push to GitHub, and restart local Docker container + trigger Cloud Run deploy.
