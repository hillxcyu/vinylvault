import requests

headers = {
    "User-Agent": "VinylVaultApp/1.0 +http://vinyl-vault-456465962826.us-central1.run.app"
}

def test_release_details(release_id: int):
    url = f"https://api.discogs.com/releases/{release_id}"
    print(f"\nFetching Discogs Release #{release_id} details -> {url}")
    resp = requests.get(url, headers=headers, timeout=5)
    print("Status:", resp.status_code)
    if resp.status_code == 200:
        data = resp.json()
        print("Title:", data.get("title"))
        print("Artists:", [a.get("name") for a in data.get("artists", [])])
        images = data.get("images", [])
        print(f"Found {len(images)} Discogs release image assets:")
        for img in images:
            print(f"  - Type: {img.get('type')} ({img.get('width')}x{img.get('height')}) -> {img.get('uri') or img.get('resource_url')}")
        return images
    else:
        print("Response:", resp.text[:200])
    return []

if __name__ == "__main__":
    # Test with Discogs releases
    test_release_details(7240212)  # Tame Impala Currents release
