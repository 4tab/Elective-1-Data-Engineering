#!/usr/bin/env bash
set -euo pipefail

PYTHON_BIN="${PYTHON_BIN:-python3}"

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "Python 3 is required but was not found. Install Python 3.11+ and rerun."
  exit 1
fi

"$PYTHON_BIN" -m venv .venv
".venv/bin/python" -m pip install --upgrade pip
".venv/bin/python" -m pip install -r requirements.txt
".venv/bin/python" -m pip install -e .

if [ ! -f .env ]; then
  cp .env.example .env
fi

echo "Environment ready. Run: source .venv/bin/activate && python -m nyc_taxi_platform.cli all"
echo
echo "If venv is not configured. Run: sudo apt install python3.12-venv
