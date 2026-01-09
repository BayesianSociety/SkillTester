#!/usr/bin/env bash
set -euo pipefail

export PYTHONHASHSEED=0
export LC_ALL=C
export LANG=C

exec python3 pipeline/run_pipeline.py


