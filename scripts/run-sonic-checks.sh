#!/usr/bin/env bash

set -eu

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
VENV_DIR="$REPO_ROOT/.venv"
PYTHON_BIN="$VENV_DIR/bin/python"

cd "$REPO_ROOT"

if [ ! -x "$PYTHON_BIN" ]; then
  python3 -m venv "$VENV_DIR"
  "$PYTHON_BIN" -m pip install --upgrade pip setuptools wheel
fi

"$PYTHON_BIN" -m pip install -e '.[dev]'
"$PYTHON_BIN" -m pytest tests
