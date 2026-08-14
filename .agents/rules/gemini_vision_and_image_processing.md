# Gemini Vision 2D Spatial & Image Processing Rules

## 1. Gemini Vision 2D Spatial Coordinate Mapping
- When requesting 2D bounding boxes or polygon masks from Gemini Vision models (`gemini-3.7-flash`):
  - `box_2d` coordinates follow `[ymin, xmin, ymax, xmax]` on a 0-1000 normalized integer scale.
  - For polygon corner masks, explicitly specify `[x, y]` order in top-left, top-right, bottom-right, bottom-left sequence.
  - Convert 0-1000 scale to pixel coordinates:
    `pixel_x = (x / 1000.0) * image_width`
    `pixel_y = (y / 1000.0) * image_height`

## 2. EXIF Orientation Normalization
- Always apply `PIL.ImageOps.exif_transpose()` to user-uploaded camera images before OpenCV matrix processing or container letterbox calculations.
- This ensures the raw pixel matrix orientation in Python matches what modern web browsers display in `<img src="..." />`, preventing aspect ratio mismatches and spatial handle offsets.
