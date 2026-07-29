# 📋 DEFINE: Mobile UI Overhaul TODO List

### Timestamp: 2026-07-29T04:03:30Z

## Tasks

- [ ] `[frontend]` **1. Meta & Viewport Safe-Area Setup**:
  - Add `viewport-fit=cover` to meta viewport in `static/index.html`.
  - Add iOS dark system color theme `<meta name="theme-color" content="#09090b">`.

- [ ] `[frontend]` **2. Apple HIG Frosted Glass & Typography Utilities**:
  - Add `.apple-glass` backdrop-blur-2xl classes (`backdrop-filter: blur(24px); background: rgba(18, 18, 18, 0.75); border: 1px solid rgba(255, 255, 255, 0.12);`).
  - Add `.active-bounce` scale transitions for haptic-like button presses (`active:scale-95 transition-transform duration-150`).

- [ ] `[frontend]` **3. Floating Mobile Navigation Dock**:
  - Refine top header for clean minimalism (logo + quick scan button).
  - Add floating translucent bottom navigation bar on mobile (`sm:hidden fixed bottom-5 left-1/2 -translate-x-1/2 z-40`) with 44px+ touch targets for Now Spinning, Crate, and Chronicle.

- [ ] `[frontend]` **4. Modern Turntable Hero & Card Grid Styling**:
  - Enhance "Now Spinning" turntable widget with glossy vinyl sheen and high-contrast typography.
  - Upgrade album cards in My Crate and Chronicle grids to rounded-2xl cards with soft shadows, 1:1 image containers, and clear badge badges.

- [ ] `[frontend]` **5. Mobile-Optimized Scanner Sheet & Corner Handles**:
  - Convert scanner modal into a full-bleed bottom sheet on mobile viewports.
  - Maintain 44px hit-testing touch targets on SVG corner handles for 4-corner crop dragging.
  - Position Apply/Auto/Resnap action bar in an ergonomic bottom dock.

- [ ] `[testing]` **6. Local Integration & Responsive Testing**:
  - Run `./test_local_integration.sh` to ensure 100% test pass rate.
  - Verify layout responsiveness and git commit/push.
