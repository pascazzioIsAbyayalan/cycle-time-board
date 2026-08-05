## Description

Personal **cycle-time board** for the GitHub Project issues assigned to you. Perfect if you want a clear view of your open work, cycle times, and PR summaries — without living inside the Project board all day.

You pick which Project(s) and repos to follow. 

#### How does it work?

1. You sign in with GitHub (`gh` / token).
2. A small **browser UI** lists Projects from your user + orgs you can access.
3. You multi-select Projects, pick repos from a searchable dropdown, then **Save and build**.
4. That writes a local snapshot: HTML board (+ optional Cursor canvas) with stats, filters, cycle timelines, and PR solution summaries parsed from your PR descriptions.

| Output | Where |
| ------ | ----- |
| Board in the browser | `dist/index.html` or http://127.0.0.1:8765/board while configure is running |
| Cursor canvas | `dist/cycle-time-board.canvas.tsx` |

GitHub MCP is **not** required. Scripts talk to GitHub through the `gh` CLI.

## Installation

Anyone can use it by cloning the repo. You’ll need **Python 3** and the [GitHub CLI](https://cli.github.com/) (`gh`).

```bash
git clone https://github.com/pascazzioIsAbyayalan/cycle-time-board.git
cd cycle-time-board

# (once) sign in to GitHub if you haven’t already
gh auth login
```

### First-time setup
```bash
python3 scripts/configure.py
```

That opens a local page (same idea as `gh auth login`):

1. **Login with GitHub** if the UI says you’re not signed in (watch the terminal for a one-time code).
2. **Select one or more Projects**.
3. Open **Switch repositories**, search, and check the repos you care about.
4. Optional: title + Area filter.
5. Click **Save and build board**.

Leave that terminal open while you use the UI (`Ctrl+C` to stop).

Your choices are saved locally in `boards.json` (gitignored — not committed).

### Open the board

While configure is still running:

```text
http://127.0.0.1:8765/board
```

Or open the static file anytime:

```bash
open dist/index.html        # macOS
# xdg-open dist/index.html  # Linux
```

### Keep it up to date

On the board itself:

- **Sync with GitHub** — fetch + regenerate now  
- **Auto-sync** — every 5 minutes while the page stays open  

(Both need `python3 scripts/configure.py` still running in a terminal.)

Or from the CLI:

```bash
python3 scripts/fetch.py
python3 scripts/generate_html.py
```

### Updating from an older clone

If you already cloned this repo before the configure UI:

```bash
cd cycle-time-board
git pull
python3 scripts/configure.py
```

Then use **Save and build** again so your board matches the new multi-project / sync flow.

### Optional: Cursor skill + canvas

```bash
mkdir -p ~/.cursor/skills/cycle-time-board
cp SKILL.md ~/.cursor/skills/cycle-time-board/SKILL.md
ln -sfn "$(pwd)" ~/.cursor/skills/cycle-time-board-pkg

python3 scripts/generate_canvas.py
# copy dist/cycle-time-board.canvas.tsx into your workspace canvases/ folder
```

In Cursor chat:

> Using the cycle-time-board skill, refresh the board from GitHub and regenerate the HTML + canvas.

## Recomendations

- Prefer opening the board at **http://127.0.0.1:8765/board** so **Sync** and **Auto-sync** work.
- Only issues **assigned to you** show up — check assignees on GitHub if the board looks empty.
- Pick the repos that actually hold your issues; more repos = slower first fetch.
- For org Projects, authorize SSO on your token if GitHub asks.
- Prefer terminal prompts instead of the UI? `python3 scripts/configure.py --cli`
- Tweak it to your preference 👾

## Troubleshooting

| Problem | What to try |
| ------- | ----------- |
| Sync button disabled | Run `python3 scripts/configure.py` and open the board via http://127.0.0.1:8765/board |
| No Projects listed | Confirm you can open the Project in GitHub; token needs `read:project` (+ `read:org` / SSO) |
| Empty board | Issues must be assigned to **your** login; check selected repos |
| No PR Solution Summary | Fill in the PR description (`## Description`, `## Changes made`, etc.), then Sync again |
| Wrong user | `gh api user --jq .login` |

## Sharing

- Send someone `dist/index.html` for a snapshot (no GitHub auth needed to view).
- Share this repo so teammates can configure **their own** board the same way.
