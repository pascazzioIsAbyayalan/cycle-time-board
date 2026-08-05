#!/usr/bin/env python3
"""Choose a GitHub Project board and write boards.json (browser UI by default)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from configure_lib import (  # noqa: E402
    build_config,
    discover_projects,
    parse_repos,
    save_board_config,
)
from configure_ui import DEFAULT_HOST, DEFAULT_PORT, run_ui  # noqa: E402


def prompt_choice(n: int) -> int:
    while True:
        raw = input(f"Select a project [1–{n}]: ").strip()
        if not raw.isdigit():
            print("Enter a number.")
            continue
        i = int(raw)
        if 1 <= i <= n:
            return i
        print(f"Choose between 1 and {n}.")


def prompt_repos(default: str = "") -> list[str]:
    print(
        "\nRepositories to scan for issues assigned to you "
        "(comma-separated owner/name)."
    )
    print("Example: acme/web-app, acme/api")
    if default:
        print(f"Default [{default}]")
    raw = input("> ").strip() or default
    try:
        return parse_repos(raw)
    except ValueError as e:
        print(str(e), file=sys.stderr)
        return []


def prompt_area() -> str | None:
    print(
        "\nOptional Project “Area” field filter "
        "(leave blank to include all areas on that board)."
    )
    raw = input("Area filter: ").strip()
    return raw or None


def prompt_title(project_title: str) -> str:
    default = f"{project_title} — Cycle Time"
    raw = input(f"Board title [{default}]: ").strip()
    return raw or default


def run_cli(*, out: Path) -> int:
    try:
        projects = discover_projects()
    except RuntimeError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    if not projects:
        print(
            "\nNo Projects found for your user/orgs.\n"
            "Make sure you can open the board in GitHub, and that your token "
            "has read:project (and read:org / SSO if needed).\n"
            "You can still create boards.json by hand from boards.example.json.",
            file=sys.stderr,
        )
        return 1

    print(f"\nFound {len(projects)} project(s):\n")
    for i, p in enumerate(projects, 1):
        print(f"  {i:3}. {p['owner']} #{p['number']} — {p['title']}")
        print(f"       {p['url']}")

    print("\nSelect one or more projects (comma-separated numbers).")
    raw = input(f"Projects [1–{len(projects)}]: ").strip()
    chosen: list[dict] = []
    for part in raw.split(","):
        part = part.strip()
        if not part.isdigit():
            continue
        i = int(part)
        if 1 <= i <= len(projects):
            chosen.append(projects[i - 1])
    if not chosen:
        idx = prompt_choice(len(projects))
        chosen = [projects[idx - 1]]

    title_default = chosen[0]["title"] if len(chosen) == 1 else f"{len(chosen)} Projects"
    title = prompt_title(title_default)
    repos = prompt_repos()
    if not repos:
        print("At least one repository is required.", file=sys.stderr)
        return 1
    area = prompt_area()

    try:
        cfg = build_config(projects=chosen, repos=repos, title=title, area=area)
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    path = save_board_config(cfg, out)
    print(f"\nWrote {path}")
    print("Next:")
    print("  python3 scripts/fetch.py")
    print("  python3 scripts/generate_html.py")
    print("  open dist/index.html")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Choose a GitHub Project board and write boards.json"
    )
    parser.add_argument(
        "--cli",
        action="store_true",
        help="Use terminal prompts instead of the browser UI",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Where to write boards.json (CLI mode)",
    )
    parser.add_argument("--host", default=DEFAULT_HOST, help="UI bind host")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="UI port")
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Do not auto-open a browser tab (UI mode)",
    )
    args = parser.parse_args()

    if args.cli:
        from config import BOARDS_PATH  # noqa: WPS433

        return run_cli(out=args.out or BOARDS_PATH)

    return run_ui(host=args.host, port=args.port, open_browser=not args.no_browser)


if __name__ == "__main__":
    raise SystemExit(main())
