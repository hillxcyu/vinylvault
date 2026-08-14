import os
import sys
from google.cloud import firestore

PROJECT_ID = "universal-trail-492014-n5"
OLD_DB_ID = "vinylvault"
NEW_DB_ID = "vinylvault-hk"

def migrate_collections():
    print(f"Connecting to source Firestore database '{OLD_DB_ID}' (nam5)...")
    db_old = firestore.Client(project=PROJECT_ID, database=OLD_DB_ID)
    
    print(f"Connecting to target Firestore database '{NEW_DB_ID}' (asia-east2)...")
    db_new = firestore.Client(project=PROJECT_ID, database=NEW_DB_ID)

    collections_to_migrate = ["records", "spins", "listening_guides", "release_assets", "metadata"]

    for col_name in collections_to_migrate:
        print(f"\n--- Migrating collection '{col_name}' ---")
        docs_old = list(db_old.collection(col_name).stream())
        print(f"Found {len(docs_old)} documents in source collection '{col_name}'.")

        if not docs_old:
            continue

        migrated_count = 0
        batch = db_new.batch()
        batch_size = 0

        for doc in docs_old:
            doc_data = doc.to_dict()
            if doc_data:
                target_ref = db_new.collection(col_name).document(doc.id)
                batch.set(target_ref, doc_data)
                batch_size += 1
                migrated_count += 1

                if batch_size >= 400:
                    batch.commit()
                    print(f"Committed batch of {batch_size} documents to '{col_name}'.")
                    batch = db_new.batch()
                    batch_size = 0

        if batch_size > 0:
            batch.commit()
            print(f"Committed final batch of {batch_size} documents to '{col_name}'.")

        # Verification
        docs_new = list(db_new.collection(col_name).stream())
        print(f"✅ Collection '{col_name}' migration complete. Source: {len(docs_old)} -> Target: {len(docs_new)}")

if __name__ == "__main__":
    migrate_collections()
