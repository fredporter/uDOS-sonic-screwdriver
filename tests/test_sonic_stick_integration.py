from __future__ import annotations

import json
from pathlib import Path

from services.sonic_stick_integration import (
    initialize_sonic_stick,
    refresh_ventoy_templates,
    register_ubuntu_profile,
    set_boot_theme,
)


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _prepare_family_repos(tmp_path: Path) -> Path:
    sonic_repo = tmp_path / "sonic-screwdriver"
    ventoy_repo = tmp_path / "uDOS-ventoy"
    ubuntu_repo = tmp_path / "uDOS-ubuntu"

    sonic_repo.mkdir(parents=True, exist_ok=True)
    ubuntu_repo.mkdir(parents=True, exist_ok=True)

    _write_json(
        ventoy_repo / "templates" / "ventoy" / "ventoy.json",
        {
            "theme": {"file": "/ventoy/theme/udos-modern/theme.txt"},
            "menu_class": [{"dir": "/images/udos-ubuntu", "class": "udos_ubuntu"}],
            "menu_alias": [],
            "menu_tip": [],
            "grubmenu": {"file": "/ventoy/grub/udos_menu.cfg"},
        },
    )
    _write_text(ventoy_repo / "templates" / "ventoy" / "grub" / "udos_menu.cfg", "menuentry 'uDOS' {}\n")
    _write_text(ventoy_repo / "templates" / "ventoy" / "theme" / "udos-modern" / "theme.txt", "title-text: modern\n")
    _write_text(ventoy_repo / "templates" / "ventoy" / "theme" / "udos-retro" / "theme.txt", "title-text: retro\n")
    _write_json(
        ventoy_repo / "profiles" / "udos-ubuntu" / "manifest.json",
        {
            "profile": "udos-ubuntu",
            "display_name": "uDOS Ubuntu",
            "modes": ["live", "install", "recovery"],
            "checksum_required": True,
        },
    )

    _write_text(ubuntu_repo / "README.md", "# uDOS-ubuntu\n")
    return sonic_repo


def test_init_generates_ventoy_templates(tmp_path: Path) -> None:
    sonic_repo = _prepare_family_repos(tmp_path)

    result = initialize_sonic_stick(
        repo_root=sonic_repo,
        stick_root=Path("memory/sonic/artifacts/sonic-stick"),
        theme="retro",
        include_persist=False,
    )

    stick_root = sonic_repo / "memory" / "sonic" / "artifacts" / "sonic-stick"
    ventoy_config = json.loads((stick_root / "ventoy" / "ventoy.json").read_text(encoding="utf-8"))

    assert result["action"] == "init"
    assert ventoy_config["theme"]["file"] == "/ventoy/theme/udos-retro/theme.txt"
    assert (stick_root / "profiles" / "udos-ubuntu" / "profile-manifest.json").exists()
    assert not (stick_root / "persistence").exists()


def test_add_registers_profile_and_checksum_assumption(tmp_path: Path) -> None:
    sonic_repo = _prepare_family_repos(tmp_path)
    initialize_sonic_stick(repo_root=sonic_repo, stick_root=Path("memory/sonic/artifacts/sonic-stick"))

    result = register_ubuntu_profile(
        repo_root=sonic_repo,
        stick_root=Path("memory/sonic/artifacts/sonic-stick"),
        image_name="udos-ubuntu-22.04.iso",
    )

    stick_root = sonic_repo / "memory" / "sonic" / "artifacts" / "sonic-stick"
    profile_entry = json.loads((stick_root / "config" / "profiles" / "udos-ubuntu.json").read_text(encoding="utf-8"))
    ventoy_config = json.loads((stick_root / "ventoy" / "ventoy.json").read_text(encoding="utf-8"))

    assert result["action"] == "add"
    assert profile_entry["image"]["checksum_required"] is True
    assert profile_entry["image"]["checksum_status"] == "required-unset"
    assert any(item["image"] == "/images/udos-ubuntu/udos-ubuntu-22.04.iso" for item in ventoy_config["menu_alias"])


def test_update_preserves_user_images_and_custom_config(tmp_path: Path) -> None:
    sonic_repo = _prepare_family_repos(tmp_path)
    initialize_sonic_stick(repo_root=sonic_repo, stick_root=Path("memory/sonic/artifacts/sonic-stick"))
    register_ubuntu_profile(repo_root=sonic_repo, stick_root=Path("memory/sonic/artifacts/sonic-stick"))

    stick_root = sonic_repo / "memory" / "sonic" / "artifacts" / "sonic-stick"
    custom_image = stick_root / "images" / "udos-ubuntu" / "custom.iso"
    custom_config = stick_root / "config" / "devices" / "device-1.json"
    _write_text(custom_image, "iso-bytes")
    _write_json(custom_config, {"hostname": "kiosk-01"})

    ventoy_path = stick_root / "ventoy" / "ventoy.json"
    ventoy_config = json.loads(ventoy_path.read_text(encoding="utf-8"))
    ventoy_config["menu_alias"].append({"image": "/images/udos-ubuntu/custom.iso", "alias": "Custom Image"})
    ventoy_config["custom_extension"] = {"enabled": True}
    _write_json(ventoy_path, ventoy_config)

    result = refresh_ventoy_templates(
        repo_root=sonic_repo,
        stick_root=Path("memory/sonic/artifacts/sonic-stick"),
        theme="modern",
    )

    updated_config = json.loads(ventoy_path.read_text(encoding="utf-8"))

    assert result["action"] == "update"
    assert custom_image.exists()
    assert custom_config.exists()
    assert any(item["image"] == "/images/udos-ubuntu/custom.iso" for item in updated_config["menu_alias"])
    assert updated_config["custom_extension"] == {"enabled": True}


def test_theme_switch_updates_ventoy_theme_file(tmp_path: Path) -> None:
    sonic_repo = _prepare_family_repos(tmp_path)
    initialize_sonic_stick(repo_root=sonic_repo, stick_root=Path("memory/sonic/artifacts/sonic-stick"))

    result = set_boot_theme(
        repo_root=sonic_repo,
        stick_root=Path("memory/sonic/artifacts/sonic-stick"),
        theme="retro",
    )

    stick_root = sonic_repo / "memory" / "sonic" / "artifacts" / "sonic-stick"
    ventoy_config = json.loads((stick_root / "ventoy" / "ventoy.json").read_text(encoding="utf-8"))

    assert result["action"] == "theme"
    assert ventoy_config["theme"]["file"] == "/ventoy/theme/udos-retro/theme.txt"
