import requests
import urllib.parse
from bs4 import BeautifulSoup

headers = {
    "User-Agent": "VinylVaultApp/1.0 (contact@example.com)"
}

def get_discogs_og_image(artist: str, title: str) -> str:
    """
    Search Discogs web for release page and extract high-resolution og:image artwork
    """
    try:
        q = f"{artist} {title} vinyl release"
        url = f"https://www.discogs.com/search/?q={urllib.parse.quote(q)}&type=release"
        resp = requests.get(url, headers=headers, timeout=5)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")
            # Find first release link or image
            img_tag = soup.find("img", class_=lambda c: c and "thumbnail" in c)
            if img_tag and img_tag.get("src"):
                src = img_tag["src"]
                print("Discogs web thumbnail found:", src)
                return src
    except Exception as e:
        print("Discogs web error:", e)
    return None

def get_musicbrainz_cover(artist: str, title: str) -> str:
    """
    Fetch high-res vinyl cover art from MusicBrainz + Cover Art Archive
    """
    try:
        q = f'artist:"{artist}" AND release:"{title}"'
        mb_url = f"https://musicbrainz.org/ws/2/release/?query={urllib.parse.quote(q)}&fmt=json"
        resp = requests.get(mb_url, headers=headers, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            releases = data.get("releases", [])
            if releases:
                release_id = releases[0]["id"]
                # Query Cover Art Archive
                caa_url = f"https://coverartarchive.org/release/{release_id}"
                caa_resp = requests.get(caa_url, headers=headers, timeout=5)
                if caa_resp.status_code == 200:
                    caa_data = caa_resp.json()
                    images = caa_data.get("images", [])
                    if images:
                        primary_img = images[0].get("image") or images[0].get("thumbnails", {}).get("large")
                        print("MusicBrainz / CoverArtArchive image found:", primary_img)
                        return primary_img
    except Exception as e:
        print("MusicBrainz error:", e)
    return None

if __name__ == "__main__":
    print("Testing MusicBrainz Cover Art Archive for 'Currents' by Tame Impala...")
    url1 = get_musicbrainz_cover("Tame Impala", "Currents")
    print("Result 1:", url1)

    print("\nTesting MusicBrainz for 'Dvořák Cello Concerto'...")
    url2 = get_musicbrainz_cover("Paul Tortelier", "Dvorak Cello Concerto")
    print("Result 2:", url2)
