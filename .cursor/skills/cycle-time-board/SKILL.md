---
name: cycle-time-board
description: >-
  Builds and refreshes a personal GitHub Project cycle-time board as standalone
  HTML and a Cursor canvas, with light/dark mode. User must choose a Project
  via the configure browser UI (no default board). Use when the user mentions
  cycle-time board, refresh board HTML, install cycle-time-board, or regenerate
  the board package.
---

# Cycle Time Board

Personal GitHub Project cycle-time board. Identity comes from **`gh` auth or `GH_TOKEN`**.

**There is no default Project.** The user must run `configure.py` (browser UI) or create `boards.json` to pick one or more Projects + repos they can access.

**GitHub MCP is not required.** Use the shell + `gh` CLI.

Outputs:

1. **HTML** — `dist/index.html`
2. **Cursor canvas** — `dist/cycle-time-board.canvas.tsx`

Full install: [README.md](README.md).

## Workflow

```
Progress:
- [ ] 1. boards.json exists — else python3 scripts/configure.py (browser UI)
- [ ] 2. Or: Save and build from the configure UI (fetch + HTML in one step)
- [ ] 3. python3 scripts/fetch.py   (if not built from UI)
- [ ] 4. python3 scripts/generate_html.py
- [ ] 5. python3 scripts/generate_canvas.py
- [ ] 6. Copy canvas into workspace canvases/ if needed
```

```bash
# First time / switch board — opens browser UI
python3 scripts/configure.py
# Prefer "Save and build board" in the UI

# Or refresh without reconfigure
python3 scripts/fetch.py
python3 scripts/generate_html.py
python3 scripts/generate_canvas.py

# Terminal-only configure fallback
python3 scripts/configure.py --cli
```

Do not assume a Kuadrant or any other org Project. Always use the user’s selected `boards.json`.
