#!/usr/bin/env python3
"""Build standalone HTML matching the UI Touch Grass board (personal)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BOARDS_PATH = ROOT / "boards.json"
DATA_DIR = ROOT / "data" / "people"
TEMPLATE = ROOT / "templates" / "board.html"
OUT = ROOT / "dist" / "index.html"


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate static HTML cycle-time board")
    parser.add_argument("--boards", type=Path, default=BOARDS_PATH)
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args()

    cfg = json.loads(args.boards.read_text())
    person = cfg.get("person") or {"login": (cfg.get("people") or [{}])[0].get("login")}
    login = person["login"]
    data_path = DATA_DIR / f"{login}.json"
    if not data_path.exists():
        raise SystemExit(f"Missing data file: {data_path}. Run scripts/fetch.py first.")

    data = json.loads(data_path.read_text())
    payload = {
        "title": cfg.get("title") or "UI Touch Grass — Cycle Time",
        "project": cfg["project"],
        "person": {
            "login": login,
            "name": person.get("name") or data.get("name") or login,
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
    print(f"Wrote {args.out}")
    print(f"Open in browser: file://{args.out.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
