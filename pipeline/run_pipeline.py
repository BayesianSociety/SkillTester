#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def run_and_log(step_name: str, cmd: List[str], cwd: Path, log_path: Path, env: Dict[str, str]) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)

    # Deterministic retry policy (fixed attempts, fixed delays)
    attempts = 3
    delays_seconds = [0, 2, 5]  # attempt 1 has no delay, then 2s, then 5s

    last_rc = None
    for attempt in range(attempts):
        if delays_seconds[attempt] > 0:
            import time
            time.sleep(delays_seconds[attempt])

        # Write each attempt into the same log (append) so you have a single deterministic log file
        mode = "ab" if attempt > 0 else "wb"
        with log_path.open(mode) as log_file:
            if attempt > 0:
                log_file.write(f"\n--- RETRY {attempt+1}/{attempts} ---\n".encode("utf-8"))

            proc = subprocess.run(
                cmd,
                cwd=str(cwd),
                env=env,
                stdout=log_file,
                stderr=subprocess.STDOUT,
                check=False,
            )
            last_rc = proc.returncode

        if last_rc == 0:
            return

    raise RuntimeError(
        f"Step '{step_name}' failed after {attempts} attempts. "
        f"Last exit code {last_rc}. See log: {log_path}"
    )



def main() -> int:
    project_root = Path(__file__).resolve().parents[1]
    logs_dir = project_root / "logs"
    outputs_dir = project_root / "outputs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    outputs_dir.mkdir(parents=True, exist_ok=True)

    # Deterministic environment
    env = dict(os.environ)
    env["PYTHONHASHSEED"] = "0"
    env["LC_ALL"] = "C"
    env["LANG"] = "C"
    env["FORCE_IPV4"] = "1"

    get_13f_path = project_root / "get_13f.py"
    extract_wrapper_path = project_root / "pipeline" / "extract_from_output.py"
    extract_filing_path = project_root / "extract_filing.py"

    if not get_13f_path.exists():
        raise FileNotFoundError(f"Missing: {get_13f_path}")
    if not extract_wrapper_path.exists():
        raise FileNotFoundError(f"Missing: {extract_wrapper_path}")
    if not extract_filing_path.exists():
        raise FileNotFoundError(f"Missing: {extract_filing_path}")

    # Step 1: run get_13f.py (your file writes output.txt in project root)
    run_and_log(
        step_name="get_13f",
        cmd=[sys.executable, str(get_13f_path)],
        cwd=project_root,
        log_path=logs_dir / "01_get_13f.log",
        env=env,
    )

    output_txt = project_root / "output.txt"
    if not output_txt.exists():
        raise RuntimeError("get_13f.py did not create output.txt (expected in project root).")

    raw = output_txt.read_text(encoding="utf-8").strip()
    if not raw.startswith("http"):
        raise RuntimeError("output.txt does not appear to contain a valid URL. See logs/01_get_13f.log")

    # Step 2: run extraction wrapper (reads output.txt, fetches filing, writes outputs/*)
    run_and_log(
        step_name="extract_fields",
        cmd=[sys.executable, str(extract_wrapper_path)],
        cwd=project_root,
        log_path=logs_dir / "02_extract_fields.log",
        env=env,
    )

    # Write a deterministic manifest with hashes + output paths
    manifest = {
        "scripts": {
            "get_13f.py": {"sha256": sha256_file(get_13f_path)},
            "extract_filing.py": {"sha256": sha256_file(extract_filing_path)},
            "pipeline/extract_from_output.py": {"sha256": sha256_file(extract_wrapper_path)},
        },
        "outputs": {
            "output.txt": str(output_txt.resolve()),
            "outputs/filing_url.txt": str((outputs_dir / "filing_url.txt").resolve()),
            "outputs/filing_fields.json": str((outputs_dir / "filing_fields.json").resolve()),
        },
        "logs": {
            "logs/01_get_13f.log": str((logs_dir / "01_get_13f.log").resolve()),
            "logs/02_extract_fields.log": str((logs_dir / "02_extract_fields.log").resolve()),
        },
        "environment": {
            "PYTHONHASHSEED": env["PYTHONHASHSEED"],
            "LC_ALL": env["LC_ALL"],
            "LANG": env["LANG"],
            "python": sys.executable,
        },
    }

    (outputs_dir / "run_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
