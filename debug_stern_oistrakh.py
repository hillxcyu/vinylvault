import requests
import urllib.parse
import re

headers = {
    "User-Agent": "VinylVaultApp/1.0 +http://vinyl-vault-456465962826.us-central1.run.app"
}

def clean_term(text: str) -> str:
    text_no_cn = re.sub(r'[\u4e00-\u9fff]+', '', text)
    cleaned = re.sub(r'[^\w\s]', ' ', text_no_cn)
    return ' '.join(cleaned.split())

def extract_key_artist(artist_str: str) -> str:
    cleaned = clean_term(artist_str)
    words = [w for w in cleaned.split() if w.lower() not in ["orchestra", "philharmonic", "symphony", "quartet", "trio", "ensemble", "band", "sir"]]
    return words[-1] if words else cleaned

artist = "Isaac Stern (伊萨克·斯特恩)"
title = "Sibelius & Bruch: Violin Concertos"

clean_a = clean_term(artist)
clean_t = clean_term(title)
key_artist = extract_key_artist(artist).lower()

print(f"clean_a: '{clean_a}'")
print(f"clean_t: '{clean_t}'")
print(f"key_artist: '{key_artist}'")

search_url = f"https://api.discogs.com/database/search?q={urllib.parse.quote(clean_a + ' ' + clean_t)}&type=release&format=vinyl"
print(f"Querying Discogs: {search_url}")

resp = requests.get(search_url, headers=headers, timeout=5)
if resp.status_code == 200:
    results = resp.json().get("results", [])
    print(f"Found {len(results)} results:")
    for r in results:
        d_title = r.get("title", "")
        rel_id = r.get("id")
        print(f"\n  - Release #{rel_id}: '{d_title}'")

        # Check why Oistrakh matched
        artist_ok = (key_artist in d_title.lower()) or (clean_a.lower() in d_title.lower())
        print(f"    artist_ok ('{key_artist}' in '{d_title.lower()}'): {artist_ok}")
