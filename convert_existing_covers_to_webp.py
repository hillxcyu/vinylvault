import os
import glob
from PIL import Image

def convert_existing_covers_to_webp(directory="static/extracted_covers", quality=80, max_dim=1024):
    if not os.path.exists(directory):
        print(f"Directory {directory} does not exist.")
        return

    pattern = os.path.join(directory, "*.*")
    files = glob.glob(pattern)

    converted_count = 0
    total_orig_bytes = 0
    total_new_bytes = 0

    print(f"Scanning {len(files)} files in {directory}...")

    for fpath in sorted(files):
        ext = os.path.splitext(fpath)[1].lower()
        if ext not in [".jpg", ".jpeg", ".png"]:
            continue

        webp_path = os.path.splitext(fpath)[0] + ".webp"
        
        try:
            orig_size = os.path.getsize(fpath)
            total_orig_bytes += orig_size

            with Image.open(fpath) as img:
                if img.mode in ("RGBA", "P", "LA"):
                    img = img.convert("RGB")
                
                w, h = img.size
                if max(w, h) > max_dim:
                    if w >= h:
                        new_w = max_dim
                        new_h = int(h * (max_dim / float(w)))
                    else:
                        new_h = max_dim
                        new_w = int(w * (max_dim / float(h)))
                    img = img.resize((new_w, new_h), resample=Image.Resampling.LANCZOS)

                img.save(webp_path, format="WEBP", quality=quality, method=6)

            new_size = os.path.getsize(webp_path)
            total_new_bytes += new_size
            converted_count += 1
            reduction = (1 - (new_size / float(orig_size))) * 100
            print(f"  Converted {os.path.basename(fpath)}: {orig_size//1024}KB -> {new_size//1024}KB ({reduction:.1f}% reduction)")
        except Exception as e:
            print(f"  Error converting {fpath}: {e}")

    if total_orig_bytes > 0:
        overall_reduction = (1 - (total_new_bytes / float(total_orig_bytes))) * 100
        print(f"\n✅ Converted {converted_count} files to WebP.")
        print(f"  Total original size: {total_orig_bytes / (1024*1024):.2f} MB")
        print(f"  Total WebP size: {total_new_bytes / (1024*1024):.2f} MB")
        print(f"  Space saved: {overall_reduction:.1f}%!")

def update_records_json_urls(json_path="data_store/records.json"):
    if not os.path.exists(json_path):
        print(f"Records JSON {json_path} not found.")
        return

    import json
    with open(json_path, "r", encoding="utf-8") as f:
        records = json.load(f)

    updated_count = 0
    for rec in records:
        cover_url = rec.get("coverUrl", "")
        if cover_url and ("/static/extracted_covers/" in cover_url or "storage.googleapis.com" in cover_url):
            ext = os.path.splitext(cover_url)[1].lower()
            if ext in [".jpg", ".jpeg", ".png"]:
                new_url = os.path.splitext(cover_url)[0] + ".webp"
                rec["coverUrl"] = new_url
                if rec.get("originalScannedCoverUrl"):
                    rec["originalScannedCoverUrl"] = os.path.splitext(rec["originalScannedCoverUrl"])[0] + ".webp"
                updated_count += 1

    if updated_count > 0:
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(records, f, indent=2, ensure_ascii=False)
        print(f"✅ Updated {updated_count} record cover URLs in {json_path} to .webp!")

if __name__ == "__main__":
    convert_existing_covers_to_webp()
    update_records_json_urls()
