# Cycle Time Board

Personal cycle-time board for **your** GitHub Project issues — as a static HTML page or a Cursor canvas.

## Important: you choose the board

This package ships **without** a default Project (nothing is pre-pointed at Kuadrant or any other org).

| Step | What happens |
| ---- | ------------ |
| 1. Authenticate | GitHub knows who you are (`gh` or `GH_TOKEN`) |
| 2. **Choose a board** | `configure.py` opens a **browser UI** to pick a Project + repos |
| 3. Fetch & build | Scripts pull **your** assigned issues and write HTML / canvas |

Until you run step 2, fetch/generate will stop and tell you to configure.

```text
clone  →  configure.py (browser)  →  Save and build  →  open dist/index.html
           login + pick Project         fetch + HTML
```

---

## What you get

- Summary stats + interactive label donut
- Search / date / label / sprint filters
- **Cycle time** view (Open / Completed, timelines, PR summaries from each PR’s description)
- **Board** and **Sprint** views
- Light / dark mode

| Output | File |
| ------ | ---- |
| Browser (no server) | `dist/index.html` |
| Cursor canvas | `dist/cycle-time-board.canvas.tsx` |

**GitHub MCP is not required.** Scripts use the `gh` CLI (or `GH_TOKEN`). The HTML file never calls GitHub from the browser.

---

## Prerequisites

| Need | Why |
| ---- | --- |
| Python 3 | Runs the scripts |
| [GitHub CLI](https://cli.github.com/) **or** `GH_TOKEN` | Auth + API |
| Access to a GitHub Project and its repos | You select these in configure |
| Cursor *(optional)* | Skill + canvas only |

---

## Setup (first time)

### 1. Clone

```bash
git clone https://github.com/pascazzioIsAbyayalan/cycle-time-board.git
cd cycle-time-board
```

### 2. Choose your Project board (browser UI)

```bash
python3 scripts/configure.py
```

This starts a local page (like `gh auth login`) and opens it in your browser:

1. **Login with GitHub** if needed (same `gh auth login --web` flow; watch the terminal for a one-time code)
2. **Pick one or more Projects** from your user account and orgs (multi-select)
3. **Choose repositories** from a searchable dropdown (GitHub-style switcher) for those Project owners
4. Optional **Area** filter and board title
5. Click **Save and build board** (writes `boards.json`, runs fetch + generate, opens the HTML)

On the generated board, use the **Repository** filter to switch which of your selected repos you are looking at.

Leave the terminal running while you use the UI (`Ctrl+C` to stop).

| Alternative | Command |
| ----------- | ------- |
| Terminal prompts (old flow) | `python3 scripts/configure.py --cli` |
| UI without auto-opening a tab | `python3 scripts/configure.py --no-browser` then visit the printed URL |
| Hand-edit config | Copy `boards.example.json` → `boards.json` |

Or authenticate ahead of time / via token:

```bash
gh auth login
# or:
export GH_TOKEN=ghp_xxxxxxxxxxxxxxxx   # needs repo, read:project, read:org (+ SSO if required)
```

### 3. Refresh later / Cursor canvas

```bash
python3 scripts/fetch.py
python3 scripts/generate_html.py
python3 scripts/generate_canvas.py   # optional, for Cursor

open dist/index.html                 # macOS
# xdg-open dist/index.html           # Linux
```

---

## Day-to-day

| Goal | How |
| ---- | --- |
| **Sync from the board** | Keep `python3 scripts/configure.py` running, open [http://127.0.0.1:8765/board](http://127.0.0.1:8765/board), click **Sync with GitHub** (optional **Auto-sync** every 5 minutes) |
| Refresh via CLI | `python3 scripts/fetch.py && python3 scripts/generate_html.py` |
| Switch Projects / repos | `python3 scripts/configure.py` (browser UI; overwrites `boards.json`) |
| Someone else’s assignments | `python3 scripts/fetch.py --person their-login` |

The HTML file itself cannot call GitHub from the browser. Sync works through the local configure server (`/api/refresh`), which uses your `gh` login.

---

## `boards.json` shape

Created by configure (not committed). Example:

```json
{
  "title": "My Teams — Cycle Time",
  "projects": [
    {
      "owner": "my-org",
      "number": 1,
      "url": "https://github.com/orgs/my-org/projects/1",
      "title": "Team board"
    }
  ],
  "project": {
    "owner": "my-org",
    "number": 1,
    "url": "https://github.com/orgs/my-org/projects/1"
  },
  "repos": ["my-org/my-repo", "my-org/another-repo"]
}
```

| Field | Required | Notes |
| ----- | -------- | ----- |
| `projects[]` | Yes* | One or more GitHub Projects (`owner` + `number`) |
| `project` | Legacy | Still written as the first selected Project for older tools |
| `repos` | Yes | `owner/name` list scanned for **your** assigned issues |
| `projects[].area` / shared area | No | If set, prefer items with that Project Area |
| `person` | No | Offline fallback only; auth wins by default |

---

## Cursor (optional)

```bash
mkdir -p ~/.cursor/skills/cycle-time-board
cp SKILL.md ~/.cursor/skills/cycle-time-board/SKILL.md
ln -sfn "$(pwd)" ~/.cursor/skills/cycle-time-board-pkg

python3 scripts/generate_canvas.py
mkdir -p ~/.cursor/projects/<your-workspace>/canvases
cp dist/cycle-time-board.canvas.tsx \
  ~/.cursor/projects/<your-workspace>/canvases/cycle-time-board.canvas.tsx
```

In chat (with `gh` working in the terminal):

> Using the cycle-time-board skill, refresh the board from GitHub and regenerate the HTML + canvas.

---

## Scripts

| Command | Purpose |
| ------- | ------- |
| `python3 scripts/configure.py` | Open browser UI → pick Project → write `boards.json` (optional build) |
| `python3 scripts/configure.py --cli` | Same setup via terminal prompts |
| `python3 scripts/fetch.py` | Fetch your issues → `data/people/<login>.json` |
| `python3 scripts/generate_html.py` | Build `dist/index.html` |
| `python3 scripts/generate_canvas.py` | Build `dist/cycle-time-board.canvas.tsx` |

---

## Sharing

- **Snapshot:** send `dist/index.html` — viewers need no GitHub auth.
- **Tool:** share this repo. Each person authenticates, runs **configure** for their own board, then fetch + generate.

---

## Troubleshooting

| Problem | Fix |
| ------- | --- |
| `No boards.json` / no Project selected | `python3 scripts/configure.py` |
| Auth errors | `gh auth login` or set `GH_TOKEN`; authorize org SSO |
| No Projects listed | Open the board in GitHub in a browser; token needs `read:project` (+ `read:org` / SSO) |
| Empty board | Issues must be **assigned to you**; check `repos` and optional `area` |
| No PR Solution Summary | Fetch builds summaries from the **PR description** (`## Description`, `## Changes made`, type checkboxes). Empty/template-only PR bodies produce no summary. Re-run `python3 scripts/fetch.py` after this fix. |
| Wrong user | `gh api user --jq .login` |

---

## License

Use and share freely within your team unless a LICENSE file is added later.
