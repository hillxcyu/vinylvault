import os
import sys
from gcs_service import gcs_service
from database import db

def upload_catalog_covers():
    covers_dir = os.path.join(os.path.dirname(__file__), "static", "extracted_covers")
    if not os.path.exists(covers_dir):
        print(f"Covers directory {covers_dir} not found.")
        return

    files = [f for f in os.listdir(covers_dir) if f.endswith(('.jpg', '.png', '.jpeg'))]
    print(f"Found {len(files)} cover images in {covers_dir}")

    uploaded_count = 0
    url_map = {}

    for fname in files:
        fpath = os.path.join(covers_dir, fname)
        with open(fpath, "rb") as f:
            content = f.read()

        content_type = "image/png" if fname.endswith(".png") else "image/jpeg"
        gcs_url = gcs_service.upload_cover(content, fname, content_type=content_type)
        url_map[f"/static/extracted_covers/{fname}"] = gcs_url
        uploaded_count += 1

    print(f"✅ Successfully uploaded {uploaded_count} covers to GCS bucket: {gcs_service.bucket_name}")

    # Update records in Firestore and local database
    recs = db.get_all_records()
    updated_recs_count = 0

    for r in recs:
        old_url = r.get("coverUrl", "")
        if old_url in url_map:
            r["coverUrl"] = url_map[old_url]
            updated_recs_count += 1
        elif old_url.startswith("/static/extracted_covers/"):
            fname = os.path.basename(old_url)
            r["coverUrl"] = f"https://storage.googleapis.com/{gcs_service.bucket_name}/covers/{fname}"
            updated_recs_count += 1

    db.save_records()

    # Save to Firestore in batch if available
    if db.firestore.db:
        success, msg = db.firestore.save_all_records_batch(recs)
        print(f"Firestore batch update result: success={success}, msg={msg}")
    else:
        print("Firestore client not connected locally; saved to local records.json.")

    print(f"🎉 Updated {updated_recs_count} record cover URLs to GCS bucket!")

if __name__ == "__main__":
    upload_catalog_covers()
