import re
import logging
from typing import List, Dict, Any, Tuple, Optional

logger = logging.getLogger("classical_service")

CLASSICAL_ERAS = [
    {
        "id": "baroque",
        "name": "Baroque Era",
        "years": "1600 – 1750",
        "icon": "🎻",
        "description": "Counterpoint, fugues, harpsichord suites, and ornate polyphonic structures.",
        "keywords": [
            "bach", "vivladi", "vivaldi", "handel", "telemann", "scarlatti", "corelli", "purcell",
            "rameau", "couperin", "van eyck", "brüggen", "bruggen", "baroque", "harpsichord", "bwv"
        ]
    },
    {
        "id": "classical",
        "name": "Classical Era",
        "years": "1750 – 1820",
        "icon": "🎼",
        "description": "Sonata-allegro forms, balance, clarity, and the birth of the symphonic orchestra.",
        "keywords": [
            "mozart", "haydn", "salieri", "boccherini", "clementi", "gluck", "c.p.e. bach", "hummel"
        ]
    },
    {
        "id": "romantic",
        "name": "Romantic Era",
        "years": "1820 – 1910",
        "icon": "📜",
        "description": "Expressive emotion, virtuosity, nationalism, expanded chromaticism, and grand opera.",
        "keywords": [
            "schubert", "beethoven", "brahms", "tchaikovsky", "dvořák", "dvorak", "chopin", "liszt", "wagner",
            "mahler", "rachmaninoff", "mendelssohn", "verdi", "schumann", "sibelius", "bruch",
            "grieg", "saint-saëns", "saint-saens", "paganini", "strauss", "puccini", "bizet",
            "berlioz", "rimsky-korsakov", "mussorgsky", "elgar", "franck", "lalo", "stern", "klemperer",
            "rubinstein", "cziffra", "lipatti", "boskovsky", "levine", "haebler", "maazel"
        ]
    },
    {
        "id": "modern_20th",
        "name": "Modern & 20th Century",
        "years": "1910 – 1980",
        "icon": "🎹",
        "description": "Impressionism, serialism, neoclassicism, avant-garde rhythms, and modern composition.",
        "keywords": [
            "debussy", "ravel", "stravinsky", "shostakovich", "prokofiev", "bartók", "bartok",
            "barber", "copland", "gershwin", "messiaen", "holst", "vaughan williams", "britten",
            "hindemith", "bernstein", "boulez", "penderecki", "ligeti", "schoenberg", "alban berg", "berg",
            "scriabin"
        ]
    },
    {
        "id": "contemporary",
        "name": "Contemporary Classical",
        "years": "1980 – Present",
        "icon": "🌌",
        "description": "Minimalism, post-minimalism, ambient classical fusion, and modern cinematic orchestrations.",
        "keywords": [
            "glass", "pärt", "part", "richter", "einaudi", "reich", "williams", "zimmer", "nyman",
            "adams", "yiruma", "arnalds", "guðnadóttir", "gudnadottir"
        ]
    }
]

CLASSICAL_GENRE_KEYWORDS = [
    "classical", "baroque", "romantic", "concerto", "symphony", "sonata", "suite", "suites",
    "opera", "orchestra", "violin", "cello", "piano", "chamber", "quartet", "quintet", "fugue",
    "requiem", "aria", "overture", "philharmonia", "philharmonic", "instrumental", "bwv", "op."
]

