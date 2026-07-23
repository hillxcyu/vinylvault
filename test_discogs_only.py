import requests
import urllib.parse
import re
from bs4 import BeautifulSoup

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
}

def clean_term(text: str) -> str:
    text_no_cn = re.sub(r'[\u4e00-\u9fff]+', '', text)
    cleaned = re.sub(r'[^\w\s]', ' ', text_no_cn)
    return ' '.join(cleaned.split())

def extract_discogs_assets(artist: str, title: str):
    clean_a = clean_term(artist)
    clean_t = clean_term(title)
    q = f"{clean_a} {clean_t} vinyl"

    search_url = f"https://www.discogs.com/search/?q={urllib.parse.quote(q)}&type=release"
    print(f"\nQuerying Discogs for '{q}' -> {search_url}")

    assets = []

    try:
        resp = requests.get(search_url, headers=headers, timeout=5)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")

            # Extract thumbnails / release images from Discogs search results
            img_tags = soup.find_all("img", class_=lambda c: c and ("thumbnail" in c or "card-img" in c or "lazy" in c))
            for img in img_tags:
                src = img.get("src") or img.get("data-src")
                if src and "discogs" in src and not src.endswith("spacer.gif"):
                    high_res = src.replace("R-90-", "R-600-").replace("/150x150/", "/600x600/")
                    if not any(a["url"] == high_res for a in assets):
                        assets.append({
                            "type": "Discogs Official Release Artwork",
                            "url": high_res,
                            "thumbnail": src,
                            "isPrimary": (len(assets) == 0),
                            "comment": "Fetched directly from Discogs"
                        })

            print(f"Retrieved {len(assets)} Discogs image assets for '{title}':")
            for a in assets[:5]:
                print(f"  - Discogs Asset: {a['url']}")
            return assets
    except Exception as e:
        print(f"Discogs fetch error: {e}")

    return []

if __name__ == "__main__":
    extract_discogs_assets("Isaac Stern", "Sibelius & Bruch Violin Concertos")
    extract_discogs_assets("Paul Tortelier", "Dvorak Cello Concerto")
    extract_discogs_assets("Tame Impala", "Currents")
