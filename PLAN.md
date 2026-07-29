# 📋 Master Execution Plan: Enhanced Comfortable Typography & Readability

### Timestamp: 2026-07-29T08:40:15Z

## Goal
Increase font sizes across all key UI components in `static/index.html` (Crate Cards, Chronicle Timeline, Composer Knowledge Cards, Composer Modal, and Navigation) for an effortless, comfortable reading experience.

---

## 🎯 Step-by-Step Implementation Plan

### Step 1: Crate Cards Typography (`renderRecordsGrid`)
- Increase album title from `text-base` to `text-lg font-bold`.
- Increase artist & year from `text-xs` to `text-sm`.
- Increase genre badge & spin count from `text-[11px]` to `text-xs`.

### Step 2: Chronicle Timeline & Composer Cards (`renderChronicle`)
- **Chronicle Items**:
  - Title: `text-sm` -> `text-base font-bold`.
  - Artist: `text-xs` -> `text-sm`.
  - Composer badge & release year: `text-[10px]` -> `text-xs`.
  - AI Insight: `text-[11px]` -> `text-xs leading-relaxed`.
- **Composer Knowledge Cards**:
  - Name: `text-sm` -> `text-base font-bold`.
  - Lifespan & Country: `text-[11px]` -> `text-xs`.
  - Highlights bio: `text-xs` -> `text-sm leading-relaxed`.

### Step 3: Composer Deep-Dive Modal & Tracklist (`#composerModal`)
- Modal section headings: `text-xs` -> `text-sm font-extrabold`.
- Bio & Innovations text: `text-xs` -> `text-sm leading-relaxed`.
- Tracklist items: `text-xs` -> `text-sm`.

### Step 4: Verification & Integration Tests
- Run `./test_local_integration.sh`.
- Restart local Docker container and commit changes to `main`.

---

## 💬 User Review Request
Please review this plan. Upon your confirmation, we will proceed with execution!
