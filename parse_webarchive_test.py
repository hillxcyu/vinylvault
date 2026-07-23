import plistlib
import os

webarchive_path = "/usr/local/google/home/xcyu/vinyl-vault/purchase_vinyl.webarchive"

def inspect_webarchive():
    if not os.path.exists(webarchive_path):
        print("File not found")
        return

    with open(webarchive_path, "rb") as f:
        data = plistlib.load(f)

    print("Keys in webarchive:", list(data.keys()))

    main_res = data.get("WebMainResource", {})
    print("Main resource MIME:", main_res.get("WebResourceMIMEType"))
    print("Main resource URL:", main_res.get("WebResourceURL"))

    subresources = data.get("WebSubresources", [])
    print(f"Total subresources: {len(subresources)}")

    image_count = 0
    for i, sub in enumerate(subresources):
        mime = sub.get("WebResourceMIMEType", "")
        url = sub.get("WebResourceURL", "")
        res_data = sub.get("WebResourceData", b"")
        if mime.startswith("image") or len(res_data) > 5000:
            image_count += 1
            print(f"[{i}] {mime} - {len(res_data)} bytes - URL: {url[:80]}")

    print(f"\nTotal image resources found: {image_count}")

if __name__ == "__main__":
    inspect_webarchive()
