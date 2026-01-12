SkillTester 13F Pipeline + MCP Server

Overview
- Fetches the latest SEC 13F-HR filing URL for a CIK.
- Extracts key filing fields and writes deterministic outputs under outputs/.
- Provides a Model Context Protocol server with tools and a resource for outputs.

Deterministic pipeline
- Run: `./run_pipeline_deterministic.sh`
- Outputs: `outputs/filing_url.txt`, `outputs/filing_fields.json`, `outputs/run_manifest.json`
- Logs: `logs/01_get_13f.log`, `logs/02_extract_fields.log`

MCP server (stdio transport)
1. Start the server in one terminal:
   - `python3 mcp_server.py`
2. Connect with a Model Context Protocol client in another terminal:
   - `python3 -m mcp.client python3 mcp_server.py`

Tools
- `get_latest_13f_url(cik: string)` -> `{ "filing_url": string | null }`
- `fetch_and_extract(filing_url: string)` -> `{ "Company Conformed Name": string | null, "Conformed period of report": string | null }`
- `run_deterministic_pipeline(cik?: string)` -> `{ "manifest_path": string, "created_files": [string], "manifest": object }`

Resource
- `skilltester://latest_outputs` returns the latest output files concatenated as text.





─ Worked for 3m 13s ──────────────────────────────────────────────────────────────────────────────────────────────

• Implemented the MCP server and wiring, plus deterministic tool tests and docs, so the repo now exposes the
  pipeline as MCP tools/resources while keeping the existing pipeline intact. Updated get_13f.py to remove import-
  time side effects and accept a CIK via environment variable or command line so MCP and the pipeline can control
  inputs safely.

  Details and rationale:

  - MCP server entry point with stdio transport, tool handlers, and resource reader is in mcp_server.py.
  - Deterministic environment setup is centralized and applied when running the server and the pipeline.
  - get_13f.py now only executes when run as a script and supports CIK or a CLI argument.
  - Added dependency declaration and usage docs in requirements.txt and README.md.
  - Added deterministic tests for MCP tool functions in tests/test_mcp_server_tools.py.

  Files changed/added:

  - get_13f.py
  - mcp_server.py
  - README.md
  - requirements.txt
  - tests/test_mcp_server_tools.py

  If you want to verify quickly:

  1. python3 mcp_server.py
  2. python3 -m mcp.client python3 mcp_server.py

  Optional next steps:

  1. Run tests with python3 -m pytest
  2. Run the deterministic pipeline with ./run_pipeline_deterministic.sh
 

• Register
Paste this into ~/.codex/config.toml (or add it to the existing file). It registers your local STDIO MCP server at /home/postnl/SkillTester/mcp_server.py:

[mcp_servers.skilltester]
command = "python3"
args = ["-u", "/home/postnl/SkillTester/mcp_server.py"]
cwd = "/home/postnl/SkillTester"
enabled = true
startup_timeout_sec = 20
tool_timeout_sec = 60

[mcp_servers.skilltester.env]
PYTHONUNBUFFERED = "1"
  
• Here’s how to run the already‑registered MCP from the Codex agent:

  1. Start Codex in the repo:

  codex --cd /home/postnl/SkillTester

  2. In the Codex chat, ask it to call the tool directly. Example:
     “Use MCP tool run_deterministic_pipeline with cik = 0002012383.”

  That’s it. Codex will auto‑start the registered MCP server over stdio and call the tool.

  If you want to verify the tools are visible first, you can use the built‑in command in the Codex UI:
  “list configured MCP tools”