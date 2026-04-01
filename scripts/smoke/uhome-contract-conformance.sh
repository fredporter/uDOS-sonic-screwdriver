#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
WORKSPACE_ROOT="${SONIC_WORKSPACE_ROOT:-$(cd "${REPO_ROOT}/.." && pwd)}"
UHOME_SERVER_ROOT="${SONIC_UHOME_SERVER_ROOT:-${WORKSPACE_ROOT}/uHOME-server}"
WIZARD_ROOT="${SONIC_WIZARD_ROOT:-${WORKSPACE_ROOT}/uDOS-wizard}"
SHARED_PYTHON_BIN="${UDOS_SHARED_PYTHON_BIN:-}"
USE_SHARED_RESOURCES="${UDOS_USE_SHARED_RESOURCES:-1}"
VENV_DIR="${UDOS_VENV_DIR:-$HOME/.udos/venv/sonic-screwdriver}"
PYTHON_BIN="${VENV_DIR}/bin/python"

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
  PYTHON_BIN="${SHARED_PYTHON_BIN}"
elif [[ ! -x "${PYTHON_BIN}" ]]; then
  PYTHON_BIN="python3"
fi

if [[ ! -d "${UHOME_SERVER_ROOT}" ]]; then
  echo "ERROR Missing sibling repo: ${UHOME_SERVER_ROOT}" >&2
  exit 1
fi

if [[ ! -d "${WIZARD_ROOT}" ]]; then
  echo "ERROR Missing sibling repo: ${WIZARD_ROOT}" >&2
  exit 1
fi

echo "[conformance] checking Sonic deployment assumptions against sibling uHOME-server and Wizard contracts"

SONIC_REPO_ROOT="${REPO_ROOT}" \
SONIC_UHOME_SERVER_ROOT="${UHOME_SERVER_ROOT}" \
SONIC_WIZARD_ROOT="${WIZARD_ROOT}" \
"${PYTHON_BIN}" - <<'PY'
import json
import os
from pathlib import Path

repo_root = Path(os.environ["SONIC_REPO_ROOT"])
uhome_server_root = Path(os.environ["SONIC_UHOME_SERVER_ROOT"])
wizard_root = Path(os.environ["SONIC_WIZARD_ROOT"])

bundle_py = uhome_server_root / "src" / "uhome_server" / "installer" / "bundle.py"
preflight_py = uhome_server_root / "src" / "uhome_server" / "installer" / "preflight.py"
plan_py = uhome_server_root / "src" / "uhome_server" / "installer" / "plan.py"
runtime_py = uhome_server_root / "src" / "uhome_server" / "routes" / "runtime.py"
standalone_bundle = uhome_server_root / "examples" / "installer" / "bundles" / "standalone" / "uhome-bundle.json"
dual_boot_bundle = uhome_server_root / "examples" / "installer" / "bundles" / "dual-boot" / "uhome-bundle.json"
wizard_contract = wizard_root / "contracts" / "uhome-network-policy-contract.json"
wizard_schema = wizard_root / "contracts" / "uhome-network-policy.schema.json"

missing = [
    str(path)
    for path in (
        bundle_py,
        preflight_py,
        plan_py,
        runtime_py,
        standalone_bundle,
        dual_boot_bundle,
        wizard_contract,
        wizard_schema,
    )
    if not path.exists()
]
if missing:
    raise SystemExit("missing required contract sources:\n- " + "\n- ".join(missing))

bundle_text = bundle_py.read_text(encoding="utf-8")
preflight_text = preflight_py.read_text(encoding="utf-8")
plan_text = plan_py.read_text(encoding="utf-8")
runtime_text = runtime_py.read_text(encoding="utf-8")

required_component_ids = [
    "jellyfin",
    "comskip",
    "hdhomerun_config",
    "udos_uhome",
]

checks: list[str] = []

if 'BUNDLE_SCHEMA_VERSION = "1.0"' not in bundle_text:
    checks.append("uHOME bundle schema version is not pinned to 1.0")
