"""P0: what the ``chorus-prototypes`` token may do (docs/implementations/2026-10-14-solo-prototypes.md).

Its only organisation permission is ``repo.contribute.write``, which the Hub
documentation does not define. In order, with the token loaded by name and
its scope checked first:

1. create a private repository ``<org>/proto-scope-probe``;
2. upload a small file; read it back; list the files;
3. create a branch;
4. commit with ``parent_commit`` set to the head; then commit again with the
   now stale parent, which the Hub should reject (an early look at P4);
5. create a private Storage Bucket ``<org>/proto-bucket-probe``; add, list
   and read back a file; delete the bucket;
6. delete the repository;
7. try to create a repository in the token owner's personal namespace, which
   must fail. If it succeeds, the repository is deleted at once and the
   result is flagged.

Every resource is recorded in the local manifest before it is created. The
token is never printed or written.

Usage:
    python scripts/proto/p0_hub_scope_probe.py --org cassandra-chorus
"""

from __future__ import annotations

import argparse
import sys
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from huggingface_hub import CommitOperationAdd, HfApi, whoami  # noqa: E402

from scripts.proto.common import RESULTS_DIR, guarded_token, record_hub_resource, write_json  # noqa: E402


def outcome_of(fn: Callable[[], Any]) -> dict[str, Any]:
    """Run ``fn``; return whether it succeeded, how long it took, its value or its error (no secrets)."""
    t0 = time.time()
    try:
        value = fn()
        return {"ok": True, "seconds": round(time.time() - t0, 2), "value": value}
    except Exception as e:  # noqa: BLE001 (a probe records every failure)
        status = getattr(getattr(e, "response", None), "status_code", None)
        message = str(e).splitlines()[0][:300] if str(e) else ""
        return {"ok": False, "seconds": round(time.time() - t0, 2), "error": type(e).__name__,
                "http_status": status, "message": message}


def run(org: str) -> dict[str, Any]:
    token = guarded_token(org)
    api = HfApi(token=token)
    user = whoami(token=token)["name"]
    repo_id, bucket_id = f"{org}/proto-scope-probe", f"{org}/proto-bucket-probe"
    steps: dict[str, dict[str, Any]] = {}

    def step(name: str, fn: Callable[[], Any], expect_ok: bool = True) -> dict[str, Any]:
        r = outcome_of(fn)
        r["expected"] = "success" if expect_ok else "failure"
        r["as_expected"] = r["ok"] == expect_ok
        steps[name] = r
        print(f"[p0] {name}: {'ok' if r['ok'] else 'failed'} ({'as expected' if r['as_expected'] else 'NOT as expected'})",
              flush=True)
        return r

    record_hub_resource("repo", repo_id, "P0")
    if step("create_private_repo", lambda: str(api.create_repo(repo_id, private=True, exist_ok=False)))["ok"]:
        step("repo_is_private", lambda: api.repo_info(repo_id).private)
        step("upload_file", lambda: api.upload_file(path_or_fileobj=b"probe\n", path_in_repo="probe.txt",
                                                    repo_id=repo_id, commit_message="P0 probe").oid)
        step("list_files", lambda: api.list_repo_files(repo_id))
        step("read_back", lambda: Path(api.hf_hub_download(repo_id, "probe.txt", force_download=True)).read_bytes().decode())
        step("create_branch", lambda: api.create_branch(repo_id, branch="probe-branch") or "created")
        head = api.repo_info(repo_id).sha  # the head of main
        step("commit_with_current_parent", lambda: api.create_commit(
            repo_id, [CommitOperationAdd("a.txt", b"a\n")], commit_message="P0 parent=head", parent_commit=head).oid)
        step("commit_with_stale_parent", lambda: api.create_commit(
            repo_id, [CommitOperationAdd("b.txt", b"b\n")], commit_message="P0 stale parent", parent_commit=head).oid,
            expect_ok=False)
        step("delete_repo", lambda: api.delete_repo(repo_id) or "deleted")

    record_hub_resource("bucket", bucket_id, "P0")
    if step("create_private_bucket", lambda: str(api.create_bucket(bucket_id, private=True)))["ok"]:
        step("bucket_add_file", lambda: str(api.batch_bucket_files(bucket_id, add=[(b"probe\n", "probe/probe.txt")])))
        step("bucket_list", lambda: [repr(f) for f in api.list_bucket_tree(bucket_id, recursive=True)])
        step("bucket_info", lambda: repr(api.bucket_info(bucket_id)))
        step("delete_bucket", lambda: api.delete_bucket(bucket_id) or "deleted")

    personal = f"{user}/proto-should-fail"
    record_hub_resource("repo", personal, "P0")
    r = step("create_repo_in_personal_namespace", lambda: str(api.create_repo(personal, private=True)), expect_ok=False)
    if r["ok"]:  # the token could write where it must not: undo at once
        steps["UNEXPECTED_personal_repo_deleted"] = outcome_of(lambda: api.delete_repo(personal) or "deleted")

    return {
        "prototype": "P0 Hub token scope probe",
        "plan": "docs/implementations/2026-10-14-solo-prototypes.md",
        "org": org,
        "token": "chorus-prototypes (organisation permission repo.contribute.write only; checked by the guard)",
        "time_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "steps": steps,
        "all_as_expected": all(s.get("as_expected", True) for s in steps.values()),
    }


def summary_markdown(report: dict[str, Any]) -> str:
    lines = ["# P0 Hub token scope probe", "",
             f"Plan: `{report['plan']}`. Organisation `{report['org']}`; token {report['token']}; run {report['time_utc']}.", "",
             "| Step | Expected | Result | Detail |", "|---|---|---|---|"]
    for name, s in report["steps"].items():
        detail = str(s.get("value", ""))[:80] if s["ok"] else f"{s.get('error')} {s.get('http_status') or ''}: {s.get('message', '')[:120]}"
        detail = " ".join(detail.split()).replace("|", "/")  # one table row: no newlines or pipes
        lines.append(f"| {name} | {s.get('expected', '')} | {'ok' if s['ok'] else 'failed'} | {detail} |")
    lines += ["", f"All steps as expected: **{'yes' if report['all_as_expected'] else 'no'}**.", ""]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--org", required=True, help="the organisation the token is scoped to")
    args = parser.parse_args(argv)
    report = run(args.org)
    write_json(RESULTS_DIR / "p0_hub_scope_probe.json", report)
    (RESULTS_DIR / "p0_hub_scope_probe.md").write_text(summary_markdown(report), encoding="utf-8")
    print(summary_markdown(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
