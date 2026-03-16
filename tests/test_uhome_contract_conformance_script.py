from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CONFORMANCE_SCRIPT = REPO_ROOT / "scripts" / "smoke" / "uhome-contract-conformance.sh"
FIRST_RUN_SCRIPT = REPO_ROOT / "scripts" / "first-run-preflight.sh"


def test_uhome_contract_conformance_script_targets_expected_family_contracts() -> None:
    contents = CONFORMANCE_SCRIPT.read_text(encoding="utf-8")

    assert "uHOME-server" in contents
    assert "uDOS-wizard" in contents
    assert '"installer" / "bundle.py"' in contents
    assert '"installer" / "preflight.py"' in contents
    assert '"installer" / "plan.py"' in contents
    assert "uhome-network-policy-contract.json" in contents
    assert "uhome-network-policy.schema.json" in contents
    assert "/contracts/uhome-network-policy" in contents
    assert "BUNDLE_SCHEMA_VERSION = \"1.0\"" in contents
    assert "sonic-screwdriver" in contents


def test_first_run_preflight_references_uhome_contract_conformance_script() -> None:
    contents = FIRST_RUN_SCRIPT.read_text(encoding="utf-8")

    assert "[4/4] uHOME contract conformance" in contents
    assert "scripts/smoke/uhome-contract-conformance.sh" in contents