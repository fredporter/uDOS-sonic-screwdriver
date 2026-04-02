#!/usr/bin/env bash
# Compatibility wrapper — canonical launcher is scripts/sonic-open.sh.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec bash "${SCRIPT_DIR}/sonic-open.sh" "$@"