COMPOSER_DATABASE = {
    "bach": {"name": "Johann Sebastian Bach", "lifespan": "1685 – 1750", "country": "Germany", "flag": "🇩🇪", "era": "Baroque", "highlights": "Master of counterpoint, organ fugues & Brandenburg Concertos."},
    "vivaldi": {"name": "Antonio Vivaldi", "lifespan": "1678 – 1741", "country": "Italy", "flag": "🇮🇹", "era": "Baroque", "highlights": "Virtuoso violinist & composer of 'The Four Seasons'."},
    "handel": {"name": "George Frideric Handel", "lifespan": "1685 – 1759", "country": "Germany / UK", "flag": "🇬🇧", "era": "Baroque", "highlights": "Famous for Messiah, Water Music & majestic choral works."},
    "mozart": {"name": "Wolfgang Amadeus Mozart", "lifespan": "1756 – 1791", "country": "Austria", "flag": "🇦🇹", "era": "Classical", "highlights": "Child prodigy, master of operas, symphonies & piano concertos."},
    "beethoven": {"name": "Ludwig van Beethoven", "lifespan": "1770 – 1827", "country": "Germany", "flag": "🇩🇪", "era": "Classical / Romantic", "highlights": "Bridged Classical & Romantic eras, 9 monumental symphonies."},
    "haydn": {"name": "Joseph Haydn", "lifespan": "1732 – 1809", "country": "Austria", "flag": "🇦🇹", "era": "Classical", "highlights": "'Father of the Symphony' & string quartet pioneer."},
    "schubert": {"name": "Franz Schubert", "lifespan": "1797 – 1828", "country": "Austria", "flag": "🇦🇹", "era": "Romantic", "highlights": "Master of German Lieder, Unfinished Symphony & chamber music."},
    "chopin": {"name": "Frédéric Chopin", "lifespan": "1810 – 1849", "country": "Poland / France", "flag": "🇵🇱", "era": "Romantic", "highlights": "The 'Poet of the Piano', nocturnes, mazurkas & ballades."},
    "tchaikovsky": {"name": "Pyotr Ilyich Tchaikovsky", "lifespan": "1840 – 1893", "country": "Russia", "flag": "🇷🇺", "era": "Romantic", "highlights": "Swan Lake, The Nutcracker, Pathétique Symphony."},
    "brahms": {"name": "Johannes Brahms", "lifespan": "1833 – 1897", "country": "Germany", "flag": "🇩🇪", "era": "Romantic", "highlights": "Master of classical forms with deep Romantic passion."},
    "dvořák": {"name": "Antonín Dvořák", "lifespan": "1841 – 1904", "country": "Czechia", "flag": "🇨🇿", "era": "Romantic", "highlights": "New World Symphony, Slavonic Dances & cello masterpieces."},
    "dvorak": {"name": "Antonín Dvořák", "lifespan": "1841 – 1904", "country": "Czechia", "flag": "🇨🇿", "era": "Romantic", "highlights": "New World Symphony, Slavonic Dances & cello masterpieces."},
    "debussy": {"name": "Claude Debussy", "lifespan": "1862 – 1918", "country": "France", "flag": "🇫🇷", "era": "Impressionist", "highlights": "Pioneer of Impressionism: Clair de lune, La Mer."},
    "ravel": {"name": "Maurice Ravel", "lifespan": "1875 – 1937", "country": "France", "flag": "🇫🇷", "era": "Impressionist", "highlights": "Master orchestrator: Boléro, Daphnis et Chloé."},
    "stravinsky": {"name": "Igor Stravinsky", "lifespan": "1882 – 1971", "country": "Russia", "flag": "🇷🇺", "era": "Modern", "highlights": "Revolutionary rhythm & harmony: The Rite of Spring."},
    "shostakovich": {"name": "Dmitri Shostakovich", "lifespan": "1906 – 1975", "country": "Russia", "flag": "🇷🇺", "era": "Modern", "highlights": "Dramatic 20th-century symphonist & string quartets."},
    "prokofiev": {"name": "Sergei Prokofiev", "lifespan": "1891 – 1953", "country": "Russia", "flag": "🇷🇺", "era": "Modern", "highlights": "Peter and the Wolf, Romeo and Juliet ballet, piano concertos."},
    "bartók": {"name": "Béla Bartók", "lifespan": "1881 – 1945", "country": "Hungary", "flag": "🇭🇺", "era": "Modern", "highlights": "Ethnomusicologist & pioneer of modern string & orchestral works."},
    "bartok": {"name": "Béla Bartók", "lifespan": "1881 – 1945", "country": "Hungary", "flag": "🇭🇺", "era": "Modern", "highlights": "Ethnomusicologist & pioneer of modern string & orchestral works."},
    "glass": {"name": "Philip Glass", "lifespan": "1937 – Present", "country": "USA", "flag": "🇺🇸", "era": "Contemporary", "highlights": "Minimalist pioneer: Einstein on the Beach, Glassworks."},
    "einaudi": {"name": "Ludovico Einaudi", "lifespan": "1955 – Present", "country": "Italy", "flag": "🇮🇹", "era": "Contemporary", "highlights": "Modern ambient minimalist piano compositions."}
}

NON_CLASSICAL_EXCLUSIONS = [
    "rock", "disco", "pop", "jazz", "latin", "bolero", "blues", "folk", "heavy metal", "hip hop",
    "ventures", "doobie brothers", "billy joel", "three degrees"
]

