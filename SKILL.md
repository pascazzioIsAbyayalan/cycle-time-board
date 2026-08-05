---
name: cycle-time-board
description: >-
  Builds and refreshes a personal GitHub Project cycle-time board as standalone
  HTML and a Cursor canvas matching the UI Touch Grass board, with light/dark
  mode. Use when the user mentions cycle-time board, UI Touch Grass board,
  refresh board HTML, install cycle-time-board, or regenerate the board package.
---

# Cycle Time Board

Personal GitHub Project cycle-time board. Outputs:

1. **HTML** — `dist/index.html` (browser; light/dark; interactive label pie; collapsible cycle sections)
2. **Cursor canvas** — `dist/cycle-time-board.canvas.tsx` (copy into a workspace `canvases/` folder)

Full end-user install: see [README.md](README.md).

## Package location

Prefer the cloned repo root as cwd (or `~/.cursor/skills/cycle-time-board-pkg` if symlinked).

## Workflow

```
Progress:
- [ ] 1. gh auth status (login if needed)
- [ ] 2. Confirm boards.json person.login
- [ ] 3. python3 scripts/fetch.py
- [ ] 4. python3 scripts/generate_html.py
- [ ] 5. python3 scripts/generate_canvas.py
- [ ] 6. Copy canvas into workspace canvases/ if using Cursor
```

```bash
python3 scripts/fetch.py
python3 scripts/generate_html.py
python3 scripts/generate_canvas.py
open dist/index.html
cp dist/cycle-time-board.canvas.tsx ~/.cursor/projects/<workspace>/canvases/
```

## Defaults

Configured in `boards.json` (see `boards.example.json`):

- Project: Kuadrant org **#18**, area **UI Touch Grass**
- Repo: `Kuadrant/kuadrant-console-plugin`
- Person: `person.login` / `person.name`

## Enriching PR summaries

`fetch.py` may store a light PR blurb. Enrich `prSummary` in `data/people/<login>.json` (problem / solution / keyChanges) before regenerating when storytelling needs more detail.
