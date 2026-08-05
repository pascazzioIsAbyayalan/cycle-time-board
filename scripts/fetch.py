#!/usr/bin/env python3
"""Fetch per-person cycle-time board data from a GitHub Project via `gh`."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import (  # noqa: E402
    BOARDS_PATH,
    DATA_DIR,
    data_path_for,
    load_config,
    require_project,
    require_repos,
    resolve_person,
    run_gh_json,
)


def graphql(query: str, variables: dict | None = None) -> dict:
    args = ["api", "graphql", "-f", f"query={query}"]
    for k, v in (variables or {}).items():
        if isinstance(v, bool):
            args += ["-F", f"{k}={json.dumps(v)}"]
        elif isinstance(v, int):
            args += ["-F", f"{k}={v}"]
        elif v is None:
            args += ["-F", f"{k}=null"]
        else:
            args += ["-f", f"{k}={v}"]
    return run_gh_json(args)


def hours_between(a: str | None, b: str | None) -> float | None:
    if not a or not b:
        return None
    t1 = datetime.fromisoformat(a.replace("Z", "+00:00"))
    t2 = datetime.fromisoformat(b.replace("Z", "+00:00"))
    return round((t2 - t1).total_seconds() / 3600, 1)


def search_assigned_issues(repo: str, login: str) -> list[dict]:
    out: list[dict] = []
    for state in ("open", "closed"):
        items = run_gh_json(
            [
                "search",
                "issues",
                "--repo",
                repo,
                "--assignee",
                login,
                "--state",
                state,
                "--limit",
                "50",
                "--json",
                "number,title,state,labels,createdAt,updatedAt,closedAt,url",
                "--sort",
                "updated",
            ]
        )
        out.extend(items)
    # dedupe by number
    seen = set()
    unique = []
    for i in out:
        if i["number"] in seen:
            continue
        seen.add(i["number"])
        unique.append(i)
    return unique


ISSUE_QUERY = """
query($owner: String!, $repo: String!, $number: Int!) {
  repository(owner: $owner, name: $repo) {
    issue(number: $number) {
      number
      title
      url
      state
      stateReason
      createdAt
      closedAt
      updatedAt
      assignees(first: 10) { nodes { login } }
      labels(first: 20) { nodes { name } }
      projectItems(first: 10) {
        nodes {
          updatedAt
          project { number }
          fieldValues(first: 25) {
            nodes {
              ... on ProjectV2ItemFieldSingleSelectValue {
                name
                updatedAt
                field { ... on ProjectV2FieldCommon { name } }
              }
              ... on ProjectV2ItemFieldIterationValue {
                title
                updatedAt
                field { ... on ProjectV2FieldCommon { name } }
              }
            }
          }
        }
      }
      closedByPullRequestsReferences(first: 5) {
        nodes {
          number
          title
          url
          createdAt
          mergedAt
          closedAt
          state
          author { login }
          body
        }
      }
      timelineItems(last: 80, itemTypes: [
        ASSIGNED_EVENT, CLOSED_EVENT, CROSS_REFERENCED_EVENT, REOPENED_EVENT
      ]) {
        nodes {
          __typename
          ... on AssignedEvent {
            createdAt
            assignee { ... on User { login } }
          }
          ... on ClosedEvent { createdAt stateReason }
          ... on CrossReferencedEvent {
            createdAt
            source {
              ... on PullRequest {
                number
                title
                url
                createdAt
                mergedAt
                closedAt
                state
                author { login }
                body
              }
            }
          }
        }
      }
    }
  }
}
"""


def project_fields(issue: dict, project_number: int) -> dict:
    status = sprint = area = None
    status_at = None
    for pi in issue.get("projectItems", {}).get("nodes", []):
        if pi.get("project", {}).get("number") != project_number:
            continue
        for fv in pi.get("fieldValues", {}).get("nodes", []):
            if not fv or "field" not in fv or not fv["field"]:
                continue
            name = fv["field"]["name"]
            if name == "Status" and "name" in fv:
                status = fv["name"]
                status_at = fv.get("updatedAt")
            elif name == "Sprint" and "title" in fv:
                sprint = fv["title"]
            elif name == "Area" and "name" in fv:
                area = fv["name"]
    return {
        "status": status,
        "sprint": sprint,
        "area": area,
        "statusUpdatedAt": status_at,
    }


def assigned_at_for(issue: dict, login: str) -> str | None:
    for t in issue.get("timelineItems", {}).get("nodes", []):
        if t.get("__typename") != "AssignedEvent":
            continue
        assignee = (t.get("assignee") or {}).get("login")
        if assignee == login:
            return t.get("createdAt")
    return None


def best_pr(issue: dict, login: str) -> dict | None:
    prs: list[dict] = []
    seen: set[int] = set()

    def add(pr: dict | None) -> None:
        if not pr or not pr.get("number"):
            return
        n = int(pr["number"])
        if n in seen:
            return
        seen.add(n)
        prs.append(pr)

    for pr in issue.get("closedByPullRequestsReferences", {}).get("nodes", []) or []:
        add(pr)
    for t in issue.get("timelineItems", {}).get("nodes", []):
        if t.get("__typename") != "CrossReferencedEvent":
            continue
        add(t.get("source") or {})

    if not prs:
        return None
    by_author = [p for p in prs if (p.get("author") or {}).get("login") == login]
    pool = by_author or prs
    merged = [p for p in pool if p.get("mergedAt")]
    if merged:
        return sorted(merged, key=lambda p: p["mergedAt"])[-1]
    return sorted(pool, key=lambda p: p.get("createdAt") or "")[-1]


def map_status(project_status: str | None, issue_state: str, state_reason: str | None) -> str:
    if project_status:
        # Normalize project casing
        normalized = {
            "todo": "Todo",
            "in progress": "In Progress",
            "ready for review": "Ready for Review",
            "in review": "Ready for Review",
            "done": "Done",
        }.get(project_status.lower(), project_status)
        if normalized == "Done" and state_reason and state_reason.upper() in {"NOT_PLANNED", "DUPLICATE"}:
            return "Closed"
        return normalized
    if issue_state == "CLOSED":
        if state_reason and state_reason.upper() in {"NOT_PLANNED", "DUPLICATE"}:
            return "Closed"
        return "Done"
    return "Todo"


_HEADING_RE = re.compile(r"^\s{0,3}#{1,6}\s+(.*)$")
_BULLET_RE = re.compile(r"^\s*([-*+]|\d+\.)\s+(.*)$")
_CHECKBOX_RE = re.compile(r"^\s*[-*+]\s+\[([ xX])\]\s+(.*)$")
_HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
_ISSUE_REF_RE = re.compile(
    r"^\s*(fixes|closes|resolves|fixed|closed|resolved)\s+#\d+\s*$",
    re.IGNORECASE,
)

# Sections whose body becomes the main narrative / key-change list / type line.
_SOLUTION_ALIASES = {
    "description",
    "summary",
    "solution",
    "what changed",
    "overview",
    "context",
}
_PROBLEM_ALIASES = {
    "problem",
    "issue",
    "background",
    "motivation",
    "why",
}
_CHANGES_ALIASES = {
    "changes made",
    "changes",
    "key changes",
    "changelog",
    "notable changes",
}
_TYPE_ALIASES = {
    "type of change",
    "type",
    "change type",
}
_SKIP_SECTIONS = {
    "test plan",
    "tests",
    "screenshots",
    "checklist",
    "how to test",
    "verification",
    "related",
    "references",
    "cc",
}


def _strip_md(text: str) -> str:
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"__(.+?)__", r"\1", text)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    return re.sub(r"\s+", " ", text).strip()


def _section_map(body: str) -> dict[str, str]:
    """Split a markdown PR body into heading → section text."""
    body = _HTML_COMMENT_RE.sub("", body or "")
    sections: dict[str, list[str]] = {"": []}
    current = ""
    for raw in body.splitlines():
        m = _HEADING_RE.match(raw)
        if m:
            current = m.group(1).strip().lower()
            # Drop trailing punctuation / badges from heading text
            current = re.sub(r"[:：]\s*$", "", current)
            sections.setdefault(current, [])
            continue
        sections.setdefault(current, []).append(raw)
    return {k: "\n".join(v).strip() for k, v in sections.items() if "\n".join(v).strip()}


def _pick_section(sections: dict[str, str], aliases: set[str]) -> str:
    for key, text in sections.items():
        if key in aliases:
            return text
    for key, text in sections.items():
        for alias in aliases:
            if alias in key:
                return text
    return ""


def _lines_of_substance(text: str) -> list[str]:
    out: list[str] = []
    for raw in (text or "").splitlines():
        line = raw.strip()
        if not line or line == "---":
            continue
        if line.startswith("<!--"):
            continue
        if _ISSUE_REF_RE.match(line):
            continue
        if _HEADING_RE.match(line):
            continue
        cb = _CHECKBOX_RE.match(line)
        if cb:
            # Keep only checked type-of-change style items elsewhere
            continue
        b = _BULLET_RE.match(line)
        if b:
            item = _strip_md(b.group(2))
            if item:
                out.append(item)
            continue
        # Bold mini-headings inside a section (e.g. **Modal Lifecycle**)
        if re.fullmatch(r"\*\*[^*]+\*\*", line):
            continue
        cleaned = _strip_md(line)
        if cleaned:
            out.append(cleaned)
    return out


def _checked_items(text: str) -> list[str]:
    items = []
    for raw in (text or "").splitlines():
        cb = _CHECKBOX_RE.match(raw)
        if not cb or cb.group(1).lower() != "x":
            continue
        item = _strip_md(cb.group(2))
        # Prefer the bracket label: "[fix] Bug fix …" → "Bug fix"
        m = re.match(r"\[([^\]]+)\]\s*(.*)", item)
        if m:
            label, rest = m.group(1).strip(), m.group(2).strip()
            # "Bug fix (non-breaking…)" from rest if label is short keyword
            if rest:
                rest = re.sub(r"^\((.+)\)$", r"\1", rest)
                item = rest.split("(")[0].strip() or label
            else:
                item = label
        if item:
            items.append(item)
    return items


def _join_blurb(lines: list[str], *, limit: int = 700) -> str:
    if not lines:
        return ""
    text = " ".join(lines) if len(lines) == 1 else " ".join(
        (ln if ln.endswith((".", "!", "?")) else ln + ".") for ln in lines
    )
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) > limit:
        text = text[: limit - 1].rsplit(" ", 1)[0] + "…"
    return text


def _infer_pr_type(type_section: str, title: str) -> str:
    checked = _checked_items(type_section)
    if checked:
        return checked[0][:80]
    t = (title or "").lower()
    if t.startswith("fix") or "bug" in t:
        return "Bug Fix"
    if t.startswith("docs") or "documentation" in t:
        return "Documentation"
    if t.startswith("chore") or t.startswith("deps"):
        return "Chore"
    if t.startswith("feat"):
        return "Feature"
    return "Pull Request"


def parse_pr_body(body: str, title: str = "") -> dict:
    """Build a board PR summary from a typical GitHub PR description."""
    sections = _section_map(body)
    # Ignore boilerplate sections when falling back to preamble
    usable = {
        k: v
        for k, v in sections.items()
        if k == "" or k not in _SKIP_SECTIONS
    }

    problem_lines = _lines_of_substance(_pick_section(usable, _PROBLEM_ALIASES))
    solution_src = _pick_section(usable, _SOLUTION_ALIASES) or usable.get("", "")
    solution_lines = _lines_of_substance(solution_src)
    changes_src = _pick_section(usable, _CHANGES_ALIASES)
    key_changes = _lines_of_substance(changes_src)[:8]

    # Description-only templates often mix problem + solution bullets.
    # If there is no dedicated Problem section, use the first half as context
    # when we have enough bullets and a Changes section (or ≥4 bullets).
    problem = _join_blurb(problem_lines, limit=500)
    solution = _join_blurb(solution_lines, limit=700)
    if not problem and len(solution_lines) >= 4:
        split = max(1, len(solution_lines) // 2)
        problem = _join_blurb(solution_lines[:split], limit=500)
        solution = _join_blurb(solution_lines[split:], limit=700)
    elif not problem and len(solution_lines) >= 2 and key_changes:
        problem = _join_blurb(solution_lines[:1], limit=500)
        solution = _join_blurb(solution_lines[1:], limit=700)

    if not solution and not problem and not key_changes:
        # Last resort: any substantive lines in the whole body
        all_lines = []
        for key, text in usable.items():
            if key in _SKIP_SECTIONS or key in _TYPE_ALIASES:
                continue
            all_lines.extend(_lines_of_substance(text))
        solution = _join_blurb(all_lines[:5], limit=700)

    return {
        "prType": _infer_pr_type(_pick_section(sections, _TYPE_ALIASES), title),
        "problem": problem,
        "solution": solution,
        "keyChanges": key_changes,
    }


def _summary_richness(summary: dict | None) -> int:
    if not summary:
        return 0
    score = 0
    if summary.get("problem"):
        score += 2
    if summary.get("solution"):
        score += 1
    score += min(len(summary.get("keyChanges") or []), 4)
    # Prefer real types over the generic placeholder
    if summary.get("prType") and summary["prType"] not in {"Pull Request", ""}:
        score += 1
    return score


def summarize_pr(pr: dict | None, status: str) -> dict | None:
    if not pr:
        if status == "Closed":
            return {
                "prType": "Closed — Won't Fix",
                "problem": "",
                "solution": "",
                "keyChanges": [],
            }
        return None
    parsed = parse_pr_body(pr.get("body") or "", pr.get("title") or "")
    if not parsed["problem"] and not parsed["solution"] and not parsed["keyChanges"]:
        return None
    return parsed


def pick_summary(existing: dict | None, parsed: dict | None) -> dict | None:
    """Keep a previously enriched summary only when it is richer than a fresh parse."""
    if _summary_richness(parsed) >= _summary_richness(existing):
        return parsed or existing
    return existing or parsed


def load_existing(login: str) -> tuple[dict[int, dict], dict[int, dict]]:
    path = DATA_DIR / f"{login}.json"
    if not path.exists():
        return {}, {}
    try:
        prev = json.loads(path.read_text())
    except json.JSONDecodeError:
        return {}, {}
    summaries: dict[int, dict] = {}
    meta: dict[int, dict] = {}
    for issue in prev.get("issues", []):
        n = issue["number"]
        summary = issue.get("prSummary")
        if summary and (summary.get("keyChanges") or summary.get("problem")):
            summaries[n] = summary
        meta[n] = {
            "todoAt": issue.get("todoAt"),
            "inProgressAt": issue.get("inProgressAt"),
            "cycleHours": issue.get("cycleHours"),
            "prOpenHours": issue.get("prOpenHours"),
        }
    return summaries, meta


def fetch_person(login: str, name: str, cfg: dict) -> dict:
    project = require_project(cfg)
    project_number = project["number"]
    area_filter = project.get("area")
    repos = require_repos(cfg)
    issues_out = []
    existing_summaries, existing_meta = load_existing(login)

    for repo in repos:
        owner, repo_name = repo.split("/", 1)
        for hit in search_assigned_issues(repo, login):
            data = graphql(
                ISSUE_QUERY,
                {"owner": owner, "repo": repo_name, "number": hit["number"]},
            )
            issue = data["data"]["repository"]["issue"]
            fields = project_fields(issue, project_number)
            if area_filter and fields["area"] and fields["area"] != area_filter:
                # Keep items with no area set (still on the personal board) if assigned
                if fields["area"] is not None:
                    continue

            status = map_status(fields["status"], issue["state"], issue.get("stateReason"))
            assigned_at = assigned_at_for(issue, login) or issue["createdAt"]
            prev_meta = existing_meta.get(issue["number"]) or {}
            todo_at = prev_meta.get("todoAt") or assigned_at
            in_progress_at = prev_meta.get("inProgressAt")
            if status == "In Progress" and fields.get("statusUpdatedAt"):
                in_progress_at = in_progress_at or fields["statusUpdatedAt"]

            pr = best_pr(issue, login)
            merged_at = None
            if pr and pr.get("mergedAt"):
                merged_at = pr["mergedAt"]
            elif status in {"Done", "Closed"} and issue.get("closedAt"):
                merged_at = issue["closedAt"]

            cycle = hours_between(assigned_at, merged_at) if merged_at else None
            pr_open = hours_between(pr.get("createdAt") if pr else None, pr.get("mergedAt") if pr else None)
            if cycle is None:
                cycle = prev_meta.get("cycleHours")
            if pr_open is None:
                pr_open = prev_meta.get("prOpenHours")

            summary = pick_summary(
                existing_summaries.get(issue["number"]),
                summarize_pr(pr, status),
            )

            item = {
                "number": issue["number"],
                "title": issue["title"],
                "url": issue["url"],
                "status": status,
                "sprint": fields["sprint"] or "Unassigned",
                "labels": [l["name"] for l in issue.get("labels", {}).get("nodes", [])],
                "assignedAt": assigned_at,
                "todoAt": todo_at,
                "inProgressAt": in_progress_at,
                "cycleHours": cycle,
                "prOpenHours": pr_open,
                "prSummary": summary,
            }
            if pr:
                item.update(
                    {
                        "prNumber": pr["number"],
                        "prTitle": pr["title"],
                        "prUrl": pr["url"],
                        "prCreatedAt": pr.get("createdAt"),
                        "mergedAt": pr.get("mergedAt") or merged_at,
                    }
                )
            elif merged_at:
                item["mergedAt"] = merged_at

            issues_out.append(item)

    # Sort: In Progress, Ready for Review, Todo, Done, Closed
    order = {"In Progress": 0, "Ready for Review": 1, "Todo": 2, "Done": 3, "Closed": 4}
    issues_out.sort(key=lambda i: (order.get(i["status"], 9), -(i["number"])))

    return {
        "login": login,
        "name": name,
        "fetchedAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "issues": issues_out,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fetch cycle-time board data for the authenticated GitHub user"
    )
    parser.add_argument(
        "--person",
        help="Override GitHub login (default: identity from gh auth / GH_TOKEN)",
    )
    parser.add_argument(
        "--boards",
        type=Path,
        default=BOARDS_PATH,
        help="boards.json from scripts/configure.py",
    )
    parser.add_argument(
        "--no-auth",
        action="store_true",
        help="Do not call GitHub for identity; use boards.json person only",
    )
    args = parser.parse_args()

    if not args.boards.exists():
        print(
            "No boards.json found. Choose a Project first:\n"
            "  python3 scripts/configure.py",
            file=sys.stderr,
        )
        return 2

    cfg = load_config(args.boards)
    require_project(cfg)
    require_repos(cfg)

    try:
        person = resolve_person(
            cfg,
            login_override=args.person,
            use_auth=not args.no_auth,
        )
    except RuntimeError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    login = person["login"]
    project = cfg["project"]
    print(f"Authenticated board user: {login}", flush=True)
    print(f"Project: {project['owner']} #{project['number']} — {cfg.get('title')}", flush=True)
    print(f"Fetching {login}…", flush=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    try:
        data = fetch_person(login, person.get("name") or login, cfg)
    except Exception as e:
        print(f"  ERROR: {e}", file=sys.stderr)
        return 1
    out = data_path_for(login)
    out.write_text(json.dumps(data, indent=2) + "\n")
    print(f"  wrote {out} ({len(data['issues'])} issues)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
