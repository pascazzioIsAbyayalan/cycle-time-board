#!/usr/bin/env python3
"""Generate a Cursor .canvas.tsx matching the UI Touch Grass board (personal)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BOARDS_PATH = ROOT / "boards.json"
DATA_DIR = ROOT / "data" / "people"
TEMPLATE = ROOT / "templates" / "canvas.tsx.template"
OUT = ROOT / "dist" / "cycle-time-board.canvas.tsx"


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate Cursor canvas for personal cycle-time board")
    parser.add_argument("--boards", type=Path, default=BOARDS_PATH)
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args()

    cfg = json.loads(args.boards.read_text())
    person = cfg.get("person") or {"login": cfg.get("defaultPerson")}
    login = person["login"]
    data_path = DATA_DIR / f"{login}.json"
    if not data_path.exists():
        raise SystemExit(f"Missing data file: {data_path}. Run scripts/fetch.py first.")

    data = json.loads(data_path.read_text())
    issues = data.get("issues") or []
    fetched = (data.get("fetchedAt") or "")[:10] or "unknown"

    # Strip nulls for cleaner TS literals (optional fields)
    clean = []
    for issue in issues:
        item = {k: v for k, v in issue.items() if v is not None}
        clean.append(item)

    template = TEMPLATE.read_text()
    if "__ISSUES__" not in template:
        raise SystemExit("canvas template missing __ISSUES__ placeholder")

    canvas = (
        template
        .replace("__ISSUES__", json.dumps(clean, indent=2))
        .replace("__FETCHED_AT__", fetched)
    )

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(canvas)
    print(f"Wrote {args.out} ({len(clean)} issues, fetched {fetched})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
