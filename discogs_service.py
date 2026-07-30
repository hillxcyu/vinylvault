import requests
import urllib.parse
import logging
import re
from typing import Optional, List, Dict, Any

logger = logging.getLogger("discogs_service")

class DiscogsService:
    def __init__(self):
        self.headers = {
            "User-Agent": "VinylVaultApp/1.0 +http://vinyl-vault-456465962826.us-central1.run.app"
        }

    def clean_search_term(self, text: str) -> str:
        text_no_cn = re.sub(r'[\u4e00-\u9fff]+', '', text)
        cleaned = re.sub(r'[^\w\s]', ' ', text_no_cn)
        return ' '.join(cleaned.split())

    def extract_artist_words(self, artist_str: str) -> List[str]:
        cleaned = self.clean_search_term(artist_str).lower()
        return [w for w in cleaned.split() if len(w) > 2 and w not in ["orchestra", "philharmonic", "symphony", "quartet", "trio", "ensemble", "band", "sir"]]

    def is_strict_discogs_match(self, req_artist: str, req_title: str, rel_data: dict) -> bool:
        clean_req_a = self.clean_search_term(req_artist).lower()
        clean_req_t = self.clean_search_term(req_title).lower()

        artist_words = self.extract_artist_words(req_artist)
        if not artist_words:
            return True

        d_title = rel_data.get("title", "").lower()
        d_artists = " ".join([a.get("name", "").lower() for a in rel_data.get("artists", [])])

        # 1. Primary Artist Check: All requested artist words must be in primary artist credits OR release title
        artist_in_credit = all(w in d_artists for w in artist_words)
        artist_in_title = all(w in d_title for w in artist_words)

        if not (artist_in_credit or artist_in_title):
            return False

        # 2. Reject mismatched lead performers in classical concertos / solo releases
        other_performers = ["oistrakh", "oistrach", "perlman", "francescatti", "heifetz", "ricci", "ishikawa", "ushioda"]
        if "stern" in clean_req_a:
            for other in other_performers:
                if other in d_title or other in d_artists:
                    logger.info(f"Rejecting Discogs release for Stern due to conflicting performer '{other}'")
                    return False

        # 3. Work Title Check
        work_words = [w for w in clean_req_t.split() if len(w) > 3 and w not in ["major", "minor", "opus", "version", "disc", "lp", "edition", "part", "vol"]]
        if not work_words:
            return True

        matches = sum(1 for w in work_words if w in d_title)
        return matches >= 1

    def fetch_official_cover(self, artist: str, title: str, cover_url: Optional[str] = None) -> Optional[str]:
        """
        Fetch official album cover art EXCLUSIVELY from Discogs API for vinyl releases.
        """
        assets = self.fetch_all_release_assets(artist, title, cover_url=cover_url)
        if assets:
            for a in assets:
                url = a.get("url", "")
                if a.get("isPrimary") and url and "shopping_cover_2.jpg" not in url:
                    return url
            for a in assets:
                url = a.get("url", "")
                if url and "shopping_cover_2.jpg" not in url:
                    return url
            return assets[0].get("url")
        return cover_url



    def fetch_all_release_assets(
        self,
        artist: str,
        title: str,
        cover_url: Optional[str] = None,
        catalog_number: Optional[str] = None,
        country: Optional[str] = "Japan"
    ) -> List[Dict[str, Any]]:
        """
        Fetch image assets EXCLUSIVELY from Discogs API for VINYL pressings.
        Prioritizes Japan pressings and catalog numbers (catno), returning top 10 front artwork choices.
        """
        assets = []

        clean_a = self.clean_search_term(artist)
        clean_t = self.clean_search_term(title)

        # Build prioritized search URLs
        search_urls = []
        clean_catno = catalog_number.strip() if catalog_number else ""

        # 1. CatNo + Vinyl Search (Precise matching)
        if clean_catno:
            search_urls.append(f"https://api.discogs.com/database/search?catno={urllib.parse.quote(clean_catno)}&type=release&format=vinyl")

        # 2. Artist + Title + Japan Region Search
        if clean_a and clean_t:
            search_urls.append(f"https://api.discogs.com/database/search?q={urllib.parse.quote(f'{clean_a} {clean_t}')}&type=release&format=vinyl&country=Japan")

        # 3. Artist + Title General Vinyl Search
        if clean_a and clean_t:
            search_urls.append(f"https://api.discogs.com/database/search?q={urllib.parse.quote(f'{clean_a} {clean_t}')}&type=release&format=vinyl")

        seen_urls = set()

        for search_url in search_urls:
            try:
                resp = requests.get(search_url, headers=self.headers, timeout=5)
                if resp.status_code == 200:
                    results = resp.json().get("results", [])
                    for r in results[:10]:
                        rel_id = r.get("id")
                        rel_country = r.get("country", "")
                        rel_catno = r.get("catno", "")
                        cover_image = r.get("cover_image") or r.get("thumb")

                        # Directly extract front cover image from search result if available
                        if cover_image and "spacer.gif" not in cover_image and cover_image not in seen_urls:
                            seen_urls.add(cover_image)
                            badge_country = "🇯🇵 Japan" if rel_country.lower() == "japan" else (rel_country or "Vinyl")
                            badge_catno = f" [{rel_catno}]" if rel_catno else ""

                            assets.append({
                                "type": f"{badge_country} Front Cover",
                                "url": cover_image,
                                "thumbnail": cover_image,
                                "isPrimary": rel_country.lower() == "japan",
                                "country": rel_country,
                                "catalogNumber": rel_catno,
                                "comment": f"{badge_country} Pressing{badge_catno}"
                            })

                        # Deep release details lookup if needed
                        if len(assets) < 10 and rel_id:
                            rel_url = f"https://api.discogs.com/releases/{rel_id}"
                            rel_resp = requests.get(rel_url, headers=self.headers, timeout=5)
                            if rel_resp.status_code == 200:
                                rel_data = rel_resp.json()
                                if self.is_strict_discogs_match(artist, title, rel_data):
                                    imgs = rel_data.get("images", [])
                                    for idx, img in enumerate(imgs):
                                        uri = img.get("uri") or img.get("resource_url")
                                        if uri and uri not in seen_urls:
                                            seen_urls.add(uri)
                                            is_prim = img.get("type") == "primary"
                                            badge_country = "🇯🇵 Japan" if rel_country.lower() == "japan" else (rel_country or "Vinyl")
                                            badge_catno = f" [{rel_catno}]" if rel_catno else ""

                                            assets.append({
                                                "type": f"{badge_country} {'Front Cover' if is_prim else 'Sleeve Asset'}",
                                                "url": uri,
                                                "thumbnail": uri,
                                                "isPrimary": is_prim and rel_country.lower() == "japan",
                                                "country": rel_country,
                                                "catalogNumber": rel_catno,
                                                "comment": f"{badge_country}{badge_catno} Release #{rel_id}"
                                            })
                                            if len(assets) >= 10:
                                                break

                        if len(assets) >= 10:
                            break
            except Exception as e:
                logger.warning(f"Discogs API search error: {e}")

            if len(assets) >= 10:
                break

        # Fallback if no online assets were found
        if not assets and cover_url:
            assets.append({
                "type": "Original Jacket Cover Art",
                "url": cover_url,
                "thumbnail": cover_url,
                "isPrimary": True,
                "comment": "Current Album Cover"
            })

        return assets[:10]

discogs_service = DiscogsService()


if __name__ == "__main__":
    print("\n--- Testing Strict Discogs Vinyl Assets for Isaac Stern ---")
    assets1 = discogs_service.fetch_all_release_assets("Isaac Stern (伊萨克·斯特恩)", "Sibelius & Bruch: Violin Concertos", "https://storage.googleapis.com/universal-trail-492014-n5-vinyl-vault-data/covers/shopping_cover_3.jpg")
    for a in assets1:
        print(f" - [{a['type']}]: {a['url']}")
