# PLAN

## [2026-07-30 17:31:00] Automatic Corner Detection & Initial Bounding Box Snapping for Manual Deskew [COMPLETED]


### Goal
Enhance the manual deskew process by automatically detecting the 4 physical corners of the vinyl album cover using OpenCV edge/contour detection, drawing the initial bounding box snapped precisely to those detected corners when the manual deskew UI is loaded.

---

### Proposed Plan

1. **Implement `detect_corners` in `deskew_service.py`**
   - Add `detect_corners(self, image_bytes: bytes)` to `DeskewService`.
   - Use OpenCV (Canny edge detection + contour approximation / minimum area bounding box) to detect quadrilateral corners.
   - Convert pixel coordinates to normalized `0.0..1.0` container coordinates accounting for aspect ratio and letterboxing.
   - Return 4 corner coordinates `[[x1,y1], [x2,y2], [x3,y3], [x4,y4]]`.

2. **Add `/api/detect-corners` Endpoint in `main.py`**
   - Create `POST /api/detect-corners` endpoint to accept an image file (or uploaded file) and return detected normalized corner coordinates.
   - Include `detectedCorners` in `/api/scan` response as well so initial scans immediately provide auto-snapped corners.

3. **Update Manual Deskew UI in `static/index.html`**
   - Update `resetCornerPoints()` and modal initialization functions to use backend-detected corners if available.
   - Add an "Auto Detect" button in the manual deskew UI controls to re-snap handles to detected corners at any time.
   - Render the initial bounding box and draggable handle controls (`TL`, `TR`, `BR`, `BL`) snapped directly on those detected corners.

---

### Verification Plan
- Unit test corner detection algorithm with sample album cover image.
- Test `/api/detect-corners` and `/api/scan` API responses.
- Verify UI handle snapping and manual dragging in browser.
