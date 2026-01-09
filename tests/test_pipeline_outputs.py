from pathlib import Path
import json


def test_pipeline_outputs_exist_and_are_well_formed():
    project_root = Path(__file__).resolve().parents[1]
    outputs = project_root / "outputs"
    logs = project_root / "logs"

    assert (logs / "01_get_13f.log").exists()
    assert (logs / "02_extract_fields.log").exists()

    assert (outputs / "filing_url.txt").exists()
    assert (outputs / "filing_fields.json").exists()
    assert (outputs / "run_manifest.json").exists()

    data = json.loads((outputs / "filing_fields.json").read_text(encoding="utf-8"))
    assert "Company Conformed Name" in data
    assert "Conformed period of report" in data

    manifest = json.loads((outputs / "run_manifest.json").read_text(encoding="utf-8"))
    assert "scripts" in manifest
    assert "outputs" in manifest
    assert "logs" in manifest
