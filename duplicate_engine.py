import re
from typing import Dict, Any, List, Set

CONDUCTOR_SOLOIST_STOP_WORDS = {
    "orchestra", "philharmonic", "symphony", "quartet", "trio", "ensemble", "band", "sir", "chorus", "choir",
    "chamber", "national", "state", "radio", "philharmonia", "vienna", "berlin", "london", "chicago", "new", "york",
    "boston", "cleveland", "philadelphia", "concertgebouw", "bbc", "dresden", "symphonie", "orchester", "orchestre",
    "piano", "violin", "violoncello", "cello", "soprano", "tenor", "baritone", "bass", "conductor", "directed"
}

FIRST_NAME_GIVEN_NAME_STOP_WORDS = {
    "wilhelm", "john", "paul", "david", "karl", "georg", "george", "herbert", "eugen", "eugene", "claudio",
    "leonard", "bruno", "arturo", "neeme", "bernard", "daniel", "charles", "otto", "joseph", "franz", "jan",
    "jean", "louis", "pierre", "richard", "robert", "felix", "antonio", "giuseppe", "giacomo", "sir", "wolfgang",
    "ludwig", "johann", "pyotr", "antonin", "antonio", "sergei", "dmitri", "igor", "claude", "maurice", "fritz"
}

WORK_FORM_KEYWORDS = {
    "symphony", "symphonies", "sonata", "sonatas", "concerto", "concertos", "quartet", "quartets",
    "quintet", "trio", "mass", "requiem", "opera", "suite", "suites", "serenade", "nocturne", "nocturnes",
    "waltz", "waltzes", "ballade", "prelude", "preludes", "fugue", "variation", "variations", "etude", "etudes", "overture"
}

def normalize_string(s: str) -> str:
    if not s:
        return ""
    return re.sub(r'[^a-z0-9]', '', s.lower()).strip()

def get_keywords(s: str) -> set:
    if not s:
        return set()
    words = re.findall(r'[a-zA-Z0-9\u00C0-\u024F]+', s.lower())
    stop_words = {"the", "a", "an", "and", "or", "of", "in", "on", "for", "with", "by", "no", "op", "vol"}
    return {w for w in words if len(w) > 1 and w not in stop_words}

def get_performer_surnames(s: str) -> set:
    if not s:
        return set()
    words = re.findall(r'[a-zA-Z0-9\u00C0-\u024F]+', s.lower())
    stop_words = {"the", "a", "an", "and", "or", "of", "in", "on", "for", "with", "by", "no", "op", "vol", "major", "minor", "symphony", "concerto", "sonata"} | CONDUCTOR_SOLOIST_STOP_WORDS | FIRST_NAME_GIVEN_NAME_STOP_WORDS
    return {w for w in words if len(w) > 1 and w not in stop_words}

def get_work_forms(s: str) -> set:
    if not s:
        return set()
    words = set(re.findall(r'[a-zA-Z0-9\u00C0-\u024F]+', s.lower()))
    return words.intersection(WORK_FORM_KEYWORDS)

def get_work_numbers(s: str) -> set:
    if not s:
        return set()
    return set(re.findall(r'\b\d+\b', s))

class DuplicateEngine:
    @staticmethod
    def check_duplicate(query: Dict[str, Any], collection: List[Dict[str, Any]], wishlist: List[Dict[str, Any]]) -> Dict[str, Any]:
        q_artist = normalize_string(query.get("artist", ""))
        q_title = normalize_string(query.get("albumTitle", "") or query.get("title", ""))
        q_cat_no = normalize_string(query.get("catalogNumber", "") or query.get("catno", ""))

        # 1. CATALOG NUMBER MATCH (Highest Precision):
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

        q_art_raw = query.get("artist", "")
        q_title_raw = query.get("albumTitle", "") or query.get("title", "")

        q_art_kw = get_keywords(q_art_raw)
        q_title_kw = get_keywords(q_title_raw)
        q_surnames = get_performer_surnames(q_art_raw)
        q_forms = get_work_forms(q_title_raw)
        q_numbers = get_work_numbers(q_title_raw)

        # 2. STRING INCLUSION / KEYWORD OVERLAP MATCH IN COLLECTION:
        for record in collection:
            r_art_raw = record.get("artist", "")
            r_title_raw = record.get("title", "")

            r_artist = normalize_string(r_art_raw)
            r_title = normalize_string(r_title_raw)

            r_art_kw = get_keywords(r_art_raw)
            r_title_kw = get_keywords(r_title_raw)
            r_surnames = get_performer_surnames(r_art_raw)
            r_forms = get_work_forms(r_title_raw)
            r_numbers = get_work_numbers(r_title_raw)

            # Check performer surname conflicts (e.g. Kempff vs Furtwängler)
            if q_surnames and r_surnames and not q_surnames.intersection(r_surnames):
                continue

            # Check musical work form conflicts (e.g. Sonatas vs Symphony)
            if q_forms and r_forms and not q_forms.intersection(r_forms):
                continue

            # Check work number conflicts (e.g. No. 1 vs No. 5)
            if q_numbers and r_numbers and not q_numbers.intersection(r_numbers):
                continue

            # Direct string inclusion match
            artist_match = q_artist and (q_artist in r_artist or r_artist in q_artist)
            title_match = q_title and (q_title in r_title or r_title in q_title)

            art_overlap = len(q_art_kw.intersection(r_art_kw)) >= 1 if (q_art_kw and r_art_kw) else False
            title_overlap = len(q_title_kw.intersection(r_title_kw)) >= 1 if (q_title_kw and r_title_kw) else False

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
            w_art_raw = item.get("artist", "")
            w_title_raw = item.get("title", "")
            w_artist = normalize_string(w_art_raw)
            w_title = normalize_string(w_title_raw)

            w_art_kw = get_keywords(w_art_raw)
            w_title_kw = get_keywords(w_title_raw)
            w_surnames = get_performer_surnames(w_art_raw)
            w_forms = get_work_forms(w_title_raw)
            w_numbers = get_work_numbers(w_title_raw)

            if q_surnames and w_surnames and not q_surnames.intersection(w_surnames):
                continue

            if q_forms and w_forms and not q_forms.intersection(w_forms):
                continue

            if q_numbers and w_numbers and not q_numbers.intersection(w_numbers):
                continue

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
            r_surnames = get_performer_surnames(r.get("artist", ""))
            if q_surnames and r_surnames and len(q_surnames.intersection(r_surnames)) >= 1:
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


