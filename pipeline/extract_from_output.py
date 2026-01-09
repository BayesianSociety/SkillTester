#!/usr/bin/env python3
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict
import sys
from pathlib import Path

# Ensure project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from extract_filing import fetch_and_extract, read_filing_url_from_file


def main() -> int:
    # Enforce deterministic environment settings (the orchestrator also enforces these)
    os.environ.setdefault("PYTHONHASHSEED", "0")

    project_root = Path(__file__).resolve().parents[1]
    outputs_dir = project_root / "outputs"
    outputs_dir.mkdir(parents=True, exist_ok=True)

    # Read the URL produced by get_13f.py (it writes output.txt in project root)
    filing_url = read_filing_url_from_file(str(project_root / "output.txt"))

    # Fetch and extract fields from the filing
    fields: Dict[str, str | None] = fetch_and_extract(filing_url)

    # Write deterministic output files
    (outputs_dir / "filing_url.txt").write_text(filing_url + "\n", encoding="utf-8")
    (outputs_dir / "filing_fields.json").write_text(
        json.dumps(fields, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
