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
    "bach": {
        "name": "Johann Sebastian Bach",
        "lifespan": "1685 – 1750",
        "country": "Germany",
        "flag": "🇩🇪",
        "era": "Baroque",
        "highlights": "Master of counterpoint, organ fugues & Brandenburg Concertos.",
        "bio": "Johann Sebastian Bach is widely considered one of the greatest composers in Western history. Born in Eisenach, Germany, he enriched established German styles through his mastery of counterpoint, harmonic organization, and motivic development.",
        "innovations": "Architect of modern polyphony, Well-Tempered Klavier tuning, complex fugal structures.",
        "keyWorks": ["Brandenburg Concertos", "The Well-Tempered Clavier", "Mass in B Minor", "Goldberg Variations"]
    },
    "vivaldi": {
        "name": "Antonio Vivaldi",
        "lifespan": "1678 – 1741",
        "country": "Italy",
        "flag": "🇮🇹",
        "era": "Baroque",
        "highlights": "Virtuoso violinist & composer of 'The Four Seasons'.",
        "bio": "Known as 'The Red Priest' due to his red hair and ordination as a priest, Vivaldi was an Italian Baroque composer, virtuoso violinist, and teacher in Venice. He wrote over 500 concertos.",
        "innovations": "Pioneered ritornello form in solo concertos, programmatic musical storytelling.",
        "keyWorks": ["The Four Seasons", "Gloria in D major", "L'estro armonico", "Stabat Mater"]
    },
    "handel": {
        "name": "George Frideric Handel",
        "lifespan": "1685 – 1759",
        "country": "Germany / UK",
        "flag": "🇬🇧",
        "era": "Baroque",
        "highlights": "Famous for Messiah, Water Music & majestic choral works.",
        "bio": "German-born British Baroque composer renowned for his operas, oratorios, anthems, and organ concertos. He established himself in London and became a naturalized British subject.",
        "innovations": "Elevated English choral oratorio, dramatic theatricality in sacred music.",
        "keyWorks": ["Messiah", "Water Music", "Music for the Royal Fireworks", "Zadok the Priest"]
    },
    "mozart": {
        "name": "Wolfgang Amadeus Mozart",
        "lifespan": "1756 – 1791",
        "country": "Austria",
        "flag": "🇦🇹",
        "era": "Classical",
        "highlights": "Child prodigy, master of operas, symphonies & piano concertos.",
        "bio": "A child prodigy born in Salzburg, Mozart composed over 600 works spanning every musical genre of his era. His melodic genius and structural perfection defined the High Classical style.",
        "innovations": "Mastered and refined sonata-allegro form, opera buffa, and the classical piano concerto.",
        "keyWorks": ["Symphony No. 41 'Jupiter'", "The Magic Flute", "Requiem in D minor", "Don Giovanni"]
    },
    "beethoven": {
        "name": "Ludwig van Beethoven",
        "lifespan": "1770 – 1827",
        "country": "Germany",
        "flag": "🇩🇪",
        "era": "Classical / Romantic",
        "highlights": "Bridged Classical & Romantic eras, 9 monumental symphonies.",
        "bio": "A crucial figure in the transition between the Classical and Romantic eras in Western art music, Beethoven expanded the scope of symphonic, sonata, and string quartet music even while suffering complete deafness.",
        "innovations": "Expansion of symphonic structure, introduce choral elements to symphony (Symphony No. 9), heroic musical narrative.",
        "keyWorks": ["Symphony No. 5 & No. 9", "Piano Sonata No. 14 'Moonlight'", "Violin Concerto", "Fidelio"]
    },
    "haydn": {
        "name": "Joseph Haydn",
        "lifespan": "1732 – 1809",
        "country": "Austria",
        "flag": "🇦🇹",
        "era": "Classical",
        "highlights": "'Father of the Symphony' & string quartet pioneer.",
        "bio": "Joseph Haydn was instrumental in the development of chamber music such as the piano trio and string quartet. His contributions to musical form have earned him the titles 'Father of the Symphony' and 'Father of the String Quartet'.",
        "innovations": "Established 4-movement symphonic format, developed classical chamber humor and motivic economy.",
        "keyWorks": ["Symphony No. 104 'London'", "The Creation", "String Quartets Op. 76", "Trumpet Concerto"]
    },
    "schubert": {
        "name": "Franz Schubert",
        "lifespan": "1797 – 1828",
        "country": "Austria",
        "flag": "🇦🇹",
        "era": "Romantic",
        "highlights": "Master of German Lieder, Unfinished Symphony & chamber music.",
        "bio": "Despite a short life, Schubert left behind a vast oeuvre, including over 600 secular vocal works (mainly Lieder), seven complete symphonies, sacred music, operas, and incidental music.",
        "innovations": "Elevated German Lieder (art songs) to high art, pioneering Romantic lyrical harmonic shifts.",
        "keyWorks": ["Symphony No. 8 'Unfinished'", "Trout Quintet", "Winterreise", "String Quartet 'Death and the Maiden'"]
    },
    "chopin": {
        "name": "Frédéric Chopin",
        "lifespan": "1810 – 1849",
        "country": "Poland / France",
        "flag": "🇵🇱",
        "era": "Romantic",
        "highlights": "The 'Poet of the Piano', nocturnes, mazurkas & ballades.",
        "bio": "Chopin was a Polish composer and virtuoso pianist of the Romantic era who wrote primarily for solo piano. All of his compositions feature the piano, often combining Polish folk rhythms with French elegance.",
        "innovations": "Invented the instrumental ballade, revolutionized piano legato, rubato, and chromatic expressive nuances.",
        "keyWorks": ["Nocturnes", "24 Preludes Op. 28", "Ballade No. 1 in G minor", "Polonaise in A-flat major"]
    },
    "tchaikovsky": {
        "name": "Pyotr Ilyich Tchaikovsky",
        "lifespan": "1840 – 1893",
        "country": "Russia",
        "flag": "🇷🇺",
        "era": "Romantic",
        "highlights": "Swan Lake, The Nutcracker, Pathétique Symphony.",
        "bio": "The first Russian composer whose music made a lasting impression internationally, Tchaikovsky wrote some of the most popular concert and theatrical music in the current classical repertoire.",
        "innovations": "Elevated ballet music into symphonic art, emotional Russian orchestral nationalism.",
        "keyWorks": ["Swan Lake", "The Nutcracker", "Symphony No. 6 'Pathétique'", "Violin Concerto in D major"]
    },
    "brahms": {
        "name": "Johannes Brahms",
        "lifespan": "1833 – 1897",
        "country": "Germany",
        "flag": "🇩🇪",
        "era": "Romantic",
        "highlights": "Master of classical forms with deep Romantic passion.",
        "bio": "Brahms was a German composer, pianist, and conductor of the Romantic period. He maintained a devotion to Classical structures while breathing rich, warm Romantic harmony into his works.",
        "innovations": "'Developing variation' technique, revival of Baroque passacaglia in Romantic symphonies.",
        "keyWorks": ["Symphony No. 4 in E minor", "A German Requiem", "Violin Concerto in D", "Hungarian Dances"]
    },
    "dvořák": {
        "name": "Antonín Dvořák",
        "lifespan": "1841 – 1904",
        "country": "Czechia",
        "flag": "🇨🇿",
        "era": "Romantic",
        "highlights": "New World Symphony, Slavonic Dances & cello masterpieces.",
        "bio": "Dvořák frequently employed aspects, specifically rhythms, of the folk music of Moravia and his native Bohemia. He later served as director of the National Conservatory of Music in New York.",
        "innovations": "Incorporated Czech and African American folk melodies into classical symphonic form.",
        "keyWorks": ["Symphony No. 9 'From the New World'", "Cello Concerto in B minor", "Slavonic Dances", "American String Quartet"]
    },
    "dvorak": {
        "name": "Antonín Dvořák",
        "lifespan": "1841 – 1904",
        "country": "Czechia",
        "flag": "🇨🇿",
        "era": "Romantic",
        "highlights": "New World Symphony, Slavonic Dances & cello masterpieces.",
        "bio": "Dvořák frequently employed aspects, specifically rhythms, of the folk music of Moravia and his native Bohemia. He later served as director of the National Conservatory of Music in New York.",
        "innovations": "Incorporated Czech and African American folk melodies into classical symphonic form.",
        "keyWorks": ["Symphony No. 9 'From the New World'", "Cello Concerto in B minor", "Slavonic Dances", "American String Quartet"]
    },
    "debussy": {
        "name": "Claude Debussy",
        "lifespan": "1862 – 1918",
        "country": "France",
        "flag": "🇫🇷",
        "era": "Impressionist",
        "highlights": "Pioneer of Impressionism: Clair de lune, La Mer.",
        "bio": "Debussy was the primary figure of Impressionist music. His use of non-traditional scales and chromaticism influenced almost every major 20th-century composer.",
        "innovations": "Whole-tone and pentatonic scales, timbre as a primary structural element.",
        "keyWorks": ["Clair de lune", "Prélude à l'après-midi d'un faune", "La Mer", "Suite bergamasque"]
    },
    "ravel": {
        "name": "Maurice Ravel",
        "lifespan": "1875 – 1937",
        "country": "France",
        "flag": "🇫🇷",
        "era": "Impressionist",
        "highlights": "Master orchestrator: Boléro, Daphnis et Chloé.",
        "bio": "Ravel was a French composer, pianist and conductor, often associated with Impressionism along with his elder contemporary Claude Debussy. He was a master of orchestration.",
        "innovations": "Complex modal harmonies, ostinato orchestration, Spanish and jazz rhythm fusions.",
        "keyWorks": ["Boléro", "Daphnis et Chloé", "Pavane pour une infante défunte", "Gaspard de la nuit"]
    },
    "stravinsky": {
        "name": "Igor Stravinsky",
        "lifespan": "1882 – 1971",
        "country": "Russia",
        "flag": "🇷🇺",
        "era": "Modern",
        "highlights": "Revolutionary rhythm & harmony: The Rite of Spring.",
        "bio": "Widely considered one of the most important and influential composers of the 20th century, Stravinsky's compositional career was notable for its stylistic diversity.",
        "innovations": "Polyrhythms, asymmetric meters, polytonality, Neoclassical revival.",
        "keyWorks": ["The Rite of Spring", "The Firebird", "Petrushka", "Symphony of Psalms"]
    },
    "shostakovich": {
        "name": "Dmitri Shostakovich",
        "lifespan": "1906 – 1975",
        "country": "Russia",
        "flag": "🇷🇺",
        "era": "Modern",
        "highlights": "Dramatic 20th-century symphonist & string quartets.",
        "bio": "Shostakovich achieved fame in the Soviet Union under the discipline of Joseph Stalin. His music is characterized by sharp contrasts, elements of the grotesque, and ambivalent tonality.",
        "innovations": "Use of the DSCH musical monogram, intense tragic symphonism, sarcastic scherzos.",
        "keyWorks": ["Symphony No. 5 in D minor", "Symphony No. 7 'Leningrad'", "String Quartet No. 8", "Cello Concerto No. 1"]
    },
    "prokofiev": {
        "name": "Sergei Prokofiev",
        "lifespan": "1891 – 1953",
        "country": "Russia",
        "flag": "🇷🇺",
        "era": "Modern",
        "highlights": "Peter and the Wolf, Romeo and Juliet ballet, piano concertos.",
        "bio": "A Russian Soviet composer, pianist, and conductor, Prokofiev is regarded as one of the major composers of the 20th century, creating masterpieces across numerous genres.",
        "innovations": "Motoric rhythms, lyricism juxtaposed with harsh dissonance, Neoclassical revival.",
        "keyWorks": ["Peter and the Wolf", "Romeo and Juliet Ballet", "Piano Concerto No. 3", "Symphony No. 1 'Classical'"]
    },
    "bartók": {
        "name": "Béla Bartók",
        "lifespan": "1881 – 1945",
        "country": "Hungary",
        "flag": "🇭🇺",
        "era": "Modern",
        "highlights": "Ethnomusicologist & pioneer of modern string & orchestral works.",
        "bio": "Bartók was a Hungarian composer, pianist, and ethnomusicologist. He is considered one of the most important composers of the 20th century.",
        "innovations": "Synthesis of Eastern European folk melodies with modern atonality and percussive piano technique.",
        "keyWorks": ["Concerto for Orchestra", "Music for Strings, Percussion and Celesta", "Mikrokosmos", "Duke Bluebeard's Castle"]
    },
    "bartok": {
        "name": "Béla Bartók",
        "lifespan": "1881 – 1945",
        "country": "Hungary",
        "flag": "🇭🇺",
        "era": "Modern",
        "highlights": "Ethnomusicologist & pioneer of modern string & orchestral works.",
        "bio": "Bartók was a Hungarian composer, pianist, and ethnomusicologist. He is considered one of the most important composers of the 20th century.",
        "innovations": "Synthesis of Eastern European folk melodies with modern atonality and percussive piano technique.",
        "keyWorks": ["Concerto for Orchestra", "Music for Strings, Percussion and Celesta", "Mikrokosmos", "Duke Bluebeard's Castle"]
    },
    "glass": {
        "name": "Philip Glass",
        "lifespan": "1937 – Present",
        "country": "USA",
        "flag": "🇺🇸",
        "era": "Contemporary",
        "highlights": "Minimalist pioneer: Einstein on the Beach, Glassworks.",
        "bio": "Philip Glass is an American composer and pianist. He is widely regarded as one of the most influential composers of the late 20th century, famous for his minimalist structures.",
        "innovations": "Additive rhythmic structures, repetitive ostinato arpeggios, opera/film score minimalism.",
        "keyWorks": ["Einstein on the Beach", "Glassworks", "Violin Concerto No. 1", "Koyaanisqatsi"]
    },
    "einaudi": {
        "name": "Ludovico Einaudi",
        "lifespan": "1955 – Present",
        "country": "Italy",
        "flag": "🇮🇹",
        "era": "Contemporary",
        "highlights": "Modern ambient minimalist piano compositions.",
        "bio": "Italian pianist and composer known for his meditative, ambient classical compositions blending pop, folk, and minimalist classical textures.",
        "innovations": "Neo-classical ambient piano melodies, modern film and streaming soundtracks.",
        "keyWorks": ["Nuvole Bianche", "Experience", "I Giorni", "Una Mattina"]
    }
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
            ("Hector Berlioz", r"\b(berlioz|symphonie fantastique)\b", "1803 – 1869", "France", "🇫🇷", "Romantic"),
            ("Johann Sebastian Bach", r"\b(bach|bwv)\b", "1685 – 1750", "Germany", "🇩🇪", "Baroque"),
            ("Wolfgang Amadeus Mozart", r"\b(mozart|k\.\s*\d+)\b", "1756 – 1791", "Austria", "🇦🇹", "Classical"),
            ("Ludwig van Beethoven", r"\bbeethoven\b", "1770 – 1827", "Germany", "🇩🇪", "Classical / Romantic"),
            ("Antonín Dvořák", r"\b(dvořák|dvorak)\b", "1841 – 1904", "Czechia", "🇨🇿", "Romantic"),
            ("Pyotr Ilyich Tchaikovsky", r"\btchaikovsky\b", "1840 – 1893", "Russia", "🇷🇺", "Romantic"),
            ("Johannes Brahms", r"\bbrahms\b", "1833 – 1897", "Germany", "🇩🇪", "Romantic"),
            ("Franz Schubert", r"\bschubert\b", "1797 – 1828", "Austria", "🇦🇹", "Romantic"),
            ("Frédéric Chopin", r"\bchopin\b", "1810 – 1849", "Poland / France", "🇵🇱", "Romantic"),
            ("Joseph Haydn", r"\bhaydn\b", "1732 – 1809", "Austria", "🇦🇹", "Classical"),
            ("Claude Debussy", r"\bdebussy\b", "1862 – 1918", "France", "🇫🇷", "Impressionist"),
            ("Maurice Ravel", r"\bravel\b", "1875 – 1937", "France", "🇫🇷", "Impressionist"),
            ("Igor Stravinsky", r"\bstravinsky\b", "1882 – 1971", "Russia", "🇷🇺", "Modern"),
            ("Dmitri Shostakovich", r"\bshostakovich\b", "1906 – 1975", "Russia", "🇷🇺", "Modern"),
            ("Sergei Prokofiev", r"\bprokofiev\b", "1891 – 1953", "Russia", "🇷🇺", "Modern"),
            ("Béla Bartók", r"\b(bartók|bartok)\b", "1881 – 1945", "Hungary", "🇭🇺", "Modern"),
            ("Jean Sibelius", r"\bsibelius\b", "1865 – 1957", "Finland", "🇫🇮", "Romantic"),
            ("Felix Mendelssohn", r"\bmendelssohn\b", "1809 – 1847", "Germany", "🇩🇪", "Romantic"),
            ("Robert Schumann", r"\bschumann\b", "1810 – 1856", "Germany", "🇩🇪", "Romantic"),
            ("Franz Liszt", r"\bliszt\b", "1811 – 1886", "Hungary", "🇭🇺", "Romantic"),
            ("Giuseppe Verdi", r"\bverdi\b", "1813 – 1901", "Italy", "🇮🇹", "Romantic"),
            ("Gustav Mahler", r"\bmahler\b", "1860 – 1911", "Austria", "🇦🇹", "Romantic"),
            ("Max Bruch", r"\bbruch\b", "1838 – 1920", "Germany", "🇩🇪", "Romantic")
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

    def _rebuild_ai_chronicle_bg(self, records: List[Dict[str, Any]]):

        from database import db
        from gemini_service import gemini_service

        self.is_rebuilding = True
        try:
            ai_chronicle = gemini_service.generate_chronicle_ai(records)
            if ai_chronicle and isinstance(ai_chronicle, dict) and "eras" in ai_chronicle:
                ai_chronicle["source"] = "gemini_3.6_flash"

                # Recalculate unique classical record count and total crate count
                unique_classical_ids = set()
                for era in ai_chronicle.get("eras", []):
                    for rec in era.get("records", []):
                        if rec.get("id"):
                            unique_classical_ids.add(rec["id"])
                    era["count"] = len(era.get("records", []))

                ai_chronicle["totalClassicalRecords"] = len(unique_classical_ids)
                ai_chronicle["totalRecordsInCrate"] = len(records)
                
                # Sort Gemini's dynamic composerStats chronologically by birth year
                if ai_chronicle.get("composerStats"):
                    ai_chronicle["composerStats"].sort(key=lambda x: (self._extract_birth_year(x.get("lifespan", "")), -x.get("count", 0)))
                else:
                    ai_chronicle["composerStats"] = self._compute_composer_stats(records)

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
            if not cached.get("composerStats") or len(cached.get("composerStats", [])) == 0:
                cached["composerStats"] = self._compute_composer_stats(records)
            return cached

        if not self.is_rebuilding:
            threading.Thread(target=self._rebuild_ai_chronicle_bg, args=(records,), daemon=True).start()

        if cached and isinstance(cached, dict) and "eras" in cached:
            cached["isRebuilding"] = True
            cached["totalRecordsInCrate"] = len(records)
            if not cached.get("composerStats") or len(cached.get("composerStats", [])) == 0:
                cached["composerStats"] = self._compute_composer_stats(records)
            return cached

        fallback = self._rule_based_chronicle_data(records)
        db.save_chronicle(fallback)
        fallback["isRebuilding"] = True
        return fallback



classical_service = ClassicalService()