class ClassicalService:
    def __init__(self):
        self.is_rebuilding = False

    def is_classical_record(self, record: Dict[str, Any]) -> bool:
        """
        Determines if a record belongs to the Classical genre.
        """
        title = (record.get("title") or "").lower()
        artist = (record.get("artist") or "").lower()
        genre = (record.get("genre") or "").lower()
        text_block = f"{title} {artist} {genre}"

        for excl in NON_CLASSICAL_EXCLUSIONS:
            if excl in text_block and "classical" not in genre:
                return False

        for kw in CLASSICAL_GENRE_KEYWORDS:
            if kw in text_block:
                return True

        for era in CLASSICAL_ERAS:
            for kw in era["keywords"]:
                if kw in text_block:
                    return True

        if re.search(r'\b(no\.\s*\d+|op\.\s*\d+|bwv\s*\d+|major|minor|concerto|symphony|sonata)\b', text_block, re.I):
            return True

        return False

    def classify_record_era(self, record: Dict[str, Any]) -> Tuple[Dict[str, Any], str]:
        """
        Classifies a classical record into its era.
        Prioritizes title over performing ensemble artist name to avoid misclassifications.
        """
        title = (record.get("title") or "").lower()
        artist = (record.get("artist") or "").lower()

        # 1. First check TITLE for composer keywords (most authoritative)
        for era in CLASSICAL_ERAS:
            for kw in era["keywords"]:
                if re.search(r'\b' + re.escape(kw) + r'\b', title):
                    return era, kw.title()

        # 2. Next check ARTIST for composer keywords
        for era in CLASSICAL_ERAS:
            for kw in era["keywords"]:
                if re.search(r'\b' + re.escape(kw) + r'\b', artist):
                    return era, kw.title()

        # 3. Fallback using releaseYear
        year = record.get("releaseYear")
        if year and isinstance(year, int):
            if year < 1750:
                return CLASSICAL_ERAS[0], "Baroque Master"
            elif 1750 <= year < 1820:
                return CLASSICAL_ERAS[1], "Classical Master"
            elif 1820 <= year < 1910:
                return CLASSICAL_ERAS[2], "Romantic Master"
            elif 1910 <= year < 1980:
                return CLASSICAL_ERAS[3], "20th Century Master"
            else:
                return CLASSICAL_ERAS[4], "Contemporary Composer"

        return CLASSICAL_ERAS[2], "Classical Composer"

    def _compute_composer_stats(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        composer_counter = {}
        for r in records:
            text_corpus = f"{r.get('artist', '')} {r.get('title', '')} {r.get('genre', '')}".lower()
            for key, info in COMPOSER_DATABASE.items():
                if key in text_corpus:
                    cname = info["name"]
                    if cname not in composer_counter:
                        composer_counter[cname] = {
                            **info,
                            "count": 0,
                            "albums": []
                        }
                    composer_counter[cname]["count"] += 1
                    if r.get("title") and r.get("title") not in composer_counter[cname]["albums"]:
                        composer_counter[cname]["albums"].append(r.get("title"))

        composer_list = list(composer_counter.values())
        composer_list.sort(key=lambda x: x["count"], reverse=True)
        return composer_list

    def _rule_based_chronicle_data(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Classifies records into classical eras using composer keywords."""
        era_map = {era["id"]: {**era, "records": [], "count": 0} for era in CLASSICAL_ERAS}
        classical_count = 0

        for r in records:
            composer = (r.get("artist") or r.get("title") or "").strip()
            text_corpus = f"{r.get('artist', '')} {r.get('title', '')} {r.get('genre', '')}".lower()

            matched_era_id = "romantic"
            for era in CLASSICAL_ERAS:
                for kw in era["keywords"]:
                    if kw in text_corpus:
                        matched_era_id = era["id"]
                        break
                if matched_era_id == era["id"] and matched_era_id != "romantic":
                    break

            classical_count += 1
            era = era_map[matched_era_id]

            rec_entry = dict(r)
            rec_entry["eraId"] = era["id"]
            rec_entry["eraName"] = era["name"]
            rec_entry["aiInsight"] = f"Masterpiece of the {era['name']} featuring {composer}."

            era_map[era["id"]]["records"].append(rec_entry)
            era_map[era["id"]]["count"] += 1

        eras_list = [era_data for era_data in era_map.values() if era_data["count"] > 0 or era_data["id"] in ["baroque", "classical", "romantic", "modern_20th"]]
        composer_list = self._compute_composer_stats(records)

        return {
            "totalClassicalRecords": classical_count,
            "totalRecordsInCrate": len(records),
            "eras": eras_list,
            "composerStats": composer_list,
            "source": "rule_based_fallback"
        }

    def get_chronicle_data(self, records: List[Dict[str, Any]], force_ai_refresh: bool = False) -> Dict[str, Any]:
        """
        Returns Classical Music Chronicle categorized by composer era.
        Uses database-persisted AI Chronicle if available.
        Calls Gemini 3.6 Flash when force_ai_refresh=True or when no DB cache exists.
        Falls back to rule-based classification if offline/unreachable.
        """
        from database import db
        from gemini_service import gemini_service

        if not force_ai_refresh:
            cached = db.get_chronicle()
            if cached and isinstance(cached, dict) and "eras" in cached and cached.get("totalClassicalRecords", 0) > 0:
                logger.info("Serving persisted AI/Fallback Chronicle from Database/Disk.")
                cached["isRebuilding"] = self.is_rebuilding
                cached["composerStats"] = self._compute_composer_stats(records)
                return cached

        self.is_rebuilding = True
        try:
            ai_chronicle = gemini_service.generate_chronicle_ai(records)
            if ai_chronicle and isinstance(ai_chronicle, dict) and "eras" in ai_chronicle:
                ai_chronicle["source"] = "gemini_3.6_flash"
                ai_chronicle["composerStats"] = self._compute_composer_stats(records)
                db.save_chronicle(ai_chronicle)
                logger.info("Saved fresh Gemini 3.6 Flash AI Chronicle to Database/Disk.")
                ai_chronicle["isRebuilding"] = False
                return ai_chronicle

            cached = db.get_chronicle()
            if cached and isinstance(cached, dict) and "eras" in cached:
                cached["isRebuilding"] = False
                cached["composerStats"] = self._compute_composer_stats(records)
                return cached

            fallback = self._rule_based_chronicle_data(records)
            db.save_chronicle(fallback)
            fallback["isRebuilding"] = False
            return fallback
        finally:
            self.is_rebuilding = False

classical_service = ClassicalService()
