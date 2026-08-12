import os
import io
import subprocess
from PIL import Image

def get_gcloud_token():
    try:
        res = subprocess.run(
            ["gcloud", "auth", "print-access-token"],
            capture_output=True,
            text=True,
            check=True,
        )
        return res.stdout.strip()
    except Exception as e:
        print(f"Warning: Failed to fetch gcloud access token: {e}")
        return None

def convert_gcs_covers_to_webp():
    from google.cloud import storage, firestore
    import google.oauth2.credentials

    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT", "universal-trail-492014-n5")
    buckets = [
        os.environ.get("GCS_BUCKET_NAME", "universal-trail-492014-n5-vinyl-vault-hk-data"),
        "universal-trail-492014-n5-vinyl-vault-data"
    ]
    
    token = get_gcloud_token()
    credentials = google.oauth2.credentials.Credentials(token) if token else None

    storage_client = storage.Client(project=project_id, credentials=credentials)

    total_orig_bytes = 0
    total_new_bytes = 0
    converted_count = 0

    print("--- Starting GCS Cover Conversion to WebP ---")

    for bucket_name in buckets:
        try:
            bucket = storage_client.bucket(bucket_name)
            if not bucket.exists():
                print(f"Bucket {bucket_name} does not exist or is inaccessible. Skipping.")
                continue

            print(f"\nScanning bucket '{bucket_name}' for cover images...")
            blobs = list(bucket.list_blobs(prefix="covers/"))

            for blob in blobs:
                filename = os.path.basename(blob.name)
                ext = os.path.splitext(filename)[1].lower()
                if ext not in [".jpg", ".jpeg", ".png"]:
                    continue

                orig_size = blob.size or 0
                total_orig_bytes += orig_size

                webp_blob_name = f"covers/{os.path.splitext(filename)[0]}.webp"
                webp_blob = bucket.blob(webp_blob_name)

                # Download bytes
                img_bytes = blob.download_as_bytes()

                # Compress to WebP using Pillow
                with Image.open(io.BytesIO(img_bytes)) as img:
                    if img.mode in ("RGBA", "P", "LA"):
                        img = img.convert("RGB")

                    w, h = img.size
                    max_dim = 1024
                    if max(w, h) > max_dim:
                        if w >= h:
                            new_w = max_dim
                            new_h = int(h * (max_dim / float(w)))
                        else:
                            new_h = max_dim
                            new_w = int(w * (max_dim / float(h)))
                        img = img.resize((new_w, new_h), resample=Image.Resampling.LANCZOS)

                    out_buffer = io.BytesIO()
                    img.save(out_buffer, format="WEBP", quality=80, method=6)
                    webp_bytes = out_buffer.getvalue()

                new_size = len(webp_bytes)
                total_new_bytes += new_size
                converted_count += 1

                # Upload compressed WebP to GCS
                webp_blob.upload_from_string(webp_bytes, content_type="image/webp")
                try:
                    webp_blob.make_public()
                except Exception:
                    pass

                reduction = (1 - (new_size / float(orig_size))) * 100 if orig_size > 0 else 0
                print(f"  Converted gs://{bucket_name}/{blob.name}: {orig_size//1024}KB -> {new_size//1024}KB ({reduction:.1f}% reduction)")

        except Exception as e:
            print(f"Error processing bucket {bucket_name}: {e}")

    if total_orig_bytes > 0:
        overall_reduction = (1 - (total_new_bytes / float(total_orig_bytes))) * 100
        print(f"\n✅ Converted {converted_count} GCS cover objects to WebP.")
        print(f"  Total original size: {total_orig_bytes / (1024*1024):.2f} MB")
        print(f"  Total WebP size: {total_new_bytes / (1024*1024):.2f} MB")
        print(f"  GCS storage saved: {overall_reduction:.1f}%!")

    # Now update Firestore database records
    db_ids = ["vinylvault-hk"]
    print("\n--- Updating Firestore Database URLs ---")
    for db_id in db_ids:
        try:
            db = firestore.Client(project=project_id, database=db_id, credentials=credentials)
            for col in ["records", "release_assets", "metadata"]:
                docs = list(db.collection(col).stream())
                updated_count = 0
                batch = db.batch()
                batch_size = 0

                for doc in docs:
                    data = doc.to_dict() or {}
                    changed = False

                    # Check coverUrl and originalScannedCoverUrl
                    for key in ["coverUrl", "originalScannedCoverUrl"]:
                        val = data.get(key)
                        if isinstance(val, str) and ("storage.googleapis.com" in val or "/static/extracted_covers/" in val):
                            ext = os.path.splitext(val)[1].lower()
                            if ext in [".jpg", ".jpeg", ".png"]:
                                new_val = os.path.splitext(val)[0] + ".webp"
                                data[key] = new_val
                                changed = True

                    if changed:
                        batch.set(db.collection(col).document(doc.id), data, merge=True)
                        batch_size += 1
                        updated_count += 1
                        if batch_size >= 400:
                            batch.commit()
                            batch = db.batch()
                            batch_size = 0

                if batch_size > 0:
                    batch.commit()

                print(f"✅ Updated {updated_count} documents in Firestore '{db_id}' -> collection '{col}'.")
        except Exception as e:
            print(f"Error updating Firestore DB '{db_id}': {e}")

if __name__ == "__main__":
    convert_gcs_covers_to_webp()
