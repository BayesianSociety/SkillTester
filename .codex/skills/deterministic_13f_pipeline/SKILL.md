---
name: deterministic-13f-pipeline
description: Deterministically fetch the latest SEC Form 13F-HR URL with get_13f.py and extract key fields with extract_filing.py; use whenever Codex must run those scripts end-to-end and capture their artifacts.
---

## Workflow
1. Change into the project root (SkillTester) so the scripts can read and write adjacent files.
2. Run `python3 get_13f.py`. This script fetches the SEC submissions feed for the hard-coded Central Index Key and writes the most recent 13F-HR filing URL to `output.txt`. If the script prints `None`, stop and investigate because the remaining steps depend on that URL.
3. Confirm that `output.txt` exists and contains a non-empty URL. Open the file or `cat output.txt` to double-check.
4. Run `python3 extract_filing.py`. It reads the URL from `output.txt`, downloads the filing, and prints the “Company Conformed Name” and “Conformed period of report” to standard output. Redirect stdout to a file inside `outputs/` if persistent artifacts are required (for example, `python3 extract_filing.py > outputs/filing_fields.txt`).
5. Copy any logs you want to keep under `logs/` (for example, pipe the command output through `tee logs/extract.log`) so downstream checks can confirm the run.

## Configurable Inputs
- `get_13f.py` currently pads and queries the Central Index Key hardcoded near the end of the file (variable `result = get_latest_13f_url("0002012383")`). Update that literal if you need to target a different filer before running the scripts.

## Expected Artifacts
- `output.txt` in the project root containing the resolved 13F-HR filing URL.
- Console output from `python3 extract_filing.py` that lists the extracted fields; optionally saved into `outputs/` if redirected manually.
- Any additional log files you manually create under `logs/` (for example, `logs/get_13f.log` or `logs/extract.log`).

## Troubleshooting
- If `output.txt` is missing or empty, rerun `python3 get_13f.py` and inspect its stdout for HTTP errors; network failures or a missing filing type are the most common causes.
- If `python3 extract_filing.py` raises “output.txt does not contain a valid filing URL,” open the file to verify it holds a full `https://` URL and rerun `get_13f.py` if it does not.
- If the extractor prints `None` for either field, ensure the SEC filing actually contains the expected headers; re-run the script after confirming the target URL.***
