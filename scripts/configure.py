#!/usr/bin/env python3
"""Interactive setup: pick a GitHub Project you can access, then save boards.json."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import (  # noqa: E402
    BOARDS_PATH,
    github_viewer,
    run_gh_json,
    save_config,
)


def list_org_logins() -> list[str]:
    try:
        orgs = run_gh_json(["api", "user/orgs", "--paginate"])
    except RuntimeError:
        return []
    if not isinstance(orgs, list):
        return []
    return [o["login"] for o in orgs if isinstance(o, dict) and o.get("login")]


def list_projects_for_owner(owner: str, *, viewer_login: str) -> list[dict]:
    """Return project dicts: owner, number, title, url."""
    try:
        raw = run_gh_json(
            ["project", "list", "--owner", owner, "--limit", "100", "--format", "json"]
        )
    except RuntimeError as e:
        if "404" in str(e) or "not found" in str(e).lower():
            return []
        print(f"  (skip {owner}: {str(e).splitlines()[0][:120]})", file=sys.stderr)
        return []

    items = raw.get("projects", raw) if isinstance(raw, dict) else raw
    if not isinstance(items, list):
        return []

    out = []
    for p in items:
        if not isinstance(p, dict):
            continue
        number = p.get("number")
        if number is None:
            continue
        title = p.get("title") or p.get("name") or f"Project {number}"
        url = p.get("url")
        if not url:
            kind = "users" if owner == viewer_login else "orgs"
            url = f"https://github.com/{kind}/{owner}/projects/{number}"
        out.append(
            {
                "owner": owner,
                "number": int(number),
                "title": title,
                "url": url,
            }
        )
    return out


def discover_projects() -> list[dict]:
    viewer = github_viewer()
    login = viewer["login"]
    print(f"Signed in as {login}")
    print("Discovering GitHub Projects you can access…\n")

    owners = [login, *list_org_logins()]
    seen: set[tuple[str, int]] = set()
    projects: list[dict] = []
    for owner in owners:
        print(f"  Checking {owner}…")
        for p in list_projects_for_owner(owner, viewer_login=login):
            key = (p["owner"], p["number"])
            if key in seen:
                continue
            seen.add(key)
            projects.append(p)
    return projects


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
    repos = []
    for part in raw.split(","):
        repo = part.strip()
        if not repo:
            continue
        if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repo):
            print(f"Skipping invalid repo slug: {repo}")
            continue
        repos.append(repo)
    return repos


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


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Choose a GitHub Project board and write boards.json"
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=BOARDS_PATH,
        help="Where to write boards.json",
    )
    args = parser.parse_args()

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

    idx = prompt_choice(len(projects))
    chosen = projects[idx - 1]

    title = prompt_title(chosen["title"])
    repos = prompt_repos()
    if not repos:
        print("At least one repository is required.", file=sys.stderr)
        return 1
    area = prompt_area()

    project = {
        "owner": chosen["owner"],
        "number": chosen["number"],
        "url": chosen["url"],
    }
    if area:
        project["area"] = area

    cfg = {
        "title": title,
        "project": project,
        "repos": repos,
    }
    out = save_config(cfg, args.out)
    print(f"\nWrote {out}")
    print("Next:")
    print("  python3 scripts/fetch.py")
    print("  python3 scripts/generate_html.py")
    print("  open dist/index.html")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
