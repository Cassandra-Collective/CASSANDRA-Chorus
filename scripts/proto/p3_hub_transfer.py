"""P3: update-sized transfers from this home (docs/implementations/2026-10-14-solo-prototypes.md).

For each host (a private Hub repository with Xet storage, and a private
Storage Bucket), each size (0.2 and 0.6 GB of float32 safetensors) and each
repeat (fresh random content every time):

* upload time, from the call until it returns;
* visibility delay, from that return until a separate process first sees the
  file in a listing (polled every 0.5 s);
* download time, in a separate process, into an empty folder, bypassing the
  file cache (``force_download``); the download's SHA-256 is checked.

Then, on the repository only, three 0.2 GB uploads that differ in how much
they share with an earlier upload: an identical copy, a copy with every value
perturbed slightly (as successive training updates are), and fresh random
values. Their upload times show what Xet's deduplication saves.

Results are written after every transfer. The token is never printed or written.

Usage:
    python scripts/proto/p3_hub_transfer.py --org cassandra-chorus --work-dir DIR [--sizes 0.2:3,0.6:1] [--repeats 3]
"""

from __future__ import annotations

import argparse
import concurrent.futures as cf
import hashlib
import shutil
import sys
import time
from pathlib import Path
from typing import Any

import torch
from safetensors.torch import load_file, save_file

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from cassandra_chorus.repro import derive_seed  # noqa: E402
from scripts.proto.common import RESULTS_DIR, guarded_token, record_hub_resource, write_json  # noqa: E402

RESULT_JSON = RESULTS_DIR / "p3_hub_transfer.json"
RESULT_MD = RESULTS_DIR / "p3_hub_transfer.md"
CHUNK_ELEMENTS = 16 * 2**20  # 64 MiB float32 tensors


def make_file(path: Path, gigabytes: float, seed_label: str) -> dict[str, Any]:
    """Seeded random float32 tensors totalling ``gigabytes`` (10^9 bytes), as one safetensors file."""
    total = int(gigabytes * 1e9 / 4)
    g = torch.Generator().manual_seed(derive_seed(7, f"p3/{seed_label}"))
    tensors, i = {}, 0
    while total > 0:
        n = min(CHUNK_ELEMENTS, total)
        tensors[f"t{i:03d}"] = torch.randn(n, generator=g)
        total -= n
        i += 1
    save_file(tensors, str(path))
    return {"bytes": path.stat().st_size, "sha256": sha256(path)}


def perturbed_copy(src: Path, dest: Path) -> dict[str, Any]:
    """Every value of ``src`` plus noise 1e-3 times its standard deviation: a 'successive update'."""
    tensors = load_file(str(src))
    g = torch.Generator().manual_seed(derive_seed(7, f"p3/perturb/{dest.name}"))
    save_file({k: v + 1e-3 * torch.randn(v.shape, generator=g) for k, v in tensors.items()}, str(dest))
    return {"bytes": dest.stat().st_size, "sha256": sha256(dest)}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(2**24), b""):
            h.update(block)
    return h.hexdigest()


def mbit_per_s(nbytes: int, seconds: float) -> float:
    return round(8 * nbytes / 1e6 / seconds, 1) if seconds > 0 else float("inf")


def _status(e: Exception) -> int | None:
    return getattr(getattr(e, "response", None), "status_code", None)


# ----- run in separate processes (fresh HTTP sessions, nothing shared with the uploader) -----


def poll_visible(token: str, host: str, target: str, path_in_host: str, seconds: float = 120) -> dict[str, Any]:
    from huggingface_hub import HfApi

    api = HfApi(token=token)
    t0 = time.time()
    polls = 0
    while time.time() - t0 < seconds:
        polls += 1
        try:
            if host == "repo":
                found = any(f.path == path_in_host for f in api.list_repo_tree(target, path_in_repo=str(Path(path_in_host).parent).replace("\\", "/")))
            else:
                found = any(getattr(f, "path", None) == path_in_host
                            for f in api.list_bucket_tree(target, prefix=str(Path(path_in_host).parent).replace("\\", "/"), recursive=True))
        except Exception:  # noqa: BLE001 (not there yet)
            found = False
        if found:
            return {"visible_after_s": round(time.time() - t0, 2), "polls": polls}
        time.sleep(0.5)
    return {"visible_after_s": None, "polls": polls}


