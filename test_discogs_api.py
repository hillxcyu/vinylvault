import requests
import urllib.parse
import re

headers = {
    "User-Agent": "VinylVaultApp/1.0 +http://vinyl-vault-456465962826.us-central1.run.app"
}

def test_discogs_api_search(artist: str, title: str):
    clean_a = re.sub(r'[\u4e00-\u9fff]+', '', artist).strip()
    clean_t = re.sub(r'[\u4e00-\u9fff]+', '', title).strip()
    q = f"{clean_a} {clean_t}"

    url = f"https://api.discogs.com/database/search?q={urllib.parse.quote(q)}&type=release"
    print(f"\nQuerying Discogs API for '{q}' -> {url}")
    try:
        resp = requests.get(url, headers=headers, timeout=5)
        print(f"Status code: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            results = data.get("results", [])
            print(f"Found {len(results)} Discogs release results:")
            for r in results[:5]:
                cover = r.get("cover_image") or r.get("thumb")
                title_discogs = r.get("title")
                catno = r.get("catno")
                print(f"  - Title: {title_discogs} (Cat#: {catno})")
                print(f"    Discogs Cover Image URL: {cover}")
        else:
            print("Response:", resp.text[:200])
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    test_discogs_api_search("Isaac Stern", "Sibelius & Bruch Violin Concertos")
    test_discogs_api_search("Paul Tortelier", "Dvorak Cello Concerto")
    test_discogs_api_search("Tame Impala", "Currents")
