# Gemini API Integration Catalog

This document maintains the canonical catalog of all Google Gemini API calls utilized within the **Vinyl Vault** application codebase (primarily defined in [`gemini_service.py`](file:///Users/hill/src/vinylvault/gemini_service.py)).

---

## Summary Table

| # | Feature / Method Name | Model | Thinking Config | MIME-Type / Modality | Tools & Grounding | Prompt Summary & Purpose |
|---|---|---|---|---|---|---|
| **1** | **Scan Corner Detection (Call A)**<br>[`get_album_segmentation_corners`](file:///Users/hill/src/vinylvault/gemini_service.py#L129) | `gemini-3.6-flash` | `thinking_level="minimal"` | `application/json` | None | Detects 4 physical outer corner coordinates (`mask`) and bounding box (`box_2d`) of the vinyl album cover for automatic perspective deskewing. |
| **2** | **Fast Duplicate Check (Call B)**<br>[`check_album_duplicate`](file:///Users/hill/src/vinylvault/gemini_service.py#L199) | `gemini-3.6-flash` | `thinking_level="minimal"` | `application/json` | None | Performs rapid OCR on album title & artist and compares against user's Crate inventory to immediately flag duplicate pressings. |
| **3** | **Fast Release Metadata (Call C)**<br>[`extract_album_metadata`](file:///Users/hill/src/vinylvault/gemini_service.py#L287) | `gemini-3.6-flash` | `thinking_level="minimal"` | `application/json` | Google Search Grounding (`google_search`) | Extracts core album metadata (`artist`, `albumTitle`, `catalogNumber`, `label`, `country`, `releaseYear`, `genre`, `confidenceScore`) with minimal reasoning latency (~1s). Uses Google Search grounding if catalog number or pressing info is not clearly visible on cover. |
| **4** | **Album Cover Analysis**<br>[`analyze_album_cover`](file:///Users/hill/src/vinylvault/gemini_service.py#L367) | `gemini-3.6-flash` | `thinking_level="minimal"` | `application/json` | None | Performs release metadata extraction and fuzzy semantic crate inventory matching for manual/single scan requests. |
| **5** | **Audiophile Listening Guide**<br>[`generate_listening_guide`](file:///Users/hill/src/vinylvault/gemini_service.py#L536) | `gemini-3.6-flash` | Default *(Standard reasoning)* | `application/json` | Google Search Grounding (`google_search`) | Generates a deep-dive listening guide including recording history (`albumBackground`), Side A/B tracklists with timestamped listening cues, pressing tips (`vinylTip`), and mood pairings. |
| **6** | **AI Chat Companion**<br>[`chat_about_album`](file:///Users/hill/src/vinylvault/gemini_service.py#L680) & [`stream_chat_response`](file:///Users/hill/src/vinylvault/gemini_service.py#L793) | `gemini-3.6-flash` | Default *(Standard reasoning)* | `text/plain`<br>*(Streaming: `text/event-stream`)* | Google Search Grounding (`google_search`) | Interactive musicologist chatbot with full visibility into the currently spinning record, attached images (labels/matrix/obi), and complete Crate inventory. |
| **7** | **Classical Music Chronicle**<br>[`generate_chronicle_ai`](file:///Users/hill/src/vinylvault/gemini_service.py#L867) | `gemini-3.6-flash` | Default *(Standard reasoning)* | `application/json` | None | Categorizes all collection records into chronological composer eras (Baroque, Classical, Romantic, Modern 20th Century, Contemporary) with composer biographies, birth years, and audiophile insights. |
| **8** | **Audio Pronunciation (TTS)**<br>[`generate_pronunciation`](file:///Users/hill/src/vinylvault/gemini_service.py#L973) | `gemini-3.1-flash-tts-preview` | N/A | `audio/l16`<br>*(Decoded to `audio/wav`)*<br>`response_modalities=["AUDIO"]` | Voice: `"Aoede"` | Text-to-speech pronunciation for classical composers, album titles, or track names: *"Pronounce clearly and naturally as a composer, album, or track name..."* |
| **9** | **Daily Record Poster Showcase**<br>[`generate_daily_poster_insights`](file:///Users/hill/src/vinylvault/gemini_service.py#L1044) | `gemini-3.6-flash` | Default *(Standard reasoning)* | `application/json` | None | Generates poetic showcase poster headlines, essential listening highlights, master tape historical trivia, and atmosphere/beverage pairing notes. |

---

## Architectural & Performance Notes

### 1. Thinking Level Minimization for Real-Time Scans
For fast, interactive user experiences on the Camera Scan screen (Calls A, B, and C), `thinking_config=types.ThinkingConfig(thinking_level="minimal")` is configured on `types.GenerateContentConfig`. This reduces reasoning overhead on `gemini-3.6-flash`, allowing metadata extraction and corner detection to execute concurrently in **~1 second**.

### 2. Search Grounding Integration
Features requiring up-to-date discographical facts, historical recording dates, or pressing comparisons (such as Listening Guides and the Chat Companion) utilize Google Search Grounding:
```python
config = types.GenerateContentConfig(
    tools=[types.Tool(google_search=types.GoogleSearch())]
)
```

### 3. Multi-Modal Vision Inspection
The Chat Companion supports multi-modal image inputs (album covers, obi strips, matrix runout etchings, liner notes). Images are converted to base64 `inlineData` parts prior to dispatching to Gemini.
