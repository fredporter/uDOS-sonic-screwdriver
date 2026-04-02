#!/usr/bin/env bash
# Double-click in Finder (macOS) — same as ./sonic-open from repo root.
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
exec bash "${REPO_ROOT}/scripts/sonic-open.sh" "$@"
