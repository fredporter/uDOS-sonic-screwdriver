from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SMOKE_SCRIPT = REPO_ROOT / "scripts" / "smoke" / "ubuntu-ventoy-integration-smoke.sh"


def test_ubuntu_ventoy_smoke_script_wires_cli_commands() -> None:
    contents = SMOKE_SCRIPT.read_text(encoding="utf-8")

    assert "apps/sonic-cli/cli.py init" in contents
    assert "apps/sonic-cli/cli.py add udos-ubuntu" in contents
    assert "apps/sonic-cli/cli.py update" in contents
    assert "apps/sonic-cli/cli.py theme modern" in contents


def test_ubuntu_ventoy_smoke_script_enforces_repo_boundaries() -> None:
    contents = SMOKE_SCRIPT.read_text(encoding="utf-8")

    assert "SONIC_VENTOY_REPO" in contents
    assert "SONIC_UBUNTU_REPO" in contents
    assert "uDOS-ventoy repository not found" in contents
    assert "uDOS-ubuntu repository not found" in contents


def test_ubuntu_ventoy_smoke_script_checks_user_data_preservation() -> None:
    contents = SMOKE_SCRIPT.read_text(encoding="utf-8")

    assert "custom image was removed during update" in contents
    assert "device config was removed during update" in contents
    assert "profile checksum metadata did not persist" in contents
