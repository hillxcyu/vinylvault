# DEFINE

## [2026-07-30 20:08:45] TODO List

- [x] `[backend]` Update `fetch_all_release_assets()` in `discogs_service.py` to search by `catno` and `country=Japan`, returning top 10 front cover candidates.
- [x] `[backend]` Update `/api/release-assets/{key}` route in `main.py` to pass `catno` and `country` parameters.
- [x] `[frontend]` Update `#rescanAssetsGrid` in `static/index.html` to render 10 top front artwork candidates with Japan/CatNo badges.
- [x] `[testing]` Test `discogs_service.fetch_all_release_assets()` with catalog numbers and Japan region queries.
- [x] `[deployment]` Stage, commit, and push to GitHub for Cloud Run deployment.
