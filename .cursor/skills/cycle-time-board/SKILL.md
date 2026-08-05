---
name: cycle-time-board
description: >-
  Builds and refreshes a personal GitHub Project cycle-time board as standalone
  HTML and a Cursor canvas matching the UI Touch Grass board, with light/dark
  mode. Use when the user mentions cycle-time board, UI Touch Grass board,
  refresh board HTML, install cycle-time-board, or regenerate the board package.
---

# Cycle Time Board

Personal GitHub Project cycle-time board. Identity comes from **`gh` auth or `GH_TOKEN`** — users do not need to edit JSON for the default board.

**GitHub MCP is not required.** Use the shell + `gh` CLI.

Outputs:

1. **HTML** — `dist/index.html`
2. **Cursor canvas** — `dist/cycle-time-board.canvas.tsx`

Full install: [README.md](README.md).

## Workflow

```
Progress:
- [ ] 1. gh auth status (or GH_TOKEN set)
- [ ] 2. python3 scripts/fetch.py
- [ ] 3. python3 scripts/generate_html.py
- [ ] 4. python3 scripts/generate_canvas.py
- [ ] 5. Copy canvas into workspace canvases/ if needed
```

```bash
python3 scripts/fetch.py
python3 scripts/generate_html.py
python3 scripts/generate_canvas.py
```

Optional project overlay: `boards.json` (see `boards.example.json`). Do not require `person` in config.
