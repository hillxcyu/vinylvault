# 🎓 Learning Proposal: Retained Best Practices & Guardrails

Based on recent session feedback and corrections, the following key insights and patterns have been identified for retention:

---

### 1️⃣ **Frontend DOM Repainting Before Async API Requests**
* **Context**: When updating an `<img>` element's `src` in web applications immediately before a long-running async operation (such as a Gemini AI API call), the browser's rendering engine postpones decoding and repainting the DOM image until after the long-running async request completes.
* **Learned Guideline**: 
  - To force the browser to visibly paint an updated `<img>` on screen *before* starting subsequent heavy network requests, wrap the `src` update in a `Promise` that waits for `img.onload` and uses double `requestAnimationFrame()`.
  ```javascript
  await new Promise((resolve) => {
    let done = false;
    const finish = () => { if (!done) { done = true; resolve(); } };
    img.onload = finish;
    img.onerror = finish;
    img.src = newUrl + '?t=' + Date.now();
    setTimeout(finish, 300); // safety fallback
  });
  await new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)));
  ```

---

### 2️⃣ **Database State & Single Source of Truth Invariant**
* **Context**: Automatic fallback logic that re-seeds an empty database with default sample records causes unexpected data overwrites on app restart or temporary network hiccups.
* **Learned Guideline**:
  - Treat the database as the strict single source of truth.
  - Never automatically re-seed or inject default sample records when a database or collection is empty.
  - Provide explicit user-triggered **Backup** (`GET /api/backup`) and **Restore** (`POST /api/restore`) capabilities for dataset migration or restoration.

---

### 📋 Proposed Action Plan:
Review these guidelines. Upon your approval, these patterns will be remembered for future development tasks.
