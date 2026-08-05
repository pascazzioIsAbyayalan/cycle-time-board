---
name: cycle-time-board
description: >-
  Builds and refreshes a personal GitHub Project cycle-time board as standalone
  HTML and a Cursor canvas matching the UI Touch Grass board, with light/dark
  mode. Use when the user mentions cycle-time board, UI Touch Grass board,
  refresh board HTML, install cycle-time-board, or regenerate the board package.
---

# Cycle Time Board

Project skill — use the repository root as the working directory.

See the root [SKILL.md](../../../SKILL.md) and [README.md](../../../README.md) for install, `gh` auth, and refresh commands.

```bash
python3 scripts/fetch.py
python3 scripts/generate_html.py
python3 scripts/generate_canvas.py
```
