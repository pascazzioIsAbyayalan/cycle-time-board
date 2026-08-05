#!/usr/bin/env python3
"""Generate a Cursor .canvas.tsx cycle-time board (personal)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import (  # noqa: E402
    BOARDS_PATH,
    DATA_DIR,
    data_path_for,
    load_config,
    require_project,
    require_repos,
    resolve_person,
)

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "templates" / "canvas.tsx.template"
OUT = ROOT / "dist" / "cycle-time-board.canvas.tsx"


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate Cursor canvas for personal cycle-time board")
    parser.add_argument("--boards", type=Path, default=BOARDS_PATH)
    parser.add_argument("--out", type=Path, default=OUT)
    parser.add_argument("--person", help="Override login (default: gh auth / GH_TOKEN)")
    parser.add_argument(
        "--no-auth",
        action="store_true",
        help="Skip GitHub identity; use boards.json person or newest data file",
    )
    args = parser.parse_args()

    if not args.boards.exists():
        raise SystemExit("No boards.json — run: python3 scripts/configure.py")

    cfg = load_config(args.boards)
    project = require_project(cfg)
    repos = require_repos(cfg)

    login = None
    if args.person or not args.no_auth or (cfg.get("person") or {}).get("login"):
        try:
            person = resolve_person(
                cfg,
                login_override=args.person,
                use_auth=not args.no_auth,
            )
            login = person["login"]
        except (RuntimeError, SystemExit):
            login = None

    if not login:
        files = sorted(DATA_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
        if not files:
            raise SystemExit("No data found. Run: python3 scripts/fetch.py")
        login = files[0].stem

    data_path = data_path_for(login)
    if not data_path.exists():
        raise SystemExit(f"Missing data file: {data_path}. Run scripts/fetch.py first.")

    data = json.loads(data_path.read_text())
    issues = data.get("issues") or []
    fetched = (data.get("fetchedAt") or "")[:10] or "unknown"

    clean = [{k: v for k, v in issue.items() if v is not None} for issue in issues]

    template = TEMPLATE.read_text()
    for key in (
        "__ISSUES__",
        "__FETCHED_AT__",
        "__BOARD_TITLE__",
        "__BOARD_REPOS__",
        "__PROJECT_URL__",
        "__PROJECT_NUMBER__",
    ):
        if key not in template:
            raise SystemExit(f"canvas template missing {key} placeholder")

    title = cfg.get("title") or "Cycle Time Board"
    canvas = (
        template
        .replace("__ISSUES__", json.dumps(clean, indent=2))
        .replace("__FETCHED_AT__", fetched)
        .replace("__BOARD_TITLE__", title)
        .replace("__BOARD_REPOS__", ", ".join(repos) or project["owner"])
        .replace("__PROJECT_URL__", project.get("url") or "#")
        .replace("__PROJECT_NUMBER__", str(project["number"]))
    )

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(canvas)
    print(f"Wrote {args.out} ({len(clean)} issues, user: {login}, fetched {fetched})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
