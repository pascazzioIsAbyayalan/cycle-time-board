---
name: cycle-time-board
description: >-
  Builds, refreshes, and serves a personal GitHub Project cycle-time board.
  Use when the user mentions cycle-time board, refresh board, open board,
  regenerate board, or sync board with GitHub.
---

# Cycle Time Board

Personal GitHub Project cycle-time board. Identity comes from **`gh` auth or `GH_TOKEN`**.

**There is no default Project.** The user must run `configure.py` to pick one or more Projects + repos.

**GitHub MCP is not required.** All GitHub access goes through the `gh` CLI.

## Quick reference

| What | Command |
| ---- | ------- |
| First-time setup (browser UI) | `python3 scripts/configure.py` |
| First-time setup (terminal) | `python3 scripts/configure.py --cli` |
| Fetch latest data | `python3 scripts/fetch.py` |
| Regenerate HTML | `python3 scripts/generate_html.py` |
| Regenerate Cursor canvas | `python3 scripts/generate_canvas.py` |
| Open board in Chrome | `open -a "Google Chrome" http://127.0.0.1:8765/board` |

## Workflow

```
Progress:
- [ ] 1. boards.json exists — else run configure.py
- [ ] 2. Fetch data from GitHub
- [ ] 3. Generate HTML board
- [ ] 4. Generate canvas
- [ ] 5. Start configure.py if it is not already running
- [ ] 6. Always open Google Chrome to http://127.0.0.1:8765/board
```

### 1. Configure (first time or switching projects)

```bash
# Browser UI — opens a local page to select projects and repos
python3 scripts/configure.py

# Terminal-only alternative
python3 scripts/configure.py --cli
```

The browser UI has a **Save and build board** button that runs fetch + generate in one step.

### 2. Refresh data without reconfiguring

```bash
python3 scripts/fetch.py
python3 scripts/generate_html.py
python3 scripts/generate_canvas.py
```

### 3. Open the board

**Always open Google Chrome.** Do not use generic `open` or `xdg-open` as the primary opener.

Start the configure server if it is not already running (enables Sync and Auto-sync):

```bash
python3 scripts/configure.py &

# Board is served at:
# http://127.0.0.1:8765/board
```

Then always open Chrome:

```bash
# macOS
open -a "Google Chrome" http://127.0.0.1:8765/board

# Linux
google-chrome http://127.0.0.1:8765/board
```

`python3 scripts/configure.py` auto-opens Chrome to the board when `dist/index.html` exists.

**Offline fallback — static file** (no sync): still always Chrome.

```bash
# macOS
open -a "Google Chrome" dist/index.html

# Linux
google-chrome dist/index.html
```

### 4. Optional: Cursor canvas

```bash
python3 scripts/generate_canvas.py
# Copy dist/cycle-time-board.canvas.tsx into workspace canvases/ folder
```

## Important notes

- Do not assume a specific org or Project. Always use the user's `boards.json`.
- `boards.json` is gitignored — it contains the user's personal project selection.
- The configure server binds to `127.0.0.1:8765` by default. Use `--port` to change.
- Only issues **assigned to the authenticated user** appear on the board.
- Always open the board in Google Chrome, never the system default browser.
