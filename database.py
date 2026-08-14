import json
import os
import uuid
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime


INITIAL_RECORDS = []
INITIAL_WISHLIST = []

DATA_DIR = os.path.join(os.path.dirname(__file__), "data_store")
RECORDS_FILE = os.path.join(DATA_DIR, "records.json")
SPINS_FILE = os.path.join(DATA_DIR, "spins.json")
CHRONICLE_FILE = os.path.join(DATA_DIR, "chronicle.json")
NOW_SPINNING_FILE = os.path.join(DATA_DIR, "now_spinning.json")



class FirestoreManager:
    def __init__(self):
        self.project_id = os.environ.get("GOOGLE_CLOUD_PROJECT", "universal-trail-492014-n5")
        self.database_id = os.environ.get("FIRESTORE_DATABASE_ID") or os.environ.get("FIRESTORE_DATABASE", "vinylvault-hk")
        self.db = None
        self.last_error = None
        self._init_firestore()


    def _init_firestore(self):
        try:
            from google.cloud import firestore
            self.db = firestore.Client(project=self.project_id, database=self.database_id)
            print(f"GCP Firestore client successfully connected to project: {self.project_id}, database: {self.database_id}")
            self.last_error = None
        except Exception as e:
            err_str = str(e)
            print(f"GCP Firestore client init error for database {self.database_id}: {err_str}")
            self.db = None
            self.last_error = f"Client Init Error: {err_str}"

    def get_records(self, timeout: float = 3.0) -> Tuple[Optional[List[Dict[str, Any]]], Optional[str]]:
        if not self.db:
            return None, self.last_error or "Firestore client is not initialized"
        try:
            docs = self.db.collection("records").get(timeout=timeout)
            records = [d.to_dict() for d in docs if d.exists and d.to_dict()]
            print(f"Loaded {len(records)} records from GCP Firestore.")
            self.last_error = None
            return records, None
        except Exception as e:
            err_str = str(e)
            print(f"Firestore get_records warning/timeout: {err_str}")
            self.last_error = f"Fetch Error: {err_str}"
            return None, err_str








    def save_all_records_batch(self, records: List[Dict[str, Any]]) -> Tuple[bool, str]:
        if not self.db:
            return False, "Firestore client is not initialized (self.db is None)"
        try:
            batch = self.db.batch()
            for r in records:
                ref = self.db.collection("records").document(r["id"])
                batch.set(ref, r)
            batch.commit()
            print(f"Batch saved {len(records)} records to Firestore.")
            return True, "OK"
        except Exception as e:
            err_str = str(e)
            print(f"Firestore batch save error: {err_str}")
            return False, err_str

    def save_record(self, record_data: Dict[str, Any]) -> bool:
        if not self.db:
            return False
        try:
            rec_id = record_data.get("id")
            if rec_id:
                self.db.collection("records").document(rec_id).set(record_data)
                print(f"Saved record '{rec_id}' ({record_data.get('title')}) to Firestore.")
                return True
        except Exception as e:
            print(f"Firestore save_record error: {e}")
        return False

    def delete_record(self, record_id: str) -> bool:
        if not self.db:
            return False
        try:
            self.db.collection("records").document(record_id).delete()
            print(f"Deleted record '{record_id}' from Firestore.")
            return True
        except Exception as e:
            print(f"Firestore delete_record error: {e}")
        return False

    def get_spins(self) -> Optional[List[Dict[str, Any]]]:
        if not self.db:
            return None
        try:
            docs = self.db.collection("spins").stream()
            spins = [d.to_dict() for d in docs]
            if spins:
                return spins
        except Exception as e:
            print(f"Firestore get_spins error: {e}")
        return None

    def save_spin(self, spin_data: Dict[str, Any]) -> bool:
        if not self.db:
            return False
        try:
            spin_id = spin_data.get("id")
            if spin_id:
                self.db.collection("spins").document(spin_id).set(spin_data)
                return True
        except Exception as e:
            print(f"Firestore save_spin error: {e}")
        return False

    def get_chronicle(self) -> Optional[Dict[str, Any]]:
        if not self.db:
            return None
        try:
            doc = self.db.collection("metadata").document("chronicle").get(timeout=2.0)
            if doc.exists:
                return doc.to_dict()
        except Exception as e:
            print(f"Firestore get_chronicle warning/timeout (using local fallback): {e}")
        return None

    def save_chronicle(self, chronicle_data: Dict[str, Any]) -> bool:
        if not self.db:
            return False
        try:
            self.db.collection("metadata").document("chronicle").set(chronicle_data)
            return True
        except Exception as e:
            print(f"Firestore save_chronicle error: {e}")
        return False




    def get_listening_guide(self, key: str) -> Optional[Dict[str, Any]]:
        if not self.db:
            return None
        try:
            doc = self.db.collection("listening_guides").document(key).get()
            if doc.exists:
                print(f"Loaded listening guide '{key}' from Firestore.")
                return doc.to_dict().get("guide")
        except Exception as e:
            print(f"Firestore get_listening_guide error: {e}")
        return None

    def save_listening_guide(self, key: str, guide_data: Dict[str, Any]) -> bool:
        if not self.db:
            return False
        try:
            self.db.collection("listening_guides").document(key).set({"guide": guide_data})
            print(f"Saved listening guide '{key}' to Firestore.")
            return True
        except Exception as e:
            print(f"Firestore save_listening_guide error: {e}")
        return False

    def get_release_assets(self, key: str) -> Optional[List[Dict[str, Any]]]:
        if not self.db:
            return None
        try:
            doc = self.db.collection("release_assets").document(key).get()
            if doc.exists:
                print(f"Loaded release assets '{key}' from Firestore.")
                return doc.to_dict().get("assets")
        except Exception as e:
            print(f"Firestore get_release_assets error: {e}")
        return None

    def save_release_assets(self, key: str, assets: List[Dict[str, Any]]) -> bool:
        if not self.db:
            return False
        try:
            self.db.collection("release_assets").document(key).set({"assets": assets})
            print(f"Saved release assets '{key}' to Firestore.")
            return True
        except Exception as e:
            print(f"Firestore save_release_assets error: {e}")
        return False

