# Gemini API Integration Catalog

This document maintains the canonical catalog of all Google Gemini API calls utilized within the **Vinyl Vault** application codebase (primarily defined in [`gemini_service.py`](file:///Users/hill/src/vinylvault/gemini_service.py)).

---

## Summary Table

| # | Feature / Method Name | Model | Thinking Config | MIME-Type / Modality | Tools & Grounding | Prompt Summary & Purpose |
|---|---|---|---|---|---|---|
| **1** | **Scan Corner Detection (Call A)**<br>[`get_album_segmentation_corners`](file:///Users/hill/src/vinylvault/gemini_service.py#L129) | `gemini-3.7-flash` | `thinking_level="LOW"` | `application/json` | None | Detects 4 physical outer corner coordinates (`mask`) and bounding box (`box_2d`) of the vinyl album cover for automatic perspective deskewing. |
| **2** | **Fast Duplicate Check (Call B)**<br>[`check_album_duplicate`](file:///Users/hill/src/vinylvault/gemini_service.py#L199) | `gemini-3.7-flash` | `thinking_level="LOW"` | `application/json` | None | Performs rapid OCR on album title & artist and compares against user's Crate inventory to immediately flag duplicate pressings. |
| **3** | **Fast Release Metadata (Call C)**<br>[`extract_album_metadata`](file:///Users/hill/src/vinylvault/gemini_service.py#L287) | `gemini-3.7-flash` | `thinking_level="LOW"` | `application/json` | None *(No Google Search)* | Extracts core album metadata (`artist`, `albumTitle`, `catalogNumber`, `label`, `country`, `releaseYear`, `genre`) directly from visible cover artwork and internal model knowledge with ultra-fast latency (~1s). Returns `null` for fields not visible or known. |
| **4** | **Album Cover Analysis**<br>[`analyze_album_cover`](file:///Users/hill/src/vinylvault/gemini_service.py#L367) | `gemini-3.7-flash` | `thinking_level="LOW"` | `application/json` | None *(No Google Search)* | Performs fast visual release metadata extraction, corner segmentation, and fuzzy semantic crate inventory matching for manual/single scan requests. Returns `null` for unknown metadata fields. |
| **5** | **Audiophile Listening Guide & Metadata Enrichment**<br>[`generate_listening_guide`](file:///Users/hill/src/vinylvault/gemini_service.py#L536) | `gemini-3.7-flash` | Default *(Standard reasoning)* | `application/json` | Google Search Grounding (`google_search`) | Deep-dive research utilizing default reasoning level and Google Search grounding. Generates recording history (`albumBackground`), Side A/B tracklists, pressing tips (`vinylTip`), and completes any missing album metadata fields (`enrichedMetadata`: `releaseYear`, `catalogNumber`, `label`, `country`, `genre`) which auto-populates back to Firestore. |
| **6** | **AI Chat Companion**<br>[`chat_about_album`](file:///Users/hill/src/vinylvault/gemini_service.py#L680) & [`stream_chat_response`](file:///Users/hill/src/vinylvault/gemini_service.py#L793) | `gemini-3.7-flash` | Default *(Standard reasoning)* | `text/plain`<br>*(Streaming: `text/event-stream`)* | Google Search Grounding (`google_search`) | Interactive musicologist chatbot with full visibility into the currently spinning record, attached images (labels/matrix/obi), and complete Crate inventory. |
| **7** | **Classical Music Chronicle**<br>[`generate_chronicle_ai`](file:///Users/hill/src/vinylvault/gemini_service.py#L867) | `gemini-3.7-flash` | `thinking_level="HIGH"` | `application/json` | None | Categorizes all collection records into chronological composer eras (Baroque, Classical, Romantic, Modern 20th Century, Contemporary) with composer biographies, birth years, and audiophile insights using deep reasoning (`thinking_level="HIGH"`). |
| **8** | **Audio Pronunciation (TTS)**<br>[`generate_pronunciation`](file:///Users/hill/src/vinylvault/gemini_service.py#L973) | `gemini-3.1-flash-tts-preview` | N/A | `audio/l16`<br>*(Decoded to `audio/wav`)*<br>`response_modalities=["AUDIO"]` | Voice: `"Aoede"` | Text-to-speech pronunciation for classical composers, album titles, or track names: *"Pronounce clearly and naturally as a composer, album, or track name..."* |
| **9** | **Daily Record Poster Showcase**<br>[`generate_daily_poster_insights`](file:///Users/hill/src/vinylvault/gemini_service.py#L1044) | `gemini-3.7-flash` | Default *(Standard reasoning)* | `application/json` | None | Generates poetic showcase poster headlines, essential listening highlights, master tape historical trivia, and atmosphere/beverage pairing notes. |

---

## Architectural & Performance Notes

### 1. Two-Stage Metadata Architecture
- **Stage 1 (Fast Cover Scan)**: During initial cover scanning (`/api/scan`, `/api/scan/deep-metadata`), Google Search grounding is intentionally disabled. Gemini relies on visual OCR of the jacket/spine/obi and internal model knowledge. If a field is not printed or known, it is set to `null` to guarantee ~1s response latency.
- **Stage 2 (Deep Research & Enrichment)**: When generating an Audiophile Listening Guide (`/api/listening-guide`), Gemini uses Google Search Grounding (`google_search`). It researches the exact pressing history, fills in missing catalog fields (`releaseYear`, `catalogNumber`, `label`, `country`, `genre`), and auto-enriches the record in Firestore.

### 2. Thinking Level Configuration
- **Fast Scans**: `thinking_config=types.ThinkingConfig(thinking_level="LOW")` reduces reasoning overhead on `gemini-3.7-flash` for ~1s real-time camera response.
- **Classical Music Chronicle**: `thinking_config=types.ThinkingConfig(thinking_level="HIGH")` enables thorough reasoning across the entire collection to synthesize complex composer lifespans, historical eras, and musicological insights.

### 3. Multi-Modal Vision Inspection
The Chat Companion supports multi-modal image inputs (album covers, obi strips, matrix runout etchings, liner notes). Images are converted to base64 `inlineData` parts prior to dispatching to Gemini.
