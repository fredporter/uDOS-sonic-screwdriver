#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
REPO_PARENT="$(cd "${REPO_ROOT}/.." && pwd)"
TMP_DIR="$(mktemp -d "${TMPDIR:-/tmp}/sonic-uv-smoke.XXXXXX")"
STICK_ROOT="${TMP_DIR}/sonic-stick"
VENTOY_REPO="${SONIC_VENTOY_REPO:-${REPO_PARENT}/uDOS-ventoy}"
UBUNTU_REPO="${SONIC_UBUNTU_REPO:-${REPO_PARENT}/uDOS-ubuntu}"

cleanup() {
  rm -rf "${TMP_DIR}"
}

trap cleanup EXIT

if [[ "$(uname -s)" != "Linux" ]]; then
  echo "ERROR This smoke script requires Linux."
  exit 1
fi

if [[ ! -d "${VENTOY_REPO}" ]]; then
  echo "ERROR uDOS-ventoy repository not found at ${VENTOY_REPO}"
  echo "Set SONIC_VENTOY_REPO to override."
  exit 1
fi

if [[ ! -d "${UBUNTU_REPO}" ]]; then
  echo "ERROR uDOS-ubuntu repository not found at ${UBUNTU_REPO}"
  echo "Set SONIC_UBUNTU_REPO to override."
  exit 1
fi

cd "${REPO_ROOT}"

echo "[1/5] Init sonic-stick from Ventoy templates"
python3 apps/sonic-cli/cli.py init \
  --repo-root "${REPO_ROOT}" \
  --stick-root "${STICK_ROOT}" \
  --ventoy-repo "${VENTOY_REPO}" \
  --theme modern \
  --profile udos-ubuntu

echo "[2/5] Register Ubuntu profile metadata"
python3 apps/sonic-cli/cli.py add udos-ubuntu \
  --repo-root "${REPO_ROOT}" \
  --stick-root "${STICK_ROOT}" \
  --ventoy-repo "${VENTOY_REPO}" \
  --ubuntu-repo "${UBUNTU_REPO}" \
  --image-name udos-ubuntu-22.04.iso \
  --checksum test-sha256

echo "[3/5] Seed custom user data"
mkdir -p "${STICK_ROOT}/images/udos-ubuntu" "${STICK_ROOT}/config/devices"
echo "local-image" > "${STICK_ROOT}/images/udos-ubuntu/custom.iso"
cat > "${STICK_ROOT}/config/devices/device-1.json" <<'JSON'
{
  "hostname": "kiosk-01",
  "mode": "living-room"
}
JSON

echo "[4/5] Refresh templates and metadata"
python3 apps/sonic-cli/cli.py update \
  --repo-root "${REPO_ROOT}" \
  --stick-root "${STICK_ROOT}" \
  --ventoy-repo "${VENTOY_REPO}" \
  --profile udos-ubuntu \
  --theme retro

echo "[5/5] Switch back to modern theme and verify"
python3 apps/sonic-cli/cli.py theme modern \
  --repo-root "${REPO_ROOT}" \
  --stick-root "${STICK_ROOT}" \
  --ventoy-repo "${VENTOY_REPO}"

export SONIC_STICK_ROOT="${STICK_ROOT}"
python3 - <<PY
import os
import json
from pathlib import Path

stick_root = Path(os.environ["SONIC_STICK_ROOT"])
ventoy = json.loads((stick_root / "ventoy" / "ventoy.json").read_text(encoding="utf-8"))
profile = json.loads((stick_root / "config" / "profiles" / "udos-ubuntu.json").read_text(encoding="utf-8"))

if ventoy.get("theme", {}).get("file") != "/ventoy/theme/udos-modern/theme.txt":
    raise SystemExit("theme switch did not set modern theme")
if not (stick_root / "images" / "udos-ubuntu" / "custom.iso").exists():
    raise SystemExit("custom image was removed during update")
if not (stick_root / "config" / "devices" / "device-1.json").exists():
    raise SystemExit("device config was removed during update")
image = profile.get("image", {})
if image.get("checksum") != "test-sha256":
    raise SystemExit("profile checksum metadata did not persist")
if image.get("checksum_required") is not True:
    raise SystemExit("profile checksum requirement not set")
print("Ubuntu/Ventoy integration smoke passed")
PY
