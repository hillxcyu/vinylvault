# 📝 DEFINE: Task Decomposition - Untruncated Titles & Composer Deep-Dive

### Timestamp: 2026-07-29T05:39:10Z

## 🎯 Task Breakdown (TODO List)

- [ ] **[frontend] Full Album Title Display (`static/index.html`)**:
  - Remove `truncate` from `renderRecordsGrid()` album titles.
  - Remove `truncate` from `renderChronicle()` album titles.
  - Add `leading-snug break-words` for clean multiline wrapping.

- [ ] **[backend] Expanded Composer Database (`classical_service.py`)**:
  - Add rich `bio`, `innovations`, and `keyWorks` to all composers in `COMPOSER_DATABASE`.

- [ ] **[frontend] Composer Deep-Dive Modal (`static/index.html`)**:
  - Build `#composerModal` overlay.
  - Add `openComposerModal(composerName)` logic to render full biography & owned albums.

- [ ] **[testing] Integration & Docker Test**:
  - Run `./test_local_integration.sh`.
  - Restart local Docker container and commit to `main`.
