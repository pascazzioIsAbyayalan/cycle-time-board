#!/usr/bin/env python3
"""Local browser UI for choosing a GitHub Project and writing boards.json."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import BOARDS_PATH, ROOT, load_config  # noqa: E402
from configure_lib import (  # noqa: E402
    auth_status,
    build_config,
    discover_projects,
    list_repos_for_owners,
    parse_repos,
    save_board_config,
)

TEMPLATE = ROOT / "templates" / "configure.html"
BOARD_HTML = ROOT / "dist" / "index.html"
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8765

_login_lock = threading.Lock()
_login_state: dict = {
    "running": False,
    "error": None,
    "finished": False,
}

_build_lock = threading.Lock()
_build_state: dict = {
    "running": False,
    "done": False,
    "stage": None,
    "message": None,
    "error": None,
    "boardUrl": None,
    "path": None,
    "startedAt": None,
    "finishedAt": None,
}


def _set_build(**kwargs) -> None:
    with _build_lock:
        _build_state.update(kwargs)


def _get_build() -> dict:
    with _build_lock:
        return dict(_build_state)


def _run_gh_login() -> None:
    global _login_state
    with _login_lock:
        _login_state = {"running": True, "error": None, "finished": False}
    env = os.environ.copy()
    try:
        stdin = open("/dev/tty", "r") if Path("/dev/tty").exists() else subprocess.DEVNULL
        try:
            r = subprocess.run(
                ["gh", "auth", "login", "--web", "-p", "https", "-h", "github.com"],
                env=env,
                stdin=stdin,
            )
        finally:
            if stdin is not subprocess.DEVNULL:
                stdin.close()
        with _login_lock:
            _login_state = {
                "running": False,
                "error": None
                if r.returncode == 0
                else "gh auth login failed. Run `gh auth login` in a terminal, then reload.",
                "finished": True,
            }
    except Exception as e:  # noqa: BLE001
        with _login_lock:
            _login_state = {
                "running": False,
                "error": str(e)[:300],
                "finished": True,
            }


def _run_build(cfg: dict | None, host: str, port: int, *, refresh_only: bool = False) -> None:
    _set_build(
        running=True,
        done=False,
        stage="save" if not refresh_only else "fetch",
        message="Writing boards.json…" if not refresh_only else "Syncing with GitHub…",
        error=None,
        boardUrl=None,
        path=None,
        startedAt=time.time(),
        finishedAt=None,
    )
    try:
        if refresh_only:
            if not BOARDS_PATH.exists():
                raise RuntimeError(
                    "No boards.json yet. Run python3 scripts/configure.py and save a board first."
                )
            cfg = load_config(BOARDS_PATH)
            _set_build(path=str(BOARDS_PATH))
        else:
            assert cfg is not None
            out = save_board_config(cfg, BOARDS_PATH)
            _set_build(path=str(out))

        repos = cfg.get("repos") or []
        _set_build(
            stage="fetch",
            message="Fetching your assigned issues from GitHub… (this can take a minute with several repos)",
        )
        print(f"\n→ Fetching issues for {len(repos)} repo(s)…", flush=True)

        fetch = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "fetch.py"), "--boards", str(BOARDS_PATH)],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
        )
        if fetch.returncode != 0:
            detail = (fetch.stderr or fetch.stdout or "fetch failed").strip()
            raise RuntimeError(f"fetch.py failed:\n{detail[:800]}")

        _set_build(stage="generate", message="Generating HTML board…")
        print("→ Generating HTML…", flush=True)
        gen = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "generate_html.py"),
                "--boards",
                str(BOARDS_PATH),
            ],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
        )
        if gen.returncode != 0:
            detail = (gen.stderr or gen.stdout or "generate failed").strip()
            raise RuntimeError(f"generate_html.py failed:\n{detail[:800]}")

        board_url = f"http://{host}:{port}/board"
        _set_build(
            running=False,
            done=True,
            stage="done",
            message="Board ready.",
            boardUrl=board_url,
            finishedAt=time.time(),
        )
        print(f"→ Board ready: {board_url}\n", flush=True)
    except Exception as e:  # noqa: BLE001
        _set_build(
            running=False,
            done=True,
            stage="error",
            message=None,
            error=str(e)[:900],
            finishedAt=time.time(),
        )
        print(f"→ Build failed: {e}\n", flush=True)


class ConfigureHandler(BaseHTTPRequestHandler):
    server_version = "CycleTimeConfigure/1.0"

    def log_message(self, fmt: str, *args) -> None:
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))

    def _cors(self) -> None:
        # Allow the static board (file:// or another port) to call sync APIs.
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _send(self, code: int, body: bytes, content_type: str) -> None:
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self._cors()
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self) -> None:  # noqa: N802
        self.send_response(204)
        self._cors()
        self.end_headers()

    def _json(self, code: int, payload: dict) -> None:
        data = json.dumps(payload).encode("utf-8")
        self._send(code, data, "application/json; charset=utf-8")

    def _read_json(self) -> dict:
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length) if length else b"{}"
        if not raw:
            return {}
        try:
            data = json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON: {e}") from e
        if not isinstance(data, dict):
            raise ValueError("JSON body must be an object")
        return data

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path in {"/", "/index.html"}:
            html = TEMPLATE.read_text(encoding="utf-8").encode("utf-8")
            self._send(200, html, "text/html; charset=utf-8")
            return
        if path == "/board":
            if not BOARD_HTML.exists():
                self._json(404, {"error": "Board not built yet. Use Save and build board."})
                return
            body = BOARD_HTML.read_bytes()
            self._send(200, body, "text/html; charset=utf-8")
            return
        if path == "/api/status":
            status = auth_status()
            with _login_lock:
                login = dict(_login_state)
            status["loginFlow"] = login
            status["build"] = _get_build()
            self._json(200, status)
            return
        if path == "/api/build":
            self._json(200, _get_build())
            return
        if path == "/api/projects":
            status = auth_status()
            if not status["authed"]:
                self._json(401, {"error": "Not signed in. Use Login with GitHub first.", **status})
                return
            try:
                projects = discover_projects(quiet=True)
            except RuntimeError as e:
                self._json(500, {"error": str(e).splitlines()[0][:300]})
                return
            current = None
            if BOARDS_PATH.exists():
                try:
                    current = load_config(BOARDS_PATH)
                except Exception:
                    current = None
            self._json(
                200,
                {
                    "login": status["login"],
                    "projects": projects,
                    "current": current,
                },
            )
            return
        if path == "/api/repos":
            status = auth_status()
            if not status["authed"]:
                self._json(401, {"error": "Not signed in. Use Login with GitHub first."})
                return
            qs = parse_qs(urlparse(self.path).query)
            owners_raw = (qs.get("owners") or [""])[0]
            owners = [o.strip() for o in owners_raw.split(",") if o.strip()]
            if not owners:
                self._json(400, {"error": "Pass ?owners=org1,org2"})
                return
            try:
                repos = list_repos_for_owners(owners)
            except RuntimeError as e:
                self._json(500, {"error": str(e).splitlines()[0][:300]})
                return
            self._json(200, {"owners": owners, "repos": repos})
            return
        self._json(404, {"error": "Not found"})

    def do_POST(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        try:
            if path == "/api/login":
                self._handle_login()
                return
            if path == "/api/save":
                self._handle_save(build=False)
                return
            if path == "/api/save-and-build":
                self._handle_save(build=True)
                return
            if path == "/api/refresh":
                self._handle_refresh()
                return
        except ValueError as e:
            self._json(400, {"error": str(e)})
            return
        except RuntimeError as e:
            self._json(500, {"error": str(e)})
            return
        self._json(404, {"error": "Not found"})

    def _handle_login(self) -> None:
        with _login_lock:
            if _login_state.get("running"):
                self._json(200, {"started": True, "running": True})
                return
        thread = threading.Thread(target=_run_gh_login, daemon=True)
        thread.start()
        print(
            "\n→ Complete GitHub login in your browser / this terminal "
            "(gh may print a one-time code).\n",
            flush=True,
        )
        self._json(200, {"started": True, "running": True})

    def _config_from_body(self) -> dict:
        body = self._read_json()
        projects = body.get("projects")
        project = body.get("project")
        if isinstance(projects, list) and projects:
            selected = projects
        elif isinstance(project, dict):
            selected = [project]
        else:
            raise ValueError("Select at least one Project")
        repos_raw = body.get("repos") or []
        repos = parse_repos(repos_raw if isinstance(repos_raw, list) else str(repos_raw))
        area = body.get("area") or None
        if isinstance(area, str):
            area = area.strip() or None
        return build_config(
            projects=selected,
            repos=repos,
            title=body.get("title"),
            area=area,
        )

    def _handle_save(self, *, build: bool) -> None:
        cfg = self._config_from_body()
        if not build:
            out = save_board_config(cfg, BOARDS_PATH)
            self._json(200, {"ok": True, "path": str(out), "config": cfg})
            return

        self._start_build(cfg, refresh_only=False)

    def _link_host_port(self) -> tuple[str, int]:
        host = self.server.server_address[0]  # type: ignore[attr-defined]
        port = self.server.server_address[1]  # type: ignore[attr-defined]
        link_host = "127.0.0.1" if host in {"0.0.0.0", "::"} else host
        return link_host, port

    def _start_build(self, cfg: dict | None, *, refresh_only: bool) -> None:
        with _build_lock:
            if _build_state.get("running"):
                self._json(
                    409,
                    {
                        "error": "A sync is already running. Wait for it to finish.",
                        "build": dict(_build_state),
                    },
                )
                return

        link_host, port = self._link_host_port()
        thread = threading.Thread(
            target=_run_build,
            kwargs={"cfg": cfg, "host": link_host, "port": port, "refresh_only": refresh_only},
            daemon=True,
        )
        thread.start()
        self._json(
            202,
            {
                "started": True,
                "message": "Sync started. Poll /api/build for progress.",
                "build": _get_build(),
            },
        )

    def _handle_refresh(self) -> None:
        """Re-fetch + regenerate using the existing boards.json (no form body)."""
        if not BOARDS_PATH.exists():
            self._json(
                400,
                {
                    "error": "No boards.json yet. Open the configure UI and save a board first.",
                },
            )
            return
        status = auth_status()
        if not status["authed"]:
            self._json(
                401,
                {
                    "error": "Not signed in to GitHub. Run: gh auth login  (or open configure UI → Login)",
                },
            )
            return
        self._start_build(None, refresh_only=True)


def run_ui(
    *,
    host: str = DEFAULT_HOST,
    port: int = DEFAULT_PORT,
    open_browser: bool = True,
) -> int:
    if not TEMPLATE.exists():
        print(f"Missing template: {TEMPLATE}", file=sys.stderr)
        return 1

    try:
        httpd = ThreadingHTTPServer((host, port), ConfigureHandler)
    except OSError as e:
        print(f"Could not bind {host}:{port}: {e}", file=sys.stderr)
        print("Try: python3 scripts/configure.py --port 8766", file=sys.stderr)
        return 1

    url = f"http://{host}:{port}/"
    print(f"Configure UI: {url}", flush=True)
    print("Leave this terminal open. Press Ctrl+C to stop.\n", flush=True)

    if open_browser:
        threading.Timer(0.4, lambda: webbrowser.open(url)).start()

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped configure UI.")
    finally:
        httpd.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(run_ui())