def download(token: str, host: str, target: str, path_in_host: str, dest_dir: str) -> dict[str, Any]:
    from huggingface_hub import HfApi

    api = HfApi(token=token)
    dest = Path(dest_dir)
    dest.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    try:
        if host == "repo":
            local = Path(api.hf_hub_download(target, path_in_host, local_dir=str(dest), force_download=True))
        else:
            local = dest / Path(path_in_host).name
            api.download_bucket_files(target, [(path_in_host, str(local))], raise_on_missing_files=True)
        seconds = time.time() - t0
        return {"ok": True, "seconds": round(seconds, 2), "sha256": sha256(local), "bytes": local.stat().st_size}
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "seconds": round(time.time() - t0, 2), "status": _status(e), "error": type(e).__name__,
                "message": str(e).splitlines()[0][:200] if str(e) else ""}


# ----- driver -----


def upload(api, host: str, target: str, local: Path, path_in_host: str) -> dict[str, Any]:
    t0 = time.time()
    try:
        if host == "repo":
            api.upload_file(path_or_fileobj=str(local), path_in_repo=path_in_host, repo_id=target,
                            commit_message=f"P3 {path_in_host}")
        else:
            api.batch_bucket_files(target, add=[(str(local), path_in_host)])
        return {"ok": True, "seconds": round(time.time() - t0, 2)}
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "seconds": round(time.time() - t0, 2), "status": _status(e), "error": type(e).__name__,
                "message": str(e).splitlines()[0][:200] if str(e) else ""}


def in_fresh_process(fn, *args) -> dict[str, Any]:
    with cf.ProcessPoolExecutor(max_workers=1) as pool:
        return pool.submit(fn, *args).result()


def transfer(api, token: str, host: str, target: str, local: Path, info: dict[str, Any], path_in_host: str,
             work: Path, label: str) -> dict[str, Any]:
    up = upload(api, host, target, local, path_in_host)
    row: dict[str, Any] = {"host": host, "label": label, "path": path_in_host, "bytes": info["bytes"], "upload": up}
    if up["ok"]:
        up["mbit_s"] = mbit_per_s(info["bytes"], up["seconds"])
        row["visibility"] = in_fresh_process(poll_visible, token, host, target, path_in_host)
        dl_dir = work / "downloads" / f"{host}-{label}"
        down = in_fresh_process(download, token, host, target, path_in_host, str(dl_dir))
        if down["ok"]:
            down["mbit_s"] = mbit_per_s(down["bytes"], down["seconds"])
            down["sha256_matches"] = down["sha256"] == info["sha256"]
        row["download"] = down
        shutil.rmtree(dl_dir, ignore_errors=True)
    print(f"[p3] {host} {label}: upload {up.get('seconds')} s ({up.get('mbit_s')} Mbit/s)"
          f"{'' if not up['ok'] else ', download ' + str(row['download'].get('seconds')) + ' s (' + str(row['download'].get('mbit_s')) + ' Mbit/s)'}",
          flush=True)
    return row


def parse_sizes(text: str, default_repeats: int) -> list[tuple[float, int]]:
    """``"0.2:3,0.6:1"`` to ``[(0.2, 3), (0.6, 1)]``; a size without ``:n`` gets ``default_repeats``."""
    out = []
    for item in text.split(","):
        size, _, n = item.partition(":")
        out.append((float(size), int(n) if n else default_repeats))
    return out


