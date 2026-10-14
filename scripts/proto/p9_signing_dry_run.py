"""P9: signing dry run (docs/implementations/2026-10-14-solo-prototypes.md).

The owner's offline step, then a client's check, on one machine:

1. generate a throwaway Ed25519 key pair in the work folder;
2. write a run configuration (JSON) and sign its exact bytes;
3. build a release archive with ``git archive`` of HEAD, write a manifest
   listing its SHA-256, and sign the manifest's exact bytes;
4. verify everything in a fresh process (``python -E -P``, started in an
   empty folder) that is given only the files and the 32-byte public key;
5. run tampering cases, each of which the verifier must reject.

Signatures cover a domain prefix plus the file's bytes,
``b"cassandra-chorus/<kind>/v1\\n" + bytes``, so a configuration signature
cannot be passed off as a manifest signature. A ``.sig`` file holds the
64-byte signature in standard base64 on one line.

Usage:
    python scripts/proto/p9_signing_dry_run.py --work-dir DIR [--keep-files]
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from scripts.proto.common import RESULTS_DIR, write_json  # noqa: E402

DOMAIN = {"config": b"cassandra-chorus/config/v1\n", "manifest": b"cassandra-chorus/manifest/v1\n"}

# The client side: stdlib and cryptography only, no repository imports. Written to a file and run in a
# fresh interpreter. Exit 0 when every check passes; otherwise exit 1 with the reason on stderr.
VERIFIER = r'''
import argparse, base64, binascii, hashlib, json, sys
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

DOMAIN = {"config": b"cassandra-chorus/config/v1\n", "manifest": b"cassandra-chorus/manifest/v1\n"}

def fail(reason):
    print(reason, file=sys.stderr)
    sys.exit(1)

def verified_bytes(key, kind, path, sig_path):
    data = open(path, "rb").read()
    try:
        sig = base64.b64decode(open(sig_path, "rb").read().strip(), validate=True)
    except (binascii.Error, ValueError):
        fail(f"{kind}: signature is not valid base64")
    if len(sig) != 64:
        fail(f"{kind}: signature has {len(sig)} bytes, expected 64")
    try:
        key.verify(sig, DOMAIN[kind] + data)
    except InvalidSignature:
        fail(f"{kind}: signature does not verify")
    return data

p = argparse.ArgumentParser()
for a in ("pubkey", "config", "config_sig", "manifest", "manifest_sig", "archive"):
    p.add_argument("--" + a.replace("_", "-"), required=True)
a = p.parse_args()
raw = base64.b64decode(a.pubkey, validate=True)
if len(raw) != 32:
    fail("public key must be 32 bytes")
key = Ed25519PublicKey.from_public_bytes(raw)
config = json.loads(verified_bytes(key, "config", a.config, a.config_sig))      # parse only after verifying
manifest = json.loads(verified_bytes(key, "manifest", a.manifest, a.manifest_sig))
archive = open(a.archive, "rb").read()
entry = manifest["files"]["release.zip"]
if len(archive) != entry["bytes"] or hashlib.sha256(archive).hexdigest() != entry["sha256"]:
    fail("archive: SHA-256 or size does not match the manifest")
print(json.dumps({"config_run": config["run"], "config_serial": config["serial"], "release": manifest["version"]}))
'''


def b64(data: bytes) -> str:
    return base64.b64encode(data).decode("ascii")


def sign_file(key: Ed25519PrivateKey, kind: str, path: Path) -> Path:
    sig_path = path.with_suffix(path.suffix + ".sig")
    sig_path.write_text(b64(key.sign(DOMAIN[kind] + path.read_bytes())) + "\n", encoding="ascii")
    return sig_path


def owner_step(work: Path) -> dict[str, Any]:
    """Key, configuration, archive, manifest and signatures, all under ``work/owner``."""
    owner = work / "owner"
    owner.mkdir(parents=True)
    key = Ed25519PrivateKey.generate()
    (owner / "throwaway-signing-key.pem").write_bytes(key.private_bytes(
        serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()))
    pub = key.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)

    config = {  # an illustrative run configuration; a float is included on purpose (bytes are signed, not values)
        "run": "p9-dry-run", "serial": 1, "round_seconds": 1800, "deadline_seconds": 1500,
        "outer": {"name": "nesterov", "lr": 0.7, "momentum": 0.9},
        "members": [{"id": "m0", "storage": "hf://cassandra-chorus/proto-m0"}],
        "client_release": {"version": "0.0.0-dryrun"},
    }
    config_path = owner / "run-config.json"
    config_path.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")

    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO, check=True, capture_output=True, text=True).stdout.strip()
    archive = owner / "release.zip"
    subprocess.run(["git", "archive", "--format=zip", "-o", str(archive), commit], cwd=REPO, check=True)
    data = archive.read_bytes()
    manifest = {"name": "cassandra-chorus-client", "version": "0.0.0-dryrun", "commit": commit,
                "files": {"release.zip": {"sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}}}
    manifest_path = owner / "release-manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    return {"key": key, "pubkey_b64": b64(pub), "commit": commit, "archive_bytes": len(data),
            "files": {"config": config_path, "config_sig": sign_file(key, "config", config_path),
                      "manifest": manifest_path, "manifest_sig": sign_file(key, "manifest", manifest_path),
                      "archive": archive}}


def verify(work: Path, pubkey_b64: str, files: dict[str, Path]) -> dict[str, Any]:
    """Run the verifier in a fresh interpreter from an empty folder; return its outcome."""
    empty = work / "client-cwd"
    empty.mkdir(exist_ok=True)
    verifier = work / "client" / "verify.py"
    verifier.parent.mkdir(exist_ok=True)
    verifier.write_text(VERIFIER, encoding="utf-8")
    cmd = [sys.executable, "-E", "-P", str(verifier), "--pubkey", pubkey_b64] + [
        x for k in ("config", "config_sig", "manifest", "manifest_sig", "archive")
        for x in (f"--{k.replace('_', '-')}", str(files[k]))]
    proc = subprocess.run(cmd, cwd=empty, capture_output=True, text=True)
    return {"accepted": proc.returncode == 0, "exit_code": proc.returncode,
            "stdout": proc.stdout.strip(), "reason": proc.stderr.strip().splitlines()[-1] if proc.stderr.strip() else ""}


def tampered_copy(work: Path, name: str, files: dict[str, Path], **replace: bytes) -> dict[str, Path]:
    """A copy of the file set in ``work/cases/name`` with the given files' bytes replaced."""
    folder = work / "cases" / name
    folder.mkdir(parents=True)
    out = {}
    for k, path in files.items():
        dest = folder / path.name
        dest.write_bytes(replace.get(k, path.read_bytes()))
        out[k] = dest
    return out


