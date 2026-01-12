import json
from pathlib import Path


def test_tool_get_latest_13f_url(monkeypatch):
    import mcp_server

    monkeypatch.setattr(mcp_server, "get_latest_13f_url", lambda cik: "http://example.test/filing.txt")
    result = mcp_server.tool_get_latest_13f_url("0000000000")
    assert result == {"filing_url": "http://example.test/filing.txt"}


def test_tool_fetch_and_extract(monkeypatch):
    import mcp_server

    expected = {
        "Company Conformed Name": "Example Capital",
        "Conformed period of report": "20240101",
    }
    monkeypatch.setattr(mcp_server, "fetch_and_extract", lambda url: expected)
    result = mcp_server.tool_fetch_and_extract("http://example.test/filing.txt")
    assert result == expected


def test_tool_run_deterministic_pipeline(monkeypatch, tmp_path):
    import mcp_server

    outputs_dir = tmp_path / "outputs"
    outputs_dir.mkdir(parents=True, exist_ok=True)

    manifest = {
        "outputs": {
            "output.txt": str((outputs_dir / "output.txt").resolve()),
            "outputs/filing_url.txt": str((outputs_dir / "filing_url.txt").resolve()),
        },
        "logs": {
            "logs/01_get_13f.log": str((tmp_path / "logs" / "01_get_13f.log").resolve()),
        },
    }
    (outputs_dir / "run_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    def fake_run(cmd, cwd, env, check):
        assert Path(cwd) == tmp_path
        assert check is True
        assert env.get("CIK") == "0000000000"
        return None

    monkeypatch.setattr(mcp_server, "OUTPUTS_DIR", outputs_dir)
    monkeypatch.setattr(mcp_server, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(mcp_server.subprocess, "run", fake_run)

    result = mcp_server.tool_run_deterministic_pipeline("0000000000")
    assert result["manifest_path"] == str((outputs_dir / "run_manifest.json").resolve())
    assert set(result["created_files"]) == set(manifest["outputs"].values()) | set(
        manifest["logs"].values()
    )
    assert result["manifest"] == manifest
