#!/usr/bin/env python3
"""Shared helpers for CLI and browser board configuration."""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import github_viewer, run_gh_json, save_config  # noqa: E402

REPO_SLUG_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")


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


def discover_projects(*, quiet: bool = False) -> list[dict]:
    viewer = github_viewer()
    login = viewer["login"]
    if not quiet:
        print(f"Signed in as {login}")
        print("Discovering GitHub Projects you can access…\n")

    owners = [login, *list_org_logins()]
    seen: set[tuple[str, int]] = set()
    projects: list[dict] = []
    for owner in owners:
        if not quiet:
            print(f"  Checking {owner}…")
        for p in list_projects_for_owner(owner, viewer_login=login):
            key = (p["owner"], p["number"])
            if key in seen:
                continue
            seen.add(key)
            projects.append(p)
    return projects


def list_repos_for_owners(owners: list[str], *, limit: int = 100) -> list[dict]:
    """List repositories for the given user/org owners (nameWithOwner + metadata)."""
    seen: set[str] = set()
    out: list[dict] = []
    for owner in owners:
        owner = (owner or "").strip()
        if not owner:
            continue
        try:
            rows = run_gh_json(
                [
                    "repo",
                    "list",
                    owner,
                    "--limit",
                    str(limit),
                    "--json",
                    "nameWithOwner,name,isFork,visibility,updatedAt",
                ]
            )
        except RuntimeError as e:
            print(f"  (skip repos for {owner}: {str(e).splitlines()[0][:120]})", file=sys.stderr)
            continue
        if not isinstance(rows, list):
            continue
        for row in rows:
            if not isinstance(row, dict):
                continue
            slug = row.get("nameWithOwner")
            if not slug or slug in seen:
                continue
            seen.add(slug)
            out.append(
                {
                    "nameWithOwner": slug,
                    "name": row.get("name") or slug.split("/")[-1],
                    "isFork": bool(row.get("isFork")),
                    "visibility": row.get("visibility") or "",
                    "updatedAt": row.get("updatedAt") or "",
                    "owner": owner,
                }
            )
    out.sort(key=lambda r: r["nameWithOwner"].lower())
    return out


def parse_repos(raw: str | list[str]) -> list[str]:
    if isinstance(raw, list):
        parts = raw
    else:
        parts = [p.strip() for p in str(raw).split(",")]
    repos: list[str] = []
    for part in parts:
        repo = str(part).strip()
        if not repo:
            continue
        if not REPO_SLUG_RE.fullmatch(repo):
            raise ValueError(f"Invalid repo slug: {repo} (expected owner/name)")
        if repo not in repos:
            repos.append(repo)
    return repos


def build_config(
    *,
    projects: list[dict] | None = None,
    project: dict | None = None,
    repos: list[str],
    title: str | None = None,
    area: str | None = None,
) -> dict:
    selected = list(projects or [])
    if not selected and project:
        selected = [project]
    if not selected:
        raise ValueError("Select at least one Project")
    if not repos:
        raise ValueError("At least one repository is required")

    projects_out: list[dict] = []
    for p in selected:
        if not p.get("owner") or p.get("number") is None:
            raise ValueError("Each project needs owner and number")
        item = {
            "owner": p["owner"],
            "number": int(p["number"]),
            "url": p.get("url")
            or f"https://github.com/orgs/{p['owner']}/projects/{p['number']}",
        }
        if p.get("title"):
            item["title"] = p["title"]
        # Per-project area, or shared area applied to all
        proj_area = p.get("area") or area
        if proj_area:
            item["area"] = proj_area
        projects_out.append(item)

    if (title or "").strip():
        board_title = title.strip()
    elif len(projects_out) == 1:
        board_title = f"{selected[0].get('title') or 'Project'} — Cycle Time"
    else:
        board_title = f"{len(projects_out)} Projects — Cycle Time"

    return {
        "title": board_title,
        "projects": projects_out,
        # Legacy single-project field (primary / first selection)
        "project": projects_out[0],
        "repos": repos,
    }


def save_board_config(cfg: dict, out: Path | None = None) -> Path:
    return save_config(cfg, out)


def auth_status() -> dict:
    try:
        user = github_viewer()
        return {
            "authed": True,
            "login": user["login"],
            "name": user.get("name") or user["login"],
            "error": None,
        }
    except RuntimeError as e:
        return {
            "authed": False,
            "login": None,
            "name": None,
            "error": str(e).splitlines()[0][:200],
        }
