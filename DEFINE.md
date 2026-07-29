# Todo List: Scanner UI Refinements (Pinch-Zoom, Pan & External Action Buttons)

This file defines the tasks needed to complete the approved plan.

## 📋 Task List

### 1️⃣ [frontend] External Action Bar Relocation (`static/index.html`)
* [ ] **Task 1.1**: Remove floating action bar from inside `#scannerPreviewContainer`.
* [ ] **Task 1.2**: Create `#scannerActionsBar` below `#scannerBox` and above `#manualQueryForm` containing `✂️ Apply 4-Corner Crop` and `🪄 Auto Deskew`.

### 2️⃣ [frontend] Pinch-Zoom & Pan Canvas Controller (`static/index.html`)
* [ ] **Task 2.1**: Implement zoom (`zoomScale`) and pan (`panX`, `panY`) transform state for `#scannerZoomStage`.
* [ ] **Task 2.2**: Add mouse wheel zoom listener (`wheel`) and touch pinch-zoom listener (`touchstart`, `touchmove`).
* [ ] **Task 2.3**: Add pan drag listener when dragging preview background.
* [ ] **Task 2.4**: Add reset zoom/pan button in header bar.

### 3️⃣ [verification & cicd] Mandatory Local Testing & Deployment (`test_local_integration.sh`)
* [ ] **Task 3.1**: Run `./test_local_integration.sh` locally in Docker to verify API compatibility.
* [ ] **Task 3.2**: Commit and push to GitHub for automated Cloud Build deployment.
