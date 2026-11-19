import os
from google.cloud import firestore

PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "your-gcp-project-id")
DB_ID = os.environ.get("FIRESTORE_DATABASE_ID", "vinylvault")
OLD_BUCKET = os.environ.get("SOURCE_GCS_BUCKET", "your-source-vinyl-vault-data")
NEW_BUCKET = os.environ.get("TARGET_GCS_BUCKET", "your-target-vinyl-vault-data")

def replace_bucket(val):
    if isinstance(val, str) and OLD_BUCKET in val:
        return val.replace(OLD_BUCKET, NEW_BUCKET)
    elif isinstance(val, dict):
        return {k: replace_bucket(v) for k, v in val.items()}
    elif isinstance(val, list):
        return [replace_bucket(item) for item in val]
    return val

def migrate_urls():
    print(f"Connecting to Firestore '{DB_ID}'...")
    db = firestore.Client(project=PROJECT_ID, database=DB_ID)

    for col in ["records", "release_assets", "metadata"]:
        docs = list(db.collection(col).stream())
        print(f"Updating URLs in collection '{col}' ({len(docs)} documents)...")
        updated_count = 0
        batch = db.batch()
        batch_size = 0

        for doc in docs:
            doc_data = doc.to_dict()
            if doc_data:
                new_data = replace_bucket(doc_data)
                if new_data != doc_data:
                    batch.set(db.collection(col).document(doc.id), new_data)
                    batch_size += 1
                    updated_count += 1

                    if batch_size >= 400:
                        batch.commit()
                        batch = db.batch()
                        batch_size = 0

        if batch_size > 0:
            batch.commit()

        print(f"✅ Updated {updated_count} documents in '{col}'.")

if __name__ == "__main__":
    migrate_urls()
