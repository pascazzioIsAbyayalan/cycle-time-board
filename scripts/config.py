#!/usr/bin/env python3
"""Shared config + GitHub identity resolution (via gh / GH_TOKEN)."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BOARDS_PATH = ROOT / "boards.json"
EXAMPLE_PATH = ROOT / "boards.example.json"
DATA_DIR = ROOT / "data" / "people"

# No project is selected by default — run scripts/configure.py first.
DEFAULT_CONFIG: dict = {
    "title": "Cycle Time Board",
    "project": None,
    "repos": [],
}


def run_gh_json(args: list[str]) -> dict | list:
    env = os.environ.copy()
    token = env.get("GH_TOKEN") or env.get("GITHUB_TOKEN")
    if token and "GH_TOKEN" not in env:
        env["GH_TOKEN"] = token
    r = subprocess.run(["gh", *args], capture_output=True, text=True, env=env)
    if r.returncode != 0:
        hint = (
            "Authenticate with GitHub first:\n"
            "  gh auth login\n"
            "or set a token:\n"
            "  export GH_TOKEN=ghp_xxxxxxxx\n"
            "  # classic PAT needs at least: repo, read:project, read:org (if private org)\n"
        )
        detail = (r.stderr or r.stdout or "gh failed").strip()
        raise RuntimeError(f"{detail}\n\n{hint}")
    if not r.stdout.strip():
        return {}
    return json.loads(r.stdout)


def github_viewer() -> dict:
    """Return {login, name, ...} for the authenticated GitHub user."""
    user = run_gh_json(["api", "user"])
    if not isinstance(user, dict) or not user.get("login"):
        raise RuntimeError("Could not resolve GitHub user from auth token / gh session.")
    return user


def load_config(boards_path: Path | None = None) -> dict:
    """Load boards.json (required for project selection)."""
    cfg = json.loads(json.dumps(DEFAULT_CONFIG))
    path = boards_path or BOARDS_PATH
    if path and path.exists():
        overlay = json.loads(path.read_text())
        for key, value in overlay.items():
            if key == "project" and isinstance(value, dict):
                base = cfg.get("project") if isinstance(cfg.get("project"), dict) else {}
                merged = {**(base or {}), **value}
                cfg["project"] = merged
            else:
                cfg[key] = value
    return cfg


def require_project(cfg: dict) -> dict:
    """Return project dict or exit with setup instructions."""
    project = cfg.get("project")
    if not isinstance(project, dict) or not project.get("owner") or not project.get("number"):
        print(
            "No GitHub Project selected yet.\n\n"
            "Pick a board you have access to:\n"
            "  python3 scripts/configure.py\n\n"
            "That writes boards.json (owner, project number, repos).\n"
            "See boards.example.json for the file shape.",
            file=sys.stderr,
        )
        raise SystemExit(2)
    return project


def require_repos(cfg: dict) -> list[str]:
    repos = cfg.get("repos") or []
    if not repos:
        print(
            "No repositories configured in boards.json.\n"
            "Re-run: python3 scripts/configure.py\n"
            "or add a \"repos\": [\"owner/name\"] list to boards.json.",
            file=sys.stderr,
        )
        raise SystemExit(2)
    return list(repos)


def resolve_person(
    cfg: dict,
    *,
    login_override: str | None = None,
    use_auth: bool = True,
) -> dict:
    """
    Resolve whose board to build.

    Priority:
      1. login_override (--person)
      2. authenticated GitHub user (gh / GH_TOKEN) when use_auth
      3. boards.json person (optional override / offline fallback)
    """
    if login_override:
        return {"login": login_override, "name": login_override}

    if use_auth:
        try:
            user = github_viewer()
            return {
                "login": user["login"],
                "name": user.get("name") or user["login"],
            }
        except RuntimeError:
            if cfg.get("person", {}).get("login"):
                p = cfg["person"]
                return {"login": p["login"], "name": p.get("name") or p["login"]}
            raise

    if cfg.get("person", {}).get("login"):
        p = cfg["person"]
        return {"login": p["login"], "name": p.get("name") or p["login"]}

    print(
        "No GitHub identity found. Run `gh auth login` or set GH_TOKEN.",
        file=sys.stderr,
    )
    raise SystemExit(2)


def data_path_for(login: str) -> Path:
    return DATA_DIR / f"{login}.json"


def save_config(cfg: dict, path: Path | None = None) -> Path:
    out = path or BOARDS_PATH
    out.write_text(json.dumps(cfg, indent=2) + "\n")
    return out
