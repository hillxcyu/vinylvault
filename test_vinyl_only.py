import requests
import urllib.parse

headers = {
    "User-Agent": "VinylVaultApp/1.0 +http://vinyl-vault-456465962826.us-central1.run.app"
}

def test_vinyl_only_discogs(artist: str, title: str):
    q = f"{artist} {title}".strip()
    search_url = f"https://api.discogs.com/database/search?q={urllib.parse.quote(q)}&type=release&format=vinyl"
    print(f"\nSearching Discogs Vinyl-Only for '{q}' -> {search_url}")

    resp = requests.get(search_url, headers=headers, timeout=5)
    if resp.status_code == 200:
        results = resp.json().get("results", [])
        print(f"Found {len(results)} Discogs Vinyl release results:")
        for r in results[:5]:
            rel_id = r.get("id")
            rel_url = f"https://api.discogs.com/releases/{rel_id}"
            rel_resp = requests.get(rel_url, headers=headers, timeout=5)
            if rel_resp.status_code == 200:
                rel_data = rel_resp.json()
                formats = rel_data.get("formats", [])
                fmt_names = [f.get("name") for f in formats]
                descriptions = [d for f in formats for d in f.get("descriptions", [])]
                print(f"  - Release #{rel_id} ({rel_data.get('title')}) Formats: {fmt_names} ({descriptions})")
                
                is_vinyl = any("Vinyl" in name or "LP" in descriptions or '12"' in descriptions for name in fmt_names)
                if is_vinyl:
                    imgs = rel_data.get("images", [])
                    print(f"    ✅ Genuine Vinyl LP Images Found: {len(imgs)} assets")
                    for img in imgs[:3]:
                        print(f"       * {img.get('uri')}")
                    return imgs

if __name__ == "__main__":
    test_vinyl_only_discogs("Paul Tortelier", "Dvorak Cello Concerto")
    test_vinyl_only_discogs("Isaac Stern", "Sibelius & Bruch Violin Concertos")
