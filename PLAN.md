# 📋 Master Execution Plan: Classical Infographic & Composer Knowledge Dashboard

### Timestamp: 2026-07-29T05:24:00Z

## Goal
Transform the **Chronicle** tab into a rich, educational **Classical Collection Infographic & Composer Knowledge Dashboard**. Provide users with visual analytics on their classical vinyl collection, including era distributions, composer lifespans, countries of origin, and key musical style characteristics.

---

## 🎯 Step-by-Step Implementation Plan

### Step 1: Composer Knowledge Base & Analytics Engine (`classical_service.py`)
- Add a curated `COMPOSER_KNOWLEDGE_BASE` dictionary mapping major classical composers (Bach, Vivaldi, Mozart, Beethoven, Chopin, Tchaikovsky, Brahms, Debussy, Stravinsky, etc.) to:
  - **Lifespan**: e.g., `1685 – 1750`
  - **Country & Flag**: e.g., `🇩🇪 Germany`, `🇦🇹 Austria`, `🇫🇷 France`, `🇮🇹 Italy`, `🇷🇺 Russia`
  - **Key Style / Innovations**: e.g., *Polyphonic Counterpoint, Orchestral Symphonism, Romantic Expressionism*.
- Update `get_chronicle_data()` to compute:
  - `eraPercentages`: Percentage breakdown of the collection by era.
  - `topComposers`: List of detected composers in the user's collection enriched with metadata.
  - `timelineSpan`: Min/Max years covered in the collection.

### Step 2: Interactive Infographic & Analytics Banner (`static/index.html`)
- Create `#chronicleInfographicSection` in the Chronicle tab:
  - **Visual Era Distribution Progress Bar**: Multi-colored bar showing exact percentages of Baroque, Classical, Romantic, Modern, and Contemporary records.
  - **Composer Knowledge Cards / Badges**: Interactive, horizontally scrollable or grid-based cards showing composer portraits/icons, lifespan, country flag, and owned album count.
  - **Click-to-Filter**: Clicking any composer badge or era segment filters the timeline below.

### Step 3: Verification & Integration Tests
- Run `./test_local_integration.sh` to verify API stability.
- Restart local Docker container and commit to `main`.

---

## 💬 User Review Request
Please review this plan. Upon your confirmation, we will proceed to `DEFINE.md` for task decomposition and execution!
