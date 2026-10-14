"""Delete the Hub resources the prototypes created (docs/implementations/2026-10-14-solo-prototypes.md).

Reads the local manifest (``proto-hub-manifest.json`` in the runs folder) and
deletes only what it lists, and only names starting with ``proto-``. Without
``--yes`` it lists what it would delete and changes nothing. Resources that
no longer exist are reported as already gone. Uses the ``chorus-prototypes``
token, checked by the guard; it can delete only inside the organisation.

Usage:
    python scripts/proto/hub_cleanup.py --org cassandra-chorus [--yes]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from scripts.proto.common import PROTO_PREFIX, guarded_token, hub_manifest_path  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--org", required=True)
    parser.add_argument("--yes", action="store_true", help="really delete (default: list only)")
    args = parser.parse_args(argv)
    path = hub_manifest_path()
    if not path.exists():
        print(f"no manifest at {path}; nothing to do")
        return 0
    entries = json.loads(path.read_text(encoding="utf-8"))
    from huggingface_hub import HfApi

    api = HfApi(token=guarded_token(args.org))
    for e in entries:
        owner, _, name = e["id"].partition("/")
        if not name.startswith(PROTO_PREFIX):
            print(f"skip (not {PROTO_PREFIX}*): {e['id']}")
            continue
        if owner != args.org:
            print(f"skip (outside {args.org}; this token cannot reach it): {e['id']}")
            continue
        if not args.yes:
            print(f"would delete {e['kind']} {e['id']} (from {e['prototype']})")
            continue
        try:
            if e["kind"] == "repo":
                api.delete_repo(e["id"], missing_ok=True)
            else:
                api.delete_bucket(e["id"], missing_ok=True)
            print(f"deleted (or already gone) {e['kind']} {e['id']}")
        except Exception as exc:  # noqa: BLE001
            print(f"FAILED {e['kind']} {e['id']}: {type(exc).__name__}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
