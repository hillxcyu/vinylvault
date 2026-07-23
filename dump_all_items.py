import plistlib
from bs4 import BeautifulSoup

webarchive_path = "/usr/local/google/home/xcyu/vinyl-vault/purchase_vinyl.webarchive"

def dump_all():
    with open(webarchive_path, "rb") as f:
        data = plistlib.load(f)

    html_bytes = data["WebMainResource"]["WebResourceData"]
    html_str = html_bytes.decode("utf-8", errors="ignore")
    soup = BeautifulSoup(html_str, "html.parser")

    # Extract all text elements
    text_blocks = [s.strip() for s in soup.stripped_strings if len(s.strip()) > 3]

    ignore_keywords = ["满30减2", "48小时发货", "7天无理由退货", "立即拼单", "川拼过的商品", "拼单", "登录", "查看更多", "客服"]

    album_items = []
    for t in text_blocks:
        if any(kw in t for kw in ignore_keywords):
            continue
        # Check if text is an album product title
        if t not in album_items and len(t) > 5:
            album_items.append(t)

    print(f"Total Unique Product Text Blocks Found: {len(album_items)}\n")
    for idx, title in enumerate(album_items, 1):
        print(f"{idx:02d}. {title}")

if __name__ == "__main__":
    dump_all()
