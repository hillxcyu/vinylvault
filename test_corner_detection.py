import os
from deskew_service import deskew_service

def test_detect_corners():
    img_path = "test_album_cover.jpg"
    if not os.path.exists(img_path):
        print(f"Skipping test: {img_path} does not exist")
        return

    with open(img_path, "rb") as f:
        img_bytes = f.read()

    corners = deskew_service.detect_corners(img_bytes)
    print("Detected Corners:", corners)

    assert corners is not None, "Corners should not be None"
    assert len(corners) == 4, f"Expected 4 corners, got {len(corners)}"
    for pt in corners:
        assert len(pt) == 2, f"Expected [x,y], got {pt}"
        assert 0.0 <= pt[0] <= 1.0, f"x out of bounds: {pt[0]}"
        assert 0.0 <= pt[1] <= 1.0, f"y out of bounds: {pt[1]}"

    print("==========================================")
    print("✅ test_detect_corners PASSED 100%!")
    print("==========================================")

if __name__ == "__main__":
    test_detect_corners()
