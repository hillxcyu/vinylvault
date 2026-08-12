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
        if not text:
            return ""
        text_no_cn = re.sub(r'[\u4e00-\u9fff]+', '', text)
        # Escape / replace ~ character with space so Discogs search parser doesn't break on Lucene operator ~
        text_no_tilde = re.sub(r'[~]', ' ', text_no_cn)
        cleaned = re.sub(r'[^\w\s]', ' ', text_no_tilde)
        return ' '.join(cleaned.split())

    def extract_artist_words(self, artist_str: str) -> List[str]:
        cleaned = self.clean_search_term(artist_str).lower()
        return [w for w in cleaned.split() if len(w) > 2 and w not in ["orchestra", "philharmonic", "symphony", "quartet", "trio", "ensemble", "band", "sir"]]

    def is_strict_discogs_match(self, req_artist: str, req_title: str, rel_data: dict, is_catno_match: bool = False) -> bool:
        if is_catno_match:
            return True

        clean_req_a = self.clean_search_term(req_artist).lower()
        clean_req_t = self.clean_search_term(req_title).lower()

        artist_words = self.extract_artist_words(req_artist)
        if not artist_words:
            return True

        d_title = rel_data.get("title", "").lower()
        d_artists = " ".join([a.get("name", "").lower() for a in rel_data.get("artists", [])])

        artist_in_credit = any(w in d_artists or w[:4] in d_artists for w in artist_words)
        artist_in_title = any(w in d_title or w[:4] in d_title for w in artist_words)

        if not (artist_in_credit or artist_in_title):
            return False

        return True

    def fetch_release_info(
        self,
        artist: str,
        title: str,
        cover_url: Optional[str] = None,
        catalog_number: Optional[str] = None,
        country: Optional[str] = "Japan"
    ) -> Dict[str, Any]:
        assets = self.fetch_all_release_assets(
            artist,
            title,
            cover_url=cover_url,
            catalog_number=catalog_number,
            country=country
        )

        chosen_url = cover_url
        chosen_year = None
        chosen_catno = catalog_number
        chosen_country = country

        if assets:
            best_asset = None
            if country:
                target_c = country.strip().lower()
                for a in assets:
                    url = a.get("url", "")
                    a_country = (a.get("country") or "").lower()
                    if url and "shopping_cover_2.jpg" not in url and a_country == target_c:
                        best_asset = a
                        break

            if not best_asset:
                for a in assets:
                    url = a.get("url", "")
                    if url and "shopping_cover_2.jpg" not in url and a.get("type") != "📸 Original Jacket":
                        best_asset = a
                        break

            if best_asset:
                if best_asset.get("url"):
                    chosen_url = best_asset["url"]
                if best_asset.get("year"):
                    chosen_year = best_asset["year"]
                if best_asset.get("catalogNumber"):
                    chosen_catno = best_asset["catalogNumber"]
                if best_asset.get("country"):
                    chosen_country = best_asset["country"]

        return {
            "coverUrl": chosen_url,
            "releaseYear": chosen_year,
            "catalogNumber": chosen_catno,
            "country": chosen_country,
            "assets": assets
        }

    def fetch_official_cover(
        self,
        artist: str,
        title: str,
        cover_url: Optional[str] = None,
        catalog_number: Optional[str] = None,
        country: Optional[str] = "Japan"
    ) -> Optional[str]:
        info = self.fetch_release_info(artist, title, cover_url=cover_url, catalog_number=catalog_number, country=country)
        return info.get("coverUrl") or cover_url

    def fetch_all_release_assets(
        self,
        artist: str,
        title: str,
        cover_url: Optional[str] = None,
        catalog_number: Optional[str] = None,
        country: Optional[str] = "Japan"
    ) -> List[Dict[str, Any]]:
        assets = []
        seen_urls = set()
        target_country = (country or "Japan").strip()

        # Always include original jacket cover art as Asset #1 if available
        if cover_url and cover_url not in seen_urls and "shopping_cover_2.jpg" not in cover_url:
            seen_urls.add(cover_url)
            assets.append({
                "type": "📸 Original Jacket",
                "url": cover_url,
                "thumbnail": cover_url,
                "isPrimary": True,
                "country": target_country or "Original",
                "comment": "Original Scanned / Uploaded Album Cover"
            })

        clean_a = self.clean_search_term(artist)
        clean_t = self.clean_search_term(title)
        clean_catno = re.sub(r'[~]', ' ', catalog_number).strip() if catalog_number else ""

        search_queries = []
        # Target country queries prioritized first when target_country is set
        if clean_catno and target_country:
            cat_parts = re.findall(r'[A-Za-z0-9\-]+', clean_catno)
            pure_cat = " ".join(cat_parts)
            search_queries.append({"url": f"https://api.discogs.com/database/search?catno={urllib.parse.quote(pure_cat)}&country={urllib.parse.quote(target_country)}&type=release", "is_catno": True})
            search_queries.append({"url": f"https://api.discogs.com/database/search?q={urllib.parse.quote(clean_catno + ' ' + target_country)}&type=release", "is_catno": True})

        if clean_a and clean_t and target_country:
            search_queries.append({"url": f"https://api.discogs.com/database/search?q={urllib.parse.quote(f'{clean_a} {clean_t}')}&type=release&format=vinyl&country={urllib.parse.quote(target_country)}", "is_catno": False})

        # Fallback queries across all countries
        if clean_catno:
            cat_parts = re.findall(r'[A-Za-z0-9\-]+', clean_catno)
            pure_cat = " ".join(cat_parts)
            search_queries.append({"url": f"https://api.discogs.com/database/search?catno={urllib.parse.quote(pure_cat)}&type=release", "is_catno": True})
            search_queries.append({"url": f"https://api.discogs.com/database/search?q={urllib.parse.quote(clean_catno)}&type=release", "is_catno": True})

        if clean_a and clean_t:
            search_queries.append({"url": f"https://api.discogs.com/database/search?q={urllib.parse.quote(f'{clean_a} {clean_t}')}&type=release&format=vinyl", "is_catno": False})

        for q_obj in search_queries:
            search_url = q_obj["url"]
            is_cat_q = q_obj["is_catno"]
            try:
                resp = requests.get(search_url, headers=self.headers, timeout=6)
                if resp.status_code == 429:
                    logger.warning("Discogs API rate limit (HTTP 429) hit; breaking early.")
                    break
                if resp.status_code == 200:


                    results = resp.json().get("results", [])
                    for r in results[:10]:
                        rel_id = r.get("id")
                        rel_country = r.get("country", "")
                        rel_catno = r.get("catno", "")
                        rel_year = r.get("year")
                        try:
                            rel_year = int(rel_year) if rel_year else None
                        except Exception:
                            rel_year = None

                        cover_image = r.get("cover_image") or r.get("thumb")

                        if cover_image and "spacer.gif" not in cover_image and cover_image not in seen_urls:
                            seen_urls.add(cover_image)
                            badge_country = f"🇯🇵 {rel_country}" if rel_country.lower() == "japan" else (rel_country or "Vinyl")
                            badge_catno = f" [{rel_catno}]" if rel_catno else ""

                            assets.append({
                                "type": f"{badge_country} Front Cover",
                                "url": cover_image,
                                "thumbnail": cover_image,
                                "isPrimary": rel_country.lower() == target_country.lower() or is_cat_q,
                                "country": rel_country,
                                "catalogNumber": rel_catno,
                                "year": rel_year,
                                "comment": f"{badge_country} Pressing{badge_catno}"
                            })

                        if (len(assets) < 12 or not cover_image) and rel_id:
                            rel_url = f"https://api.discogs.com/releases/{rel_id}"
                            rel_resp = requests.get(rel_url, headers=self.headers, timeout=6)
                            if rel_resp.status_code == 200:
                                rel_data = rel_resp.json()
                                d_year = rel_data.get("year") or rel_year
                                try:
                                    d_year = int(d_year) if d_year else None
                                except Exception:
                                    d_year = None

                                if self.is_strict_discogs_match(artist, title, rel_data, is_catno_match=is_cat_q):
                                    imgs = rel_data.get("images", [])
                                    for idx, img in enumerate(imgs):
                                        uri = img.get("uri") or img.get("resource_url")
                                        if uri and uri not in seen_urls:
                                            seen_urls.add(uri)
                                            is_prim = img.get("type") == "primary"
                                            badge_country = f"🇯🇵 {rel_country}" if rel_country.lower() == "japan" else (rel_country or "Vinyl")
                                            badge_catno = f" [{rel_catno}]" if rel_catno else ""

                                            assets.append({
                                                "type": f"{badge_country} {'Front Cover' if is_prim else 'Sleeve Asset'}",
                                                "url": uri,
                                                "thumbnail": uri,
                                                "isPrimary": is_prim or rel_country.lower() == target_country.lower(),
                                                "country": rel_country,
                                                "catalogNumber": rel_catno,
                                                "year": d_year,
                                                "comment": f"{badge_country} Release{badge_catno}"
                                            })
                                            if len(assets) >= 10:
                                                break

                        if len(assets) >= 10:
                            break
            except Exception as e:
                logger.warning(f"Discogs API search error: {e}")

            if len(assets) >= 10:
                break

        if not assets and cover_url:
            assets.append({
                "type": "Original Jacket Cover Art",
                "url": cover_url,
                "thumbnail": cover_url,
                "isPrimary": True,
                "comment": "Current Album Cover"
            })

        # Priority sort assets so target country (e.g. Japan) and matching catno appear first
        def asset_priority(asset):
            if asset.get("type", "").startswith("📸 Original"):
                return 0
            cntry = (asset.get("country") or "").lower()
            asset_cat = (asset.get("catalogNumber") or "").lower()
            target_cat = (clean_catno or "").lower()

            matches_country = target_country.lower() in cntry or cntry in target_country.lower()
            matches_catno = target_cat and (target_cat in asset_cat or asset_cat in target_cat)

            if matches_country and matches_catno:
                return 1
            if matches_country:
                return 2
            if matches_catno:
                return 3
            return 4

        assets.sort(key=asset_priority)
        return assets[:12]


discogs_service = DiscogsService()



if __name__ == "__main__":
    print("\n--- Testing Strict Discogs Vinyl Assets for Isaac Stern ---")
    assets1 = discogs_service.fetch_all_release_assets("Isaac Stern (伊萨克·斯特恩)", "Sibelius & Bruch: Violin Concertos", "https://storage.googleapis.com/universal-trail-492014-n5-vinyl-vault-data/covers/shopping_cover_3.jpg")
    for a in assets1:
        print(f" - [{a['type']}]: {a['url']}")
