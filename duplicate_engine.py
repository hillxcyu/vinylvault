import logging
from typing import Dict, Any, List

logger = logging.getLogger("vinyl_vault")

class DuplicateEngine:
    @staticmethod
    def check_duplicate(query: Dict[str, Any], collection: List[Dict[str, Any]], wishlist: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Pure Gemini Vision Crate Duplicate Engine:
        Evaluates Gemini Vision's grounded semantic crate check (isAlreadyInCrate, crateMatchId, crateMatchReason)
        and exact catalog numbers, raising an error if Gemini Vision evaluation fails.
        """
        if not isinstance(query, dict):
            raise ValueError("Invalid analysis query object")

        collection = collection or []
        wishlist = wishlist or []

        # 1. Exact Catalog Number Match (Physical Pressing Match)
        q_cat = (query.get("catalogNumber") or query.get("catno") or "").strip().lower()
        q_cat_clean = "".join(c for c in q_cat if c.isalnum())

        if q_cat_clean and len(q_cat_clean) >= 3:
            for record in collection:
                r_cat = (record.get("catalogNumber") or record.get("catno") or "").strip().lower()
                r_cat_clean = "".join(c for c in r_cat if c.isalnum())

                if r_cat_clean and r_cat_clean == q_cat_clean:
                    pressings = record.get("pressings", [])
                    primary_p = pressings[0] if pressings else {}
                    return {
                        "status": "EXACT_MATCH",
                        "matchingRecord": record,
                        "matchingPressing": primary_p,
                        "message": f"ALREADY IN YOUR COLLECTION! Catalog Number '{record.get('catalogNumber', q_cat)}' matches '{record.get('title', '')}'."
                    }

                for p in record.get("pressings", []):
                    p_cat = (p.get("catalogNumber") or "").strip().lower()
                    p_cat_clean = "".join(c for c in p_cat if c.isalnum())
                    if p_cat_clean and p_cat_clean == q_cat_clean:
                        return {
                            "status": "EXACT_MATCH",
                            "matchingRecord": record,
                            "matchingPressing": p,
                            "message": f"ALREADY IN YOUR COLLECTION! Catalog Number '{p_cat}' matches '{record.get('title', '')}'."
                        }

        # 2. Pure Gemini Vision Grounded Match
        if "isAlreadyInCrate" in query and query.get("isAlreadyInCrate") is not None:
            if query.get("isAlreadyInCrate") is True:
                match_id = query.get("crateMatchId")
                match_rec = next((r for r in collection if r.get("id") == match_id), None) if match_id else None

                # Secondary fuzzy match if crateMatchId was not specified but Gemini set isAlreadyInCrate=True
                if not match_rec:
                    q_art = (query.get("artist") or "").strip().lower()
                    q_tit = (query.get("albumTitle") or query.get("title") or "").strip().lower()
                    for r in collection:
                        r_tit = (r.get("title") or "").strip().lower()
                        r_art = (r.get("artist") or "").strip().lower()
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

        # 3. Wishlist Match Check
        q_art = (query.get("artist") or "").strip().lower()
        q_tit = (query.get("albumTitle") or query.get("title") or "").strip().lower()
        if q_art and q_tit:
            for item in wishlist:
                w_art = (item.get("artist") or "").strip().lower()
                w_tit = (item.get("title") or "").strip().lower()
                if (q_art in w_art or w_art in q_art) and (q_tit in w_tit or w_tit in q_tit):
                    return {
                        "status": "WISHLIST_MATCH",
                        "message": f"ON YOUR WISHLIST! Priority: {item.get('priority', 'MEDIUM')}."
                    }

        # If Gemini Vision AI output lacked duplicate status, prompt an error
        raise ValueError("Gemini Vision AI duplicate evaluation failed or incomplete. Cannot verify Crate status.")
