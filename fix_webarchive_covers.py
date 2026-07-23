import json
from batch_import_all_48 import ALBUM_ITEMS_CATALOG

records_list = []
for i, item in enumerate(ALBUM_ITEMS_CATALOG, 1):
    # Fix 1-item offset: cover 1 was introductory banner, cover 2 is item 1!
    img_idx = i + 1  # Item 1 -> shopping_cover_2.jpg, Item 2 -> shopping_cover_3.jpg ...
    rec = {
        "id": f"rec-webarchive-{i:03d}",
        "title": item["title"],
        "artist": item["artist"],
        "releaseYear": item["year"],
        "genre": item["genre"],
        "coverUrl": f"/static/extracted_covers/shopping_cover_{img_idx}.jpg",
        "catalogNumber": f"IMP-2026-{i:03d}",
        "createdAt": "2026-07-14T07:30:00Z",
        "spinsCount": (i * 3) % 15,
        "lastSpunAt": "2026-07-14T07:00:00Z",
        "pressings": [
            {
                "id": f"press-webarchive-{i:03d}",
                "recordId": f"rec-webarchive-{i:03d}",
                "label": item["label"],
                "country": "US / Japan",
                "releaseYear": item["year"],
                "formatDetails": "12\" Mastered LP",
                "catalogNumber": f"IMP-2026-{i:03d}"
            }
        ]
    }
    records_list.append(rec)

database_py_content = f"""import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime

INITIAL_RECORDS = {json.dumps(records_list, indent=4, ensure_ascii=False)}

INITIAL_WISHLIST = [
    {{
        "id": "wish-1",
        "title": "Demon Days",
        "artist": "Gorillaz",
        "notes": "VMP Red vinyl pressing preferred",
        "priority": "HIGH",
        "createdAt": "2026-06-01T10:00:00Z"
    }},
    {{
        "id": "wish-2",
        "title": "Rumours",
        "artist": "Fleetwood Mac",
        "notes": "45 RPM Hoffman/Gray mastering",
        "priority": "MEDIUM",
        "createdAt": "2026-06-15T12:00:00Z"
    }}
]

class VinylDatabase:
    def __init__(self):
        self.records = list(INITIAL_RECORDS)
        self.wishlist = list(INITIAL_WISHLIST)
        self.spins_log = [
            {{"id": "spin-1", "recordId": "rec-webarchive-001", "spunAt": "2026-07-14T07:00:00Z", "notes": "Bach French Suites - Excellent pressing"}},
            {{"id": "spin-2", "recordId": "rec-webarchive-009", "spunAt": "2026-07-14T06:30:00Z", "notes": "Dvořák Cello Concerto performance"}}
        ]

    def get_all_records(self) -> List[Dict[str, Any]]:
        return self.records

    def get_record_by_id(self, record_id: str) -> Optional[Dict[str, Any]]:
        for r in self.records:
            if r["id"] == record_id:
                return r
        return None

    def add_record(self, record_data: Dict[str, Any]) -> Dict[str, Any]:
        new_id = f"rec-user-{{len(self.records) + 100}}"
        record_data["id"] = new_id
        record_data["createdAt"] = datetime.utcnow().isoformat() + "Z"
        record_data["spinsCount"] = 0
        if "pressings" not in record_data or not record_data["pressings"]:
            record_data["pressings"] = [{{
                "id": f"press-{{new_id}}",
                "recordId": new_id,
                "label": record_data.get("label", "Standard Release"),
                "formatDetails": "Standard Vinyl Pressing",
                "catalogNumber": record_data.get("catalogNumber", "")
            }}]
        self.records.insert(0, record_data)
        return record_data

    def log_spin(self, record_id: str, notes: str = "") -> Dict[str, Any]:
        rec = self.get_record_by_id(record_id)
        now_str = datetime.utcnow().isoformat() + "Z"
        if rec:
            rec["spinsCount"] += 1
            rec["lastSpunAt"] = now_str
        spin_entry = {{
            "id": f"spin-{{len(self.spins_log) + 1}}",
            "recordId": record_id,
            "spunAt": now_str,
            "notes": notes
        }}
        self.spins_log.insert(0, spin_entry)
        return spin_entry

    def get_wishlist(self) -> List[Dict[str, Any]]:
        return self.wishlist

    def get_spins_log(self) -> List[Dict[str, Any]]:
        return self.spins_log

db = VinylDatabase()
"""

with open("/usr/local/google/home/xcyu/vinyl-vault/database.py", "w", encoding="utf-8") as f:
    f.write(database_py_content)

print("database.py successfully updated with 1-item offset fix! (shopping_cover_2.jpg is item 1)")
