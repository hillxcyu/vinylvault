import os
import sys
import json
import logging

logging.basicConfig(level=logging.INFO)

# Ensure project directory is in python path
sys.path.insert(0, '/Users/hill/src/vinylvault')

from gemini_service import GeminiVisionService
from discogs_service import DiscogsService

image_path = '/Users/hill/.gemini/antigravity/brain/7714029d-685e-4e40-833c-d11a04ef5e33/.user_uploaded/media_1786545692314.jpg'

with open(image_path, 'rb') as f:
    img_bytes = f.read()

gemini = GeminiVisionService()
discogs = DiscogsService()

print("--- 1. Testing Gemini extract_album_metadata ---", flush=True)
meta = gemini.extract_album_metadata(img_bytes, filename="test_bach.jpg")
print(json.dumps(meta, indent=2, ensure_ascii=False), flush=True)

print("\n--- 2. Testing Gemini analyze_album_cover ---", flush=True)
scan_meta = gemini.analyze_album_cover(img_bytes, filename="test_bach.jpg")
print(json.dumps(scan_meta, indent=2, ensure_ascii=False), flush=True)

artist = meta.get("artist") or scan_meta.get("artist") or "Bach"
title = meta.get("albumTitle") or scan_meta.get("albumTitle") or "Messe in h-moll"
catno = meta.get("catalogNumber") or scan_meta.get("catalogNumber") or "MGX7096"
country = meta.get("country") or scan_meta.get("country") or "Japan"

print(f"\n--- 3. Testing Discogs fetch_release_info for ({artist}, {title}, catno={catno}, country={country}) ---", flush=True)
discogs_info = discogs.fetch_release_info(artist, title, catalog_number=catno, country=country)
print(json.dumps(discogs_info, indent=2, ensure_ascii=False), flush=True)
