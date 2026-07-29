# 📱 PLAN: Apple HIG-Inspired Mobile UI Overhaul for Vinyl Vault

### Timestamp: 2026-07-29T04:03:30Z

## Goal
Overhaul the Vinyl Vault mobile web UI to deliver an immersive, simplistic, and modern experience adhering to Apple Human Interface Guidelines (HIG):
- Translucency & Frosted Glass (`backdrop-blur-2xl bg-black/75`)
- Ergonomic Floating Navigation Dock with Touch-Optimized Targets (min 44x44px)
- Tactile Album Cards with High-Contrast Typography
- Immersive Full-Bleed Mobile Scanner Overlay with Large Touch Handle Targets
- Mobile Safe-Area & Viewport Fitting (`viewport-fit=cover`)

---

## Step-by-Step Execution Plan

### Step 1: Core Layout & iOS Styling Enhancements (`static/index.html`)
- Update `viewport` meta tag for `viewport-fit=cover` and iOS notch/home-indicator safe areas.
- Refine CSS variables and custom utility classes for iOS-style frosted glass, subtle borders (`border-white/10`), ambient drop shadows (`shadow-2xl shadow-black/80`), and smooth spring animations.

### Step 2: Floating Mobile Navigation Dock & Header Bar
- Transform the top navigation bar into a clean, translucent header with San Francisco-style typography.
- Implement a floating bottom navigation dock for mobile viewports (`fixed bottom-4 left-1/2 -translate-x-1/2 z-40`) featuring pill buttons and crisp icons.

### Step 3: Immersive "Now Spinning" Hero & Crate Grid Overhaul
- Redesign the turntable vinyl widget with depth, glossy vinyl groove ring highlights, and high-contrast typography.
- Refine album grid cards with 1:1 aspect ratio, rounded corners (`rounded-2xl`), subtle hover/tap scale effects (`active:scale-95`), and dark badges.

### Step 4: Ergonomic Mobile Scanner & 4-Corner Crop Overlay
- Elevate the camera scanner modal to a full-screen sheet overlay (`backdrop-blur-2xl bg-black/90`).
- Ensure corner handles have generous 44x44px touch targets for easy dragging on touchscreens.
- Position the 3-button action bar (`Apply`, `Auto`, `Resnap`) in an ergonomic bottom dock with clear labels.

### Step 5: Verification & Local Docker Testing
- Run `./test_local_integration.sh` to ensure zero regressions across all 8 API endpoints.
- Test responsive layout and touch interactions.
