#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
SHARED_PYTHON_BIN="${UDOS_SHARED_PYTHON_BIN:-}"
USE_SHARED_RESOURCES="${UDOS_USE_SHARED_RESOURCES:-1}"
VENV_DIR="${UDOS_VENV_DIR:-$HOME/.udos/venv/sonic-screwdriver}"
VENV_PYTHON="${VENV_DIR}/bin/python"
SONIC_BIN="${VENV_DIR}/bin/sonic"
SONIC_API_BIN="${VENV_DIR}/bin/sonic-api"
API_PORT="${SONIC_FIRST_RUN_PORT:-8991}"
API_PID=""
API_LOG=""

cleanup() {
  if [[ -n "${API_PID}" ]] && kill -0 "${API_PID}" 2>/dev/null; then
    kill "${API_PID}" 2>/dev/null || true
    wait "${API_PID}" 2>/dev/null || true
  fi
  if [[ -n "${API_LOG}" && -f "${API_LOG}" ]]; then
    rm -f "${API_LOG}"
  fi
}

trap cleanup EXIT

cd "${REPO_ROOT}"
mkdir -p "${VENV_DIR}"

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
  VENV_PYTHON="${SHARED_PYTHON_BIN}"
  SONIC_BIN="${SHARED_BIN_DIR}/sonic"
  SONIC_API_BIN="${SHARED_BIN_DIR}/sonic-api"
fi

echo "[1/5] Repo validation"
bash "${SCRIPT_DIR}/run-sonic-checks.sh"

echo "[2/5] v2 structure check"
expected_roots=(
  apps
  build
  config
  core
  courses
  datasets
  distribution
  docs
  examples
  installers
  library
  memory
  modules
  payloads
  scripts
  services
  tests
  ui
  vault
  wiki
)

missing_roots=()
for root in "${expected_roots[@]}"; do
  if [[ ! -d "${REPO_ROOT}/${root}" ]]; then
    missing_roots+=("${root}")
  fi
done

if (( ${#missing_roots[@]} > 0 )); then
  echo "ERROR Missing canonical v2 roots:"
  for root in "${missing_roots[@]}"; do
    echo "  - ${root}/"
  done
  exit 1
fi

echo "v2 structure check passed."

echo "[3/5] Quickstart preflight"
os_name="$(uname -s)"
if [[ "${os_name}" == "Linux" ]]; then
  "${SONIC_BIN}" plan \
    --usb-device /dev/sdz \
    --dry-run \
    --out memory/sonic/sonic-manifest.json
  echo "Linux quickstart dry-run completed: memory/sonic/sonic-manifest.json"
else
  echo "Non-Linux host detected (${os_name})."
  echo "Build/apply commands are Linux-only, running API health preflight instead."

  API_LOG="$(mktemp "${TMPDIR:-/tmp}/sonic-first-run-api.XXXXXX.log")"
  "${SONIC_API_BIN}" --host 127.0.0.1 --port "${API_PORT}" >"${API_LOG}" 2>&1 &
  API_PID=$!

  for _ in {1..20}; do
    if "${VENV_PYTHON}" - <<PY >/dev/null 2>&1
import urllib.request
urllib.request.urlopen("http://127.0.0.1:${API_PORT}/api/sonic/health", timeout=1).read()
PY
    then
      break
    fi
    sleep 1
  done

  if ! "${VENV_PYTHON}" - <<PY >/dev/null 2>&1
import urllib.request
urllib.request.urlopen("http://127.0.0.1:${API_PORT}/api/sonic/health", timeout=1).read()
PY
  then
    echo "ERROR Sonic API health check failed on port ${API_PORT}."
    echo "--- sonic-api log ---"
    cat "${API_LOG}"
    exit 1
  fi

  echo "API quickstart preflight passed on http://127.0.0.1:${API_PORT}/api/sonic/health"
fi

echo "[4/5] uHOME contract conformance"
if [[ -d "${REPO_ROOT}/../uHOME-server" && -d "${REPO_ROOT}/../uDOS-wizard" ]]; then
  bash "${REPO_ROOT}/scripts/smoke/uhome-contract-conformance.sh"
else
  echo "Skipping uHOME contract conformance check: sibling repos not found at ../uHOME-server and ../uDOS-wizard"
fi

echo "[5/5] Ubuntu/Ventoy integration smoke"
if [[ "${os_name}" != "Linux" ]]; then
  echo "Skipping Ubuntu/Ventoy smoke: Linux required for init flow"
elif [[ ! -d "${REPO_ROOT}/../sonic-ventoy" || ! -d "${REPO_ROOT}/../uDOS-ubuntu" ]]; then
  echo "Skipping Ubuntu/Ventoy smoke: sibling repos not found at ../sonic-ventoy and ../uDOS-ubuntu"
else
  bash "${REPO_ROOT}/scripts/smoke/ubuntu-ventoy-integration-smoke.sh"
fi

echo "First-run preflight complete."
