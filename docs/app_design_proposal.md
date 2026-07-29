# 🎵 Vinyl Vault: Smart Vinyl Collection & Listening Assistant

An intelligent, AI-powered vinyl collection manager designed to prevent duplicate purchases, catalog records effortlessly with Gemini Vision, and track your listening habits.

---

## 🎨 UI & Workflow Mockups

````carousel
![Dashboard View - My Crate & Now Spinning](/usr/local/google/home/xcyu/.gemini/jetski/brain/060421de-903c-4ee0-a3a3-8d729042ca9f/vinyl_app_dashboard_mockup_1784000588970.jpg)
<!-- slide -->
![AI Scanner - Anti-Duplicate Check in Action](/usr/local/google/home/xcyu/.gemini/jetski/brain/060421de-903c-4ee0-a3a3-8d729042ca9f/vinyl_app_scanner_mockup_1784000602640.jpg)
````

---

## 💡 Core Solution & Key Features

### 1. 🛑 "In the Shop" Duplicate Shield
* **Camera Scan / Quick Search**: Point your camera at an album cover (or search title/artist online).
* **Gemini Multimodal Matching**: Instantly matches the image against your saved collection and external catalog (Discogs API).
* **Smart Ownership Alert**:
  - `ALREADY IN COLLECTION`: Displays pressings owned (e.g., *"1977 Original US Pressing"*, *"2020 Remaster"*).
  - `SIMILAR ARTIST / ALBUM`: Highlights matching live albums, compilations, or side projects to prevent redundant purchases.
  - `WISHLIST STATUS`: Indicates if this album was on your saved shopping list.

### 2. 🎧 "Quick Look" & Listening Tracker
* **"Spinning Now" Widget**: Tap an album to log a spin. Displays active playback metadata, track list, and liner notes.
* **Crate Flip Experience**: Interactive digital crate flipping to browse albums visually by spine or album art.
* **Listening Insights**:
  - Weekly/Monthly spin count.
  - Most played genres and favorite artists.
  - *"Dust off this Gem"* prompt: Suggestions for great albums in your collection that haven't been played in over 6 months.

### 3. 📷 Instant AI Cataloging & Metadata Extraction
* **Cover & Spine Recognition**: Snap a photo of new purchases; Gemini Vision extracts album title, artist, record label, year, catalog number, and track list.
* **Discogs Marketplace Sync**: Automatically fetches average market value, release variants, and track details.

---

## 📐 Proposed Architecture & Data Flow

```mermaid
flowchart TD
    User([Vinyl Collector]) -->|1. Takes Photo of Cover/Spine| Camera UI
    User -->|2. Queries Album Title/Artist| Search UI

    subgraph App Core
        Camera UI --> GeminiSDK[Gemini Multimodal API]
        GeminiSDK --> MetadataParser[AI Metadata & Feature Extraction]
        MetadataParser --> LocalDB[(Collection Database)]
        Search UI --> LocalDB
    end

    subgraph External APIs
        MetadataParser --> DiscogsAPI[Discogs / MusicBrainz API]
        DiscogsAPI --> LocalDB
    end

    LocalDB -->|Matches Found| DupAlert[Duplicate Shield Notification]
    LocalDB -->|No Match| AddOption[Catalog New Record]
```

---

## 📋 Recommended Tech Stack

| Component | Technology | Rationale |
| :--- | :--- | :--- |
| **Frontend** | React / Next.js (PWA) or Flutter | Seamless cross-platform access across Mobile (camera-native) and Desktop. |
| **AI Layer** | Google Gen AI SDK (Gemini Flash / Pro Vision) | Fast image-to-metadata extraction, cover recognition, OCR on album spines. |
| **Metadata API** | Discogs REST API / MusicBrainz | Detailed pressing info, tracklists, release IDs, and marketplace values. |
| **Database** | Supabase (PostgreSQL) or SQLite/IndexedDB | Fast offline search for record store digging without cellular connection. |

---

## ❓ Next Steps & Feedback
Please review the design proposal and mockups above. 

1. Would you like to proceed with creating **`DEFINE.md`** to break down the technical tasks?
2. Which stack component (e.g. Next.js PWA with Gemini SDK vs. Flutter app) do you prefer?
