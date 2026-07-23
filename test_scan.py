import sys
import os

from gemini_service import gemini_service

def test_image_scan():
    img_path = "/usr/local/google/home/xcyu/vinyl-vault/test_album_cover.jpg"
    if not os.path.exists(img_path):
        print(f"File not found: {img_path}")
        return

    with open(img_path, "rb") as f:
        img_bytes = f.read()

    print(f"Loaded image {img_path} ({len(img_bytes)} bytes)")
    result = gemini_service.analyze_album_cover(img_bytes, filename="test_album_cover.jpg")
    print("\n--- GEMINI SCAN RESULT ---")
    print(result)

if __name__ == "__main__":
    test_image_scan()
