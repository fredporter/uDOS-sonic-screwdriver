from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_pyproject_exposes_console_scripts() -> None:
    contents = (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")

    assert 'name = "udos-sonic"' in contents
    assert 'sonic = "sonic_cli:main"' in contents
    assert 'sonic-api = "services.http_api:main"' in contents
    assert 'sonic-mcp = "services.mcp_server:main"' in contents


def test_editable_install_script_uses_repo_root_install() -> None:
    contents = (REPO_ROOT / "installers" / "setup" / "install-sonic-editable.sh").read_text(encoding="utf-8")

    assert "python3 -m pip install --upgrade pip setuptools wheel" in contents
    assert "python3 -m pip install -e ." in contents
    assert "sonic-api" in contents
    assert "sonic-mcp" in contents
