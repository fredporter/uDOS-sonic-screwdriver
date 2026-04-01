#!/bin/bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
REPO_PARENT="$(cd "${REPO_ROOT}/.." && pwd)"
SHARED_PYTHON_BIN="${UDOS_SHARED_PYTHON_BIN:-}"
USE_SHARED_RESOURCES="${UDOS_USE_SHARED_RESOURCES:-1}"
VENV_DIR="${UDOS_VENV_DIR:-$HOME/.udos/venv/sonic-screwdriver}"
SONIC_BIN="${VENV_DIR}/bin/sonic"

DRY_RUN_MANIFEST="${SONIC_LINUX_DRY_RUN_MANIFEST:-/tmp/sonic-linux-dry-run.json}"
TARGET_USB="${SONIC_TARGET_USB:-}"
RUN_INTEGRATION_SMOKE="${SONIC_RUN_INTEGRATION_SMOKE:-auto}"
RUN_REAL_APPLY="${SONIC_RUN_REAL_APPLY:-0}"
FORCE_REAL_APPLY="${SONIC_FORCE_REAL_APPLY:-0}"

VENTOY_REPO="${SONIC_VENTOY_REPO:-${REPO_PARENT}/sonic-ventoy}"
UBUNTU_REPO="${SONIC_UBUNTU_REPO:-${REPO_PARENT}/uDOS-ubuntu}"
UHOME_REPO="${SONIC_UHOME_REPO:-${REPO_PARENT}/uHOME-server}"
WIZARD_REPO="${SONIC_WIZARD_REPO:-${REPO_PARENT}/uDOS-wizard}"

require_cmd() {
  local cmd="$1"
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "ERROR Missing required command: $cmd" >&2
    exit 1
  fi
}

header() {
  echo
  echo "=============================================="
  echo "$*"
  echo "=============================================="
}

run_cmd() {
  echo "+ $*"
  "$@"
}

detect_linux_family() {
  if [[ -f /etc/alpine-release ]]; then
    echo "alpine"
    return 0
  fi
  if [[ -f /etc/os-release ]]; then
    if grep -q '^ID=ubuntu' /etc/os-release; then
      echo "ubuntu"
      return 0
    fi
    if grep -q '^ID=debian' /etc/os-release; then
      echo "debian"
      return 0
    fi
    if grep -q '^ID=alpine' /etc/os-release; then
      echo "alpine"
      return 0
    fi
  fi
  echo "linux"
}

header "Sonic Linux Runner Validation"
echo "Repo root: $REPO_ROOT"
echo "Linux family: $(detect_linux_family)"
echo "Dry-run manifest: $DRY_RUN_MANIFEST"
echo "Integration smoke mode: $RUN_INTEGRATION_SMOKE"
echo "Real apply mode: $RUN_REAL_APPLY"

if [[ "$(uname -s)" != "Linux" ]]; then
  echo "ERROR This script must run on Linux." >&2
  exit 1
fi

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
  SONIC_BIN="${SHARED_BIN_DIR}/sonic"
fi

require_cmd bash
require_cmd python3
require_cmd node
require_cmd npm
require_cmd lsblk
require_cmd sgdisk
require_cmd partprobe
require_cmd mount
require_cmd umount
require_cmd dd

if ! command -v mkfs.exfat >/dev/null 2>&1 && ! command -v mkexfatfs >/dev/null 2>&1; then
  echo "ERROR Missing exFAT formatter: mkfs.exfat or mkexfatfs" >&2
  exit 1
fi

header "1. Repo Validation"
cd "$REPO_ROOT"
run_cmd bash scripts/run-sonic-checks.sh
run_cmd bash scripts/first-run-preflight.sh

header "2. CLI Dry-Run"
run_cmd "${SONIC_BIN}" plan \
  --usb-device /dev/sdz \
  --dry-run \
  --out "$DRY_RUN_MANIFEST"

if [[ ! -f "$DRY_RUN_MANIFEST" ]]; then
  echo "ERROR Dry-run manifest not written: $DRY_RUN_MANIFEST" >&2
  exit 1
fi

header "3. Bash Dry-Run"
run_cmd bash scripts/sonic-stick.sh \
  --manifest "$DRY_RUN_MANIFEST" \
  --dry-run

header "4. Linux Runtime Smoke"
run_cmd bash scripts/smoke/linux-runtime-smoke.sh

header "5. Ubuntu/Ventoy Integration Smoke"
if [[ "$RUN_INTEGRATION_SMOKE" == "0" ]]; then
  echo "Skipping integration smoke: SONIC_RUN_INTEGRATION_SMOKE=0"
elif [[ -d "$VENTOY_REPO" && -d "$UBUNTU_REPO" && -d "$UHOME_REPO" && -d "$WIZARD_REPO" ]]; then
  run_cmd bash scripts/smoke/ubuntu-ventoy-integration-smoke.sh
else
  if [[ "$RUN_INTEGRATION_SMOKE" == "1" ]]; then
    echo "ERROR Integration smoke requested but sibling repos are missing." >&2
    echo "VENTOY_REPO=$VENTOY_REPO" >&2
    echo "UBUNTU_REPO=$UBUNTU_REPO" >&2
    echo "UHOME_REPO=$UHOME_REPO" >&2
    echo "WIZARD_REPO=$WIZARD_REPO" >&2
    exit 1
  fi
  echo "Skipping integration smoke: sibling repos not fully present."
fi

if [[ "$RUN_REAL_APPLY" == "1" ]]; then
  header "6. Real Device Apply"
  if [[ -z "$TARGET_USB" ]]; then
    echo "ERROR SONIC_RUN_REAL_APPLY=1 requires SONIC_TARGET_USB=/dev/sdX" >&2
    exit 1
  fi
  if [[ "$FORCE_REAL_APPLY" != "1" ]]; then
    echo "ERROR Refusing destructive apply without SONIC_FORCE_REAL_APPLY=1" >&2
    exit 1
  fi
  if [[ ! -b "$TARGET_USB" ]]; then
    echo "ERROR Target is not a block device: $TARGET_USB" >&2
    exit 1
  fi

  run_cmd "${SONIC_BIN}" plan \
    --usb-device "$TARGET_USB" \
    --out memory/sonic/sonic-manifest.json

  run_cmd bash scripts/sonic-stick.sh \
    --manifest memory/sonic/sonic-manifest.json
else
  header "6. Real Device Apply"
  echo "Skipping destructive apply. Set:"
  echo "  SONIC_RUN_REAL_APPLY=1"
  echo "  SONIC_FORCE_REAL_APPLY=1"
  echo "  SONIC_TARGET_USB=/dev/sdX"
fi

header "Complete"
echo "Linux runner validation finished."
