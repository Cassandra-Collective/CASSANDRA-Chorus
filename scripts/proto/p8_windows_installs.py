"""P8: do the candidate libraries install and import natively on Windows? (docs/implementations/2026-10-14-solo-prototypes.md)

Creates a fresh virtual environment (outside the repository), then installs
each package in its own ``pip install`` so one failure does not hide the
others. For each package, recorded:

* whether pip used a prebuilt wheel or tried to build from source;
* the installed version (``pip show``), or the tail of pip's output on failure;
* whether the module imports, in the virtual environment's own interpreter.

iroh and libp2p are imported only, never started: started with defaults they
would contact third-party relays and DHTs, which D37 rules out. Package list
approved by the owner on 2026-10-14 ("latest versions").

Usage:
    python scripts/proto/p8_windows_installs.py --venv DIR [--keep]
"""

from __future__ import annotations

import argparse
import platform
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from scripts.proto.common import RESULTS_DIR, write_json  # noqa: E402

# (pip requirement, module to import, distribution name for pip show)
PACKAGES = [
    ("huggingface_hub[hf_xet]", "huggingface_hub", "huggingface_hub"),
    ("hf_xet", "hf_xet", "hf_xet"),
    ("safetensors", "safetensors", "safetensors"),
    ("cryptography", "cryptography", "cryptography"),
    ("iroh", "iroh", "iroh"),
    ("libp2p", "libp2p", "libp2p"),
]


def sh(cmd: list[str], timeout: int = 1800) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, encoding="utf-8", errors="replace")


def run(venv: Path) -> dict[str, Any]:
    t0 = time.time()
    created = sh([sys.executable, "-m", "venv", str(venv)])
    py = venv / "Scripts" / "python.exe"
    report: dict[str, Any] = {
        "prototype": "P8 Windows installs", "plan": "docs/implementations/2026-10-14-solo-prototypes.md",
        "time_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "os": platform.platform(),
        "base_python": sys.version.split()[0], "venv_created": created.returncode == 0 and py.exists(),
        "packages": [],
    }
    if not report["venv_created"]:
        report["venv_error"] = (created.stderr or created.stdout)[-1500:]
        return report
    pip_up = sh([str(py), "-m", "pip", "install", "--upgrade", "pip"])
    report["pip"] = sh([str(py), "-m", "pip", "--version"]).stdout.strip()
    report["pip_upgrade_ok"] = pip_up.returncode == 0
    for requirement, module, dist in PACKAGES:
        t = time.time()
        try:
            r = sh([str(py), "-m", "pip", "install", requirement])
            out = (r.stdout or "") + (r.stderr or "")
            entry: dict[str, Any] = {
                "requirement": requirement, "install_ok": r.returncode == 0, "seconds": round(time.time() - t, 1),
                "built_from_source": "Building wheel for" in out or "setup.py" in out or "Preparing metadata (pyproject.toml)" in out,
            }
        except subprocess.TimeoutExpired:
            out, entry = "", {"requirement": requirement, "install_ok": False, "seconds": round(time.time() - t, 1),
                              "error": "timeout after 1800 s"}
        if entry["install_ok"]:
            show = sh([str(py), "-m", "pip", "show", dist]).stdout
            entry["version"] = next((ln.split(":", 1)[1].strip() for ln in show.splitlines() if ln.startswith("Version:")), None)
            imp = sh([str(py), "-c", f"import {module}; print(getattr({module}, '__version__', 'imported'))"])
            entry["import_ok"] = imp.returncode == 0
            if imp.returncode == 0:
                entry["import_output"] = imp.stdout.strip()[:300]
            else:
                entry["import_output"] = (imp.stderr.strip().splitlines() or [""])[-1][:300]
        else:
            entry["pip_tail"] = out[-2500:]
        report["packages"].append(entry)
        print(f"[p8] {requirement}: install {'ok' if entry['install_ok'] else 'FAILED'}"
              f"{', import ' + ('ok' if entry.get('import_ok') else 'FAILED') if entry['install_ok'] else ''}", flush=True)
    report["freeze"] = sh([str(py), "-m", "pip", "freeze"]).stdout.splitlines()
    report["seconds"] = round(time.time() - t0, 1)
    return report


def summary_markdown(r: dict[str, Any]) -> str:
    lines = ["# P8 Windows installs", "",
             f"Plan: `{r['plan']}`. Run {r['time_utc']} on {r['os']}; base Python {r['base_python']}; fresh virtual environment; "
             f"{r.get('pip', 'pip unknown')}. Packages installed one at a time at their latest versions (owner's choice).", "",
             "| Requirement | Install | Built from source | Version | Import | Note |", "|---|---|---|---|---|---|"]
    for p in r["packages"]:
        if p["install_ok"]:
            note = "" if p.get("import_ok") else p.get("import_output", "")  # the version column already says what imported
        else:
            note = p.get("error") or (p.get("pip_tail", "").strip().splitlines() or [""])[-1]
        note = " ".join(str(note).split()).replace("|", "/")[:160]
        lines.append(f"| {p['requirement']} | {'ok' if p['install_ok'] else '**failed**'} | "
                     f"{'yes' if p.get('built_from_source') else 'no'} | {p.get('version', '')} | "
                     f"{'ok' if p.get('import_ok') else ('**failed**' if p['install_ok'] else 'n/a')} | {note} |")
    lines += ["", f"Total time: {r.get('seconds')} s. `pip freeze` of the environment is in the JSON file.", ""]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--venv", type=Path, required=True, help="new folder for the virtual environment (outside the repository)")
    parser.add_argument("--keep", action="store_true", help="keep the virtual environment afterwards")
    args = parser.parse_args(argv)
    venv = args.venv.resolve()
    if venv.exists():
        raise SystemExit(f"{venv} exists; pass a new folder")
    if REPO in venv.parents:
        raise SystemExit("the virtual environment must be outside the repository")
    try:
        report = run(venv)
    finally:
        if not args.keep:
            shutil.rmtree(venv, ignore_errors=True)
    write_json(RESULTS_DIR / "p8_windows_installs.json", report)
    (RESULTS_DIR / "p8_windows_installs.md").write_text(summary_markdown(report), encoding="utf-8")
    print(summary_markdown(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
