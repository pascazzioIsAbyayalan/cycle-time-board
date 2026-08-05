# Cycle Time Board

A personal **GitHub Project cycle-time board** you can open in the browser or in Cursor.

It shows **your** assigned issues (identity comes from your GitHub login/token) for a Project — default: Kuadrant Project #18 · UI Touch Grass — with:

- Summary stats and an interactive label donut chart
- Search / date / label / sprint filters
- **Cycle time** view (collapsible Open / Completed sections, timelines, PR summaries)
- **Board** and **Sprint table** views
- Light / dark mode

| Format | What you get |
| ------ | ------------ |
| **Browser HTML** | `dist/index.html` — static snapshot, no server |
| **Cursor canvas + skill** | Board beside chat + agent refresh workflow |

---

## Prerequisites

| Requirement | Why |
| ----------- | --- |
| [Python 3](https://www.python.org/) | Runs fetch + generate scripts |
| [GitHub CLI](https://cli.github.com/) (`gh`) **or** a GitHub token in `GH_TOKEN` | Authenticates API calls |
| Access to the target org/project/repos | Scripts read Project fields and your assigned issues |
| [Cursor](https://cursor.com/) *(optional)* | Skill + canvas only |

**You do not need the GitHub MCP** in Cursor for this package. Scripts talk to GitHub through `gh` (which uses your login or `GH_TOKEN`). Cursor’s GitHub MCP is unrelated and optional.

No Node/npm install. The HTML board does **not** call GitHub from the browser.

---

## Connect your GitHub (no JSON editing)

Your board user is detected automatically from auth. You do **not** need to put your username in a config file.

### Option A — GitHub CLI (recommended)

```bash
gh auth login
gh auth status
```

Use a browser login or paste a token when `gh` asks. For org projects you may need SSO authorization on the token.

### Option B — Token environment variable

Create a [personal access token](https://github.com/settings/tokens) (classic) with at least:

- `repo` (or fine-grained read access to the repos)
- `read:project`
- `read:org` if the Project lives in a private/SSO org

Then:

```bash
export GH_TOKEN=ghp_xxxxxxxxxxxxxxxx
# GITHUB_TOKEN is also accepted
```

`gh` and these scripts will use that token. No `boards.json` edit required for the default Kuadrant board.

---

## Quick start

```bash
git clone https://github.com/pascazzioIsAbyayalan/cycle-time-board.git
cd cycle-time-board

# 1. Authenticate (once)
gh auth login
# or: export GH_TOKEN=ghp_...

# 2. Pull YOUR issues + build outputs
python3 scripts/fetch.py
python3 scripts/generate_html.py
python3 scripts/generate_canvas.py

# 3. Open the board
open dist/index.html        # macOS
# xdg-open dist/index.html  # Linux
```

Refresh anytime by re-running step 2.

---

## Optional configuration

Built-in defaults target Kuadrant Project #18 / `kuadrant-console-plugin`.  
Only create/edit `boards.json` if you need a **different project or repo** (copy from `boards.example.json`).

```json
{
  "title": "UI Touch Grass — Cycle Time",
  "project": {
    "owner": "Kuadrant",
    "number": 18,
    "url": "https://github.com/orgs/Kuadrant/projects/18",
    "area": "UI Touch Grass"
  },
  "repos": ["Kuadrant/kuadrant-console-plugin"]
}
```

`person` is optional. If present it is only used as a fallback when auth is unavailable, or with `--no-auth`.

```bash
# Fetch someone else’s assigned issues (override)
python3 scripts/fetch.py --person other-login
```

---

## Install in Cursor (optional)

GitHub MCP is **not** required.

```bash
# Personal skill
mkdir -p ~/.cursor/skills/cycle-time-board
cp SKILL.md ~/.cursor/skills/cycle-time-board/SKILL.md
ln -sfn "$(pwd)" ~/.cursor/skills/cycle-time-board-pkg

# Canvas into a workspace
python3 scripts/generate_canvas.py
mkdir -p ~/.cursor/projects/<your-workspace>/canvases
cp dist/cycle-time-board.canvas.tsx \
  ~/.cursor/projects/<your-workspace>/canvases/cycle-time-board.canvas.tsx
```

In Cursor chat (with `gh` already authenticated in that environment):

> Using the cycle-time-board skill, refresh the board from GitHub and regenerate the HTML + canvas.

---

## Scripts

| Command | Purpose |
| ------- | ------- |
| `python3 scripts/fetch.py` | Resolve you via `gh`/`GH_TOKEN`, fetch issues → `data/people/<login>.json` |
| `python3 scripts/generate_html.py` | Build `dist/index.html` |
| `python3 scripts/generate_canvas.py` | Build `dist/cycle-time-board.canvas.tsx` |

---

## Sharing

- **Snapshot:** share `dist/index.html` (self-contained; viewers need no GitHub auth).
- **Tool:** share this repo; each person authenticates as themselves and runs fetch + generate.

---

## Troubleshooting

| Problem | What to try |
| ------- | ----------- |
| Auth errors | `gh auth login` or set `GH_TOKEN`; for orgs authorize SSO on the token |
| Empty board | Issues must be **assigned to your user**; check Project Area filter in defaults |
| Wrong user | `gh api user --jq .login` — that login is whose board is fetched |
| Cursor refresh fails | Ensure the integrated terminal can run `gh auth status` (MCP not used) |

---

## License

Use and share freely within your team unless a LICENSE file is added later.
