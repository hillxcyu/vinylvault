# 📋 Master Execution Plan: Untruncated Titles & Expanded Composer Deep-Dive

### Timestamp: 2026-07-29T05:39:00Z

## Goal
1. **Remove Title Truncation**: Allow full album titles to render naturally with clean line-wrapping (`leading-snug`) across Crate grid cards, Chronicle timeline items, and Now Spinning hero views.
2. **Expand Composer Knowledge Base & Deep-Dive Modal**:
   - Enrich `COMPOSER_DATABASE` in `classical_service.py` with in-depth biographies, musical innovations, historical context, and signature compositions.
   - Create a dedicated **Composer Deep-Dive Modal** (`#composerModal`) in `static/index.html` displaying full biography, country flag, lifespan, key innovations, and a filtered list of all albums by that composer with 1-click spin buttons.

---

## 🎯 Step-by-Step Implementation Plan

### Step 1: Remove Album Title Truncation (`static/index.html`)
- Remove `truncate` classes from album title elements in `renderRecordsGrid()`, `renderChronicle()`, and `updateNowSpinningUI()`.
- Apply `leading-snug break-words` for clean multiline title presentation.

### Step 2: Expand Composer Database (`classical_service.py`)
- Expand `COMPOSER_DATABASE` with:
  - `bio`: In-depth 2-3 sentence historical profile.
  - `innovations`: Major musical contributions (e.g., *Development of 4-movement symphonic form, Wagnerian Leitmotifs*).
  - `keyWorks`: Signature masterpieces.

### Step 3: Interactive Composer Modal (`static/index.html`)
- Add `#composerModal` in `static/index.html` with glassmorphic styling (`ios-liquid-glass`).
- When a user clicks any Composer Card, trigger `openComposerModal(composerName)`.
- Display full biography, country flag, lifespan, musical innovations, and a list of their albums in the user's collection.

### Step 4: Verification & Integration Tests
- Run `./test_local_integration.sh`.
- Restart local Docker container and commit to `main`.

---

## 💬 User Review Request
Please review this plan. Upon your confirmation, we will proceed with execution!
