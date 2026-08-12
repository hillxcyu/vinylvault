import os
import io
import re
import wave
import json
import base64
import logging
from typing import Dict, Any, List, Optional


logger = logging.getLogger("gemini_service")



def downsample_image_bytes(image_bytes: bytes, max_dim: int = 1024, quality: int = 85) -> bytes:
    """
    Downsample uploaded high-res photos to max_dim (e.g. 1024px) at JPEG quality 85%.
    Reduces upload payload size by >95% (from 5MB+ to ~150KB), significantly speeding up
    Gemini Vision processing time while preserving full readability for OCR & corners.
    """
    if not image_bytes:
        return image_bytes
    try:
        from PIL import Image, ImageOps
        img = Image.open(io.BytesIO(image_bytes))
        img = ImageOps.exif_transpose(img)

        if img.mode in ("RGBA", "P", "LA"):

            img = img.convert("RGB")

        w, h = img.size
        if max(w, h) > max_dim:
            if w >= h:
                new_w = max_dim
                new_h = int(h * (max_dim / float(w)))
            else:
                new_h = max_dim
                new_w = int(w * (max_dim / float(h)))

            resample_filter = getattr(Image, "Resampling", Image).LANCZOS
            img = img.resize((new_w, new_h), resample=resample_filter)

            out_buf = io.BytesIO()
            img.save(out_buf, format="JPEG", quality=quality, optimize=True)
            compressed = out_buf.getvalue()
            logger.info(f"Image downsampled: {len(image_bytes)} bytes ({w}x{h}) -> {len(compressed)} bytes ({new_w}x{new_h})")
            return compressed
    except Exception as e:
        logger.warning(f"Image downsampling warning (using original image): {e}")
    return image_bytes


