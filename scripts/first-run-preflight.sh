#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
VENV_PYTHON="${REPO_ROOT}/.venv/bin/python"
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

echo "[1/4] Repo validation"
bash "${SCRIPT_DIR}/run-sonic-checks.sh"

echo "[2/4] v2 structure check"
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

echo "[3/4] Quickstart preflight"
os_name="$(uname -s)"
if [[ "${os_name}" == "Linux" ]]; then
  "${REPO_ROOT}/.venv/bin/sonic" plan \
    --usb-device /dev/sdz \
    --dry-run \
    --out memory/sonic/sonic-manifest.json
  echo "Linux quickstart dry-run completed: memory/sonic/sonic-manifest.json"
else
  echo "Non-Linux host detected (${os_name})."
  echo "Build/apply commands are Linux-only, running API health preflight instead."

  API_LOG="$(mktemp "${TMPDIR:-/tmp}/sonic-first-run-api.XXXXXX.log")"
  "${REPO_ROOT}/.venv/bin/sonic-api" --host 127.0.0.1 --port "${API_PORT}" >"${API_LOG}" 2>&1 &
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

echo "[4/4] uHOME contract conformance"
if [[ -d "${REPO_ROOT}/../uHOME-server" && -d "${REPO_ROOT}/../uDOS-wizard" ]]; then
  bash "${REPO_ROOT}/scripts/smoke/uhome-contract-conformance.sh"
else
  echo "Skipping uHOME contract conformance check: sibling repos not found at ../uHOME-server and ../uDOS-wizard"
fi

echo "First-run preflight complete."
