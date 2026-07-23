import re
from typing import Dict, Any, List

def normalize_string(s: str) -> str:
    if not s:
        return ""
    return re.sub(r'[^a-z0-9]', '', s.lower()).strip()

class DuplicateEngine:
    @staticmethod
    def check_duplicate(query: Dict[str, str], collection: List[Dict[str, Any]], wishlist: List[Dict[str, Any]]) -> Dict[str, Any]:
        q_artist = normalize_string(query.get("artist", ""))
        q_title = normalize_string(query.get("albumTitle", "") or query.get("title", ""))
        q_cat_no = normalize_string(query.get("catalogNumber", ""))

        if not q_artist and not q_title:
            return {
                "status": "NOT_OWNED",
                "message": "Insufficient info to check duplicate."
            }

        # 1. Exact Match / Pressing Match in Collection
        for record in collection:
            r_artist = normalize_string(record.get("artist", ""))
            r_title = normalize_string(record.get("title", ""))

            artist_match = q_artist and (q_artist in r_artist or r_artist in q_artist)
            title_match = q_title and (q_title in r_title or r_title in q_title)

            if artist_match and title_match:
                # Check pressings
                pressings = record.get("pressings", [])
                if q_cat_no:
                    for p in pressings:
                        p_cat = normalize_string(p.get("catalogNumber", ""))
                        if p_cat and p_cat == q_cat_no:
                            return {
                                "status": "EXACT_MATCH",
                                "matchingRecord": record,
                                "matchingPressing": p,
                                "message": f"ALREADY IN YOUR COLLECTION! You own this exact pressing ({p.get('formatDetails', 'Standard')})."
                            }

                primary_p = pressings[0] if pressings else {}
                return {
                    "status": "EXACT_MATCH",
                    "matchingRecord": record,
                    "matchingPressing": primary_p,
                    "message": f"ALREADY IN YOUR COLLECTION! You own 1 copy of '{record['title']}' by {record['artist']}."
                }

        # 2. Wishlist Match
        for item in wishlist:
            w_artist = normalize_string(item.get("artist", ""))
            w_title = normalize_string(item.get("title", ""))

            if q_artist and q_title and (q_artist in w_artist or w_artist in q_artist) and (q_title in w_title or w_title in q_title):
                return {
                    "status": "WISHLIST_MATCH",
                    "message": f"ON YOUR WISHLIST! Priority: {item.get('priority', 'MEDIUM')}. Notes: {item.get('notes', 'No notes')}"
                }

        # 3. Similar Artist Match
        artist_records = []
        for r in collection:
            r_artist = normalize_string(r.get("artist", ""))
            if q_artist and (q_artist in r_artist or r_artist in q_artist):
                artist_records.append(r)

        if artist_records:
            titles_str = ", ".join([f"'{r['title']}'" for r in artist_records])
            return {
                "status": "SIMILAR_ALBUM",
                "message": f"NOT OWNED, but you own {len(artist_records)} other album(s) by {query.get('artist')}: {titles_str}."
            }

        # 4. Not Owned
        return {
            "status": "NOT_OWNED",
            "message": f"NOT IN COLLECTION. Safe to buy!"
        }