def flip(data: bytes, index: int) -> bytes:
    b = bytearray(data)
    b[index] ^= 0x01
    return bytes(b)


def cases(work: Path, o: dict[str, Any]) -> list[tuple[str, str, dict[str, Path], str, bool]]:
    """Per case: name, description, files, the client's public key (base64), whether it must be accepted."""
    f = o["files"]
    config, sig = f["config"].read_bytes(), f["config_sig"].read_bytes()
    raw_sig = base64.b64decode(sig.strip())
    other_key = Ed25519PrivateKey.generate().public_key().public_bytes(serialization.Encoding.Raw,
                                                                       serialization.PublicFormat.Raw)
    archive = f["archive"].read_bytes()
    return [
        ("genuine", "the files as signed", f, o["pubkey_b64"], True),
        ("config-byte-flipped", "one bit flipped in the configuration's first value",
         tampered_copy(work, "config-byte-flipped", f, config=flip(config, config.index(b"p9-dry-run"))), o["pubkey_b64"], False),
        ("config-signature-flipped", "one bit flipped in the configuration's signature",
         tampered_copy(work, "config-signature-flipped", f, config_sig=(b64(flip(raw_sig, 10)) + "\n").encode()), o["pubkey_b64"], False),
        ("config-signature-truncated", "the configuration's signature cut to 63 bytes",
         tampered_copy(work, "config-signature-truncated", f, config_sig=(b64(raw_sig[:63]) + "\n").encode()), o["pubkey_b64"], False),
        ("wrong-public-key", "the client holds a different public key", f, b64(other_key), False),
        ("archive-modified", "one bit flipped in the middle of the release archive",
         tampered_copy(work, "archive-modified", f, archive=flip(archive, len(archive) // 2)), o["pubkey_b64"], False),
        ("signature-cross-type", "the configuration and its signature presented as the manifest and its signature",
         tampered_copy(work, "signature-cross-type", f, manifest=config, manifest_sig=sig), o["pubkey_b64"], False),
    ]


def run(work: Path) -> dict[str, Any]:
    import cryptography

    t0 = time.time()
    o = owner_step(work)
    results = []
    for name, description, files, pubkey, must_accept in cases(work, o):
        outcome = verify(work, pubkey, files)
        results.append({"case": name, "description": description, "must_accept": must_accept,
                        "as_expected": outcome["accepted"] == must_accept, **outcome})
    return {
        "prototype": "P9 signing dry run",
        "plan": "docs/implementations/2026-10-14-solo-prototypes.md",
        "python": sys.version.split()[0], "cryptography": cryptography.__version__,
        "verifier_command": "python -E -P verify.py ... (fresh process, started in an empty folder)",
        "release_commit": o["commit"], "archive_bytes": o["archive_bytes"],
        "domain_prefixes": {k: v.decode() for k, v in DOMAIN.items()},
        "cases": results,
        "all_as_expected": all(r["as_expected"] for r in results),
        "seconds": round(time.time() - t0, 1),
    }


def summary_markdown(report: dict[str, Any]) -> str:
    lines = ["# P9 signing dry run", "",
             f"Plan: `{report['plan']}`. Python {report['python']}, cryptography {report['cryptography']}; "
             f"release archive of commit `{report['release_commit'][:12]}` ({report['archive_bytes']:,} bytes). "
             f"Verifier: {report['verifier_command']}. One machine; throwaway key, deleted afterwards.", "",
             "| Case | What was changed | Must be | Verifier said | As expected |", "|---|---|---|---|---|"]
    for r in report["cases"]:
        said = "accepted" if r["accepted"] else f"rejected: {r['reason']}"
        lines.append(f"| {r['case']} | {r['description']} | {'accepted' if r['must_accept'] else 'rejected'} "
                     f"| {said} | {'yes' if r['as_expected'] else '**no**'} |")
    lines += ["", f"All cases as expected: **{'yes' if report['all_as_expected'] else 'no'}**.", ""]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--work-dir", type=Path, required=True, help="empty or missing folder outside the repository")
    parser.add_argument("--keep-files", action="store_true", help="keep the work folder (including the throwaway key)")
    args = parser.parse_args(argv)
    work = args.work_dir.resolve()
    if work.exists() and any(work.iterdir()):
        raise SystemExit(f"{work} is not empty")
    if REPO in work.parents or work == REPO:
        raise SystemExit("the work folder must be outside the repository (it holds a private key)")
    try:
        report = run(work)
    finally:
        if not args.keep_files:
            shutil.rmtree(work, ignore_errors=True)
    write_json(RESULTS_DIR / "p9_signing_dry_run.json", report)
    (RESULTS_DIR / "p9_signing_dry_run.md").write_text(summary_markdown(report), encoding="utf-8")
    print(summary_markdown(report))
    return 0 if report["all_as_expected"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
