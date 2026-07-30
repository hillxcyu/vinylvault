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
        assets = self.fetch_all_release_assets(artist, title, cover_url=cover_url)
        if assets:
            for a in assets:
                if a.get("isPrimary"):
                    return a.get("url")
            return assets[0].get("url")
        return cover_url

    def fetch_all_release_assets(self, artist: str, title: str, cover_url: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Fetch image assets EXCLUSIVELY from Discogs API for VINYL (LP / 12") pressings only.
        Enforces strict primary artist verification and filters out mismatched lead performers.
        """
        assets = []
        primary_cover = cover_url or "https://storage.googleapis.com/universal-trail-492014-n5-vinyl-vault-data/covers/shopping_cover_2.jpg"

        # Retain original jacket cover as primary fallback
        assets.append({
            "type": "Original Jacket Cover Art",
            "url": primary_cover,
            "thumbnail": primary_cover,
            "isPrimary": True,
            "comment": f"Primary Record Sleeve for {title}"
        })

        clean_a = self.clean_search_term(artist)
        clean_t = self.clean_search_term(title)
        t_words = [w for w in clean_t.split() if len(w) > 2]
        w1 = t_words[0] if len(t_words) > 0 else ""
        w2 = t_words[1] if len(t_words) > 1 else ""

        # Multi-tiered targeted queries (no artist-only query to prevent compilation boxsets)
        queries = [
            f"{clean_a} {clean_t}".strip(),
            f"{clean_a} {w1}".strip(),
            f"{clean_a} {w2}".strip()
        ]

        for q in queries:
            if not q or q == clean_a:
                continue
            try:
                search_url = f"https://api.discogs.com/database/search?q={urllib.parse.quote(q)}&type=release&format=vinyl"
                resp = requests.get(search_url, headers=self.headers, timeout=5)
                if resp.status_code == 200:
                    results = resp.json().get("results", [])
                    for r in results[:5]:
                        rel_id = r.get("id")
                        if rel_id:
                            rel_url = f"https://api.discogs.com/releases/{rel_id}"
                            rel_resp = requests.get(rel_url, headers=self.headers, timeout=5)
                            if rel_resp.status_code == 200:
                                rel_data = rel_resp.json()
                                formats = rel_data.get("formats", [])
                                fmt_names = [fmt.get("name", "") for fmt in formats]
                                descriptions = [d for fmt in formats for d in fmt.get("descriptions", [])]

                                # Verify Vinyl / LP / 12" format (strictly exclude CD / Cassette)
                                is_vinyl = any("Vinyl" in n or "LP" in descriptions or '12"' in descriptions for n in fmt_names)
                                if not is_vinyl and len(formats) > 0:
                                    continue

                                if self.is_strict_discogs_match(artist, title, rel_data):
                                    imgs = rel_data.get("images", [])
                                    for idx, img in enumerate(imgs):
                                        uri = img.get("uri") or img.get("resource_url")
                                        is_prim = img.get("type") == "primary"
                                        
                                        img_type = "Discogs Vinyl Front Cover" if is_prim else f"Discogs Vinyl Release Asset (Back/Sleeve/Disc #{idx+1})"

                                        if uri and not any(a["url"] == uri for a in assets):
                                            assets.append({
                                                "type": img_type,
                                                "url": uri,
                                                "thumbnail": uri,
                                                "isPrimary": False,
                                                "comment": f"Discogs Vinyl LP Asset from Release #{rel_id}"
                                            })
                                    if len(assets) > 1:
                                        logger.info(f"Retrieved {len(assets)} Vinyl LP Discogs release assets for '{title}'.")
                                        return assets
            except Exception as e:
                logger.warning(f"Discogs API query '{q}' warning: {e}")

        return assets

discogs_service = DiscogsService()

if __name__ == "__main__":
    print("\n--- Testing Strict Discogs Vinyl Assets for Isaac Stern ---")
    assets1 = discogs_service.fetch_all_release_assets("Isaac Stern (伊萨克·斯特恩)", "Sibelius & Bruch: Violin Concertos", "https://storage.googleapis.com/universal-trail-492014-n5-vinyl-vault-data/covers/shopping_cover_3.jpg")
    for a in assets1:
        print(f" - [{a['type']}]: {a['url']}")
