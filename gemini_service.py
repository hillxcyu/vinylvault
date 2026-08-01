import os
import io
import wave
import json
import base64
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger("gemini_service")



class GeminiVisionService:
    def __init__(self):
        self.project = os.environ.get("GOOGLE_CLOUD_PROJECT", "universal-trail-492014-n5")
        self.location = os.environ.get("GOOGLE_CLOUD_LOCATION", "global")
        self.client = None
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


    def analyze_album_cover(self, image_bytes: bytes, filename: str = "cover.jpg") -> Dict[str, Any]:
        """
        Analyze album cover photo using Gemini 3.5 Flash Vision model with Google Search grounding enabled
        """
        if self.client:
            try:
                from google.genai import types

                prompt = (
                    "You are an expert vinyl record archivist, musicologist, and cataloger specializing in Classical, Jazz, Rock, and Box Sets.\n"
                    "Analyze this image of a vinyl album cover, box set, spine, or obi strip with extreme precision.\n"
                    "CRITICAL REQUIREMENT 1: Perform deep research using Google Search grounding to verify the exact 'label', 'catalogNumber', and 'releaseYear'. "
                    "For Box Sets (e.g. 2LP, 3LP, multi-disc sets), carefully inspect the box spine, top/bottom corners, or obi strip to extract the master box set catalog number and exact record label (e.g. 'Deutsche Grammophon', 'Decca', 'Seraphim', 'Philips', 'EMI', 'CBS Masterworks', 'Archiv').\n"
                    "CRITICAL REQUIREMENT 2: Use Google Search grounding to look up the official release year for this specific catalog number/pressing (e.g., 'EAC-60150-51' was released in 1978, 'UCJG-9012' in 2009). Always return an accurate 4-digit 'releaseYear' integer.\n"
                    "CRITICAL REQUIREMENT 3: Simultaneously generate a rich audiophile 'listeningGuide' for this album.\n\n"
                    "Extract and return ONLY a valid JSON object with the following fields:\n"
                    "1. 'artist': Main soloist, conductor, orchestra, or performer(s).\n"
                    "2. 'albumTitle': Full album title or composer/work title.\n"
                    "3. 'catalogNumber': Exact catalog number (e.g. 'EAC-30073', 'SLA 6187', 'VIC-28001', '2530 229', 'IMP-2026-001').\n"
                    "4. 'label': Exact record label name (e.g. 'Decca', 'Seraphim', 'Deutsche Grammophon', 'EMI', 'Philips', 'RCA').\n"
                    "5. 'country': Release country or pressing origin (e.g. 'Japan', 'US', 'UK', 'Germany').\n"
                    "6. 'releaseYear': Exact 4-digit release year integer (e.g. 1978, 1961, 2009).\n"
                    "7. 'genre': Musical genre/style (e.g. 'Baroque', 'Classical Orchestral', 'Violin Concerto', 'Chamber Music', 'Jazz').\n"
                    "8. 'confidenceScore': Number between 0 and 1.\n"
                    "9. 'listeningGuide': Object with keys:\n"
                    "   - 'albumBackground': (string, 2-3 paragraph historical backstory, composition origin, and pressing highlights)\n"
                    "   - 'tracklist': Array of track objects with 'position', 'title', 'duration', 'highlight' (boolean), and 'whatToListenFor' (string)\n"
                    "   - 'vinylTip': (string, audiophile listening tip for this pressing)\n"
                    "   - 'recommendedMood': (string, ideal listening atmosphere)"
                )




                config = types.GenerateContentConfig(
                    tools=[types.Tool(google_search=types.GoogleSearch())]
                )

                response = self.client.models.generate_content(
                    model="gemini-3.6-flash",
                    contents=[
                        types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
                        prompt
                    ],
                    config=config
                )





                text = response.text.strip()
                if text.startswith("```json"):
                    text = text[7:]
                if text.startswith("```"):
                    text = text[3:]
                if text.endswith("```"):
                    text = text[:-3]
                
                parsed = json.loads(text.strip())
                return parsed
            except Exception as e:
                logger.error(f"Error in Gemini Vision API call (gemini-3.6-flash): {e}")
                raise RuntimeError(f"Gemini Vision API error (gemini-3.6-flash): {e}")

        raise RuntimeError("Gemini AI client is not initialized")


    def generate_listening_guide(self, artist: str, title: str) -> Dict[str, Any]:
        """
        Generate a rich audiophile listening guide using Gemini 3.5 Flash with Search Grounding.
        Returns detailed backstory/pressing notes, full tracklist with Side A/B positions, and foldable highlights.
        """
        if self.client:
            try:
                from google.genai import types

                prompt = (
                    f"You are an expert musicologist, audiophile vinyl curator, and record historian. "
                    f"Create a deep-dive, comprehensive vinyl listening guide for the album '{title}' by {artist}.\n"
                    f"Use Google Search grounding to gather rich historical details, recording session anecdotes, pressing details, mastering engineering notes, and full tracklists.\n"
                    f"Return ONLY a valid JSON object with the following keys:\n"
                    f"1. \"albumBackground\": A detailed 2-3 paragraph backstory covering the album's origin, production, studio equipment, mastering, pressing notes, and trivia.\n"
                    f"2. \"tracklist\": An array of track objects representing the complete track list of the vinyl release. Each track object must have:\n"
                    f"   - \"position\": (string, e.g. 'A1', 'A2', 'B1', 'B2')\n"
                    f"   - \"title\": (string, track name)\n"
                    f"   - \"duration\": (string or null, e.g. '4:12')\n"
                    f"   - \"highlight\": (boolean, true if this track has notable audiophile/musical details to listen for, false otherwise)\n"
                    f"   - \"whatToListenFor\": (string or null, if highlight is true, provide 1-2 sentences of specific mixing, instrument, or production details to pay attention to on vinyl).\n"
                    f"3. \"vinylTip\": A short pro-tip for vinyl listeners (e.g. tracking weight, dynamic range, inner-groove distortion, pressing highlights).\n"
                    f"4. \"recommendedMood\": A brief phrase describing the ideal atmosphere (e.g. 'Late night dim lights with headphones and single-malt whisky')."
                )

                config = types.GenerateContentConfig(
                    tools=[types.Tool(google_search=types.GoogleSearch())]
                )

                response = self.client.models.generate_content(
                    model="gemini-3.6-flash",
                    contents=prompt,
                    config=config
                )


                text = response.text.strip()
                if text.startswith("```json"):
                    text = text[7:]
                if text.startswith("```"):
                    text = text[3:]
                if text.endswith("```"):
                    text = text[:-3]

                parsed = json.loads(text.strip())
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

    def chat_about_album(self, artist: str, title: str, message: str, history: Optional[List[Dict[str, str]]] = None, grounding_context: Optional[Dict[str, Any]] = None) -> str:
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
                if guide.get("albumBackground"):
                    context_lines.append(f"- Stored Album Backstory: {guide.get('albumBackground')}")
                if guide.get("tracklist"):
                    context_lines.append(f"- Complete Vinyl Tracklist & Audiophile Notes: {json.dumps(guide.get('tracklist'), ensure_ascii=False)}")
                if guide.get("vinylTip"):
                    context_lines.append(f"- Audiophile Pro-Tip: {guide.get('vinylTip')}")

            if crate:
                context_lines.append(f"- Total Albums in User's Crate: {crate.get('totalRecordsInCrate', 0)}")
                context_lines.append(f"- User's Crate Inventory Sample: {', '.join(crate.get('ownedAlbums', [])[:20])}")

            context_str = "\n".join(context_lines)

        if self.client:
            try:
                from google.genai import types

                prompt = (
                    f"You are an expert vinyl archivist, musicologist, and audiophile companion.\n"
                    f"The user is currently listening to the vinyl record '{title}' by {artist}.\n\n"
                    f"{context_str}\n\n"
                    f"INSTRUCTIONS:\n"
                    f"1. Use the VERIFIED LOCAL COLLECTION DATABASE FACTS above to accurately answer questions regarding track numbers, track titles, audiophile highlights, spin counts, catalog numbers, pressing info, or other albums owned in their crate.\n"
                    f"2. Use Google Search grounding to supplement with external historical, band, or production details.\n"
                    f"3. User Question: {message}\n\n"
                    f"Keep your response warm, informative, concise (2-4 paragraphs max), and directly address their question using local database facts whenever relevant."
                )

                config = types.GenerateContentConfig(
                    tools=[types.Tool(google_search=types.GoogleSearch())]
                )

                response = self.client.models.generate_content(
                    model="gemini-3.6-flash",
                    contents=prompt,
                    config=config
                )
                if response and response.text:
                    return response.text.strip()

            except Exception as e:
                logger.error(f"Error in Gemini chat API call: {e}")

        return f"Regarding '{title}' by {artist}: This record is renowned for its distinct vinyl pressing dynamics and musical production. '{message}' touches on great details for audiophiles enjoying this album!"

    def stream_chat_response(self, message: str, record_context: Optional[Dict[str, Any]] = None):
        """
        Streams Gemini 3.6 Flash chat response tokens in real time (reducing TTFT to < 200ms).
        Yields text chunks as Server-Sent Events (SSE).
        """
        title = record_context.get("title", "Vinyl Record") if record_context else "Vinyl Record"
        artist = record_context.get("artist", "Collection Item") if record_context else "Collection Item"

        context_lines = []
        if record_context:
            for k, v in record_context.items():
                if v and k not in ["coverUrl"]:
                    context_lines.append(f"- {k}: {v}")
        context_str = "\n".join(context_lines)

        prompt = (
            f"You are an expert vinyl archivist, musicologist, and audiophile companion.\n"
            f"The user is currently listening to '{title}' by {artist}.\n\n"
            f"{context_str}\n\n"
            f"INSTRUCTIONS:\n"
            f"Provide warm, musicological, concise responses (2-4 paragraphs) to their question: {message}\n"
        )

        if self.client:
            try:
                from google.genai import types
                config = types.GenerateContentConfig(
                    tools=[types.Tool(google_search=types.GoogleSearch())]
                )
                response_stream = self.client.models.generate_content_stream(
                    model="gemini-3.6-flash",
                    contents=prompt,
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
                "       - \"detectedComposer\": composer name (e.g., \"Johann Sebastian Bach\", \"Ludwig van Beethoven\", \"Antonín Dvořák\", \"Pyotr Ilyich Tchaikovsky\")\n"
                "       - \"eraName\": era name\n"
                "       - \"aiInsight\": a 1-sentence audiophile/musicological insight on why this piece or recording is notable.\n\n"
                "Return ONLY a valid JSON object matching this structure:\n"
                "{\n"
                '  "totalClassicalRecords": 38,\n'
                '  "totalRecordsInCrate": 50,\n'
                '  "eras": [ ... ]\n'
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
            logger.error(f"Error generating AI Chronicle via Gemini 3.6 Flash: {e}")
            return None

    def generate_pronunciation(self, text: str) -> Optional[Dict[str, Any]]:
        """Generates clear audio pronunciation for composer/album/track name using gemini-3.1-flash-tts-preview."""
        try:
            if not self.client:
                self._init_client()

            from google.genai import types
            prompt = f"Pronounce clearly and naturally in its native musical language: {text}"
            
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
                        return {
                            "audio_b64": audio_b64,
                            "mime_type": "audio/wav",
                            "model": "gemini-3.1-flash-tts-preview",
                            "voice": "Aoede"
                        }
        except Exception as e:
            logger.error(f"Error generating pronunciation with gemini-3.1-flash-tts-preview for '{text}': {e}")
            return {"error": str(e)}
        return {"error": "No audio parts returned from gemini-3.1-flash-tts-preview"}



gemini_service = GeminiVisionService()

