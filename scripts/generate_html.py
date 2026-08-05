#!/usr/bin/env python3
"""Build standalone HTML matching the UI Touch Grass board (personal)."""

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
    resolve_person,
)

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "templates" / "board.html"
OUT = ROOT / "dist" / "index.html"


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate static HTML cycle-time board")
    parser.add_argument("--boards", type=Path, default=BOARDS_PATH)
    parser.add_argument("--out", type=Path, default=OUT)
    parser.add_argument("--person", help="Override login (default: gh auth / GH_TOKEN)")
    parser.add_argument(
        "--no-auth",
        action="store_true",
        help="Skip GitHub identity; use boards.json person or newest data file",
    )
    args = parser.parse_args()

    cfg = load_config(args.boards if args.boards.exists() else None)

    login = None
    name = None
    if args.person or not args.no_auth or (cfg.get("person") or {}).get("login"):
        try:
            person = resolve_person(
                cfg,
                login_override=args.person,
                use_auth=not args.no_auth,
            )
            login, name = person["login"], person.get("name")
        except (RuntimeError, SystemExit):
            login = None

    if not login:
        # Offline: use sole / newest snapshot in data/people
        files = sorted(DATA_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
        if not files:
            raise SystemExit("No data found. Run: python3 scripts/fetch.py")
        login = files[0].stem

    data_path = data_path_for(login)
    if not data_path.exists():
        raise SystemExit(f"Missing data file: {data_path}. Run scripts/fetch.py first.")

    data = json.loads(data_path.read_text())
    payload = {
        "title": cfg.get("title") or "UI Touch Grass — Cycle Time",
        "project": cfg["project"],
        "person": {
            "login": login,
            "name": name or data.get("name") or login,
        },
        "fetchedAt": data.get("fetchedAt"),
        "issues": data.get("issues") or [],
    }

    template = TEMPLATE.read_text()
    if "__BOARD_DATA__" not in template:
        raise SystemExit("templates/board.html missing __BOARD_DATA__ placeholder")
    html = template.replace("__BOARD_DATA__", json.dumps(payload))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(html)
    print(f"Wrote {args.out} (user: {login})")
    print(f"Open in browser: file://{args.out.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
