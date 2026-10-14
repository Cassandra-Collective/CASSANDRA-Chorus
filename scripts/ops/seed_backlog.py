"""Create the project's labels, milestones and issues from a TOML backlog file.

See docs/implementations/2026-10-14-team-workflow-and-backlog.md.

The file has ``repo``, ``owner_login`` and arrays of tables ``labels``,
``milestones`` and ``issues``. Each issue has a unique ``key`` and ``title``,
``labels``, a ``milestone`` title, optional ``assignees`` (``"owner"`` means
``owner_login``) and a ``body``. In a body, ``{#key}`` becomes the number of
an issue that appears *earlier* in the file, and ``{blob}`` becomes
``https://github.com/<repo>/blob/main/`` (relative links do not resolve in
issues).

Behaviour:
* the whole file is validated before anything is sent;
* labels are created or updated; milestones are created if missing (by title);
* an issue whose title already exists (open or closed) is skipped, so a
  re-run resumes after an interruption and never duplicates;
* creations are paced (``--pause``, default 1.5 s): GitHub allows 80
  content-creating requests per minute and 500 per hour;
* at the end every planned title must exist exactly once, and a key-to-number
  table is written (``--out``).

Uses the ``gh`` command, already authenticated. ``--dry-run`` sends nothing.

Usage:
    python scripts/ops/seed_backlog.py docs/planning/2026-10-14-backlog.toml --out docs/planning/2026-10-14-backlog-issues.md [--dry-run]
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
import tomllib
import urllib.parse
from pathlib import Path
from typing import Any

GITHUB_DEFAULT_LABELS = {"bug", "documentation", "duplicate", "enhancement", "good first issue", "help wanted",
                         "invalid", "question", "wontfix", "accessibility"}
REF = re.compile(r"\{#([a-z0-9][a-z0-9-]*)\}")


class BacklogError(ValueError):
    """The backlog file is inconsistent."""


def load(path: Path) -> dict[str, Any]:
    with path.open("rb") as f:
        data = tomllib.load(f)
    validate(data)
    return data


def validate(data: dict[str, Any]) -> None:
    """Raise :class:`BacklogError` on any inconsistency; no network."""
    for field in ("repo", "owner_login", "labels", "milestones", "issues"):
        if field not in data:
            raise BacklogError(f"missing top-level field {field!r}")
    labels = {lab["name"] for lab in data["labels"]} | GITHUB_DEFAULT_LABELS
    milestones = {m["title"] for m in data["milestones"]}
    seen_keys: set[str] = set()
    seen_titles: set[str] = set()
    for i, issue in enumerate(data["issues"]):
        where = f"issue {i} ({issue.get('key')!r})"
        for field in ("key", "title", "labels", "milestone", "body"):
            if field not in issue:
                raise BacklogError(f"{where}: missing {field!r}")
        if issue["key"] in seen_keys:
            raise BacklogError(f"{where}: duplicate key")
        if issue["title"] in seen_titles:
            raise BacklogError(f"{where}: duplicate title {issue['title']!r}")
        unknown = [lab for lab in issue["labels"] if lab not in labels]
        if unknown:
            raise BacklogError(f"{where}: unknown labels {unknown}")
        if issue["milestone"] not in milestones:
            raise BacklogError(f"{where}: unknown milestone {issue['milestone']!r}")
        for ref in REF.findall(issue["body"]):
            if ref not in seen_keys:
                raise BacklogError(f"{where}: {{#{ref}}} does not name an earlier issue")
        seen_keys.add(issue["key"])
        seen_titles.add(issue["title"])


def render_body(body: str, repo: str, numbers: dict[str, int]) -> str:
    """Substitute ``{blob}`` and ``{#key}`` placeholders."""
    body = body.replace("{blob}", f"https://github.com/{repo}/blob/main/")
    return REF.sub(lambda m: f"#{numbers[m.group(1)]}", body).strip() + "\n"


def assignees(issue: dict[str, Any], owner_login: str) -> list[str]:
    return [owner_login if a == "owner" else a for a in issue.get("assignees", [])]


# ----- GitHub through the gh command -----


def gh(args: list[str], payload: dict[str, Any] | None = None) -> Any:
    proc = subprocess.run(["gh", *args], input=json.dumps(payload) if payload is not None else None,
                          capture_output=True, text=True, encoding="utf-8")
    if proc.returncode != 0:
        raise RuntimeError(f"gh {' '.join(args[:3])} failed: {proc.stderr.strip()[:500]}")
    return json.loads(proc.stdout) if proc.stdout.strip() else None


def gh_paged(path: str) -> list[dict[str, Any]]:
    return [item for page in gh(["api", "--paginate", "--slurp", path]) for item in page]


def sync_labels(repo: str, labels: list[dict[str, Any]], dry: bool) -> None:
    existing = {lab["name"] for lab in gh_paged(f"repos/{repo}/labels?per_page=100")}
    for lab in labels:
        payload = {"name": lab["name"], "color": lab["color"], "description": lab.get("description", "")}
        action = "update" if lab["name"] in existing else "create"
        print(f"[labels] {action} {lab['name']!r}")
        if dry:
            continue
        if action == "update":
            gh(["api", "--method", "PATCH", f"repos/{repo}/labels/{urllib.parse.quote(lab['name'], safe='')}", "--input", "-"],
               {"new_name": lab["name"], "color": lab["color"], "description": lab.get("description", "")})
        else:
            gh(["api", "--method", "POST", f"repos/{repo}/labels", "--input", "-"], payload)


def sync_milestones(repo: str, milestones: list[dict[str, Any]], dry: bool) -> dict[str, int]:
    numbers = {m["title"]: m["number"] for m in gh_paged(f"repos/{repo}/milestones?state=all&per_page=100")}
    for m in milestones:
        if m["title"] in numbers:
            print(f"[milestones] exists {m['title']!r} (#{numbers[m['title']]})")
            continue
        print(f"[milestones] create {m['title']!r}")
        if not dry:
            created = gh(["api", "--method", "POST", f"repos/{repo}/milestones", "--input", "-"],
                         {"title": m["title"], "description": m.get("description", "")})
            numbers[m["title"]] = created["number"]
    return numbers


def existing_issues(repo: str) -> dict[str, list[int]]:
    """Issue titles (pull requests excluded) to their numbers, all states."""
    out: dict[str, list[int]] = {}
    for item in gh_paged(f"repos/{repo}/issues?state=all&per_page=100"):
        if "pull_request" not in item:
            out.setdefault(item["title"], []).append(item["number"])
    return out


def seed(data: dict[str, Any], out: Path | None, dry: bool, pause: float) -> dict[str, int]:
    repo, owner_login = data["repo"], data["owner_login"]
    sync_labels(repo, data["labels"], dry)
    milestone_numbers = sync_milestones(repo, data["milestones"], dry)
    existing = existing_issues(repo)
    numbers: dict[str, int] = {}
    created = skipped = 0
    for issue in data["issues"]:
        if issue["title"] in existing:
            numbers[issue["key"]] = existing[issue["title"]][0]
            skipped += 1
            print(f"[issues] exists #{numbers[issue['key']]} {issue['title']}")
            continue
        if dry:
            numbers[issue["key"]] = -(len(numbers) + 1)  # placeholder so later references render
            print(f"[issues] would create: {issue['title']}")
            continue
        payload = {"title": issue["title"], "body": render_body(issue["body"], repo, numbers),
                   "labels": issue["labels"], "milestone": milestone_numbers[issue["milestone"]],
                   "assignees": assignees(issue, owner_login)}
        result = gh(["api", "--method", "POST", f"repos/{repo}/issues", "--input", "-"], payload)
        numbers[issue["key"]] = result["number"]
        created += 1
        print(f"[issues] created #{result['number']} {issue['title']}", flush=True)
        time.sleep(pause)
    print(f"[issues] created {created}, already existed {skipped}, planned {len(data['issues'])}")
    if not dry:
        verify(repo, data)
        if out is not None:
            write_table(out, data, numbers)
    return numbers


def verify(repo: str, data: dict[str, Any], attempts: int = 4, wait: float = 10.0) -> None:
    """Every planned title exists exactly once. Retries: GitHub's issue listing lags new issues by
    a few seconds (seen 2026-10-14: the last two of 89 were missing from a listing made just after)."""
    for attempt in range(1, attempts + 1):
        existing = existing_issues(repo)
        missing = [i["title"] for i in data["issues"] if i["title"] not in existing]
        doubled = [i["title"] for i in data["issues"] if len(existing.get(i["title"], [])) > 1]
        if not missing and not doubled:
            print(f"[verify] all {len(data['issues'])} planned issues exist exactly once")
            return
        if attempt < attempts:
            print(f"[verify] attempt {attempt}: {len(missing)} missing, {len(doubled)} duplicated; retrying in {wait:g} s")
            time.sleep(wait)
    raise RuntimeError(f"verification failed: missing {missing[:5]}, duplicated {doubled[:5]}")


def write_table(out: Path, data: dict[str, Any], numbers: dict[str, int]) -> None:
    repo = data["repo"]
    lines = [f"# Seed backlog: created issues", "",
             f"Generated by `scripts/ops/seed_backlog.py` from `docs/planning/2026-10-14-backlog.toml`. After seeding, the "
             f"issues on GitHub are the source of truth; this table records what was planned.", ""]
    for milestone in [m["title"] for m in data["milestones"]]:
        rows = [i for i in data["issues"] if i["milestone"] == milestone]
        if not rows:
            continue
        lines += [f"## {milestone}", "", "| Issue | Key | Title |", "|---|---|---|"]
        lines += [f"| [#{numbers[i['key']]}](https://github.com/{repo}/issues/{numbers[i['key']]}) | `{i['key']}` | {i['title']} |"
                  for i in rows]
        lines.append("")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"[out] wrote {out}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("backlog", type=Path)
    parser.add_argument("--out", type=Path, default=None, help="Markdown table of created issues")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--pause", type=float, default=1.5, help="seconds between issue creations")
    args = parser.parse_args(argv)
    seed(load(args.backlog), args.out, args.dry_run, args.pause)
    return 0


if __name__ == "__main__":
    sys.exit(main())