class VinylDatabase:
    def __init__(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        self.firestore = FirestoreManager()
        self._has_synced_firestore = False

        self.wishlist = list(INITIAL_WISHLIST)
        
        # Load local storage first for instant server startup (< 0.1s)
        self.records = self._load_records()
        self.spins_log = self._load_spins()
        self.chronicle = self._load_chronicle()
        self.now_spinning = None  # In-memory only state (resets to Standby on cold boot)

        # Non-blocking background Firestore sync
        if self.firestore.db:
            import threading
            threading.Thread(target=self.sync_firestore_on_startup, daemon=True).start()

    def ensure_firestore_synced(self):
        """Lazy-syncs Firestore in a non-blocking background thread when /api/records is called."""
        if self._has_synced_firestore:
            return
        self._has_synced_firestore = True
        import threading
        threading.Thread(target=self.sync_firestore_on_startup, daemon=True).start()

    def sync_firestore_on_startup(self):
        """Non-blocking background sync called after web server binds to PORT."""
        if not self.firestore.db:
            print("Firestore client unavailable; skipping startup sync.")
            return

        try:
            fs_recs, err = self.firestore.get_records()
            if fs_recs is None:
                print(f"Firestore get_records returned None ({err}); preserving existing records.")
                return

            if len(fs_recs) > 0:
                print(f"Firestore active with {len(fs_recs)} records.")
                self.records = fs_recs
                self._save_json(RECORDS_FILE, fs_recs)
                self._rebuild_record_map()
                print(f"Startup sync complete: {len(self.records)} records active from Firestore.")
            else:
                print("Firestore collection returned 0 records. Preserving local disk records.")
                if not self.records:
                    self.records = []
                    self.save_records()

        except Exception as e:
            print(f"Background Firestore sync warning: {e}")



    def _load_records(self) -> List[Dict[str, Any]]:
        loaded = []
        if os.path.exists(RECORDS_FILE):
            try:
                with open(RECORDS_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if data:
                        loaded = data
            except Exception as e:
                print(f"Error reading records.json: {e}")

        # No automatic reseeding from INITIAL_RECORDS
        filtered = [r for r in loaded if r.get("id") != "rec-001" and r.get("title") != "In Rainbows"]
        
        # Deduplicate records by normalized (title, artist)
        seen_keys = set()
        deduped = []
        for r in filtered:
            key = ((r.get("title") or "").strip().lower(), (r.get("artist") or "").strip().lower())
            if key not in seen_keys:
                seen_keys.add(key)
                deduped.append(r)

        if len(deduped) != len(loaded):
            self._save_json(RECORDS_FILE, deduped)
        return deduped

    def _load_spins(self) -> List[Dict[str, Any]]:
        if os.path.exists(SPINS_FILE):
            try:
                with open(SPINS_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if data:
                        return data
            except Exception as e:
                print(f"Error reading spins.json: {e}")
        return []

    def export_backup(self) -> Dict[str, Any]:
        return {
            "version": "1.0",
            "exportedAt": datetime.utcnow().isoformat() + "Z",
            "records": self.records,
            "spins_log": self.spins_log,
            "wishlist": self.wishlist
        }

    def restore_backup(self, backup_data: Dict[str, Any]) -> Dict[str, Any]:
        records = backup_data.get("records", [])
        spins = backup_data.get("spins_log", [])
        wishlist = backup_data.get("wishlist", [])

        if not isinstance(records, list):
            records = []

        self.records = records
        self.spins_log = spins if isinstance(spins, list) else []
        self.wishlist = wishlist if isinstance(wishlist, list) else []

        self.save_records()
        self.save_spins()

        if self.firestore.db and self.records:
            self.firestore.save_all_records_batch(self.records)

        return {
            "restoredRecordsCount": len(self.records),
            "restoredSpinsCount": len(self.spins_log)
        }

    def restore_sample_data(self) -> Dict[str, Any]:
        return {
            "restoredRecordsCount": 0,
            "restoredSpinsCount": 0
        }

    def _save_json(self, filepath: str, data: Any):
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error writing {filepath}: {e}")

    def _load_chronicle(self) -> Optional[Dict[str, Any]]:
        if os.path.exists(CHRONICLE_FILE):
            try:
                with open(CHRONICLE_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if data:
                        return data
            except Exception as e:
                print(f"Error reading chronicle.json: {e}")
        return None

    def save_chronicle(self, chronicle_data: Dict[str, Any]):
        self.chronicle = chronicle_data
        self._save_json(CHRONICLE_FILE, chronicle_data)
        if self.firestore.db:
            self.firestore.save_chronicle(chronicle_data)

    def get_chronicle(self) -> Optional[Dict[str, Any]]:
        if self.firestore.db:
            fs_chronicle = self.firestore.get_chronicle()
            if fs_chronicle and isinstance(fs_chronicle, dict) and fs_chronicle.get("totalClassicalRecords", 0) > 0:
                self.chronicle = fs_chronicle
                return fs_chronicle
        if not hasattr(self, "chronicle") or self.chronicle is None:
            self.chronicle = self._load_chronicle()
        return self.chronicle

    def clear_chronicle(self):
        self.chronicle = None
        self._save_json(CHRONICLE_FILE, {})
        if self.firestore.db:
            try:
                self.firestore.db.collection("metadata").document("chronicle").delete()
            except Exception as e:
                print(f"Firestore clear_chronicle error: {e}")


    def get_now_spinning(self) -> Optional[Dict[str, Any]]:
        return self.now_spinning

    def set_now_spinning(self, record_data: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        now_str = datetime.utcnow().isoformat() + "Z"
        if record_data:
            spinning_payload = {
                "recordId": record_data.get("id"),
                "startedAt": now_str,
                "record": record_data
            }
            self.now_spinning = spinning_payload
            return spinning_payload
        else:
            self.now_spinning = None
            return None




    def save_records(self):
        self._rebuild_record_map()
        self._save_json(RECORDS_FILE, self.records)


    def save_spins(self):
        self._save_json(SPINS_FILE, self.spins_log)

    def get_all_records(self, sync_if_needed: bool = False) -> List[Dict[str, Any]]:
        if sync_if_needed:
            if not self.firestore or not self.firestore.db:
                if self.firestore:
                    self.firestore._init_firestore()

            if self.firestore and self.firestore.db:
                try:
                    fs_recs, err = self.firestore.get_records()
                    if fs_recs is not None and len(fs_recs) > 0:
                        self.records = fs_recs
                        self._save_json(RECORDS_FILE, fs_recs)
                        self._rebuild_record_map()
                except Exception as e:
                    print(f"Error fetching direct records from Firestore: {e}")
        return self.records

    def get_all_records_with_status(self, sync_if_needed: bool = True) -> Tuple[List[Dict[str, Any]], bool, Optional[str]]:
        fs_connected = True
        fs_error = None

        if sync_if_needed:
            if not self.firestore or not self.firestore.db:
                if self.firestore:
                    self.firestore._init_firestore()

            if self.firestore and self.firestore.db:
                try:
                    fs_recs, err = self.firestore.get_records()
                    if fs_recs is not None:
                        self.records = fs_recs
                        self._save_json(RECORDS_FILE, fs_recs)
                        self._rebuild_record_map()
                    else:
                        fs_connected = False
                        fs_error = err or (self.firestore.last_error if self.firestore else "Firestore query returned None")
                except Exception as e:
                    fs_connected = False
                    fs_error = str(e)
            else:
                fs_connected = False
                fs_error = self.firestore.last_error if self.firestore else "Firestore client not initialized"

        return self.records, fs_connected, fs_error



    def _rebuild_record_map(self):
        self._record_map = {r["id"]: r for r in self.records if r and isinstance(r, dict) and r.get("id")}

    def get_record_by_id(self, record_id: str) -> Optional[Dict[str, Any]]:
        if hasattr(self, "_record_map") and self._record_map:
            return self._record_map.get(record_id)
        for r in self.records:
            if r.get("id") == record_id:
                return r
        return None


    def add_record(self, record_data: Dict[str, Any]) -> Dict[str, Any]:
        # Check for existing duplicate record by normalized title and artist
        norm_title = (record_data.get("title") or "").strip().lower()
        norm_artist = (record_data.get("artist") or "").strip().lower()

        for existing in self.records:
            e_title = (existing.get("title") or "").strip().lower()
            e_artist = (existing.get("artist") or "").strip().lower()
            if norm_title == e_title and norm_artist == e_artist:
                print(f"Prevented adding duplicate record for '{record_data.get('title')}'")
                return existing

        new_id = f"rec-user-{uuid.uuid4().hex[:8]}"

        record_data["id"] = new_id
        record_data["createdAt"] = datetime.utcnow().isoformat() + "Z"
        record_data["spinsCount"] = 0
        if "pressings" not in record_data or not record_data["pressings"]:
            record_data["pressings"] = [{
                "id": f"press-{new_id}",
                "recordId": new_id,
                "label": record_data.get("label", "Standard Release"),
                "formatDetails": "Standard Vinyl Pressing",
                "catalogNumber": record_data.get("catalogNumber", "")
            }]
        self.records.insert(0, record_data)
        self.save_records()

        fs_saved = False
        try:
            if self.firestore.db:
                fs_saved = self.firestore.save_record(record_data)
                print(f"Saved new record '{new_id}' ({record_data.get('title')}) to Firestore: {fs_saved}")
        except Exception as e:
            print(f"Error saving new record '{new_id}' to Firestore: {e}")

        self.clear_chronicle()
        return record_data


    def update_record(self, record_data: Any, record_dict_fallback: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Updates an existing record in memory and persists to Firestore.
        Flexible signature supports both update_record(rec_dict) and update_record(rec_id, rec_dict).
        """
        if isinstance(record_data, str) and record_dict_fallback is not None:
            record_data = record_dict_fallback
        elif not isinstance(record_data, dict) and isinstance(record_dict_fallback, dict):
            record_data = record_dict_fallback

        rec_id = record_data.get("id") if isinstance(record_data, dict) else None
        if not rec_id:
            return record_data if isinstance(record_data, dict) else {}

        for i, r in enumerate(self.records):
            if r.get("id") == rec_id:
                self.records[i] = record_data
                break
        else:
            self.records.insert(0, record_data)

        self.save_records()


        try:
            if self.firestore.db:
                success = self.firestore.save_record(record_data)
                print(f"Persisted record update '{rec_id}' to Firestore: {success}")
        except Exception as e:
            print(f"Error persisting record update '{rec_id}' to Firestore: {e}")

        self.clear_chronicle()
        return record_data


    def log_spin(self, record_id: str, notes: str = "") -> Dict[str, Any]:
        rec = self.get_record_by_id(record_id)
        now_str = datetime.utcnow().isoformat() + "Z"
        if rec:
            rec["spinsCount"] += 1
            rec["lastSpunAt"] = now_str
            self.save_records()
            self.firestore.save_record(rec)
        spin_entry = {
            "id": f"spin-{len(self.spins_log) + 1}",
            "recordId": record_id,
            "spunAt": now_str,
            "notes": notes
        }
        self.spins_log.insert(0, spin_entry)
        self.save_spins()
        self.firestore.save_spin(spin_entry)
        return spin_entry

    def get_wishlist(self) -> List[Dict[str, Any]]:
        return self.wishlist

    def get_spins_log(self) -> List[Dict[str, Any]]:
        return self.spins_log

    def delete_record(self, record_id: str) -> bool:
        initial_len = len(self.records)
        self.records = [r for r in self.records if r["id"] != record_id]
        if len(self.records) < initial_len:
            self.save_records()
            self.firestore.delete_record(record_id)
            return True
        return False

db = VinylDatabase()
