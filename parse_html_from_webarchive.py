import plistlib
from bs4 import BeautifulSoup

webarchive_path = "/usr/local/google/home/xcyu/vinyl-vault/purchase_vinyl.webarchive"

def parse_html():
    with open(webarchive_path, "rb") as f:
        data = plistlib.load(f)

    html_bytes = data["WebMainResource"]["WebResourceData"]
    html_str = html_bytes.decode("utf-8", errors="ignore")

    print(f"HTML Length: {len(html_str)} chars")

    soup = BeautifulSoup(html_str, "html.parser")
    
    # Print page title and text snippets
    print("Title:", soup.title.string if soup.title else "No title")

    # Search for text elements (goods titles, prices, album names)
    text_blocks = [s.strip() for s in soup.stripped_strings if len(s.strip()) > 3]
    print("\n--- SAMPLE TEXT BLOCKS FROM WEBARCHIVE (First 30) ---")
    for t in text_blocks[:30]:
        print("•", t)

if __name__ == "__main__":
    parse_html()
