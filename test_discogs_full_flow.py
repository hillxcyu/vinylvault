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

def is_strict_discogs_match(req_artist: str, req_title: str, discogs_title: str) -> bool:
    clean_req_a = clean_term(req_artist).lower()
    clean_req_t = clean_term(req_title).lower()
    ret_title = discogs_title.lower()

    key_artist = extract_key_artist(req_artist).lower()
    artist_ok = (key_artist in ret_title) or (clean_req_a in ret_title)

    if not artist_ok:
        return False

    req_t_words = [w for w in clean_req_t.split() if len(w) > 3 and w not in ["major", "minor", "opus", "version", "disc", "lp", "edition"]]
    if not req_t_words:
        return True

    matches = sum(1 for w in req_t_words if w in ret_title)
    return matches >= 1

def fetch_discogs_only_assets(artist: str, title: str):
    clean_a = clean_term(artist)
    clean_t = clean_term(title)
    first_word = clean_t.split()[0] if clean_t else ""

    queries = [
        f"{clean_a} {clean_t}".strip(),
        f"{clean_a} {first_word}".strip()
    ]

    print(f"\nSearching Discogs for '{artist}' - '{title}'...")

    for q in queries:
        url = f"https://api.discogs.com/database/search?q={urllib.parse.quote(q)}&type=release"
        try:
            resp = requests.get(url, headers=headers, timeout=5)
            if resp.status_code == 200:
                results = resp.json().get("results", [])
                for r in results[:5]:
                    d_title = r.get("title", "")
                    rel_id = r.get("id")
                    if rel_id and is_strict_discogs_match(artist, title, d_title):
                        print(f"  ✅ Matched Discogs Release #{rel_id}: '{d_title}'")
                        # Fetch release images from Discogs Release Endpoint
                        rel_url = f"https://api.discogs.com/releases/{rel_id}"
                        rel_resp = requests.get(rel_url, headers=headers, timeout=5)
                        if rel_resp.status_code == 200:
                            imgs = rel_resp.json().get("images", [])
                            print(f"  -> Found {len(imgs)} Discogs CDN Image Assets:")
                            discogs_assets = []
                            for img in imgs:
                                uri = img.get("uri") or img.get("resource_url")
                                img_type = "Discogs Primary Cover" if img.get("type") == "primary" else "Discogs Release Asset (Sleeve / Disc)"
                                print(f"     * [{img_type}]: {uri}")
                                discogs_assets.append({
                                    "type": img_type,
                                    "url": uri,
                                    "isPrimary": img.get("type") == "primary"
                                })
                            if discogs_assets:
                                return discogs_assets
        except Exception as e:
            print("Error querying Discogs API:", e)

    print("No Discogs match found")
    return []

if __name__ == "__main__":
    fetch_discogs_only_assets("Paul Tortelier", "Dvorak Cello Concerto")
    fetch_discogs_only_assets("Isaac Stern", "Sibelius & Bruch Violin Concertos")
    fetch_discogs_only_assets("Otto Klemperer", "Beethoven Symphony No 7")
