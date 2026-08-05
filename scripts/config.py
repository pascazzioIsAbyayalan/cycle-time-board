#!/usr/bin/env python3
"""Shared defaults + GitHub identity resolution (via gh / GH_TOKEN)."""

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

DEFAULT_CONFIG = {
    "title": "UI Touch Grass — Cycle Time",
    "project": {
        "owner": "Kuadrant",
        "number": 18,
        "url": "https://github.com/orgs/Kuadrant/projects/18",
        "area": "UI Touch Grass",
    },
    "repos": ["Kuadrant/kuadrant-console-plugin"],
}


def run_gh_json(args: list[str]) -> dict | list:
    env = os.environ.copy()
    # Prefer explicit token env vars; gh also reads GH_TOKEN
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
    return json.loads(r.stdout)


def github_viewer() -> dict:
    """Return {login, name, ...} for the authenticated GitHub user."""
    user = run_gh_json(["api", "user"])
    if not isinstance(user, dict) or not user.get("login"):
        raise RuntimeError("Could not resolve GitHub user from auth token / gh session.")
    return user


def load_config(boards_path: Path | None = None) -> dict:
    """Merge optional boards.json over built-in defaults. person is optional."""
    cfg = json.loads(json.dumps(DEFAULT_CONFIG))  # deep copy
    path = boards_path or BOARDS_PATH
    if path.exists():
        overlay = json.loads(path.read_text())
        for key, value in overlay.items():
            if key == "project" and isinstance(value, dict):
                cfg.setdefault("project", {}).update(value)
            else:
                cfg[key] = value
    return cfg


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
                # Fall back to config if auth unavailable
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
