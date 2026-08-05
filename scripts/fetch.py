#!/usr/bin/env python3
"""Fetch per-person cycle-time board data from a GitHub Project via `gh`."""

from __future__ import annotations

import argparse
import json
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
    prs = []
    for t in issue.get("timelineItems", {}).get("nodes", []):
        if t.get("__typename") != "CrossReferencedEvent":
            continue
        src = t.get("source") or {}
        if not src.get("number"):
            continue
        # Prefer PRs by the assignee; otherwise keep any merged PR
        prs.append(src)
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
    body = pr.get("body") or ""
    # Keep a light summary; agent / skill can enrich later
    first = next((ln.strip() for ln in body.splitlines() if ln.strip()), "")
    return {
        "prType": "Pull Request",
        "problem": "",
        "solution": first[:400],
        "keyChanges": [],
    }


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
    project_number = cfg["project"]["number"]
    area_filter = cfg["project"].get("area")
    repos = cfg.get("repos") or []
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

            summary = existing_summaries.get(issue["number"]) or summarize_pr(pr, status)

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
        help="Optional boards.json overlay (project/repos). Not required.",
    )
    parser.add_argument(
        "--no-auth",
        action="store_true",
        help="Do not call GitHub for identity; use boards.json person only",
    )
    args = parser.parse_args()

    cfg = load_config(args.boards if args.boards.exists() else None)
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
    print(f"Authenticated board user: {login}", flush=True)
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
