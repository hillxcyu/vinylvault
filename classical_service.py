import re
import logging
import unicodedata
from typing import List, Dict, Any, Tuple, Optional

logger = logging.getLogger("classical_service")
logger.setLevel(logging.INFO)

CLASSICAL_ERAS = [
    {
        "id": "baroque",
        "name": "Baroque Era",
        "years": "1600 – 1750",
        "icon": "🎻",
        "description": "Counterpoint, fugues, harpsichord suites, and ornate polyphonic structures.",
        "keywords": [
            "bach", "vivladi", "vivaldi", "handel", "händel", "haendel", "telemann", "scarlatti", "corelli", "purcell",
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
            "mozart", "haydn", "salieri", "boccherini", "clementi", "gluck", "c.p.e. bach", "cpe bach", "hummel"
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
            "mahler", "rachmaninoff", "rachmaninov", "mendelssohn", "verdi", "schumann", "sibelius", "bruch",
            "grieg", "saint-saëns", "saint-saens", "saint saens", "paganini", "strauss", "puccini", "bizet",
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
        label = (record.get("label") or "").lower()
        catno = (record.get("catalogNumber") or "").lower()
        text_block = f"{title} {artist} {genre} {label} {catno}"

        for excl in NON_CLASSICAL_EXCLUSIONS:
            if excl in text_block and "classical" not in genre:
                return False

        classical_labels = [
            "deutsche grammophon", "dg", "decca", "emi", "philips", "erato", "harmonia mundi",
            "telefunken", "archiv", "cbs masterworks", "melodiya", "chandos", "naxos", "hungaroton",
            "supraphon", "rca victor red seal", "columbia masterworks"
        ]
        for l in classical_labels:
            if l in label:
                return True

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

    def _extract_birth_year(self, lifespan_str: str) -> int:
        match = re.search(r'\b(1[3-9]\d\d|20\d\d)\b', str(lifespan_str))
        if match:
            return int(match.group(1))
        return 9999

    def _compute_composer_stats(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        composer_counter = {}
        classical_recs = [r for r in records if self.is_classical_record(r)]
        
        composer_patterns = [
            ("Camille Saint-Saëns", r"\b(saint-saëns|saint-saens|saint saens)\b", "1835 – 1921", "France", "🇫🇷", "Romantic"),
            ("Antonio Vivaldi", r"\bvivaldi\b", "1678 – 1741", "Italy", "🇮🇹", "Baroque"),
            ("Johann Sebastian Bach", r"\b(bach|bwv)\b", "1685 – 1750", "Germany", "🇩🇪", "Baroque"),
            ("George Frideric Handel", r"\b(handel|händel|haendel)\b", "1685 – 1759", "Germany / UK", "🇬🇧", "Baroque"),
            ("Wolfgang Amadeus Mozart", r"\b(mozart|k\.\s*\d+)\b", "1756 – 1791", "Austria", "🇦🇹", "Classical"),
            ("Ludwig van Beethoven", r"\bbeethoven\b", "1770 – 1827", "Germany", "🇩🇪", "Classical / Romantic"),
            ("Joseph Haydn", r"\bhaydn\b", "1732 – 1809", "Austria", "🇦🇹", "Classical"),
            ("Carl Philipp Emanuel Bach", r"\b(c\.p\.e\.\s*bach|cpe\s*bach)\b", "1714 – 1788", "Germany", "🇩🇪", "Classical"),
            ("Johann Nepomuk Hummel", r"\bhummel\b", "1778 – 1837", "Austria", "🇦🇹", "Classical"),
            ("Franz Schubert", r"\bschubert\b", "1797 – 1828", "Austria", "🇦🇹", "Romantic"),
            ("Hector Berlioz", r"\b(berlioz|symphonie fantastique)\b", "1803 – 1869", "France", "🇫🇷", "Romantic"),
            ("Felix Mendelssohn", r"\bmendelssohn\b", "1809 – 1847", "Germany", "🇩🇪", "Romantic"),
            ("Frédéric Chopin", r"\bchopin\b", "1810 – 1849", "Poland / France", "🇵🇱", "Romantic"),
            ("Robert Schumann", r"\bschumann\b", "1810 – 1856", "Germany", "🇩🇪", "Romantic"),
            ("Franz Liszt", r"\bliszt\b", "1811 – 1886", "Hungary", "🇭🇺", "Romantic"),
            ("Giuseppe Verdi", r"\bverdi\b", "1813 – 1901", "Italy", "🇮🇹", "Romantic"),
            ("Richard Wagner", r"\bwagner\b", "1813 – 1883", "Germany", "🇩🇪", "Romantic"),
            ("César Franck", r"\bfranck\b", "1822 – 1890", "Belgium / France", "🇫🇷", "Romantic"),
            ("Édouard Lalo", r"\blalo\b", "1823 – 1892", "France", "🇫🇷", "Romantic"),
            ("Johann Strauss II", r"\b(johann strauss|strauss ii)\b", "1825 – 1899", "Austria", "🇦🇹", "Romantic"),
            ("Johannes Brahms", r"\bbrahms\b", "1833 – 1897", "Germany", "🇩🇪", "Romantic"),
            ("Max Bruch", r"\bbruch\b", "1838 – 1920", "Germany", "🇩🇪", "Romantic"),
            ("Georges Bizet", r"\bbizet\b", "1838 – 1875", "France", "🇫🇷", "Romantic"),
            ("Modest Mussorgsky", r"\bmussorgsky\b", "1839 – 1881", "Russia", "🇷🇺", "Romantic"),
            ("Pyotr Ilyich Tchaikovsky", r"\btchaikovsky\b", "1840 – 1893", "Russia", "🇷🇺", "Romantic"),
            ("Antonín Dvořák", r"\b(dvořák|dvorak)\b", "1841 – 1904", "Czechia", "🇨🇿", "Romantic"),
            ("Edvard Grieg", r"\bgrieg\b", "1843 – 1907", "Norway", "🇳🇴", "Romantic"),
            ("Nikolai Rimsky-Korsakov", r"\b(rimsky-korsakov|rimsky korsakov)\b", "1844 – 1908", "Russia", "🇷🇺", "Romantic"),
            ("Edward Elgar", r"\belgar\b", "1857 – 1934", "UK", "🇬🇧", "Romantic"),
            ("Giacomo Puccini", r"\bpuccini\b", "1858 – 1924", "Italy", "🇮🇹", "Romantic"),
            ("Gustav Mahler", r"\bmahler\b", "1860 – 1911", "Austria", "🇦🇹", "Romantic"),
            ("Claude Debussy", r"\bdebussy\b", "1862 – 1918", "France", "🇫🇷", "Impressionist"),
            ("Richard Strauss", r"\brichard strauss\b", "1864 – 1949", "Germany", "🇩🇪", "Romantic"),
            ("Jean Sibelius", r"\bsibelius\b", "1865 – 1957", "Finland", "🇫🇮", "Romantic"),
            ("Alexander Scriabin", r"\bscriabin\b", "1872 – 1915", "Russia", "🇷🇺", "Modern"),
            ("Sergei Rachmaninoff", r"\b(rachmaninoff|rachmaninov)\b", "1873 – 1943", "Russia", "🇷🇺", "Romantic"),
            ("Maurice Ravel", r"\bravel\b", "1875 – 1937", "France", "🇫🇷", "Impressionist"),
            ("Béla Bartók", r"\b(bartók|bartok)\b", "1881 – 1945", "Hungary", "🇭🇺", "Modern"),
            ("Igor Stravinsky", r"\bstravinsky\b", "1882 – 1971", "Russia", "🇷🇺", "Modern"),
            ("Alban Berg", r"\balban berg\b", "1885 – 1935", "Austria", "🇦🇹", "Modern"),
            ("Sergei Prokofiev", r"\bprokofiev\b", "1891 – 1953", "Russia", "🇷🇺", "Modern"),
            ("Dmitri Shostakovich", r"\bshostakovich\b", "1906 – 1975", "Russia", "🇷🇺", "Modern"),
            ("Leonard Bernstein", r"\bbernstein\b", "1918 – 1990", "USA", "🇺🇸", "Modern"),
            ("Philip Glass", r"\bphilip glass\b", "1937 – Present", "USA", "🇺🇸", "Contemporary")
        ]

        for r in classical_recs:
            text_corpus = f"{r.get('artist', '')} {r.get('title', '')} {r.get('genre', '')}".lower()
            for cname, pattern, lifespan, country, flag, era in composer_patterns:
                if re.search(pattern, text_corpus):
                    if cname not in composer_counter:
                        composer_counter[cname] = {
                            "name": cname,
                            "lifespan": lifespan,
                            "country": country,
                            "flag": flag,
                            "era": era,
                            "highlights": f"Master of {era} classical compositions.",
                            "count": 0,
                            "albums": []
                        }
                    composer_counter[cname]["count"] += 1
                    if r.get("title") and r.get("title") not in composer_counter[cname]["albums"]:
                        composer_counter[cname]["albums"].append(r.get("title"))

        composer_list = list(composer_counter.values())
        composer_list.sort(key=lambda x: (self._extract_birth_year(x.get("lifespan", "")), -x.get("count", 0)))
        return composer_list



    def _rule_based_chronicle_data(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Classifies records into classical eras using composer keywords."""
        era_map = {era["id"]: {**era, "records": [], "count": 0} for era in CLASSICAL_ERAS}
        classical_count = 0

        for r in records:
            if not self.is_classical_record(r):
                continue

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

    def _reconcile_composer_stats(self, records: List[Dict[str, Any]], ai_chronicle: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Reconciles Gemini/Fallback composerStats with actual records in the user's crate.
        Ensures 'records', 'albums', and 'count' under each composer are 100% accurate and consistent.
        """
        all_era_recs = []
        for era in ai_chronicle.get("eras", []):
            all_era_recs.extend(era.get("records", []))

        raw_composers = ai_chronicle.get("composerStats", [])
        if not raw_composers or not isinstance(raw_composers, list):
            raw_composers = self._compute_composer_stats(records)

        def _get_composer_key(name: str) -> str:
            if not name:
                return ""
            deaccent = "".join(c for c in unicodedata.normalize('NFD', str(name)) if unicodedata.category(c) != 'Mn')
            tokens = [t for t in re.split(r'[\s\-_,.]+', deaccent.lower()) if t and t not in ["ii", "iii", "jr", "sr"]]
            if not tokens:
                return name.lower()
            surname = tokens[-1]
            if len(tokens) >= 2 and tokens[-2] in ["saint", "rimsky", "castelnuovo", "vaughan"]:
                surname = f"{tokens[-2]}_{tokens[-1]}"
            if surname == "strauss":
                if "richard" in tokens:
                    return "strauss_richard"
                if "johann" in tokens:
                    return "strauss_johann"
            if surname == "bach":
                if "cpe" in tokens or "carl" in tokens:
                    return "bach_cpe"
                if "js" in tokens or "johann" in tokens or "sebastian" in tokens:
                    return "bach_js"
            return surname

        reconciled = []
        processed_keys = set()

        for comp in raw_composers:
            if not isinstance(comp, dict) or not comp.get("name"):
                continue
            cname = comp.get("name")
            ckey = _get_composer_key(cname)
            if ckey in processed_keys:
                continue

            matched_records = self._match_records_for_composer(cname, records, all_era_recs)
            if not matched_records:
                continue

            comp["records"] = matched_records
            comp["albums"] = [r.get("title") for r in matched_records if r.get("title")]
            comp["count"] = len(matched_records)
            reconciled.append(comp)
            processed_keys.add(ckey)

        base_composers = self._compute_composer_stats(records)
        for bc in base_composers:
            bc_name = bc.get("name")
            bckey = _get_composer_key(bc_name)
            if bc_name and bckey not in processed_keys:
                matched_records = self._match_records_for_composer(bc_name, records, all_era_recs)
                if matched_records:
                    bc["records"] = matched_records
                    bc["albums"] = [r.get("title") for r in matched_records if r.get("title")]
                    bc["count"] = len(matched_records)
                    reconciled.append(bc)
                    processed_keys.add(bckey)

        reconciled.sort(key=lambda x: (self._extract_birth_year(x.get("lifespan", "")), -x.get("count", 0)))
        return reconciled

    def _match_records_for_composer(self, composer_name: str, records: List[Dict[str, Any]], era_records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Matches actual records in crate/era_records to a specific composer name with strict accuracy."""
        era_detected_map = {}
        for er in era_records:
            if er.get("id"):
                era_detected_map[str(er["id"])] = er.get("detectedComposer")

        matched = []
        seen_ids = set()

        for er in era_records:
            rec_id = er.get("id")
            if not rec_id or str(rec_id) in seen_ids:
                continue
            detected_comp = er.get("detectedComposer")
            if self._is_composer_match(composer_name, er, detected_comp):
                seen_ids.add(str(rec_id))
                matched.append({
                    "id": rec_id,
                    "title": er.get("title"),
                    "artist": er.get("artist"),
                    "coverUrl": er.get("coverUrl"),
                    "releaseYear": er.get("releaseYear")
                })

        for r in records:
            rec_id = r.get("id")
            if not rec_id or str(rec_id) in seen_ids:
                continue
            detected_comp = era_detected_map.get(str(rec_id))
            if self._is_composer_match(composer_name, r, detected_comp):
                seen_ids.add(str(rec_id))
                matched.append({
                    "id": rec_id,
                    "title": r.get("title"),
                    "artist": r.get("artist"),
                    "coverUrl": r.get("coverUrl"),
                    "releaseYear": r.get("releaseYear")
                })

        return matched

    def _is_composer_match(self, comp_name: str, record: Dict[str, Any], detected_comp: Optional[str]) -> bool:
        """
        Determines if a record belongs to a specific composer without cross-matching unrelated composers.
        Handles diacritics (Saint-Saëns / Saint-Saens) and hyphens safely.
        """
        if not comp_name:
            return False

        def _norm(s: str) -> str:
            if not s:
                return ""
            s_deaccent = "".join(c for c in unicodedata.normalize('NFD', str(s)) if unicodedata.category(c) != 'Mn')
            return s_deaccent.lower().strip()

        norm_comp = _norm(comp_name)

        if detected_comp:
            norm_det = _norm(detected_comp)
            if norm_comp in norm_det or norm_det in norm_comp:
                return True

            comp_tokens = [t for t in re.split(r'[\s\-_,.]+', norm_comp) if t]
            det_tokens = [t for t in re.split(r'[\s\-_,.]+', norm_det) if t]

            if comp_tokens and det_tokens:
                comp_surname = comp_tokens[-1]
                det_surname = det_tokens[-1]
                if comp_surname.lower() in ["ii", "iii", "jr", "sr"] and len(comp_tokens) >= 2:
                    comp_surname = comp_tokens[-2]
                if det_surname.lower() in ["ii", "iii", "jr", "sr"] and len(det_tokens) >= 2:
                    det_surname = det_tokens[-2]

                if comp_surname == det_surname:
                    if "strauss" in comp_surname:
                        if "johann" in norm_comp and "richard" in norm_det:
                            return False
                        if "richard" in norm_comp and "johann" in norm_det:
                            return False
                    if "bach" in comp_surname:
                        if ("carl" in norm_det or "cpe" in norm_det) and ("sebastian" in norm_comp or "js" in norm_comp):
                            return False
                        if ("sebastian" in norm_det or "js" in norm_det) and ("carl" in norm_comp or "cpe" in norm_comp):
                            return False
                    return True

        r_artist = _norm(record.get("artist") or "")
        r_title = _norm(record.get("title") or "")
        corpus = f"{r_artist} {r_title}"

        comp_tokens = [t for t in re.split(r'[\s\-_,.]+', norm_comp) if t]
        if comp_tokens and comp_tokens[-1] in ["ii", "iii", "jr", "sr"] and len(comp_tokens) >= 2:
            comp_tokens.pop()

        if not comp_tokens:
            return False

        surname = comp_tokens[-1]
        if len(comp_tokens) >= 2 and comp_tokens[-2] in ["saint", "rimsky", "castelnuovo", "vaughan"]:
            surname_phrase = f"{comp_tokens[-2]} {comp_tokens[-1]}"
        else:
            surname_phrase = surname

        parts = surname_phrase.split()
        regex_parts = [re.escape(p) for p in parts]
        pattern = r'\b' + r'[\s\-_]+'.join(regex_parts) + r'\b'

        if re.search(pattern, corpus):
            if "strauss" in surname:
                if "johann" in norm_comp and ("richard" in corpus and "johann" not in corpus):
                    return False
                if "richard" in norm_comp and ("johann" in corpus and "richard" not in corpus):
                    return False
            if "bach" in surname:
                if ("cpe" in norm_comp or "carl" in norm_comp) and ("js" in corpus or "johann sebastian" in corpus or "bwv" in corpus):
                    return False
                if ("johann sebastian" in norm_comp or "js" in norm_comp) and ("cpe" in corpus or "carl philipp" in corpus):
                    return False
                if "bach" not in r_title and re.search(r'\bbach[\s\-_]*(chor|choir|orchester|orchestra|collegium|ensemble|verein|solisten)\b', r_artist):
                    return False
            if surname in ["bernstein", "boulez", "furtwangler", "furtwaengler"]:
                if surname not in r_title and (not detected_comp or surname not in _norm(detected_comp)):
                    return False
            return True

        return False

    def _rebuild_ai_chronicle_bg(self, records: List[Dict[str, Any]]):

        from database import db
        from gemini_service import gemini_service

        self.is_rebuilding = True
        try:
            ai_chronicle = gemini_service.generate_chronicle_ai(records)
            if ai_chronicle and isinstance(ai_chronicle, dict) and "eras" in ai_chronicle:
                ai_chronicle["source"] = "gemini_3.6_flash"

                unique_classical_ids = set()
                for era in ai_chronicle.get("eras", []):
                    for rec in era.get("records", []):
                        if rec.get("id"):
                            unique_classical_ids.add(rec["id"])
                    era["count"] = len(era.get("records", []))

                ai_chronicle["totalClassicalRecords"] = len(unique_classical_ids)
                ai_chronicle["totalRecordsInCrate"] = len(records)
                
                ai_chronicle["composerStats"] = self._reconcile_composer_stats(records, ai_chronicle)

                db.save_chronicle(ai_chronicle)
                logger.info(f"Saved fresh Gemini 3.6 Flash AI Chronicle ({len(unique_classical_ids)} classical / {len(records)} total records) to Database/Disk in background.")
        except Exception as e:
            logger.error(f"Background AI chronicle rebuild error: {e}")
        finally:
            self.is_rebuilding = False

    def get_chronicle_data(self, records: List[Dict[str, Any]], force_ai_refresh: bool = False) -> Dict[str, Any]:
        """
        Returns Classical Music Chronicle categorized by composer era.
        Uses database-persisted AI Chronicle if available (< 5ms).
        If missing or force_ai_refresh=True, returns immediate rule-based fallback (< 10ms)
        and triggers Gemini 3.6 Flash rebuilding asynchronously in a background thread.
        """
        import threading
        from database import db

        cached = db.get_chronicle()
        if cached and isinstance(cached, dict) and "eras" in cached and cached.get("totalClassicalRecords", 0) > 0 and not force_ai_refresh:
            logger.info("Serving persisted AI/Fallback Chronicle from Database/Disk.")
            cached["isRebuilding"] = self.is_rebuilding
            cached["totalRecordsInCrate"] = len(records)
            cached["composerStats"] = self._reconcile_composer_stats(records, cached)
            return cached

        if not self.is_rebuilding:
            threading.Thread(target=self._rebuild_ai_chronicle_bg, args=(records,), daemon=True).start()

        if cached and isinstance(cached, dict) and "eras" in cached:
            cached["isRebuilding"] = True
            cached["totalRecordsInCrate"] = len(records)
            cached["composerStats"] = self._reconcile_composer_stats(records, cached)
            return cached

        fallback = self._rule_based_chronicle_data(records)
        fallback["composerStats"] = self._reconcile_composer_stats(records, fallback)
        db.save_chronicle(fallback)
        fallback["isRebuilding"] = True
        return fallback



classical_service = ClassicalService()
