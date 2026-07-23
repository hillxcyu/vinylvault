import requests
import urllib.parse
import re

headers = {
    "User-Agent": "VinylVaultApp/1.0 (vinyl-vault@example.com)",
    "Accept": "application/json"
}

def clean_search_term(text: str) -> str:
    text_no_cn = re.sub(r'[\u4e00-\u9fff]+', '', text)
    cleaned = re.sub(r'[^\w\s]', ' ', text_no_cn)
    return ' '.join(cleaned.split())

def test_online_assets(artist: str, title: str):
    clean_a = clean_search_term(artist)
    clean_t = clean_search_term(title)

    q = f"{clean_a} {clean_t}"
    mb_url = f"https://musicbrainz.org/ws/2/release/?query={urllib.parse.quote(q)}&fmt=json"
    print(f"\nTrying MusicBrainz query: '{q}'")
    try:
        resp = requests.get(mb_url, headers=headers, timeout=5)
        if resp.status_code == 200:
            releases = resp.json().get("releases", [])
            print(f"Found {len(releases)} releases on MusicBrainz")
            for rel in releases[:5]:
                rel_id = rel["id"]
                # Use http:// or caa URL
                caa_url = f"http://coverartarchive.org/release/{rel_id}"
                try:
                    caa_resp = requests.get(caa_url, headers=headers, timeout=5)
                    if caa_resp.status_code == 200:
                        imgs = caa_resp.json().get("images", [])
                        print(f"  -> SUCCESS! Found {len(imgs)} CoverArtArchive online image assets for release {rel_id} ({rel.get('title')}):")
                        for img in imgs:
                            print(f"     - Type: {img.get('types')} -> {img.get('image')}")
                        return imgs
                except Exception as caa_err:
                    print(f"  CAA error for release {rel_id}: {caa_err}")
    except Exception as mb_err:
        print(f"MB error: {mb_err}")

if __name__ == "__main__":
    test_online_assets("Paul Tortelier", "Dvorak Cello Concerto")
    test_online_assets("Tame Impala", "Currents")
