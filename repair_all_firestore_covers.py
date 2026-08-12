import os
import sys
import subprocess
import logging
from discogs_service import discogs_service

logger = logging.getLogger("vinyl_vault")

def get_gcloud_token():
    try:
        token = subprocess.check_output(
            ["gcloud", "auth", "print-access-token"], text=True
        ).strip()
        return token
    except Exception as e:
        print(f"Warning: Failed to fetch gcloud access token: {e}")
        return None

def repair_firestore_covers():
    from google.cloud import firestore, storage
    import google.oauth2.credentials

    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT", "universal-trail-492014-n5")
    db_id = os.environ.get("FIRESTORE_DATABASE", "vinylvault-hk")
    bucket_name = "universal-trail-492014-n5-vinyl-vault-data"

    token = get_gcloud_token()
    credentials = google.oauth2.credentials.Credentials(token) if token else None

    print(f"Connecting to Firestore: project={project_id}, database={db_id}...")
    db = firestore.Client(project=project_id, database=db_id, credentials=credentials)
    storage_client = storage.Client(project=project_id, credentials=credentials)

    recs_ref = db.collection("records")
    docs = list(recs_ref.stream())
    print(f"Loaded {len(docs)} records from Firestore.")

    updated_count = 0
    batch = db.batch()

    for doc in docs:
        r = doc.to_dict()
        rec_id = r.get("id")
        artist = r.get("artist", "")
        title = r.get("title", "")
        old_url = r.get("coverUrl", "")

        new_url = None

        if old_url.startswith("/static/extracted_covers/"):
            fname = os.path.basename(old_url)
            new_url = f"https://storage.googleapis.com/{bucket_name}/covers/{fname}"
        elif old_url.startswith("/static/uploads/") or not old_url or "shopping_cover" in old_url:
            # User scan or missing cover -> query Discogs for official vinyl front cover art
            print(f"🔍 Repairing user scan cover art for [{rec_id}] '{artist} - {title}' (old: {old_url})...")
            discogs_url = discogs_service.fetch_official_cover(artist, title)
            if discogs_url and "shopping_cover" not in discogs_url:
                new_url = discogs_url
                print(f"  ✅ Discogs official cover found: {discogs_url}")
            else:
                # Fallback to GCS catalog cover
                new_url = f"https://storage.googleapis.com/{bucket_name}/covers/shopping_cover_2.jpg"
                print(f"  ⚠️ Fallback to GCS cover: {new_url}")

        if new_url and new_url != old_url:
            r["coverUrl"] = new_url
            doc_ref = recs_ref.document(rec_id)
            batch.set(doc_ref, r)
            updated_count += 1
            print(f"  -> Updated [{rec_id}] '{title}' -> {new_url}")

    if updated_count > 0:
        batch.commit()
        print(f"🎉 Successfully committed {updated_count} repaired cover art URLs to Firestore!")
    else:
        print("No records required cover URL repair.")

if __name__ == "__main__":
    repair_firestore_covers()
