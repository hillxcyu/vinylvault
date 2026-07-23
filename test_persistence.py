from database import db

print("Initial record count:", len(db.get_all_records()))

# Add new record
new_rec = db.add_record({
    "artist": "Radiohead",
    "title": "In Rainbows",
    "genre": "Alternative Rock",
    "releaseYear": 2007,
    "coverUrl": "/static/extracted_covers/shopping_cover_2.jpg"
})
print("Added new record:", new_rec["id"], "-", new_rec["title"])

# Re-instantiate db (simulating service restart)
from database import VinylDatabase
new_db_instance = VinylDatabase()
records_after_restart = new_db_instance.get_all_records()
print("Record count after service restart:", len(records_after_restart))
print("First record in crate:", records_after_restart[0]["title"], "(Artist:", records_after_restart[0]["artist"], ")")
