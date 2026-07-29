# 🚀 Plan: Scanner UI UX Refinement — External Action Buttons + Pinch-Zoom & Pan

This plan details relocating the deskew action buttons below the preview container and implementing **pinch-zoom & pan gestures** for high-precision 4-corner bounding box adjustment.

---

## 🛠️ UI Architecture

```
+-----------------------------------------------------------------------------------+
|                                  SCANNER MODAL                                    |
|                                                                                   |
|  +-----------------------------------------------------------------------------+  |
|  |                     PREVIEW AREA (PINCH-ZOOM & PAN)                         |  |
|  |                                                                             |  |
|  |    (o)=======================================================o              |  |
|  |     |   Draggable Corner (Top-Left)   Draggable (Top-Right) |              |  |
|  |     |                                                       |              |  |
|  |     |                       [RAW PHOTO]                     |              |  |
|  |    (o)=======================================================o              |  |
|  |         Draggable (Bottom-Left)      Draggable (Bottom-Right)             |  |
|  +-----------------------------------------------------------------------------+  |
|                                                                                   |
|  +-----------------------------------------------------------------------------+  |
|  |  [ ✂️ Apply 4-Corner Crop ]              [ 🪄 Auto Deskew ]                 |  |
|  +-----------------------------------------------------------------------------+  |
|                                                                                   |
|  -------------------------- Or Search Manually -------------------------------    |
|  [ Artist Input ]                       [ Album Title Input ]                     |
+-----------------------------------------------------------------------------------+
```

---

## 📋 Task List

### 1️⃣ [frontend] Relocate Action Buttons Below Preview Box (`static/index.html`)
* Move `#scannerActionsBar` below `#scannerBox` and above `#manualQueryForm`.
* Ensure buttons do not obstruct the 4 corner handles or cover image.

### 2️⃣ [frontend] Pinch-Zoom & Pan Canvas Controller (`static/index.html`)
* Add zoom/pan state (`zoomScale`, `panX`, `panY`).
* Mouse Wheel listener (`wheel` event for desktop zoom in/out).
* Touch Pinch listener (`touchstart`, `touchmove` distance for mobile pinch zoom).
* Drag to Pan listener when dragging container outside handle targets.
* Scale handle positions & SVG polygon seamlessly with zoom/pan transforms.

### 3️⃣ [verification & cicd] Mandatory Local Testing & Deployment (`test_local_integration.sh`)
* Run `./test_local_integration.sh` locally in Docker.
* Commit and push to GitHub for automated Cloud Build deployment.
