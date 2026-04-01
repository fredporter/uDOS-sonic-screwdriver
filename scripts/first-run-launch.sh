#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
RUN_DIR="${REPO_ROOT}/.run"
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

require_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "missing required command: $1" >&2
    exit 1
  fi
}

wait_for_http() {
  local url="$1"
  local attempts="${2:-20}"
  local delay="${3:-1}"
  for ((i=0; i<attempts; i++)); do
    if python3 - <<PY >/dev/null 2>&1
import urllib.request
urllib.request.urlopen("${url}", timeout=1).read()
PY
    then
      return 0
    fi
    sleep "${delay}"
  done
  return 1
}

start_if_needed() {
  local name="$1"
  local pid_file="$2"
  shift 2
  if [[ -f "${pid_file}" ]]; then
    local existing_pid
    existing_pid="$(cat "${pid_file}")"
    if kill -0 "${existing_pid}" 2>/dev/null; then
      echo "${name} already running (pid ${existing_pid})"
      return 0
    fi
  fi
  nohup "$@" >/dev/null 2>>"${RUN_DIR}/${name}.stderr.log" &
  local pid=$!
  echo "${pid}" >"${pid_file}"
  echo "Started ${name} (pid ${pid})"
}

open_url() {
  local url="$1"
  if command -v open >/dev/null 2>&1; then
    open "${url}" >/dev/null 2>&1 || true
  elif command -v xdg-open >/dev/null 2>&1; then
    xdg-open "${url}" >/dev/null 2>&1 || true
  fi
}

require_cmd python3
require_cmd node
require_cmd npm
require_cmd bash

mkdir -p "${RUN_DIR}"
mkdir -p "${VENV_DIR}"
cd "${REPO_ROOT}"

if [[ "${USE_SHARED_RESOURCES}" == "1" && -z "${SHARED_PYTHON_BIN}" ]]; then
  FAMILY_HELPER="${REPO_ROOT}/../scripts/lib/family-python.sh"
  if [[ -f "${FAMILY_HELPER}" ]]; then
    # shellcheck source=/dev/null
    . "${FAMILY_HELPER}"
    ensure_shared_python
    SHARED_PYTHON_BIN="${UDOS_SHARED_PYTHON_BIN:-}"
  fi
fi

if [[ -n "${SHARED_PYTHON_BIN}" && -x "${SHARED_PYTHON_BIN}" ]]; then
  SHARED_BIN_DIR="$(cd "$(dirname "${SHARED_PYTHON_BIN}")" && pwd)"
  PYTHON_BIN="${SHARED_PYTHON_BIN}"
  SONIC_BIN="${SHARED_BIN_DIR}/sonic"
  API_BIN="${SHARED_BIN_DIR}/sonic-api"
elif [[ ! -x "${PYTHON_BIN}" ]]; then
  echo "Creating Sonic virtual environment..."
  python3 -m venv "${VENV_DIR}"
  "${PYTHON_BIN}" -m pip install --upgrade pip setuptools wheel
fi

echo "Installing Sonic editable package..."
"${PYTHON_BIN}" -m pip install -e '.[dev]' >/dev/null

if [[ ! -d "${UI_ROOT}/node_modules" ]]; then
  echo "Installing Sonic UI dependencies..."
  (
    cd "${UI_ROOT}"
    npm install >/dev/null
  )
else
  echo "Sonic UI dependencies already present"
fi

echo "Starting Sonic API on http://127.0.0.1:${API_PORT}"
if [[ ! -f "${API_PID_FILE}" ]] || ! kill -0 "$(cat "${API_PID_FILE}" 2>/dev/null)" 2>/dev/null; then
  nohup "${API_BIN}" --host 127.0.0.1 --port "${API_PORT}" >"${API_LOG}" 2>&1 &
  echo $! >"${API_PID_FILE}"
fi

if ! wait_for_http "http://127.0.0.1:${API_PORT}/api/sonic/health" 20 1; then
  echo "Sonic API failed to start on port ${API_PORT}" >&2
  echo "--- sonic-api log ---" >&2
  cat "${API_LOG}" >&2 || true
  exit 1
fi

echo "Starting Sonic UI on http://127.0.0.1:${UI_PORT}"
if [[ ! -f "${UI_PID_FILE}" ]] || ! kill -0 "$(cat "${UI_PID_FILE}" 2>/dev/null)" 2>/dev/null; then
  (
    cd "${UI_ROOT}"
    nohup npm run dev -- --host 127.0.0.1 --port "${UI_PORT}" >"${UI_LOG}" 2>&1 &
    echo $! >"${UI_PID_FILE}"
  )
fi

if ! wait_for_http "http://127.0.0.1:${UI_PORT}" 20 1; then
  echo "Sonic UI failed to start on port ${UI_PORT}" >&2
  echo "--- sonic-ui log ---" >&2
  cat "${UI_LOG}" >&2 || true
  exit 1
fi

open_url "http://127.0.0.1:${UI_PORT}"

echo ""
echo "Sonic GUI is running."
echo "  UI:  http://127.0.0.1:${UI_PORT}"
echo "  API: http://127.0.0.1:${API_PORT}/api/sonic/health"
echo "  API log: ${API_LOG}"
echo "  UI log:  ${UI_LOG}"
echo ""
echo "Next:"
echo "  sonic status"
echo "  sonic test thinui"
