import requests
import urllib.parse

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def test_itunes_album_assets(artist: str, title: str):
    q = f"{artist} {title}"
    url = f"https://itunes.apple.com/search?term={urllib.parse.quote(q)}&entity=album&limit=5"
    print(f"\nQuerying iTunes API for '{q}'...")
    try:
        resp = requests.get(url, headers=headers, timeout=5)
        if resp.status_code == 200:
            results = resp.json().get("results", [])
            print(f"Found {len(results)} album matches on iTunes API")
            for r in results:
                art100 = r.get("artworkUrl100", "")
                art1000 = art100.replace("100x100bb", "1000x1000bb") if art100 else ""
                print(f"  -> Album: {r.get('collectionName')} by {r.get('artistName')}")
                print(f"     High-Res Cover URL: {art1000}")
                return art1000
    except Exception as e:
        print(f"iTunes API error: {e}")
    return None

if __name__ == "__main__":
    test_itunes_album_assets("Paul Tortelier", "Dvorak Cello Concerto")
    test_itunes_album_assets("Tame Impala", "Currents")
    test_itunes_album_assets("Michio Kobayashi", "Bach French Suites")
