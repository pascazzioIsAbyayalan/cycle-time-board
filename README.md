# Cycle Time Board

Personal cycle-time board for **your** GitHub Project issues — as a static HTML page or a Cursor canvas.

## Important: you choose the board

This package ships **without** a default Project (nothing is pre-pointed at Kuadrant or any other org).

| Step | What happens |
| ---- | ------------ |
| 1. Authenticate | GitHub knows who you are (`gh` or `GH_TOKEN`) |
| 2. **Choose a board** | `configure.py` lists Projects you can access; you pick one + repos |
| 3. Fetch & build | Scripts pull **your** assigned issues and write HTML / canvas |

Until you run step 2, fetch/generate will stop and tell you to configure.

```text
clone  →  gh auth login  →  configure.py  →  fetch.py  →  open dist/index.html
              (who am I?)     (which board?)   (my issues)
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

### 2. Authenticate with GitHub

Your username is taken from auth — do **not** put it in a config file.

```bash
gh auth login
gh auth status
```

Or use a classic PAT with `repo`, `read:project`, and `read:org` (if the Project is in a private/SSO org):

```bash
export GH_TOKEN=ghp_xxxxxxxxxxxxxxxx
```

For org boards, authorize SSO on the token if GitHub asks.

### 3. Choose your Project board

```bash
python3 scripts/configure.py
```

What it does:

1. Signs in as you (`gh api user`)
2. Lists Projects on **your user** and **your orgs**
3. Asks you to pick one
4. Asks which repos to scan for issues assigned to you
5. Optionally asks for a Project **Area** filter
6. Writes **`boards.json`** (local only — gitignored)

Example session:

```text
Signed in as your-login
Discovering GitHub Projects you can access…

  Checking your-login…
  Checking my-org…

Found 3 project(s):

    1. my-org #12 — Platform backlog
       https://github.com/orgs/my-org/projects/12
    2. my-org #4 — Team board
       https://github.com/orgs/my-org/projects/4
    3. your-login #1 — Personal
       https://github.com/users/your-login/projects/1

Select a project [1–3]: 2
Board title [Team board — Cycle Time]:
Repositories to scan for issues assigned to you (comma-separated owner/name).
Example: acme/web-app, acme/api
> my-org/frontend, my-org/api
Area filter:

Wrote boards.json
Next:
  python3 scripts/fetch.py
  python3 scripts/generate_html.py
  open dist/index.html
```

Prefer hand-editing? Copy `boards.example.json` → `boards.json`.

### 4. Fetch your issues and open the board

```bash
python3 scripts/fetch.py
python3 scripts/generate_html.py
python3 scripts/generate_canvas.py   # optional, for Cursor

open dist/index.html                 # macOS
# xdg-open dist/index.html           # Linux
```

---

## Day-to-day

| Goal | Command |
| ---- | ------- |
| Refresh data + HTML | `python3 scripts/fetch.py && python3 scripts/generate_html.py` |
| Switch to another Project | `python3 scripts/configure.py` (overwrites `boards.json`) |
| Someone else’s assignments | `python3 scripts/fetch.py --person their-login` |

---

## `boards.json` shape

Created by configure (not committed). Example:

```json
{
  "title": "My Team — Cycle Time",
  "project": {
    "owner": "my-org-or-username",
    "number": 1,
    "url": "https://github.com/orgs/my-org-or-username/projects/1"
  },
  "repos": ["my-org/my-repo"]
}
```

| Field | Required | Notes |
| ----- | -------- | ----- |
| `project.owner` + `project.number` | Yes | Which GitHub Project |
| `repos` | Yes | `owner/name` list scanned for **your** assigned issues |
| `project.area` | No | If set, keep only items with that Project Area |
| `project.url` | No | Used in the board subtitle link |
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
| `python3 scripts/configure.py` | Pick a Project → write `boards.json` |
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
