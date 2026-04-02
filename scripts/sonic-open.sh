#!/usr/bin/env bash
# One-command Sonic setup + launcher for operators (macOS/Linux).
# - Checks python3, node, npm
# - Creates ~/.udos/venv/sonic-screwdriver, pip install -e, npm install (first time or --repair)
# - Starts API + UI, waits on health, opens browser (unless --no-open)
#
# Usage:
#   bash scripts/sonic-open.sh
#   ./sonic-open                    # from repo root
#   open ./scripts/sonic-open.command   # macOS Finder
#
# Options:
#   --repair     Force reinstall (pip + npm) and recreate setup marker
#   --no-open    Do not open a browser (headless / SSH)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
RUN_DIR="${REPO_ROOT}/.run"
SETUP_MARKER="${RUN_DIR}/sonic-setup-complete"
SHARED_PYTHON_BIN="${UDOS_SHARED_PYTHON_BIN:-}"
USE_SHARED_RESOURCES="${UDOS_USE_SHARED_RESOURCES:-1}"
VENV_DIR="${UDOS_VENV_DIR:-$HOME/.udos/venv/sonic-screwdriver}"
PYTHON_BIN="${VENV_DIR}/bin/python"
SONIC_BIN="${VENV_DIR}/bin/sonic"
API_BIN="${VENV_DIR}/bin/sonic-api"
UI_ROOT="${REPO_ROOT}/apps/sonic-ui"
API_PORT="${SONIC_API_PORT:-8991}"
UI_PORT="${SONIC_UI_PORT:-5173}"
API_LOG="${RUN_DIR}/sonic-api.log"
UI_LOG="${RUN_DIR}/sonic-ui.log"
API_PID_FILE="${RUN_DIR}/sonic-api.pid"
UI_PID_FILE="${RUN_DIR}/sonic-ui.pid"

REPAIR=0
NO_OPEN=0
for arg in "$@"; do
  case "$arg" in
    --repair) REPAIR=1 ;;
    --no-open) NO_OPEN=1 ;;
    *)
      echo "Unknown option: $arg (use --repair or --no-open)" >&2
      exit 1
      ;;
  esac
done

print_requirements_help() {
  local os
  os="$(uname -s)"
  echo ""
  echo "Sonic needs Python 3, Node.js, and npm on your PATH."
  echo ""
  case "$os" in
    Darwin)
      echo "macOS — install with Homebrew (https://brew.sh), then for example:"
      echo "  brew install python@3.12 node"
      echo "Or install Python from python.org and Node from https://nodejs.org/"
      ;;
    Linux)
      echo "Linux — Debian/Ubuntu example:"
      echo "  sudo apt-get update"
      echo "  sudo apt-get install -y python3 python3-venv python3-pip nodejs npm"
      echo "Use your distro's packages if you are not on Debian/Ubuntu."
      ;;
    *)
      echo "Install Python 3, Node.js, and npm, then run this script again."
      ;;
  esac
  echo ""
}

require_prereqs() {
  local miss=0
  for cmd in python3 node npm bash; do
    if ! command -v "$cmd" >/dev/null 2>&1; then
      echo "[sonic-open] Missing on PATH: ${cmd}" >&2
      miss=1
    fi
  done
  if [[ "$miss" -ne 0 ]]; then
    print_requirements_help
    exit 1
  fi
  echo "[sonic-open] (1/5) Prerequisites OK — python3, node, npm, bash"
}

wait_for_http() {
  local url="$1"
  local attempts="${2:-30}"
  local delay="${3:-1}"
  local i
  for ((i = 0; i < attempts; i++)); do
    if python3 - <<PY >/dev/null 2>&1
import urllib.request
urllib.request.urlopen("${url}", timeout=2).read()
PY
    then
      return 0
    fi
    sleep "${delay}"
  done
  return 1
}

open_url() {
  [[ "$NO_OPEN" -eq 1 ]] && return 0
  local url="$1"
  if command -v open >/dev/null 2>&1; then
    open "${url}" >/dev/null 2>&1 || true
  elif command -v xdg-open >/dev/null 2>&1; then
    xdg-open "${url}" >/dev/null 2>&1 || true
  fi
}

mkdir -p "${RUN_DIR}"
mkdir -p "${VENV_DIR}"
cd "${REPO_ROOT}"

if [[ "$REPAIR" -eq 1 ]]; then
  rm -f "${SETUP_MARKER}"
  echo "[sonic-open] --repair: cleared setup marker; will reinstall dependencies."
fi

require_prereqs

if [[ "${USE_SHARED_RESOURCES}" == "1" && -z "${SHARED_PYTHON_BIN}" ]]; then
  FAMILY_HELPER="${REPO_ROOT}/../scripts/lib/family-python.sh"
  if [[ -f "${FAMILY_HELPER}" ]]; then
    # shellcheck source=/dev/null
    . "${FAMILY_HELPER}"
    ensure_shared_python
    SHARED_PYTHON_BIN="${UDOS_SHARED_PYTHON_BIN:-}"
  fi
