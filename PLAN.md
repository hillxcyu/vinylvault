# PLAN

## [2026-07-30 18:51:00] Rescan Album Cover Art Feature [COMPLETED]


### Goal
Allow users to click on any album cover art in the UI (Now Spinning, Collection Grid, or Fullscreen Lightbox) to rescan, upload, or auto-fetch new official high-resolution cover art for that record.

---

### Proposed Plan

1. **Backend Endpoints in `main.py`**
   - Add `POST /api/records/{record_id}/rescan-cover`: Queries iTunes Search API and Discogs for official high-res 600x600 cover art, updates the record in Firestore/local storage, and returns the updated record.
   - Add `POST /api/records/{record_id}/update-cover`: Accepts a `coverUrl` parameter, updates the record in Firestore/local storage, and returns success.

2. **Frontend UI in `static/index.html`**
   - Add a **Rescan Cover Art Modal** (`#rescanModal`).
   - Add click handlers on album cover images (Now Spinning cover, Collection cards, Lightbox viewer) to trigger `openRescanModal(recordId)`.
   - Implement 3 rescan action buttons in the modal:
     - 🔍 **Auto-Fetch Official Cover**: Invokes `POST /api/records/{record_id}/rescan-cover`.
     - 📷 **Upload/Snap Photo**: Allows file upload/camera photo, runs auto/manual deskew, uploads to GCS, and updates record cover.
     - 🎨 **Choose from Release Assets**: Fetches Discogs release assets for the album and lets the user pick their preferred artwork with 1 click.

3. **Verification**
   - Test `POST /api/records/{record_id}/rescan-cover` via curl.
   - Verify modal opening and artwork updates in frontend web browser.
