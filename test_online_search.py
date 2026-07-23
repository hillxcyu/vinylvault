import requests
import urllib.parse
import re

headers = {"User-Agent": "VinylVaultApp/1.0 (vinyl-vault@example.com)"}

def clean_search_term(text: str) -> str:
    # Remove Chinese characters and brackets
    text_no_cn = re.sub(r'[\u4e00-\u9fff]+', '', text)
    # Remove special chars
    cleaned = re.sub(r'[^\w\s]', ' ', text_no_cn)
    return ' '.join(cleaned.split())

def test_online_assets(artist: str, title: str):
    clean_a = clean_search_term(artist)
    clean_t = clean_search_term(title)

    queries = [
        f"{clean_a} {clean_t}",
        f"{clean_t}",
        clean_t.split()[0] + " " + clean_t.split()[1] if len(clean_t.split()) > 1 else clean_t
    ]

    for q in queries:
        mb_url = f"https://musicbrainz.org/ws/2/release/?query={urllib.parse.quote(q)}&fmt=json"
        print(f"\nTrying MusicBrainz query: '{q}'")
        resp = requests.get(mb_url, headers=headers, timeout=5)
        if resp.status_code == 200:
            releases = resp.json().get("releases", [])
            print(f"Found {len(releases)} releases on MusicBrainz")
            for rel in releases[:5]:
                rel_id = rel["id"]
                caa_url = f"https://coverartarchive.org/release/{rel_id}"
                caa_resp = requests.get(caa_url, headers=headers, timeout=5)
                if caa_resp.status_code == 200:
                    imgs = caa_resp.json().get("images", [])
                    print(f"  -> Found {len(imgs)} CoverArtArchive online image assets for release {rel_id} ({rel.get('title')}):")
                    for img in imgs:
                        print(f"     - Type: {img.get('types')} -> {img.get('image')}")
                    return imgs

if __name__ == "__main__":
    test_online_assets("Paul Tortelier / Sir Malcolm Sargent", "Dvořák: Cello Concerto in B minor")
    test_online_assets("Michio Kobayashi (小林道夫)", "Bach: French Suites BWV 812-817 (法国组曲 2LP)")