def run(org: str, work: Path, sizes: list[tuple[float, int]], hosts: list[str], dedup: bool) -> dict[str, Any]:
    token = guarded_token(org)
    from huggingface_hub import HfApi

    api = HfApi(token=token)
    repo_id, bucket_id = f"{org}/proto-transfer", f"{org}/proto-transfer-bucket"
    work.mkdir(parents=True, exist_ok=True)
    report: dict[str, Any] = {"prototype": "P3 transfers from this home", "plan": "docs/implementations/2026-10-14-solo-prototypes.md",
                              "org": org, "repo": repo_id, "bucket": bucket_id,
                              "time_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "transfers": [], "dedup": []}
    if "repo" in hosts:
        record_hub_resource("repo", repo_id, "P3")
        api.create_repo(repo_id, private=True, exist_ok=True)
    if "bucket" in hosts:
        record_hub_resource("bucket", bucket_id, "P3")
        api.create_bucket(bucket_id, private=True, exist_ok=True)

    def save() -> None:
        write_json(RESULT_JSON, report)
        RESULT_MD.write_text(summary_markdown(report), encoding="utf-8")

    for size, repeats in sizes:
        for rep in range(repeats):
            label = f"{size:g}GB-r{rep}"
            local = work / f"{label}.safetensors"
            info = make_file(local, size, label)
            for host in hosts:
                target = repo_id if host == "repo" else bucket_id
                report["transfers"].append(transfer(api, token, host, target, local, info, f"p3/{label}.safetensors", work, label))
                save()
            local.unlink()

    if dedup and "repo" in hosts:
        base = work / "dedup-base.safetensors"
        info = make_file(base, 0.2, "dedup-base")
        report["dedup"].append({"case": "base (fresh random)", **transfer(api, token, "repo", repo_id, base, info, "p3/dedup/base.safetensors", work, "dedup-base")})
        save()
        report["dedup"].append({"case": "identical copy", **transfer(api, token, "repo", repo_id, base, info, "p3/dedup/identical.safetensors", work, "dedup-identical")})
        save()
        pert = work / "dedup-perturbed.safetensors"
        pinfo = perturbed_copy(base, pert)
        report["dedup"].append({"case": "every value perturbed (1e-3 sd)", **transfer(api, token, "repo", repo_id, pert, pinfo, "p3/dedup/perturbed.safetensors", work, "dedup-perturbed")})
        save()
        fresh = work / "dedup-fresh.safetensors"
        finfo = make_file(fresh, 0.2, "dedup-fresh")
        report["dedup"].append({"case": "fresh random", **transfer(api, token, "repo", repo_id, fresh, finfo, "p3/dedup/fresh.safetensors", work, "dedup-fresh")})
        save()
        for p in (base, pert, fresh):
            p.unlink(missing_ok=True)
    report["finished_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    save()
    return report


def summary_markdown(r: dict[str, Any]) -> str:
    def cell(d: dict[str, Any] | None, key: str = "seconds") -> str:
        if not d:
            return "n/a"
        if not d.get("ok", True):
            return f"failed ({d.get('status')} {d.get('error')})"
        return f"{d.get(key)} s, {d.get('mbit_s')} Mbit/s"

    lines = ["# P3 transfers from this home", "",
             f"Plan: `{r['plan']}`. Repository `{r['repo']}` and bucket `{r['bucket']}` (both private); started {r['time_utc']}"
             f"{', finished ' + r['finished_utc'] if 'finished_utc' in r else ' (unfinished)'}. One home connection, one machine; "
             "uploads and downloads of float32 safetensors with fresh random content (sizes in 10^9 bytes).", "",
             "| Host | File | Bytes | Upload | Visible after (s) | Download | SHA-256 matches |", "|---|---|---|---|---|---|---|"]
    for t in r["transfers"]:
        lines.append(f"| {t['host']} | {t['label']} | {t['bytes']:,} | {cell(t['upload'])} | "
                     f"{(t.get('visibility') or {}).get('visible_after_s', 'n/a')} | {cell(t.get('download'))} | "
                     f"{(t.get('download') or {}).get('sha256_matches', 'n/a')} |")
    if r["dedup"]:
        lines += ["", "## Xet deduplication (repository, 0.2 GB)", "", "| Case | Upload | Download |", "|---|---|---|"]
        for d in r["dedup"]:
            lines.append(f"| {d['case']} | {cell(d['upload'])} | {cell(d.get('download'))} |")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--org", required=True)
    parser.add_argument("--work-dir", type=Path, required=True, help="local folder for the generated files")
    parser.add_argument("--sizes", default="0.2,0.6", help='sizes in GB, each optionally with ":repeats", e.g. "0.2:3,0.6:1"')
    parser.add_argument("--repeats", type=int, default=3, help="repeats for sizes given without :n")
    parser.add_argument("--hosts", default="repo,bucket")
    parser.add_argument("--no-dedup", action="store_true")
    args = parser.parse_args(argv)
    from cassandra_chorus.ops.power import keep_awake

    with keep_awake() as awake:  # held from launch: standby would stall the transfers (laptop power notes)
        report = run(args.org, args.work_dir, parse_sizes(args.sizes, args.repeats), args.hosts.split(","), not args.no_dedup)
        report["keep_awake"] = dict(awake)
        write_json(RESULT_JSON, report)
    print(summary_markdown(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
