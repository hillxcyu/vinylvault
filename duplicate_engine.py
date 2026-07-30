import re
from typing import Dict, Any, List

def normalize_string(s: str) -> str:
    if not s:
        return ""
    return re.sub(r'[^a-z0-9]', '', s.lower()).strip()

def get_keywords(s: str) -> set:
    if not s:
        return set()
    words = re.findall(r'[a-zA-Z0-9]+', s.lower())
    stop_words = {"the", "a", "an", "and", "or", "of", "in", "on", "for", "with", "by", "no", "op", "vol"}
    return {w for w in words if len(w) > 1 and w not in stop_words}

class DuplicateEngine:
    @staticmethod
    def check_duplicate(query: Dict[str, Any], collection: List[Dict[str, Any]], wishlist: List[Dict[str, Any]]) -> Dict[str, Any]:
        q_artist = normalize_string(query.get("artist", ""))
        q_title = normalize_string(query.get("albumTitle", "") or query.get("title", ""))
        q_cat_no = normalize_string(query.get("catalogNumber", "") or query.get("catno", ""))

        # 1. CATALOG NUMBER MATCH (Highest Precision):
        # If catalog numbers match exactly (e.g. SLA 6187 == SLA 6187), it is 100% the same record!
        if q_cat_no and len(q_cat_no) >= 3:
            for record in collection:
                r_cat = normalize_string(record.get("catalogNumber", "") or record.get("catno", ""))
                if r_cat and r_cat == q_cat_no:
                    pressings = record.get("pressings", [])
                    primary_p = pressings[0] if pressings else {}
                    return {
                        "status": "EXACT_MATCH",
                        "matchingRecord": record,
                        "matchingPressing": primary_p,
                        "message": f"ALREADY IN YOUR COLLECTION! Catalog Number '{record.get('catalogNumber', q_cat_no)}' matches '{record.get('title', '')}'."
                    }
                for p in record.get("pressings", []):
                    p_cat = normalize_string(p.get("catalogNumber", ""))
                    if p_cat and p_cat == q_cat_no:
                        return {
                            "status": "EXACT_MATCH",
                            "matchingRecord": record,
                            "matchingPressing": p,
                            "message": f"ALREADY IN YOUR COLLECTION! Catalog Number '{p_cat}' matches '{record.get('title', '')}'."
                        }

        if not q_artist and not q_title:
            return {
                "status": "NOT_OWNED",
                "message": "Insufficient info to check duplicate."
            }

        q_art_kw = get_keywords(query.get("artist", ""))
        q_title_kw = get_keywords(query.get("albumTitle", "") or query.get("title", ""))

        # 2. STRING INCLUSION / KEYWORD OVERLAP MATCH IN COLLECTION:
        for record in collection:
            r_artist = normalize_string(record.get("artist", ""))
            r_title = normalize_string(record.get("title", ""))

            r_art_kw = get_keywords(record.get("artist", ""))
            r_title_kw = get_keywords(record.get("title", ""))

            # Direct string inclusion match
            artist_match = q_artist and (q_artist in r_artist or r_artist in q_artist)
            title_match = q_title and (q_title in r_title or r_title in q_title)

            # Keyword overlap match (handles different ordering of conductors/composers/soloists)
            art_overlap = len(q_art_kw.intersection(r_art_kw)) >= 1 if (q_art_kw and r_art_kw) else False
            title_overlap = len(q_title_kw.intersection(r_title_kw)) >= 1 if (q_title_kw and r_title_kw) else False

            # Combination of artist + title keyword overlap
            if (artist_match or art_overlap) and (title_match or title_overlap):
                combined_q = q_art_kw.union(q_title_kw)
                combined_r = r_art_kw.union(r_title_kw)
                shared = combined_q.intersection(combined_r)

                if len(shared) >= 2 or (len(shared) >= 1 and (artist_match or title_match)):
                    pressings = record.get("pressings", [])
                    primary_p = pressings[0] if pressings else {}
                    return {
                        "status": "EXACT_MATCH",
                        "matchingRecord": record,
                        "matchingPressing": primary_p,
                        "message": f"ALREADY IN YOUR COLLECTION! You own '{record.get('title', '')}' by {record.get('artist', '')}."
                    }

        # 3. WISHLIST MATCH:
        for item in wishlist:
            w_artist = normalize_string(item.get("artist", ""))
            w_title = normalize_string(item.get("title", ""))
            w_art_kw = get_keywords(item.get("artist", ""))
            w_title_kw = get_keywords(item.get("title", ""))

            w_art_match = (q_artist in w_artist or w_artist in q_artist) or (len(q_art_kw.intersection(w_art_kw)) >= 1 if q_art_kw and w_art_kw else False)
            w_title_match = (q_title in w_title or w_title in q_title) or (len(q_title_kw.intersection(w_title_kw)) >= 1 if q_title_kw and w_title_kw else False)

            if w_art_match and w_title_match:
                return {
                    "status": "WISHLIST_MATCH",
                    "message": f"ON YOUR WISHLIST! Priority: {item.get('priority', 'MEDIUM')}. Notes: {item.get('notes', 'No notes')}"
                }

        # 4. SIMILAR ARTIST MATCH:
        artist_records = []
        for r in collection:
            r_art_kw = get_keywords(r.get("artist", ""))
            if q_art_kw and len(q_art_kw.intersection(r_art_kw)) >= 1:
                artist_records.append(r)

        if artist_records:
            titles_str = ", ".join([f"'{r.get('title', '')}'" for r in artist_records[:3]])
            return {
                "status": "SIMILAR_ALBUM",
                "message": f"NOT OWNED, but you own {len(artist_records)} other album(s) by {query.get('artist')}: {titles_str}."
            }

        # 5. NOT OWNED
        return {
            "status": "NOT_OWNED",
            "message": f"NOT IN COLLECTION. Safe to buy!"
        }
