# Cycle Time Board

A personal **GitHub Project cycle-time board** you can open in the browser or in Cursor.

It shows your assigned issues from a GitHub Project (default: Kuadrant Project #18 · UI Touch Grass area) with:

- Summary stats and label breakdown (interactive donut chart)
- Search / date / label / sprint filters
- **Cycle time** view (open issues first, collapsible sections, timeline bars, PR summaries)
- **Board** and **Sprint table** views
- Light / dark mode

| Format | What you get |
| ------ | ------------ |
| **Browser HTML** | `dist/index.html` — static snapshot, no server |
| **Cursor canvas + skill** | Live-looking board beside chat + agent refresh workflow |

---

## Prerequisites

| Requirement | Why |
| ----------- | --- |
| [Python 3](https://www.python.org/) | Runs fetch + generate scripts |
| [GitHub CLI](https://cli.github.com/) (`gh`) | Authenticates and queries GitHub |
| Access to the target org/project/repos | Scripts read Project fields and assigned issues |
| [Cursor](https://cursor.com/) *(optional)* | For the skill + canvas install |

No Node/npm install. The HTML board does **not** call GitHub from the browser — you regenerate it locally after fetching.

---

## Connect your GitHub

Authentication is via the GitHub CLI (not a token pasted into the HTML):

```bash
# Install gh if needed: https://cli.github.com/
gh auth login
```

Follow the prompts (HTTPS or SSH, authenticate in the browser). Then verify:

```bash
gh auth status
gh api user --jq .login
```

That login should match `person.login` in `boards.json` (or change `boards.json` to match).

If Project queries fail, check:

- You can open the project URL in the browser while logged in
- Org **SSO** is authorized for the `gh` token (`gh auth refresh -s read:project` if needed)
- You have at least read access to the repository and Project

---

## Quick start (browser board)

```bash
git clone https://github.com/pascazzioIsAbyayalan/cycle-time-board.git
cd cycle-time-board

# 1. Point the board at yourself
cp boards.example.json boards.json
# Edit boards.json → person.login / person.name

# 2. Pull your issues from GitHub
python3 scripts/fetch.py

# 3. Build the HTML (and Cursor canvas)
python3 scripts/generate_html.py
python3 scripts/generate_canvas.py

# 4. Open in your browser
open dist/index.html        # macOS
# xdg-open dist/index.html  # Linux
# start dist/index.html     # Windows
```

Refresh later by re-running steps 2–4.

---

## Configure

Edit `boards.json` (start from `boards.example.json`):

```json
{
  "title": "UI Touch Grass — Cycle Time",
  "project": {
    "owner": "Kuadrant",
    "number": 18,
    "url": "https://github.com/orgs/Kuadrant/projects/18",
    "area": "UI Touch Grass"
  },
  "repos": ["Kuadrant/kuadrant-console-plugin"],
  "person": {
    "login": "YOUR_GITHUB_USERNAME",
    "name": "Your Name"
  }
}
```

| Field | Meaning |
| ----- | ------- |
| `project.owner` / `number` | GitHub org (or user) Project |
| `project.area` | Optional Project “Area” filter (omit or `null` to skip) |
| `repos` | Repositories to search for issues assigned to you |
| `person.login` | Your GitHub username |

This package is **personal only** (one assignee board). Share the generated HTML if others should view a snapshot of your board.

---

## Install in Cursor (optional)

### 1. Personal skill

From the repo root:

```bash
mkdir -p ~/.cursor/skills/cycle-time-board
cp SKILL.md ~/.cursor/skills/cycle-time-board/SKILL.md
ln -sfn "$(pwd)" ~/.cursor/skills/cycle-time-board-pkg
```

The symlink lets the agent find `scripts/` and `boards.json` when you ask it to refresh.

### 2. Canvas in a workspace

```bash
python3 scripts/generate_canvas.py
mkdir -p ~/.cursor/projects/<your-workspace>/canvases
cp dist/cycle-time-board.canvas.tsx \
  ~/.cursor/projects/<your-workspace>/canvases/cycle-time-board.canvas.tsx
```

Open the `.canvas.tsx` file beside chat in Cursor.

### 3. Refresh via the agent

In Cursor chat:

> Using the cycle-time-board skill, refresh the board from GitHub and regenerate the HTML + canvas.

---

## Scripts

| Command | Purpose |
| ------- | ------- |
| `python3 scripts/fetch.py` | Fetch assigned issues + Project status/sprint/PRs into `data/people/<login>.json` |
| `python3 scripts/generate_html.py` | Build `dist/index.html` |
| `python3 scripts/generate_canvas.py` | Build `dist/cycle-time-board.canvas.tsx` |

```bash
# Fetch only (uses boards.json person)
python3 scripts/fetch.py

# Fetch a specific login (writes data/people/<login>.json)
python3 scripts/fetch.py --person someuser
```

---

## Repository layout

```
boards.json                 # Your config (gitignored patterns optional; example provided)
boards.example.json         # Template for new users
data/people/<login>.json    # Fetched snapshots
scripts/fetch.py
scripts/generate_html.py
scripts/generate_canvas.py
templates/board.html
templates/canvas.tsx.template
dist/index.html             # Browser board
dist/cycle-time-board.canvas.tsx
SKILL.md                    # Cursor agent skill
```

---

## Sharing with others

- **Snapshot:** send or host `dist/index.html` (self-contained; no GitHub auth in the browser).
- **Reusable tool:** share this repo; each person runs `gh auth login`, edits `boards.json`, then fetch + generate.
- **Cursor teammates:** they clone the repo and follow **Install in Cursor** above.

---

## Troubleshooting

| Problem | What to try |
| ------- | ----------- |
| `gh` / GraphQL errors | `gh auth status`, re-run `gh auth login`, authorize SSO for the org |
| Empty board | Confirm `person.login`, that issues are assigned to you, and `repos` / `project.area` match reality |
| Project field missing | Status/Area/Sprint names must exist on that Project; Area filter skips mismatched items when set |
| Canvas not appearing | File must live under `~/.cursor/projects/<workspace>/canvases/` and end in `.canvas.tsx` |

---

## License

Use and share freely within your team unless a LICENSE file is added later.