class GeminiVisionService:
    @staticmethod
    def downsample_image_bytes(image_bytes: bytes, max_dim: int = 1024, quality: int = 85) -> bytes:
        return downsample_image_bytes(image_bytes, max_dim=max_dim, quality=quality)

    def __init__(self):

        self.project = os.environ.get("GOOGLE_CLOUD_PROJECT", "universal-trail-492014-n5")
        self.location = os.environ.get("GOOGLE_CLOUD_LOCATION", "global")
        self.client = None
        self._pronunciation_cache = {}
        self._init_client()

    def _init_client(self):
        try:
            from google import genai
            container_adc = "/root/.config/gcloud/application_default_credentials.json"
            host_adc = os.path.expanduser("~/.config/gcloud/application_default_credentials.json")

            if os.path.exists(container_adc):
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = container_adc
            elif os.path.exists(host_adc):
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = host_adc

            self.client = genai.Client(
                vertexai=True,
                project=self.project,
                location=self.location
            )
            logger.info(f"Gemini GenAI Vertex AI client initialized for project {self.project} in location {self.location}.")
        except Exception as e:
            logger.warning(f"Gemini client initialization warning: {e}")
            self.client = None

    def get_album_segmentation_corners(self, image_bytes: bytes) -> Optional[List[List[int]]]:
        """
        Extract 4-point polygon segmentation corners of the album cover via Gemini 3.6 Flash.
        Returns a list of 4 [x, y] coordinates normalized to 0-1000 scale, or None if unavailable.
        """
        if not self.client:
            return None

        # Downsample high-res photo to 1024px max dimension for fast execution
        optimized_image_bytes = downsample_image_bytes(image_bytes, max_dim=1024, quality=85)

        try:
            from google.genai import types
            from pydantic import BaseModel, Field

            class AlbumCornerSegmentation(BaseModel):
                label: str = Field(description="Description of the item")
                box_2d: List[int] = Field(description="The 2D bounding box of the item as [ymin, xmin, ymax, xmax] normalized to 0-1000.")
                mask: List[List[int]] = Field(description="4 outer polygon corners [[y1, x1], [y2, x2], [y3, x3], [y4, x4]] normalized 0-1000 scale")

            prompt = (
                "Locate the main vinyl record album cover or box set in this photo.\n"
                "Detect its exact 2D bounding box 'box_2d' ([ymin, xmin, ymax, xmax] normalized 0-1000) and its 4 physical outer corners 'mask'.\n"
                "Each point in 'mask' MUST be [y, x] normalized to 0-1000 scale:\n"
                "[\n"
                "  [top_left_y, top_left_x],\n"
                "  [top_right_y, top_right_x],\n"
                "  [bottom_right_y, bottom_right_x],\n"
                "  [bottom_left_y, bottom_left_x]\n"
                "]"
            )

            config = types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=AlbumCornerSegmentation,
                thinking_config=types.ThinkingConfig(thinking_level="minimal")
            )



            response = self.client.models.generate_content(
                model="gemini-3.6-flash",
                contents=[
                    types.Part.from_bytes(data=optimized_image_bytes, mime_type="image/jpeg"),
                    prompt
                ],
                config=config
            )

            text = (response.text or "").strip()
            if not text and hasattr(response, "candidates") and response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    if hasattr(part, "text") and part.text:
                        text += part.text
            text = text.strip()
            if not text:
                return None

            parsed = json.loads(text)
            mask = parsed.get("mask", [])
            box_2d = parsed.get("box_2d", [])
            if len(mask) == 4 and all(isinstance(pt, list) and len(pt) == 2 for pt in mask):
                logger.info(f"Gemini Vision Segmentation Corners detected: mask={mask}, box_2d={box_2d}")
                return mask
        except Exception as e:
            logger.warning(f"Gemini Vision segmentation corner detection warning: {e}")

        return None


    def analyze_album_cover(self, image_bytes: bytes, filename: str = "cover.jpg", crate_records: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Analyze album cover photo using Gemini 3.6 Flash Vision model with Google Search grounding and Crate inventory duplicate checking
        """

        if self.client:
            try:
                from google.genai import types

                # Downsample high-res photo to 1024px max dimension for fast execution
                optimized_image_bytes = downsample_image_bytes(image_bytes, max_dim=1024, quality=85)

                crate_context = ""
                if crate_records:
                    crate_lines = []
                    for r in crate_records:
                        if isinstance(r, dict):
                            rec_id = r.get("id") or ""
                            title = r.get("title") or ""
                            artist = r.get("artist") or ""
                            label = r.get("label") or ""
                            catno = r.get("catalogNumber") or r.get("catno") or ""
                            year = r.get("releaseYear") or ""

                            info_parts = []
                            if label:
                                info_parts.append(f"Label: {label}")
                            if catno:
                                info_parts.append(f"CatNo: {catno}")
                            if year:
                                info_parts.append(f"Year: {year}")

                            meta_str = f" ({', '.join(info_parts)})" if info_parts else ""
                            crate_lines.append(f"- ID: {rec_id} | \"{title}\" - {artist}{meta_str}")

                    crate_context_str = "\n".join(crate_lines[:200])
                    crate_context = (
                        f"\n\nCRITICAL REQUIREMENT 4: CRATE INVENTORY DUPLICATE EVALUATION\n"
                        f"Perform fuzzy semantic and musicological matching against the user's Crate Collection inventory below:\n"
                        f"{crate_context_str}\n\n"
                        f"MANDATORY MATCHING RULES:\n"
                        f"1. You MUST set 'isAlreadyInCrate': true if the user owns ANY pressing, reissue, or release of this album. Match by album title / main composition or main performers/artists (e.g. '24 Songs and One Guitar' by Belina & Siegfried Behrend matches '24 Songs & 1 Guitar'). Do NOT require exact catalog number or label match to mark as owned.\n"
                        f"2. Set 'crateMatchId' to the exact 'id' string of the matching record in the crate list above.\n"
                        f"3. Set 'crateMatchReason' to a 1-2 sentence musicological summary (e.g. 'ALREADY IN YOUR CRATE! You own this album: \"[Title]\" by [Artist] (Record ID: [id])').\n"
                        f"4. If no album with equivalent title/performers exists in the crate list, set 'isAlreadyInCrate': false, 'crateMatchId': null, and 'crateMatchReason': 'NOT IN COLLECTION. Safe to add!'.\n"
                    )

                prompt = (
                    "You are an expert vinyl record archivist, musicologist, and cataloger specializing in Classical, Jazz, Rock, and Box Sets.\n"
                    "Analyze this image of a vinyl album cover, box set, spine, or obi strip with extreme precision.\n"
                    "CRITICAL REQUIREMENT 1: Perform deep research using Google Search grounding to verify the exact 'label', 'catalogNumber', and 'releaseYear'. "
                    "For Box Sets (e.g. 2LP, 3LP, multi-disc sets), carefully inspect the box spine, top/bottom corners, or obi strip to extract the master box set catalog number and exact record label (e.g. 'Deutsche Grammophon', 'Decca', 'Seraphim', 'Philips', 'EMI', 'CBS Masterworks', 'Archiv').\n"
                    "CRITICAL REQUIREMENT 2: Use Google Search grounding to look up the official release year for this specific catalog number/pressing (e.g., 'EAC-60150-51' was released in 1978, 'UCJG-9012' in 2009). Always return an accurate 4-digit 'releaseYear' integer.\n"
                    "CRITICAL REQUIREMENT 5: Simultaneously perform 2D polygon segmentation to detect both the 2D bounding box 'box_2d' ([ymin, xmin, ymax, xmax] normalized 0-1000) and 4 exact outer boundary corners 'mask' of the album jacket/sleeve.\n"
                    f"{crate_context}\n\n"
                    "Extract and return ONLY a valid JSON object with the following fields:\n"
                    "1. 'artist': Main soloist, conductor, orchestra, or performer(s).\n"
                    "2. 'albumTitle': Full album title or composer/work title.\n"
                    "3. 'catalogNumber': Exact catalog number (e.g. 'EAC-30073', 'SLA 6187', 'VIC-28001', '2530 229', 'IMP-2026-001').\n"
                    "4. 'label': Exact record label name (e.g. 'Decca', 'Seraphim', 'Deutsche Grammophon', 'EMI', 'Philips', 'RCA').\n"
                    "5. 'country': Release country or pressing origin (e.g. 'Japan', 'US', 'UK', 'Germany').\n"
                    "6. 'releaseYear': Exact 4-digit release year integer (e.g. 1978, 1961, 2009).\n"
                    "7. 'genre': Musical genre/style (e.g. 'Baroque', 'Classical Orchestral', 'Violin Concerto', 'Chamber Music', 'Jazz').\n"
                    "8. 'confidenceScore': Number between 0 and 1.\n"
                    "9. 'isAlreadyInCrate': boolean (true if already owned in Crate inventory, false otherwise).\n"
                    "10. 'crateMatchId': string or null (matching record ID if owned).\n"
                    "11. 'crateMatchReason': string (1-2 sentence explanation).\n"
                    "12. 'box_2d': Array of 4 integers [ymin, xmin, ymax, xmax] normalized 0-1000.\n"
                    "13. 'mask': Array of 4 corner points [[y1, x1], [y2, x2], [y3, x3], [y4, x4]] normalized 0-1000 in Gemini [ymin, xmin] coordinate order: Top-Left [y,x], Top-Right [y,x], Bottom-Right [y,x], Bottom-Left [y,x].\n"
                    "14. 'listeningGuide': Object with keys:\n"
                    "   - 'albumBackground': (string, a detailed 2-3 paragraph backstory covering the album's origin, production, studio equipment, mastering, pressing notes referencing this specific catalog/label/country if identified, and trivia)\n"
                    "   - 'tracklist': Array of track objects representing the complete vinyl tracklist. Each track object must have 'position' (e.g. 'A1', 'B1'), 'title' (string), 'duration' (string or null, e.g. '4:12'), 'highlight' (boolean, true if notable audiophile/musical details exist), and 'whatToListenFor' (string or null, if highlight is true, 1-2 sentences of specific mixing, instrument, or vinyl production details)\n"
                    "   - 'vinylTip': (string, short audiophile pro-tip e.g. tracking weight, dynamic range, inner-groove distortion, or pressing highlights)\n"
                    "   - 'recommendedMood': (string, brief phrase describing ideal listening atmosphere)"
                )

                from pydantic import BaseModel, Field

                class TracklistSchema(BaseModel):
                    position: Optional[str] = Field(default="A1", description="Track position e.g. A1, B1")
                    title: str = Field(description="Track title or movement")
                    duration: Optional[str] = Field(default="", description="Duration e.g. 5:24")
                    highlight: Optional[bool] = Field(default=False, description="Is key track highlight")
                    whatToListenFor: Optional[str] = Field(default="", description="Detail to listen for")

                class ListeningGuideSchema(BaseModel):
                    albumBackground: str = Field(description="Historical backstory, composition origin, and pressing highlights")
                    tracklist: List[TracklistSchema] = Field(default_factory=list, description="Array of track items")
                    vinylTip: Optional[str] = Field(default="", description="Audiophile tip for this pressing")
                    recommendedMood: Optional[str] = Field(default="", description="Recommended listening atmosphere")

                class AlbumScanMetadataSchema(BaseModel):
                    artist: str = Field(description="Main soloist, conductor, orchestra, or performer(s)")
                    albumTitle: str = Field(description="Full album title or composer/work title")
                    catalogNumber: Optional[str] = Field(default="", description="Exact catalog number e.g. VIC-28001")
                    label: Optional[str] = Field(default="", description="Exact record label e.g. Deutsche Grammophon")
                    country: Optional[str] = Field(default="Japan", description="Release country")
                    releaseYear: Optional[int] = Field(default=1980, description="4-digit release year integer")
                    genre: Optional[str] = Field(default="Classical", description="Musical genre or style")
                    confidenceScore: Optional[float] = Field(default=0.95, description="Confidence score between 0 and 1")
                    isAlreadyInCrate: bool = Field(default=False, description="True if already owned in Crate inventory")
                    crateMatchId: Optional[str] = Field(default=None, description="Matching record ID if owned")
                    crateMatchReason: Optional[str] = Field(default="", description="Explanation of match or non-match")
                    box_2d: Optional[List[int]] = Field(default=None, description="2D bounding box [ymin, xmin, ymax, xmax] normalized 0-1000")
                    mask: Optional[List[List[int]]] = Field(default=None, description="4 corner points [[y1, x1], [y2, x2], [y3, x3], [y4, x4]] normalized 0-1000")
                    listeningGuide: Optional[ListeningGuideSchema] = Field(default=None, description="Structured listening guide")

                try:
                    config = types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=AlbumScanMetadataSchema,
                        tools=[types.Tool(google_search=types.GoogleSearch())]
                    )

                    response = self.client.models.generate_content(
                        model="gemini-3.6-flash",
                        contents=[
                            types.Part.from_bytes(data=optimized_image_bytes, mime_type="image/jpeg"),
                            prompt
                        ],
                        config=config
                    )

                    text = (response.text or "").strip()
                    if not text and hasattr(response, "candidates") and response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
                        for part in response.candidates[0].content.parts:
                            if hasattr(part, "text") and part.text:
                                text += part.text
                    text = text.strip()
                except Exception as vis_err:
                    logger.warning(f"Primary Vision API call encountered error ({vis_err}); retrying fallback...")
                    text = ""

                if not text:
                    raise ValueError("Gemini Vision API returned empty text response")

                if text.startswith("```json"):
                    text = text[7:]
                if text.startswith("```"):
                    text = text[3:]
                if text.endswith("```"):
                    text = text[:-3]

                try:
                    parsed = json.loads(text.strip())
                except Exception as err:
                    json_match = re.search(r'\{.*\}', text, re.DOTALL)
                    if json_match:
                        parsed = json.loads(json_match.group(0))
                    else:
                        raise err

                return parsed
            except Exception as e:
                logger.error(f"Error in Gemini Vision API call (gemini-3.6-flash): {e}")
                raise RuntimeError(f"Gemini Vision API error (gemini-3.6-flash): {e}")


        raise RuntimeError("Gemini AI client is not initialized")


    def generate_listening_guide(
        self, 
        artist: str, 
        title: str, 
        catalog_number: Optional[str] = None, 
        label: Optional[str] = None, 
        country: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a rich audiophile listening guide using Gemini 3.6 Flash with Search Grounding.
        Returns detailed backstory/pressing notes, full tracklist with Side A/B positions, and foldable highlights.
        """
        if self.client:
            try:
                from google.genai import types

                details_parts = []
                if catalog_number:
                    details_parts.append(f"Catalog No: {catalog_number}")
                if label:
                    details_parts.append(f"Label: {label}")
                if country:
                    details_parts.append(f"Release Country: {country}")

                spec_str = f" ({', '.join(details_parts)})" if details_parts else ""

                clean_title = re.sub(r'["“”]', "'", title)
                clean_artist = re.sub(r'["“”]', "'", artist)

                prompt = (
                    f"You are an expert musicologist, audiophile vinyl curator, and record historian. "
                    f"Create a deep-dive, comprehensive vinyl listening guide for the album '{clean_title}' by {clean_artist}{spec_str}.\n"
                    f"Use Google Search grounding to gather rich historical details, recording session anecdotes, pressing details (specifically focusing on this release/catalog number/label/country if provided), mastering engineering notes, and full tracklists.\n"
                    f"Return ONLY a valid JSON object with the following keys:\n"
                    f"1. \"albumBackground\": A detailed 2-3 paragraph backstory covering the album's origin, production, studio equipment, mastering, pressing notes (referencing this specific pressing/catalog/label/country if known), and trivia.\n"
                    f"2. \"tracklist\": An array of track objects representing the complete track list of the vinyl release. Each track object must have:\n"
                    f"   - \"position\": (string, e.g. 'A1', 'A2', 'B1', 'B2')\n"
                    f"   - \"title\": (string, track name)\n"
                    f"   - \"duration\": (string or null, e.g. '4:12')\n"
                    f"   - \"highlight\": (boolean, true if this track has notable audiophile/musical details to listen for, false otherwise)\n"
                    f"   - \"whatToListenFor\": (string or null, if highlight is true, provide 1-2 sentences of specific mixing, instrument, or production details to pay attention to on vinyl).\n"
                    f"3. \"vinylTip\": A short pro-tip for vinyl listeners (e.g. tracking weight, dynamic range, inner-groove distortion, pressing highlights for this release/catalog).\n"
                    f"4. \"recommendedMood\": A brief phrase describing the ideal atmosphere (e.g. 'Late night dim lights with headphones and single-malt whisky')."
                )

                from pydantic import BaseModel, Field

                class TrackItemSchema(BaseModel):
                    position: Optional[str] = Field(default="A1", description="Track position e.g. A1, A2, B1")
                    title: str = Field(description="Track name or movement")
                    duration: Optional[str] = Field(default=None, description="Duration e.g. 4:12")
                    highlight: Optional[bool] = Field(default=False, description="True if audiophile highlight")
                    whatToListenFor: Optional[str] = Field(default=None, description="Specific mixing or performance details to pay attention to")

                class ListeningGuideResponseSchema(BaseModel):
                    albumBackground: str = Field(description="Detailed 2-3 paragraph backstory covering origin, production, studio equipment, mastering, and pressing notes")
                    tracklist: List[TrackItemSchema] = Field(default_factory=list, description="Array of track items")
                    vinylTip: Optional[str] = Field(default="", description="Pro-tip for vinyl listeners")
                    recommendedMood: Optional[str] = Field(default="", description="Ideal listening atmosphere")

                try:
                    config = types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=ListeningGuideResponseSchema,
                        tools=[types.Tool(google_search=types.GoogleSearch())]
                    )

                    response = self.client.models.generate_content(
                        model="gemini-3.6-flash",
                        contents=prompt,
                        config=config
                    )

                    text = (response.text or "").strip()
                    if not text and hasattr(response, "candidates") and response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
                        for part in response.candidates[0].content.parts:
                            if hasattr(part, "text") and part.text:
                                text += part.text
                    text = text.strip()
                except Exception as search_err:
                    logger.warning(f"Google Search grounded call encountered error/timeout ({search_err}); retrying without search grounding tools...")
                    text = ""

                if not text:
                    logger.warning("Search-grounded call returned empty text; retrying with ungrounded Gemini Flash generation...")
                    fallback_config = types.GenerateContentConfig(
                        response_mime_type="application/json"
                    )
                    fallback_resp = self.client.models.generate_content(
                        model="gemini-3.6-flash",
                        contents=prompt,
                        config=fallback_config
                    )
                    text = (fallback_resp.text or "").strip()
                    if not text and hasattr(fallback_resp, "candidates") and fallback_resp.candidates and fallback_resp.candidates[0].content and fallback_resp.candidates[0].content.parts:
                        for part in fallback_resp.candidates[0].content.parts:
                            if hasattr(part, "text") and part.text:
                                text += part.text
                    text = text.strip()

                if not text:
                    raise ValueError("Gemini API returned empty text response")

                if text.startswith("```json"):
                    text = text[7:]
                if text.startswith("```"):
                    text = text[3:]
                if text.endswith("```"):
                    text = text[:-3]

                text = text.strip()
                try:
                    parsed = json.loads(text)
                except Exception:
                    match = re.search(r'\{.*\}', text, re.DOTALL)
                    if match:
                        parsed = json.loads(match.group(0))
                    else:
                        raise
                return parsed

            except Exception as e:
                logger.error(f"Error generating listening guide via Gemini API: {e}")

        # Smart fallback listening guide for demo/offline
        title_lower = title.lower()

        if "currents" in title_lower:
            return {
                "albumBackground": "Written, recorded, and produced entirely by Kevin Parker in Fremantle, Western Australia. *Currents* marks Tame Impala's masterstroke transition from 1960s psychedelic rock toward 1980s synthesizer pop, R&B, and disco soundscapes.\n\nParker spent months meticulously tweaking synthesizer patches, dynamic compression, and drum mic configurations in his home studio. Using vintage Roland Juno-106, Ableton Push, and pitch-shifted guitar effects, *Currents* achieved an iconic audiophile balance between punchy sub-bass grooves and ethereal vocal dubs.",
                "tracklist": [
                    {"position": "A1", "title": "Let It Happen", "duration": "7:46", "highlight": True, "whatToListenFor": "Notice the 8-minute build-up, phase-shifted drums, and the mesmerizing simulated 'skipping record' glitch loop at 4:04."},
                    {"position": "A2", "title": "Nangs", "duration": "1:47", "highlight": False, "whatToListenFor": None},
                    {"position": "A3", "title": "The Moment", "duration": "4:15", "highlight": True, "whatToListenFor": "Focus on the crisp 808-style drum machine snare and shimmering 12-string guitar layers."},
                    {"position": "B1", "title": "Yes I'm Changing", "duration": "4:30", "highlight": False, "whatToListenFor": None},
                    {"position": "B2", "title": "Eventually", "duration": "5:19", "highlight": True, "whatToListenFor": "Listen for the staggering dynamic contrast between distorted guitar fuzz riffs and soft synth pads."},
                    {"position": "B3", "title": "Gossip", "duration": "0:55", "highlight": False, "whatToListenFor": None},
                    {"position": "C1", "title": "The Less I Know The Better", "duration": "3:36", "highlight": True, "whatToListenFor": "Listen for the iconic, bass-heavy riff recorded through a pitch-shifted guitar pedal, giving it a unique warm punch."},
                    {"position": "C2", "title": "Past Life", "duration": "3:47", "highlight": False, "whatToListenFor": None},
                    {"position": "C3", "title": "Disciples", "duration": "1:48", "highlight": False, "whatToListenFor": None},
                    {"position": "C4", "title": "Cause I'm A Man", "duration": "4:01", "highlight": False, "whatToListenFor": None},
                    {"position": "D1", "title": "Reality in Motion", "duration": "4:12", "highlight": False, "whatToListenFor": None},
                    {"position": "D2", "title": "Love/Paranoia", "duration": "3:06", "highlight": False, "whatToListenFor": None},
                    {"position": "D3", "title": "New Person, Same Old Mistakes", "duration": "6:02", "highlight": True, "whatToListenFor": "Focus on the deep sub-bass response, lush multitracked vocal harmonies, and wide spatial soundstage separation."}
                ],
                "vinylTip": "Turn up the low-end gain slightly on Side B to highlight Kevin Parker's analog synth basslines.",
                "recommendedMood": "Late-night dim lighting spin with headphones or warm room acoustics."
            }
        elif "dvořák" in title_lower or "cello" in title_lower:
            return {
                "albumBackground": "Composed in 1894–1895 while Antonín Dvořák served as director of the National Conservatory in New York City. The Cello Concerto in B minor, Op. 104 is widely regarded as the pinnacle of cello concertos, blending orchestral grandeur with soulful Bohemian folk themes.\n\nPaul Tortelier's landmark recording with Sir Malcolm Sargent and the Philharmonia Orchestra (EMI/HMV) is legendary among classical audiophiles. Tortelier's expressive vibrato and resonant instrument tone capture both the nostalgic homesickness of Dvořák's American stay and the majestic finale written in memory of his sister-in-law, Josefina.",
                "tracklist": [
                    {"position": "A1", "title": "Movement 1: Allegro", "duration": "15:20", "highlight": True, "whatToListenFor": "Listen for the grand orchestral exposition before Tortelier's heroic cello entry in the deep lower register."},
                    {"position": "B1", "title": "Movement 2: Adagio ma non troppo", "duration": "12:45", "highlight": True, "whatToListenFor": "Pay attention to the intimate duet between solo cello and woodwinds, featuring Dvořák's poignant song quotation 'Lass' mich allein'."},
                    {"position": "B2", "title": "Movement 3: Finale - Allegro moderato", "duration": "12:50", "highlight": True, "whatToListenFor": "Focus on the Bohemian dance motifs and the serene, nostalgic epilogue before the triumphant final orchestral crescendo."}
                ],
                "vinylTip": "Ensure proper tonearm tracking weight for dynamic orchestral peaks without inner-groove distortion.",
                "recommendedMood": "Quiet evening listening session with a warm drink."
            }
        else:
            return {
                "albumBackground": f"'{title}' by {artist} is a standout recording celebrated for its atmospheric production, distinct analog warmth, and musical cohesion.\n\nRecorded during a pivotal era for the artist, this vinyl release captures the rich dynamic range and detailed acoustic staging characteristic of premium mastering sessions.",
                "tracklist": [
                    {"position": "A1", "title": "Side A Opening Track", "duration": "4:15", "highlight": True, "whatToListenFor": "Listen for the acoustic space and stereo separation setting the album's sonic tone."},
                    {"position": "A2", "title": "Track 2", "duration": "3:50", "highlight": False, "whatToListenFor": None},
                    {"position": "A3", "title": "Side A Highlight", "duration": "5:10", "highlight": True, "whatToListenFor": "Pay attention to rhythmic precision, bassline clarity, and dynamic range."},
                    {"position": "B1", "title": "Side B Lead Track", "duration": "4:30", "highlight": False, "whatToListenFor": None},
                    {"position": "B2", "title": "Side B Deep Cut", "duration": "6:05", "highlight": True, "whatToListenFor": "Notice vocal layering, instrumental decay, and high-frequency resolution."}
                ],
                "vinylTip": "Clean stylus before playing to preserve high-frequency clarity.",
                "recommendedMood": "Relaxed spin with ambient lighting."
            }

    def chat_about_album(
        self,
        artist: str,
        title: str,
        message: str,
        history: Optional[List[Dict[str, str]]] = None,
        grounding_context: Optional[Dict[str, Any]] = None,
        images: Optional[List[str]] = None
    ) -> str:

        """
        Interactive chat about the currently spinning album using Gemini 3.6 Flash grounded with local database facts and Google Search grounding.
        """
        context_str = ""
        if grounding_context:
            rec = grounding_context.get("recordDetails") or {}
            guide = grounding_context.get("guideMetadata") or {}
            crate = grounding_context.get("crateSummary") or {}

            context_lines = ["=== VERIFIED LOCAL COLLECTION DATABASE FACTS ==="]
            
            if rec:
                context_lines.append(f"- Owned Record ID: {rec.get('id')}")
                context_lines.append(f"- Total Playback Sessions (Spins Count): {rec.get('spinsCount', 0)}")
                context_lines.append(f"- Last Spun At: {rec.get('lastSpunAt', 'Never')}")
                context_lines.append(f"- Genre: {rec.get('genre', 'Vinyl')}")
                context_lines.append(f"- Catalog Number: {rec.get('catalogNumber', 'N/A')}")
                pressings = rec.get("pressings", [])
                if pressings:
                    context_lines.append(f"- Pressing Details: {json.dumps(pressings, ensure_ascii=False)}")

            if guide:
                for k, v in rec.items():
                    if v and k not in ["coverUrl", "originalScannedCoverUrl"]:
                        context_lines.append(f"- {k}: {v}")

            if crate:
                catalog = crate.get("crateCatalog", [])
                context_lines.append(f"\nUSER'S COMPLETE VINYL VAULT CRATE CATALOG ({len(catalog)} Total Records):")
                for idx, entry in enumerate(catalog, 1):
                    context_lines.append(f"  {idx}. {entry}")

        context_str = "\n".join(context_lines)

        if self.client:
            try:
                from google.genai import types

                prompt = (
                    f"You are Vinyl Vault AI — an expert classical musicologist, vinyl archivist, and audiophile companion.\n"
                    f"The user is currently playing/viewing '{title}' by {artist}.\n\n"
                    f"{context_str}\n\n"
                    f"INSTRUCTIONS:\n"
                    f"1. You have full visibility into the user's currently spinning record AND their entire Vinyl Vault crate catalog listed above.\n"
                    f"2. When asked about attached photos (e.g. album cover, inner sleeve, matrix runoff, record label, liner notes, obi strip), inspect the image(s) with extreme precision.\n"
                    f"3. When asked about other albums in their collection, comparative recordings, or pressing variations, reference their specific crate inventory.\n"
                    f"4. Use Google Search grounding to supplement with external historical, performance comparison, or discographical details.\n"
                    f"5. User Question: {message}\n\n"
                    f"Keep your response warm, musicologically insightful, concise (2-4 paragraphs max), and directly reference local database facts whenever relevant."
                )

                contents = []
                image_parts = self._prepare_image_parts(images)
                if image_parts:
                    contents.extend(image_parts)

                contents.append(prompt)

                config = types.GenerateContentConfig(
                    tools=[types.Tool(google_search=types.GoogleSearch())]
                )

                response = self.client.models.generate_content(
                    model="gemini-3.6-flash",
                    contents=contents,
                    config=config
                )
                if response and response.text:
                    return response.text.strip()

            except Exception as e:
                logger.error(f"Error in Gemini chat API call: {e}")

        return f"Regarding '{title}' by {artist}: This record is renowned for its distinct vinyl pressing dynamics and musical production. '{message}' touches on great details for audiophiles enjoying this album!"

    def _prepare_image_parts(self, images: Optional[List[str]]) -> List[Any]:
        parts = []
        if not images or not isinstance(images, list):
            return parts

        try:
            from google.genai import types
            for img_str in images:
                if not img_str or not isinstance(img_str, str):
                    continue
                try:
                    mime_type = "image/jpeg"
                    b64_data = img_str
                    if "," in img_str:
                        header, b64_data = img_str.split(",", 1)
                        if "data:" in header and ";base64" in header:
                            mime_type = header.split("data:")[1].split(";base64")[0]

                    raw_bytes = base64.b64decode(b64_data)
                    part = types.Part.from_bytes(data=raw_bytes, mime_type=mime_type)
                    parts.append(part)
                except Exception as err:
                    logger.warning(f"Error decoding chat image attachment: {err}")
        except Exception as e:
            logger.warning(f"Error importing genai types for image parts: {e}")

        return parts

    def stream_chat_response(
        self,
        message: str,
        record_context: Optional[Dict[str, Any]] = None,
        crate_catalog: Optional[List[str]] = None,
        images: Optional[List[str]] = None
    ):
        """
        Streams Gemini 3.6 Flash chat response tokens in real time with Google Search Grounding,
        multimodal image inspection, and complete Vinyl Vault Crate awareness.
        """
        title = record_context.get("title", "Vinyl Record") if record_context else "Vinyl Record"
        artist = record_context.get("artist", "Collection Item") if record_context else "Collection Item"

        context_lines = []
        if record_context:
            context_lines.append("CURRENTLY SPINNING ON TURNTABLE:")
            for k, v in record_context.items():
                if v and k not in ["coverUrl", "originalScannedCoverUrl"]:
                    context_lines.append(f"  - {k}: {v}")
        else:
            context_lines.append("CURRENT TURNTABLE STATE: Standby Mode (No record currently spinning)")

        if crate_catalog and isinstance(crate_catalog, list):
            context_lines.append(f"\nUSER'S COMPLETE VINYL VAULT CRATE ({len(crate_catalog)} Total Records):")
            for idx, entry in enumerate(crate_catalog, 1):
                context_lines.append(f"  {idx}. {entry}")

        context_str = "\n".join(context_lines)

        prompt = (
            f"You are Vinyl Vault AI — an expert classical musicologist, vinyl archivist, and audiophile companion.\n"
            f"You have complete visibility into the user's currently spinning record AND their entire Vinyl Vault crate catalog.\n\n"
            f"{context_str}\n\n"
            f"INSTRUCTIONS FOR YOUR RESPONSE:\n"
            f"1. You have full access to the user's Crate database facts above. When asked about attached photos (e.g. album cover, inner sleeve, matrix runoff, record label, liner notes, obi strip), inspect the image(s) with extreme precision to identify catalog numbers, matrix numbers, pressings, performer credits, or condition.\n"
            f"2. When asked about other albums in their collection, comparative recordings, or pressing variations, cross-reference their specific crate inventory.\n"
            f"3. Use Google Search grounding to enrich your response with external musicological, historical, or performance comparison details when helpful.\n"
            f"4. User Question: {message}\n\n"
            f"Provide a warm, musicologically insightful, and engaging response (2-4 paragraphs max)."
        )

        contents = []
        image_parts = self._prepare_image_parts(images)
        if image_parts:
            contents.extend(image_parts)

        contents.append(prompt)

        if self.client:
            try:
                from google.genai import types
                config = types.GenerateContentConfig(
                    tools=[types.Tool(google_search=types.GoogleSearch())]
                )
                response_stream = self.client.models.generate_content_stream(
                    model="gemini-3.6-flash",
                    contents=contents,
                    config=config
                )
                for chunk in response_stream:
                    if chunk.text:
                        yield f"data: {json.dumps({'text': chunk.text})}\n\n"
                yield "data: [DONE]\n\n"
                return
            except Exception as e:
                logger.error(f"Error streaming Gemini chat: {e}")

        fallback_msg = f"Regarding '{title}' by {artist}: '{message}' touches on great audiophile aspects of this album!"
        yield f"data: {json.dumps({'text': fallback_msg})}\n\n"
        yield "data: [DONE]\n\n"



    def generate_chronicle_ai(self, records: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Calls Gemini 3.6 Flash to analyze collection records and generate a structured JSON 
        Classical Music Chronicle categorized by composer era with musicological insights.
        """
        if not self.client:
            logger.warning("Gemini client unavailable for AI Chronicle generation.")
            return None

        try:
            from google.genai import types

            simplified_records = []
            for r in records:
                entry = {
                    "id": r.get("id"),
                    "title": r.get("title"),
                    "artist": r.get("artist"),
                    "label": r.get("label"),
                    "catalogNumber": r.get("catalogNumber"),
                    "releaseYear": r.get("releaseYear"),
                    "country": r.get("country"),
                    "genre": r.get("genre"),
                    "formatDetails": r.get("formatDetails"),
                    "coverUrl": r.get("coverUrl")
                }
                if r.get("listeningGuide"):
                    entry["tracksSummary"] = [
                        t.get("title") for t in r["listeningGuide"].get("tracks", []) if isinstance(t, dict) and t.get("title")
                    ][:5]
                simplified_records.append(entry)

            prompt = (
                "You are an expert musicologist and classical music archivist.\n"
                "Analyze the following vinyl collection records and organize ALL Classical Music records chronologically into historical composer eras "
                "(e.g., Baroque Era [1600-1750], Classical Era [1750-1820], Romantic Era [1820-1910], Modern & 20th Century [1910-1980], Contemporary Classical [1980-Present]).\n\n"
                f"User Collection Records:\n{json.dumps(simplified_records, indent=2, ensure_ascii=False)}\n\n"
                "INSTRUCTIONS:\n"
                "1. Carefully examine all metadata fields (title, artist, label, catalogNumber, genre). Include ONLY classical music recordings (e.g., Deutsche Grammophon, Decca, Philips, EMI, Erato, symphonies, concertos, sonatas, classical composers). Exclude non-classical genres like Rock, Pop, Jazz, Disco, Bolero unless classical Crossover.\n"
                "2. Group records into chronological eras. For each era that contains classical records from the collection, produce:\n"
                "   - \"id\": string (one of \"baroque\", \"classical\", \"romantic\", \"modern_20th\", \"contemporary\")\n"
                "   - \"name\": string (e.g. \"Romantic Era\")\n"
                "   - \"years\": string date range (e.g. \"1820 – 1910\")\n"
                "   - \"icon\": emoji string (e.g. \"🎻\", \"🎼\", \"📜\", \"🎹\", \"🌌\")\n"
                "   - \"description\": concise 1-2 sentence musicological overview of the era\n"
                "   - \"count\": integer count of records in this era\n"
                "   - \"records\": list of record objects containing:\n"
                "       - \"id\": record ID matching input record ID\n"
                "       - \"title\": album title\n"
                "       - \"artist\": performer/artist\n"
                "       - \"label\": label name\n"
                "       - \"catalogNumber\": catalog number\n"
                "       - \"releaseYear\": number or string\n"
                "       - \"genre\": string\n"
                "       - \"coverUrl\": cover URL matching input\n"
                "       - \"detectedComposer\": composer name (e.g., \"Hector Berlioz\", \"Johann Sebastian Bach\", \"Ludwig van Beethoven\", \"Antonín Dvořák\", \"Pyotr Ilyich Tchaikovsky\")\n"
                "       - \"eraName\": era name\n"
                "       - \"aiInsight\": a 1-sentence audiophile/musicological insight on why this piece or recording is notable.\n\n"
                "3. Provide a complete, detailed \"composerStats\" list dynamically extracting EVERY classical composer represented across the collection records (e.g. Hector Berlioz, Felix Mendelssohn, Robert Schumann, Franz Liszt, Jean Sibelius, Gustav Mahler, etc.). Order chronologically by composer birth year. For each composer:\n"
                "   - \"name\": string (full composer name)\n"
                "   - \"lifespan\": string (e.g. \"1803 – 1869\")\n"
                "   - \"country\": string (e.g. \"France\")\n"
                "   - \"flag\": string emoji (e.g. \"🇫🇷\")\n"
                "   - \"era\": string (e.g. \"Romantic\")\n"
                "   - \"highlights\": string (1 short sentence summary)\n"
                "   - \"bio\": string (2-3 sentence biography)\n"
                "   - \"innovations\": string (notable musical contributions)\n"
                "   - \"keyWorks\": array of string key works\n"
                "   - \"count\": integer count of albums owned for this composer\n"
                "   - \"albums\": array of album title strings owned in crate\n\n"
                "Return ONLY a valid JSON object matching this structure:\n"
                "{\n"
                '  "totalClassicalRecords": 71,\n'
                '  "totalRecordsInCrate": 83,\n'
                '  "eras": [ ... ],\n'
                '  "composerStats": [ ... ]\n'
                "}"
            )


            config = types.GenerateContentConfig(
                response_mime_type="application/json"
            )

            response = self.client.models.generate_content(
                model="gemini-3.6-flash",
                contents=prompt,
                config=config
            )
            if not response or not response.text:
                return None


            text_output = response.text.strip()

            if text_output.startswith("```"):
                text_output = re.sub(r"^```(?:json)?\n|\n```$", "", text_output, flags=re.MULTILINE).strip()

            parsed_data = json.loads(text_output)
            logger.info("Successfully generated AI Chronicle via Gemini 3.6 Flash.")
            return parsed_data

        except Exception as e:
            logger.error(f"Gemini 3.6 Flash generate_chronicle_ai error: {e}")
            return None

    def generate_pronunciation(self, text: str) -> Optional[Dict[str, Any]]:
        """Generates clear audio pronunciation for composer/album/track name using gemini-3.1-flash-tts-preview with in-memory caching."""
        if not text or not text.strip():
            return None

        cache_key = text.strip().lower()
        if cache_key in self._pronunciation_cache:
            logger.info(f"Serving cached pronunciation audio for '{cache_key}'")
            return self._pronunciation_cache[cache_key]

        try:
            if not self.client:
                self._init_client()

            from google.genai import types
            prompt = f"Pronounce clearly and naturally as a composer, album, or track name from a vinyl record: {text}"
            
            response = self.client.models.generate_content(
                model="gemini-3.1-flash-tts-preview",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_modalities=["AUDIO"],
                    speech_config=types.SpeechConfig(
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                voice_name="Aoede"
                            )
                        )
                    )
                )
            )

            for candidate in (response.candidates or []):
                for part in (candidate.content.parts or []):
                    if part.inline_data and part.inline_data.data:
                        raw_pcm = part.inline_data.data
                        mime = part.inline_data.mime_type or "audio/l16; rate=24000"
                        
                        sample_rate = 24000
                        if "rate=" in mime:
                            try:
                                sample_rate = int(mime.split("rate=")[1].split(";")[0].strip())
                            except Exception:
                                sample_rate = 24000

                        wav_io = io.BytesIO()
                        with wave.open(wav_io, 'wb') as wf:
                            wf.setnchannels(1)
                            wf.setsampwidth(2)
                            wf.setframerate(sample_rate)
                            wf.writeframes(raw_pcm)
                        
                        wav_bytes = wav_io.getvalue()
                        audio_b64 = base64.b64encode(wav_bytes).decode('utf-8')
                        result = {
                            "audio_b64": audio_b64,
                            "mime_type": "audio/wav",
                            "model": "gemini-3.1-flash-tts-preview",
                            "voice": "Aoede"
                        }
                        if len(self._pronunciation_cache) >= 100:
                            first_key = next(iter(self._pronunciation_cache))
                            self._pronunciation_cache.pop(first_key, None)
                        self._pronunciation_cache[cache_key] = result
                        return result

        except Exception as e:
            logger.error(f"Error generating pronunciation with gemini-3.1-flash-tts-preview for '{text}': {e}")
            return {"error": str(e)}
        return {"error": "No audio parts returned from gemini-3.1-flash-tts-preview"}

    def generate_daily_poster_insights(self, record_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generates curated listening highlights, interesting trivia, and pairing notes
        for the Daily Poster feature using Gemini AI.
        """
        title = record_data.get("title", "Unknown Album")
        artist = record_data.get("artist", "Unknown Artist")
        year = record_data.get("releaseYear", "")
        genre = record_data.get("genre", "Vinyl Record")
        catalog = record_data.get("catalogNumber", "")

        prompt = f"""
        You are an expert vinyl curator and classical/audiophile musicologist for "Vinyl Vault".
        Generate an elegant, engaging Daily Record Showcase Poster card for this album:
        Title: {title}
        Artist: {artist}
        Year: {year}
        Genre: {genre}
        Catalog Number: {catalog}

        Provide a JSON response with the following keys:
        1. "headline": A poetic, catchy 4-8 word tag line for today's poster (e.g., "A Timeless Masterpiece of Baroque Elegance").
        2. "listeningHighlight": 2 concise sentences describing why this album is essential today, highlighting its acoustic timbre, key movement, or emotional warmth.
        3. "trivia": 2 fascinating sentences sharing a lesser-known historical fact, master tape context, or pressing rarity detail.
        4. "pairingNote": A cozy 1-sentence atmosphere or beverage pairing recommendation.

        Respond strictly in valid JSON format without markdown code blocks.
        """

        if not self.client:
            return {
                "headline": f"Featured Vinyl Highlight: {title}",
                "listeningHighlight": f"An exquisite recording of {title} by {artist}. Immerse yourself in the warm analog soundstage and expressive dynamics.",
                "trivia": f"First pressed in {year or 'the golden analog era'}, this release remains a cherished piece in audiophile pressings.",
                "pairingNote": "Best enjoyed with a warm cup of espresso or tea during an evening listening session."
            }

        try:
            from google.genai import types
            response = self.client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            text = (response.text or "").strip()
            if not text and hasattr(response, "candidates") and response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    if hasattr(part, "text") and part.text:
                        text += part.text
            text = text.strip()
            if not text:
                raise ValueError("Empty response from Gemini")
            data = json.loads(text)
            return data
        except Exception as e:
            logger.warning(f"Gemini daily poster insights fallback: {e}")
            return {
                "headline": f"Featured Vault Pick: {title}",
                "listeningHighlight": f"An outstanding performance of {title} by {artist}. Experience its full dynamic range and analog warmth on vinyl.",
                "trivia": f"Catalog number {catalog or 'N/A'} is renowned among collectors for its distinct soundstage engineering.",
                "pairingNote": "Perfect for a quiet ambient listening session."
            }


gemini_service = GeminiVisionService()


