from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
TEST_WORKFLOW = REPO_ROOT / ".github" / "workflows" / "test.yml"


def test_test_workflow_includes_ubuntu_ventoy_smoke_job() -> None:
    contents = TEST_WORKFLOW.read_text(encoding="utf-8")

    assert "ubuntu-ventoy-integration-smoke:" in contents
    assert "scripts/smoke/ubuntu-ventoy-integration-smoke.sh" in contents


def test_test_workflow_checks_out_sibling_repos_for_smoke_job() -> None:
    contents = TEST_WORKFLOW.read_text(encoding="utf-8")

    assert "repository: fredporter/uDOS-ventoy" in contents
    assert "repository: fredporter/uDOS-ubuntu" in contents
    assert "SONIC_VENTOY_REPO" in contents
    assert "SONIC_UBUNTU_REPO" in contents
