# DEFINE

## [2026-07-30 20:31:58] TODO List

- [x] `[backend]` Update Gemini Vision prompt in `gemini_service.py` to extract `catalogNumber` and `country` from cover/spine/obi strip.
- [x] `[backend]` Accept `catalog_number` and `country` in `fetch_official_cover()` in `discogs_service.py`.
- [x] `[backend]` Pass `catalogNumber` and `country` from `/api/scan` to Discogs in `main.py`.
- [x] `[testing]` Test vision metadata extraction and Discogs search integration.
- [x] `[deployment]` Stage, commit, push to GitHub, and restart local Docker container + trigger Cloud Run deploy.