fi

USING_SHARED=0
if [[ -n "${SHARED_PYTHON_BIN}" && -x "${SHARED_PYTHON_BIN}" ]]; then
  SHARED_BIN_DIR="$(cd "$(dirname "${SHARED_PYTHON_BIN}")" && pwd)"
  PYTHON_BIN="${SHARED_PYTHON_BIN}"
  SONIC_BIN="${SHARED_BIN_DIR}/sonic"
  API_BIN="${SHARED_BIN_DIR}/sonic-api"
  USING_SHARED=1
  echo "[sonic-open] (2/5) Using shared Python at ${PYTHON_BIN}"
fi

if [[ "${USING_SHARED}" -eq 0 ]]; then
  if [[ ! -x "${VENV_DIR}/bin/python" ]]; then
    echo "[sonic-open] (2/5) Creating Python virtual environment at ${VENV_DIR}"
    python3 -m venv "${VENV_DIR}"
    "${VENV_DIR}/bin/python" -m pip install --upgrade pip setuptools wheel
  else
    echo "[sonic-open] (2/5) Python venv ready at ${VENV_DIR}"
  fi
  PYTHON_BIN="${VENV_DIR}/bin/python"
  SONIC_BIN="${VENV_DIR}/bin/sonic"
  API_BIN="${VENV_DIR}/bin/sonic-api"
fi

do_full_install=1
if [[ -f "${SETUP_MARKER}" && "$REPAIR" -eq 0 ]]; then
  if [[ -x "${PYTHON_BIN}" && -x "${SONIC_BIN}" && -x "${API_BIN}" && -d "${UI_ROOT}/node_modules" ]]; then
    do_full_install=0
  fi
fi

if [[ "$do_full_install" -eq 1 ]]; then
  echo "[sonic-open] (3/5) Installing Python + UI dependencies (pip, npm)…"
  "${PYTHON_BIN}" -m pip install -e '.[dev]' >/dev/null
  (
    cd "${UI_ROOT}"
    npm install >/dev/null
  )
else
  echo "[sonic-open] (3/5) Skipping pip/npm — already set up (use --repair to reinstall)"
fi

echo "[sonic-open] (4/5) Starting API on http://127.0.0.1:${API_PORT}"
if [[ ! -f "${API_PID_FILE}" ]] || ! kill -0 "$(cat "${API_PID_FILE}" 2>/dev/null)" 2>/dev/null; then
  nohup "${API_BIN}" --host 127.0.0.1 --port "${API_PORT}" >"${API_LOG}" 2>&1 &
  echo $! >"${API_PID_FILE}"
fi

if ! wait_for_http "http://127.0.0.1:${API_PORT}/api/sonic/health" 30 1; then
  echo "[sonic-open] FAILED — API did not become healthy." >&2
  echo "  Log: ${API_LOG}" >&2
  echo "--- tail of API log ---" >&2
  tail -40 "${API_LOG}" >&2 || true
  exit 1
fi
echo "[sonic-open] API health OK — http://127.0.0.1:${API_PORT}/api/sonic/health"

echo "[sonic-open] (5/5) Starting UI on http://127.0.0.1:${UI_PORT}"
if [[ ! -f "${UI_PID_FILE}" ]] || ! kill -0 "$(cat "${UI_PID_FILE}" 2>/dev/null)" 2>/dev/null; then
  (
    cd "${UI_ROOT}"
    nohup npm run dev -- --host 127.0.0.1 --port "${UI_PORT}" >"${UI_LOG}" 2>&1 &
    echo $! >"${UI_PID_FILE}"
  )
fi

if ! wait_for_http "http://127.0.0.1:${UI_PORT}" 40 1; then
  echo "[sonic-open] FAILED — UI did not become ready." >&2
  echo "  Log: ${UI_LOG}" >&2
  echo "--- tail of UI log ---" >&2
  tail -40 "${UI_LOG}" >&2 || true
  exit 1
fi
echo "[sonic-open] UI OK — http://127.0.0.1:${UI_PORT}"

touch "${SETUP_MARKER}"
open_url "http://127.0.0.1:${UI_PORT}"

echo ""
echo "Sonic OK — GUI is running."
echo "  UI:  http://127.0.0.1:${UI_PORT}"
echo "  API: http://127.0.0.1:${API_PORT}/api/sonic/health"
echo "  Logs: ${API_LOG} | ${UI_LOG}"
echo ""
if [[ "${USING_SHARED}" -eq 1 ]]; then
  echo "Next: add ${SHARED_BIN_DIR} to PATH to use the sonic CLI, or run ./sonic-open again."
else
  echo "Next: add ${VENV_DIR}/bin to PATH to use the sonic CLI, or run ./sonic-open again."
fi
echo "  bash scripts/run-sonic-checks.sh  # full test suite (developers)"