for component in required_component_ids:
    if f'"{component}"' not in bundle_text:
        checks.append(f"uHOME bundle contract missing component id reference: {component}")

for marker in ("STANDALONE_LINUX_PROFILE", "DUAL_BOOT_STEAM_NODE_PROFILE", "HOST_PROFILES"):
    if marker not in preflight_text:
        checks.append(f"uHOME preflight contract marker missing: {marker}")

for marker in ("class UHOMEInstallPlan", "class UHOMEInstallStep", "class InstallPhase"):
    if marker not in plan_text:
        checks.append(f"uHOME install-plan contract marker missing: {marker}")

for route in (
    '/contracts/uhome-network-policy',
    '/contracts/uhome-network-policy/validate',
):
    if route not in runtime_text:
        checks.append(f"uHOME runtime consumer route missing: {route}")

standalone_payload = json.loads(standalone_bundle.read_text(encoding="utf-8"))
dual_boot_payload = json.loads(dual_boot_bundle.read_text(encoding="utf-8"))

if standalone_payload.get("schema_version") != "1.0":
    checks.append("standalone bundle schema_version drifted from 1.0")
if dual_boot_payload.get("schema_version") != "1.0":
    checks.append("dual-boot bundle schema_version drifted from 1.0")
if standalone_payload.get("host_profile", {}).get("profile_id") != "standalone-linux":
    checks.append("standalone bundle host_profile.profile_id drifted")
if dual_boot_payload.get("host_profile", {}).get("profile_id") != "dual-boot-steam-node":
    checks.append("dual-boot bundle host_profile.profile_id drifted")

standalone_components = {item.get("component_id") for item in standalone_payload.get("components", [])}
dual_components = {item.get("component_id") for item in dual_boot_payload.get("components", [])}
if standalone_components != set(required_component_ids):
    checks.append("standalone bundle component ids drifted from required set")
if dual_components != set(required_component_ids):
    checks.append("dual-boot bundle component ids drifted from required set")

wizard_contract_payload = json.loads(wizard_contract.read_text(encoding="utf-8"))
wizard_schema_payload = json.loads(wizard_schema.read_text(encoding="utf-8"))

if wizard_contract_payload.get("version") != "v2.0.4":
    checks.append("Wizard uHOME policy contract version drifted from v2.0.4")
if wizard_contract_payload.get("owner") != "uDOS-wizard":
    checks.append("Wizard uHOME policy contract owner drifted from uDOS-wizard")

profiles = wizard_contract_payload.get("profiles", {})
for profile in ("beacon", "crypt", "tomb", "home"):
    if profile not in profiles:
        checks.append(f"Wizard uHOME policy contract missing profile: {profile}")

for profile_name, profile_payload in profiles.items():
    if profile_payload.get("runtime_owner") != "uHOME-server":
        checks.append(f"Wizard policy profile {profile_name} runtime_owner drifted")
    if profile_payload.get("policy_owner") != "uDOS-wizard":
        checks.append(f"Wizard policy profile {profile_name} policy_owner drifted")
    consumers = set(profile_payload.get("consumer_repos", []))
    if "sonic-screwdriver" not in consumers:
        checks.append(f"Wizard policy profile {profile_name} no longer names sonic-screwdriver as a consumer")

if wizard_schema_payload.get("title") != "WizardToUHomeNetworkPolicy":
    checks.append("Wizard uHOME policy schema title drifted")
required_schema_fields = set(wizard_schema_payload.get("required", []))
for field_name in ("runtime_owner", "policy_owner", "consumer_repos", "secret_refs"):
    if field_name not in required_schema_fields:
        checks.append(f"Wizard uHOME policy schema missing required field: {field_name}")

if checks:
    raise SystemExit("contract conformance check failed:\n- " + "\n- ".join(checks))

print("uHOME-server and Wizard contract conformance check passed.")
print(f"checked from {repo_root}")
PY

echo "[conformance] completed"
