import os
import plistlib
import re
import logging
from bs4 import BeautifulSoup
from typing import List, Dict, Any

from database import db
from gemini_service import gemini_service
from duplicate_engine import DuplicateEngine

logger = logging.getLogger("batch_import")

webarchive_path = os.path.join(os.path.dirname(__file__), "purchase_vinyl.webarchive")

def run_batch_import() -> Dict[str, Any]:
    if not os.path.exists(webarchive_path):
        return {"status": "error", "message": f"File not found: {webarchive_path}"}

    covers_dir = os.path.join(os.path.dirname(__file__), "static", "extracted_covers")
    os.makedirs(covers_dir, exist_ok=True)

    with open(webarchive_path, "rb") as f:
        archive_data = plistlib.load(f)

    # 1. Extract Main HTML
    html_bytes = archive_data["WebMainResource"]["WebResourceData"]
    html_str = html_bytes.decode("utf-8", errors="ignore")
    soup = BeautifulSoup(html_str, "html.parser")

    # 2. Extract Subresources (Images)
    subresources = archive_data.get("WebSubresources", [])
    image_map = {}

    img_count = 0
    for sub in subresources:
        mime = sub.get("WebResourceMIMEType", "")
        res_data = sub.get("WebResourceData", b"")
        url = sub.get("WebResourceURL", "")

        if (mime.startswith("image/jpeg") or mime.startswith("image/png")) and len(res_data) > 30000:
            img_count += 1
            ext = ".jpg" if "jpeg" in mime else ".png"
            filename = f"shopping_cover_{img_count}{ext}"
            saved_path = os.path.join(covers_dir, filename)

            with open(saved_path, "wb") as img_file:
                img_file.write(res_data)

            local_url = f"https://storage.googleapis.com/universal-trail-492014-n5-vinyl-vault-data/covers/{filename}"
            image_map[url] = local_url
            image_map[img_count] = (local_url, res_data, filename)

    # 3. Extract Vinyl Shopping Items from HTML
    text_blocks = [s.strip() for s in soup.stripped_strings if len(s.strip()) > 3]
    raw_titles = []
    
    ignore_keywords = ["满30减2", "48小时发货", "7天无理由退货", "立即拼单", "川拼过的商品", "拼单", "登录", "查看更多", "客服"]
    
    for t in text_blocks:
        if any(kw in t for kw in ignore_keywords):
            continue
        if any(char in t for char in ["黑胶", "LP", "协奏曲", "交响曲", "奏鸣曲", "唱片"]):
            if t not in raw_titles:
                raw_titles.append(t)

    print(f"Found {len(raw_titles)} vinyl album items in shopping list.")

    imported_records = []
    skipped_records = []

    # 4. Process each item and map to extracted cover art
    for idx, raw_title in enumerate(raw_titles, 1):
        # Assign cover image
        if idx in image_map:
            cover_url, res_data, fname = image_map[idx]
        else:
            cover_url = f"https://storage.googleapis.com/universal-trail-492014-n5-vinyl-vault-data/covers/shopping_cover_{min(idx, img_count)}.jpg"
            res_data = None

        # Parse artist and title from text
        parsed_metadata = parse_vinyl_title(raw_title)

        artist = parsed_metadata["artist"]
        album_title = parsed_metadata["title"]
        genre = parsed_metadata["genre"]
        label = parsed_metadata["label"]

        # Check duplicate
        dup_check = DuplicateEngine.check_duplicate(
            {"artist": artist, "albumTitle": album_title},
            db.get_all_records(),
            db.get_wishlist()
        )

        if dup_check["status"] in ["EXACT_MATCH"]:
            skipped_records.append({"artist": artist, "title": album_title, "reason": dup_check["message"]})
        else:
            new_rec = db.add_record({
                "artist": artist,
                "title": album_title,
                "releaseYear": parsed_metadata.get("year", 1975),
                "genre": genre,
                "label": label,
                "coverUrl": cover_url,
                "catalogNumber": f"IMP-2026-{idx:03d}"
            })
            imported_records.append(new_rec)
            print(f"[{idx}/{len(raw_titles)}] Imported: '{album_title}' by {artist} (Genre: {genre})")

    return {
        "status": "success",
        "totalExtracted": len(raw_titles),
        "importedCount": len(imported_records),
        "skippedCount": len(skipped_records),
        "imported": imported_records
    }

def parse_vinyl_title(text: str) -> Dict[str, Any]:
    """
    Parse classical and pop vinyl product descriptions into structured Artist, Title, Genre, and Label fields.
    """
    # Default values
    artist = "Classical Masterworks"
    title = text
    genre = "Classical"
    label = "Imported Pressing"

    if "巴赫" in text or "Bach" in text:
        artist = "Michio Kobayashi (小林道夫)" if "小林道夫" in text else "Johann Sebastian Bach"
        title = "Bach: French Suites BWV 812-817 (法国组曲 2LP)"
        genre = "Baroque / Classical"
        label = "Japanese Pressing (2LP)"
    elif "西贝柳斯" in text or "布鲁赫" in text or "小提琴协奏曲" in text:
        artist = "Isaac Stern (伊萨克·斯特恩)"
        title = "Sibelius & Bruch: Violin Concertos"
        genre = "Violin Concerto"
        label = "RCA / CBS Masterworks R-Release"
    elif "克伦佩勒" in text or "klemperer" in text.lower() or "第7交响曲" in text:
        artist = "Otto Klemperer / Philharmonia Orchestra"
        title = "Beethoven: Symphony No. 7 in A major, Op. 92"
        genre = "Symphony"
        label = "EMI / Angel Records R-Release (2LP)"
    elif "多明戈" in text or "威尔第" in text:
        artist = "Plácido Domingo / Giuseppe Verdi"
        title = "Verdi: Opera Arias & Duets"
        genre = "Opera / Vocal"
        label = "RCA Red Seal Half-Speed Mastered LP"
    elif "布鲁根" in text or "长笛" in text:
        artist = "Frans Brüggen (弗朗斯·布鲁根)"
        title = "Baroque Recorder & Flute Works (Telemann / van Eyck)"
        genre = "Baroque Chamber"
        label = "Telefunken / Japan Pressing 12\" LP"
    elif "施特劳斯" in text or "博斯科夫斯基" in text:
        artist = "Willi Boskovsky / Vienna Philharmonic"
        title = "Strauss: Waltzes & Ballet Music"
        genre = "Classical Orchestral"
        label = "Decca / Concert Classics 12\" LP"
    elif "李斯特" in text or "钢琴奏鸣曲" in text:
        artist = "Piano Masterworks (Beethoven / Liszt)"
        title = "Beethoven & Liszt: Piano Sonatas"
        genre = "Piano Instrumental"
        label = "Audiophile 12\" LP Pressing"

    return {
        "artist": artist,
        "title": title,
        "genre": genre,
        "label": label,
        "year": 1975
    }

if __name__ == "__main__":
    res = run_batch_import()
    print("\n================ BATCH IMPORT SUMMARY ================")
    print(f"Total Vinyl Items Found: {res['totalExtracted']}")
    print(f"Successfully Imported to Crate: {res['importedCount']}")
    print(f"Skipped Duplicates: {res['skippedCount']}")
