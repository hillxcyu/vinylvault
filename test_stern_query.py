import requests
import urllib.parse
from test_artist_strict_matching import is_strict_release_match, clean_term, headers

def test_stern():
    artist = "Isaac Stern"
    title = "Sibelius & Bruch Violin Concertos"

    clean_a = clean_term(artist)
    clean_t = clean_term(title)
    first_word = clean_t.split()[0] if clean_t else ""

    queries = [
        f"{clean_a} {clean_t}",
        f"{clean_a} {first_word}",
        clean_a
    ]

    for q in queries:
        url = f"https://itunes.apple.com/search?term={urllib.parse.quote(q)}&entity=album&limit=10"
        resp = requests.get(url, headers=headers, timeout=5)
        if resp.status_code == 200:
            results = resp.json().get("results", [])
            for r in results:
                ret_a = r.get("artistName", "")
                ret_t = r.get("collectionName", "")
                if is_strict_release_match(artist, title, ret_a, ret_t):
                    art1000 = r.get("artworkUrl100", "").replace("100x100bb", "1000x1000bb")
                    print(f"✅ FOUND MATCH FOR STERN: '{ret_t}' by '{ret_a}' -> {art1000}")
                    return art1000
    print("No match found")
    return None

if __name__ == "__main__":
    test_stern()
