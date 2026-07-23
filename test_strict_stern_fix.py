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

def is_strict_primary_artist_match(req_artist: str, req_title: str, discogs_release_data: dict) -> bool:
    clean_req_a = clean_term(req_artist).lower()
    clean_req_t = clean_term(req_title).lower()

    artist_words = [w for w in clean_req_a.split() if len(w) > 2 and w not in ["orchestra", "philharmonic", "symphony", "quartet", "trio", "ensemble", "band", "sir"]]

    d_title = discogs_release_data.get("title", "").lower()
    d_artists = " ".join([a.get("name", "").lower() for a in discogs_release_data.get("artists", [])])

    # 1. Primary Artist Check: All requested artist words must be in primary artist credits OR release title
    artist_in_credit = all(w in d_artists for w in artist_words)
    artist_in_title = all(w in d_title for w in artist_words)

    if not (artist_in_credit or artist_in_title):
        return False

    # 2. Reject mismatched lead performers in classical concertos
    other_violinists = ["oistrakh", "oistrach", "perlman", "francescatti", "heifetz", "ricci", "ishikawa", "ushioda"]
    if "stern" in clean_req_a:
        for other in other_violinists:
            if other in d_title or other in d_artists:
                print(f"    -> Rejected because '{other}' was found in release!")
                return False

    # 3. Check Work Title (e.g. "sibelius" or "bruch" or "violin concerto")
    work_words = [w for w in clean_req_t.split() if len(w) > 3 and w not in ["major", "minor", "opus", "version", "disc", "lp", "edition"]]
    work_matches = sum(1 for w in work_words if w in d_title)
    return work_matches >= 1

def test_strict_stern():
    artist = "Isaac Stern (伊萨克·斯特恩)"
    title = "Sibelius & Bruch: Violin Concertos"

    clean_a = clean_term(artist)
    clean_t = clean_term(title)

    queries = [
        f"{clean_a} Sibelius",
        f"{clean_a} Bruch",
        f"{clean_a} Violin Concerto"
    ]

    print(f"\nTesting strict primary artist queries for '{clean_a}' - '{clean_t}'...")

    for q in queries:
        search_url = f"https://api.discogs.com/database/search?q={urllib.parse.quote(q)}&type=release&format=vinyl"
        resp = requests.get(search_url, headers=headers, timeout=5)
        if resp.status_code == 200:
            results = resp.json().get("results", [])
            for r in results[:5]:
                rel_id = r.get("id")
                rel_url = f"https://api.discogs.com/releases/{rel_id}"
                rel_resp = requests.get(rel_url, headers=headers, timeout=5)
                if rel_resp.status_code == 200:
                    rel_data = rel_resp.json()
                    if is_strict_primary_artist_match(artist, title, rel_data):
                        imgs = rel_data.get("images", [])
                        print(f"  ✅ PERFECT ISAAC STERN RELEASE #{rel_id}: '{rel_data.get('title')}'")
                        print(f"     Primary Cover: {imgs[0].get('uri') if imgs else 'None'}")
                        return imgs
                    else:
                        print(f"  ❌ REJECTED MISMATCH #{rel_id}: '{rel_data.get('title')}'")
    return []

if __name__ == "__main__":
    test_strict_stern()
