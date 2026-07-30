# DEFINE

## [2026-07-30 17:31:00] TODO List

- [x] `[backend]` Add `detect_corners(self, image_bytes)` in `deskew_service.py` to calculate normalized container corner coordinates.
- [x] `[backend]` Add `POST /api/detect-corners` endpoint and include `detectedCorners` in `/api/scan` response in `main.py`.
- [x] `[x]` `[frontend]` Update `static/index.html` to snap initial `cornerPoints` handles (`TL`, `TR`, `BR`, `BL`) directly to detected corners.
- [x] `[frontend]` Add "Auto Detect Corners" button to the manual deskew control bar in `static/index.html`.
- [x] `[testing]` Create `test_corner_detection.py` and run verification tests on sample images.
