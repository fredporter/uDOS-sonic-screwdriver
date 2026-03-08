#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

cd "${REPO_ROOT}"
python3 -m pip install --upgrade pip setuptools wheel
python3 -m pip install -e .

echo "Installed editable Sonic entrypoints:"
echo "  sonic"
echo "  sonic-api"
echo "  sonic-mcp"
