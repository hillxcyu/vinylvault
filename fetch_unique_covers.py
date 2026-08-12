import os
import sys
import json
import urllib.request
import urllib.parse
from discogs_service import discogs_service
from gcs_service import gcs_service

def fetch_itunes_cover(artist, title):
    if not artist or not title:
        return None

    # Clean artist and title for search query
    clean_artist = artist.split('(')[0].split('/')[0].split('&')[0].strip()
    clean_title = title.split('(')[0].split(':')[0].strip()

    queries = [
        f"{clean_artist} {clean_title}",
        f"{clean_artist} {title.split('(')[0].strip()}",
        clean_title
    ]

    for q in queries:
        url = f"https://itunes.apple.com/search?term={urllib.parse.quote(q)}&entity=album&limit=3"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                results = data.get("results", [])
                for r in results:
                    art = r.get("artworkUrl100", "")
                    if art:
                        return art.replace("100x100bb", "600x600bb")
        except Exception as e:
            print(f"Query '{q}' warning: {e}")

    return None

def repair_unique_covers():
    from google.cloud import firestore, storage
    import google.oauth2.credentials

    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT", "universal-trail-492014-n5")
    db_id = os.environ.get("FIRESTORE_DATABASE", "vinylvault-hk")

    # Get gcloud token for authenticated GCP client
    import subprocess
    token = subprocess.check_output(["gcloud", "auth", "print-access-token"], text=True).strip()
    credentials = google.oauth2.credentials.Credentials(token)

    print(f"Connecting to Firestore: project={project_id}, database={db_id}...")
    db = firestore.Client(project=project_id, database=db_id, credentials=credentials)

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

        # Check if record is a user scan or using shopping_cover_2.jpg repeatedly
        if "rec-user" in rec_id or "shopping_cover_2.jpg" in old_url or "uploads/" in old_url:
            print(f"🔍 Searching unique cover art for [{rec_id}] '{artist} - {title}'...")
            cover_art = fetch_itunes_cover(artist, title)

            if not cover_art:
                discogs_art = discogs_service.fetch_official_cover(artist, title)
                if discogs_art and "shopping_cover_2.jpg" not in discogs_art:
                    cover_art = discogs_art

            if cover_art and cover_art != old_url:
                r["coverUrl"] = cover_art
                doc_ref = recs_ref.document(rec_id)
                batch.set(doc_ref, r)
                updated_count += 1
                print(f"  ✅ Updated [{rec_id}] '{title}' -> {cover_art}")

    if updated_count > 0:
        batch.commit()
        print(f"🎉 Successfully updated {updated_count} records with unique authentic album cover art!")
    else:
        print("All records already have unique cover art.")

if __name__ == "__main__":
    repair_unique_covers()
