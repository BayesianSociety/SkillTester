#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Iterable

import anyio
from mcp import types
from mcp.server import Server
from mcp.server.stdio import stdio_server

from extract_filing import fetch_and_extract
from get_13f import get_latest_13f_url

PROJECT_ROOT = Path(__file__).resolve().parent
OUTPUTS_DIR = PROJECT_ROOT / "outputs"
LOGS_DIR = PROJECT_ROOT / "logs"

LATEST_OUTPUTS_URI = "skilltester://latest_outputs"


def _set_deterministic_env(env: Dict[str, str]) -> None:
    env["PYTHONHASHSEED"] = "0"
    env["LC_ALL"] = "C"
    env["LANG"] = "C"


def tool_get_latest_13f_url(cik: str) -> Dict[str, str | None]:
    return {"filing_url": get_latest_13f_url(cik)}


def tool_fetch_and_extract(filing_url: str) -> Dict[str, str | None]:
    return fetch_and_extract(filing_url)


def tool_run_deterministic_pipeline(cik: str | None = None) -> Dict[str, Any]:
    env = dict(os.environ)
    _set_deterministic_env(env)
    if cik:
        env["CIK"] = cik

    run_script = PROJECT_ROOT / "pipeline" / "run_pipeline.py"
    subprocess.run(
        [sys.executable, str(run_script)],
        cwd=str(PROJECT_ROOT),
        env=env,
        check=True,
    )

    manifest_path = OUTPUTS_DIR / "run_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    created_files = []
    created_files.extend(manifest.get("outputs", {}).values())
    created_files.extend(manifest.get("logs", {}).values())

    return {
        "manifest_path": str(manifest_path.resolve()),
        "created_files": created_files,
        "manifest": manifest,
    }


def read_latest_outputs_text() -> str:
    parts: list[str] = []
    for name in ("filing_url.txt", "filing_fields.json", "run_manifest.json"):
        path = OUTPUTS_DIR / name
        if path.exists():
            content = path.read_text(encoding="utf-8")
            parts.append(f"## {name}\n{content}")
        else:
            parts.append(f"## {name}\n<missing>\n")
    return "\n".join(parts)


def create_server() -> Server:
    server = Server(
        name="skilltester-13f",
        instructions="Retrieve and parse SEC 13F filings deterministically.",
    )

    @server.list_tools()
    async def list_tools() -> list[types.Tool]:
        return [
            types.Tool(
                name="get_latest_13f_url",
                title="Get Latest 13F Filing URL",
                description="Resolve the most recent 13F-HR filing URL for a CIK.",
                inputSchema={
                    "type": "object",
                    "properties": {"cik": {"type": "string"}},
                    "required": ["cik"],
                    "additionalProperties": False,
                },
                outputSchema={
                    "type": "object",
                    "properties": {"filing_url": {"type": ["string", "null"]}},
                    "required": ["filing_url"],
                    "additionalProperties": False,
                },
            ),
            types.Tool(
                name="fetch_and_extract",
                title="Fetch Filing Fields",
                description="Fetch a filing URL and extract key fields.",
                inputSchema={
                    "type": "object",
                    "properties": {"filing_url": {"type": "string"}},
                    "required": ["filing_url"],
                    "additionalProperties": False,
                },
                outputSchema={
                    "type": "object",
                    "properties": {
                        "Company Conformed Name": {"type": ["string", "null"]},
                        "Conformed period of report": {"type": ["string", "null"]},
                    },
                    "required": [
                        "Company Conformed Name",
                        "Conformed period of report",
                    ],
                    "additionalProperties": False,
                },
            ),
            types.Tool(
                name="run_deterministic_pipeline",
                title="Run Deterministic Pipeline",
                description="Run the deterministic pipeline and return the manifest and created files.",
                inputSchema={
                    "type": "object",
                    "properties": {"cik": {"type": "string"}},
                    "additionalProperties": False,
                },
                outputSchema={
                    "type": "object",
                    "properties": {
                        "manifest_path": {"type": "string"},
                        "created_files": {"type": "array", "items": {"type": "string"}},
                        "manifest": {"type": "object"},
                    },
                    "required": ["manifest_path", "created_files", "manifest"],
                    "additionalProperties": False,
                },
            ),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict[str, Any]) -> Dict[str, Any]:
        if name == "get_latest_13f_url":
            return tool_get_latest_13f_url(arguments["cik"])
        if name == "fetch_and_extract":
            return tool_fetch_and_extract(arguments["filing_url"])
        if name == "run_deterministic_pipeline":
            return tool_run_deterministic_pipeline(arguments.get("cik"))
        raise ValueError(f"Unknown tool: {name}")

    @server.list_resources()
    async def list_resources() -> list[types.Resource]:
        return [
            types.Resource(
                name="latest_outputs",
                title="Latest Pipeline Outputs",
                uri=LATEST_OUTPUTS_URI,
                description="Concatenated contents of the latest output files.",
                mimeType="text/plain",
            )
        ]

    @server.read_resource()
    async def read_resource(uri: str) -> str:
        if uri != LATEST_OUTPUTS_URI:
            raise ValueError(f"Unknown resource URI: {uri}")
        return read_latest_outputs_text()

    return server


async def _run_server() -> None:
    server = create_server()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


def main() -> int:
    env = os.environ
    _set_deterministic_env(env)
    anyio.run(_run_server)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
