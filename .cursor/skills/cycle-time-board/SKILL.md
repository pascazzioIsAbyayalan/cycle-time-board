---
name: cycle-time-board
description: >-
  Builds and refreshes a personal GitHub Project cycle-time board as standalone
  HTML and a Cursor canvas, with light/dark mode. User must choose a Project
  via configure.py (no default board). Use when the user mentions cycle-time
  board, refresh board HTML, install cycle-time-board, or regenerate the board
  package.
---

# Cycle Time Board

Personal GitHub Project cycle-time board. Identity comes from **`gh` auth or `GH_TOKEN`**.

**There is no default Project.** The user must run `configure.py` (or create `boards.json`) to pick a board they can access.

**GitHub MCP is not required.** Use the shell + `gh` CLI.

Outputs:

1. **HTML** — `dist/index.html`
2. **Cursor canvas** — `dist/cycle-time-board.canvas.tsx`

Full install: [README.md](README.md).

## Workflow

```
Progress:
- [ ] 1. gh auth status (or GH_TOKEN set)
- [ ] 2. boards.json exists — else python3 scripts/configure.py
- [ ] 3. python3 scripts/fetch.py
- [ ] 4. python3 scripts/generate_html.py
- [ ] 5. python3 scripts/generate_canvas.py
- [ ] 6. Copy canvas into workspace canvases/ if needed
```

```bash
# First time / switch board
python3 scripts/configure.py

python3 scripts/fetch.py
python3 scripts/generate_html.py
python3 scripts/generate_canvas.py
```

Do not assume a Kuadrant or any other org Project. Always use the user’s selected `boards.json`.
