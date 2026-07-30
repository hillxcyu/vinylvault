# PLAN

## [2026-07-30 21:06:30] Fix Scan Sticking at Step 2/2 in /api/analyze-deskewed

### Goal
Fix issue where snapping/scanning a cover image got stuck at "Step 2/2: Parsing title, artist & pressing details via Gemini AI..." because `/api/analyze-deskewed` failed when `coverUrl` was a full HTTP/GCS URL instead of a local disk path.

---

### Proposed Plan

1. **Update `/api/analyze-deskewed` in `main.py`**
   - Support reading image bytes directly from HTTP/GCS URLs (`https://storage.googleapis.com/...`) as well as local disk paths.
   - Pass extracted `catalogNumber` and `country` to Discogs.

2. **Update Scan Exception Handling in `static/index.html`**
   - Ensure errors during Gemini analysis render a clear toast/error alert so the UI never stays stuck in the loading state.

3. **Testing & Deployment**
   - Test `/api/analyze-deskewed` with HTTP/GCS cover URLs via Python test script.
   - Commit, push to GitHub, restart local Docker container, and deploy to Cloud Run.
