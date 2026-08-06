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

COMMON_CLASSICAL_COMPOSERS = {
    "bach", "beethoven", "mozart", "brahms", "tchaikovsky", "schubert", "chopin", "liszt",
    "haydn", "vivaldi", "handel", "mahler", "dvorak", "dvořák", "rachmaninoff", "rachmaninov",
    "debussy", "ravel", "stravinsky", "saintsaens", "saint-saëns", "saint-saens", "saëns", "saens",
    "mendelssohn", "schumann", "berlioz", "strauss", "wagner", "verdi", "puccini", "sibelius",
    "bartok", "bartók", "prokofiev", "shostakovich", "elgar", "grieg", "bruckner", "fauré", "faure",
    "teleman", "telemann", "corelli", "scarlatti", "purcell", "monteverdi", "rameau", "couperin", "paganini"
}

INSTRUMENT_KEYWORDS = {
    "piano", "violin", "cello", "violoncello", "flute", "clarinet", "oboe", "organ",
    "harpsichord", "guitar", "trumpet", "horn", "voice", "soprano", "tenor", "baritone"
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

def get_composers(s: str) -> set:
    if not s:
        return set()
    words = re.findall(r'[a-zA-Z0-9\u00C0-\u024F\-]+', s.lower())
    found = set()
    for w in words:
        w_norm = w.replace('-', '')
        for comp in COMMON_CLASSICAL_COMPOSERS:
            comp_norm = comp.replace('-', '')
            if w_norm == comp_norm:
                found.add(comp_norm)
    return found

def get_instruments(s: str) -> set:
    if not s:
        return set()
    words = set(re.findall(r'[a-zA-Z0-9\u00C0-\u024F]+', s.lower()))
    return words.intersection(INSTRUMENT_KEYWORDS)

class DuplicateEngine:
    @staticmethod
    def check_duplicate(query: Dict[str, Any], collection: List[Dict[str, Any]], wishlist: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Grounded AI Duplicate Engine:
        Relies on Gemini Vision's semantic collection reasoning (isAlreadyInCrate, crateMatchId, crateMatchReason)
        and exact Catalog Number verification, eliminating brittle rule-based string overlap false positives.
        """
        q_cat_no = normalize_string(query.get("catalogNumber", "") or query.get("catno", ""))

        # 1. CATALOG NUMBER MATCH (Exact Physical Pressing Match):
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

        # 2. GEMINI VISION SEMANTIC CRATE GROUNDING (100% AI Evaluation):
        if "isAlreadyInCrate" in query:
            if query.get("isAlreadyInCrate") is True:
                match_id = query.get("crateMatchId")
                match_rec = next((r for r in collection if r.get("id") == match_id), None) if match_id else None

                # Fallback: search collection by title/artist similarity if match_id was omitted
                if not match_rec:
                    q_art = (query.get("artist") or "").lower()
                    q_tit = (query.get("albumTitle") or query.get("title") or "").lower()
                    for r in collection:
                        r_tit = (r.get("title") or "").lower()
                        r_art = (r.get("artist") or "").lower()
                        if (q_tit and q_tit in r_tit) or (q_art and q_art in r_art):
                            match_rec = r
                            break

                pressings = match_rec.get("pressings", []) if match_rec else []
                primary_p = pressings[0] if pressings else {}
                reason = query.get("crateMatchReason") or (f"ALREADY IN YOUR COLLECTION! Gemini identified '{match_rec.get('title')}' in your Crate." if match_rec else "ALREADY IN YOUR COLLECTION!")
                
                return {
                    "status": "EXACT_MATCH",
                    "matchingRecord": match_rec,
                    "matchingPressing": primary_p,
                    "message": reason
                }
            else:
                reason = query.get("crateMatchReason") or "NOT IN COLLECTION. Safe to add!"
                return {
                    "status": "NOT_OWNED",
                    "message": reason
                }

        # 3. WISHLIST CHECK (If needed):
        q_artist = normalize_string(query.get("artist", ""))
        q_title = normalize_string(query.get("albumTitle", "") or query.get("title", ""))
        if q_artist and q_title:
            for item in wishlist:
                w_artist = normalize_string(item.get("artist", ""))
                w_title = normalize_string(item.get("title", ""))
                if (q_artist in w_artist or w_artist in q_artist) and (q_title in w_title or w_title in q_title):
                    return {
                        "status": "WISHLIST_MATCH",
                        "message": f"ON YOUR WISHLIST! Priority: {item.get('priority', 'MEDIUM')}. Notes: {item.get('notes', 'No notes')}"
                    }

        # Default NOT OWNED
        return {
            "status": "NOT_OWNED",
            "message": "NOT IN COLLECTION. Safe to add!"
        }



