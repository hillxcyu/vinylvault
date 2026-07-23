import requests
import urllib.parse
import re

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

def clean_term(text: str) -> str:
    text_no_cn = re.sub(r'[\u4e00-\u9fff]+', '', text)
    cleaned = re.sub(r'[^\w\s]', ' ', text_no_cn)
    return ' '.join(cleaned.split())

def extract_key_artist(artist_str: str) -> str:
    cleaned = clean_term(artist_str)
    words = [w for w in cleaned.split() if w.lower() not in ["orchestra", "philharmonic", "symphony", "quartet", "trio", "ensemble", "band", "sir"]]
    return words[-1] if words else cleaned

def is_strict_release_match(req_artist: str, req_title: str, ret_artist: str, ret_title: str) -> bool:
    clean_req_a = clean_term(req_artist).lower()
    clean_req_t = clean_term(req_title).lower()
    clean_ret_a = ret_artist.lower()
    clean_ret_t = ret_title.lower()

    key_artist = extract_key_artist(req_artist).lower()
    artist_ok = (key_artist in clean_ret_a) or (key_artist in clean_ret_t) or (clean_req_a in clean_ret_a)

    if not artist_ok:
        return False

    req_t_words = [w for w in clean_req_t.split() if len(w) > 3 and w not in ["major", "minor", "opus", "version", "disc", "lp", "edition", "part", "vol"]]
    if not req_t_words:
        return True

    matches = sum(1 for w in req_t_words if w in clean_ret_t)
    return matches >= 1

def test_strict_itunes(artist: str, title: str):
    q = f"{clean_term(artist)} {clean_term(title)}".strip()
    url = f"https://itunes.apple.com/search?term={urllib.parse.quote(q)}&entity=album&limit=10"
    print(f"\nQuerying iTunes API for '{q}'...")
    resp = requests.get(url, headers=headers, timeout=5)
    if resp.status_code == 200:
        results = resp.json().get("results", [])
        verified_results = []
        for r in results:
            ret_a = r.get("artistName", "")
            ret_t = r.get("collectionName", "")
            if is_strict_release_match(artist, title, ret_a, ret_t):
                art1000 = r.get("artworkUrl100", "").replace("100x100bb", "1000x1000bb")
                verified_results.append((ret_a, ret_t, art1000))
                print(f"  ✅ STERN/ARTIST MATCH: '{ret_t}' by '{ret_a}' -> {art1000}")
            else:
                print(f"  ❌ REJECTED (Artist Mismatch): '{ret_t}' by '{ret_a}'")
        return verified_results

if __name__ == "__main__":
    test_strict_itunes("Isaac Stern", "Sibelius & Bruch Violin Concertos")
    test_strict_itunes("Paul Tortelier", "Dvorak Cello Concerto")
    test_strict_itunes("Otto Klemperer", "Beethoven Symphony No. 7")
