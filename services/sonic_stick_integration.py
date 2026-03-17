"""Sonic v2 helpers for uDOS-ventoy and uDOS-ubuntu integration."""

from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional


THEME_FILES: Dict[str, str] = {
    "modern": "/ventoy/theme/udos-modern/theme.txt",
    "retro": "/ventoy/theme/udos-retro/theme.txt",
}

THEME_FOLDERS: Dict[str, str] = {
    "modern": "udos-modern",
    "retro": "udos-retro",
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _normalize_theme(theme: str) -> str:
    token = str(theme or "modern").strip().lower()
    if token in {"modern", "udos-modern"}:
        return "modern"
    if token in {"retro", "udos-retro"}:
        return "retro"
    raise ValueError(f"unsupported theme '{theme}'. Use modern or retro.")


def _resolve_repo_path(repo_root: Path, provided: Optional[Path], sibling_name: str) -> Path:
    if provided is None:
        candidate = repo_root.parent / sibling_name
    else:
        candidate = Path(provided).expanduser()
        if not candidate.is_absolute():
            candidate = repo_root / candidate
    candidate = candidate.resolve()
    if not candidate.exists():
        raise ValueError(f"required repository not found: {candidate}")
    return candidate


def _resolve_local_path(repo_root: Path, target: Path) -> Path:
    candidate = Path(target).expanduser()
    if not candidate.is_absolute():
        candidate = repo_root / candidate
    return candidate.resolve()


def _load_json(path: Path, default: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    if not path.exists():
        if default is not None:
            return default
        raise ValueError(f"required file missing: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON in {path}: {exc}") from exc


def _write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _copy_file(source: Path, destination: Path, changed_files: List[str]) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    changed_files.append(str(destination))


def _copy_tree(source_root: Path, destination_root: Path, changed_files: List[str]) -> None:
    if not source_root.exists():
        raise ValueError(f"required source directory missing: {source_root}")
    for item in source_root.rglob("*"):
        relative = item.relative_to(source_root)
        destination = destination_root / relative
        if item.is_dir():
            destination.mkdir(parents=True, exist_ok=True)
            continue
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(item, destination)
        changed_files.append(str(destination))


def _merge_entries(
    existing: List[Dict[str, Any]],
    template: List[Dict[str, Any]],
    identity: Callable[[Dict[str, Any]], str],
) -> List[Dict[str, Any]]:
    merged: List[Dict[str, Any]] = []
    seen: set[str] = set()
    for item in existing + template:
        if not isinstance(item, dict):
            continue
        marker = identity(item)
        if marker in seen:
            continue
        seen.add(marker)
        merged.append(item)
    return merged


def _menu_class_identity(item: Dict[str, Any]) -> str:
    if item.get("dir"):
        return f"dir:{item['dir']}"
    if item.get("key"):
        return f"key:{item['key']}"
    return json.dumps(item, sort_keys=True)


def _path_identity(field: str) -> Callable[[Dict[str, Any]], str]:
    def _identity(item: Dict[str, Any]) -> str:
        value = item.get(field)
        if value:
            return f"{field}:{value}"
        return json.dumps(item, sort_keys=True)

    return _identity


def _selected_theme_from_config(config: Dict[str, Any]) -> Optional[str]:
    theme_section = config.get("theme")
    if not isinstance(theme_section, dict):
        return None
    file_path = str(theme_section.get("file", ""))
    if "/udos-retro/" in file_path:
        return "retro"
    if "/udos-modern/" in file_path:
        return "modern"
    return None


def _with_theme(config: Dict[str, Any], theme: str) -> Dict[str, Any]:
    themed = dict(config)
    theme_block = dict(themed.get("theme") or {})
    theme_block["file"] = THEME_FILES[theme]
    themed["theme"] = theme_block
    return themed


def _ensure_layout_dirs(stick_root: Path, profile: str, include_persist: bool) -> None:
    required_dirs = [
        stick_root / "ventoy",
        stick_root / "images" / profile,
        stick_root / "images" / "recovery",
        stick_root / "images" / "extras",
        stick_root / "config" / "global",
        stick_root / "config" / "devices",
        stick_root / "config" / "profiles",
        stick_root / "profiles" / profile,
        stick_root / "recovery" / "tools",
        stick_root / "udos" / "bootstrap",
        stick_root / "udos" / "assets",
        stick_root / "udos" / "manifests",
    ]
    if include_persist:
        required_dirs.append(stick_root / "persistence")
    for path in required_dirs:
        path.mkdir(parents=True, exist_ok=True)


def _load_template_assets(ventoy_repo: Path) -> tuple[Path, Dict[str, Any]]:
    template_root = ventoy_repo / "templates" / "ventoy"
    required_files = [
        template_root / "ventoy.json",
        template_root / "grub" / "udos_menu.cfg",
        template_root / "theme" / "udos-modern" / "theme.txt",
        template_root / "theme" / "udos-retro" / "theme.txt",
    ]
    for required in required_files:
        if not required.exists():
            raise ValueError(f"required template asset missing: {required}")
    return template_root, _load_json(template_root / "ventoy.json")


def _load_profile_manifest(ventoy_repo: Path, profile: str) -> tuple[Path, Dict[str, Any]]:
    manifest_path = ventoy_repo / "profiles" / profile / "manifest.json"
    return manifest_path, _load_json(manifest_path)


def _default_image_name(profile: str) -> str:
    if profile == "udos-ubuntu":
        return "udos-ubuntu-22.04.iso"
    return f"{profile}.iso"


def initialize_sonic_stick(
    repo_root: Path,
    stick_root: Path,
    *,
    ventoy_repo: Optional[Path] = None,
    theme: str = "modern",
    profile: str = "udos-ubuntu",
    stick_size: str = "128gb",
    include_persist: bool = True,
) -> Dict[str, Any]:
    resolved_repo_root = repo_root.resolve()
    resolved_stick_root = _resolve_local_path(resolved_repo_root, stick_root)
    resolved_ventoy_repo = _resolve_repo_path(resolved_repo_root, ventoy_repo, "uDOS-ventoy")
    normalized_theme = _normalize_theme(theme)

    changed_files: List[str] = []
    notes: List[str] = []

    _ensure_layout_dirs(resolved_stick_root, profile, include_persist)
    template_root, template_config = _load_template_assets(resolved_ventoy_repo)

    _copy_tree(template_root / "grub", resolved_stick_root / "ventoy" / "grub", changed_files)
    _copy_tree(template_root / "theme", resolved_stick_root / "ventoy" / "theme", changed_files)

    themed_config = _with_theme(template_config, normalized_theme)
    ventoy_config_path = resolved_stick_root / "ventoy" / "ventoy.json"
    _write_json(ventoy_config_path, themed_config)
    changed_files.append(str(ventoy_config_path))

    profile_manifest_path, _ = _load_profile_manifest(resolved_ventoy_repo, profile)
    local_profile_manifest = resolved_stick_root / "profiles" / profile / "profile-manifest.json"
    _copy_file(profile_manifest_path, local_profile_manifest, changed_files)

    layout_summary_path = resolved_stick_root / "config" / "global" / "sonic-stick-layout.json"
    _write_json(
        layout_summary_path,
        {
            "layout": "sonic-stick",
            "size_profile": stick_size,
            "persistence_enabled": include_persist,
            "active_theme": normalized_theme,
            "active_profile": profile,
            "updated_at": _utc_now(),
        },
    )
    changed_files.append(str(layout_summary_path))

    if not include_persist:
        notes.append("persistence directory was not created")

    return {
        "action": "init",
        "stick_root": str(resolved_stick_root),
        "theme": normalized_theme,
        "profile": profile,
        "changed_files": sorted(set(changed_files)),
        "notes": notes,
    }


def register_ubuntu_profile(
    repo_root: Path,
    stick_root: Path,
    *,
    profile: str = "udos-ubuntu",
    image_name: Optional[str] = None,
    checksum: Optional[str] = None,
    checksum_algorithm: str = "sha256",
    ventoy_repo: Optional[Path] = None,
    ubuntu_repo: Optional[Path] = None,
    replace: bool = False,
) -> Dict[str, Any]:
    resolved_repo_root = repo_root.resolve()
    resolved_stick_root = _resolve_local_path(resolved_repo_root, stick_root)
    resolved_ventoy_repo = _resolve_repo_path(resolved_repo_root, ventoy_repo, "uDOS-ventoy")
    resolved_ubuntu_repo = _resolve_repo_path(resolved_repo_root, ubuntu_repo, "uDOS-ubuntu")

    ventoy_config_path = resolved_stick_root / "ventoy" / "ventoy.json"
    if not ventoy_config_path.exists():
        raise ValueError(f"missing generated ventoy config: {ventoy_config_path}. Run sonic init first.")

    changed_files: List[str] = []
    notes: List[str] = []

    profile_manifest_path, profile_manifest = _load_profile_manifest(resolved_ventoy_repo, profile)
    local_profile_manifest = resolved_stick_root / "profiles" / profile / "profile-manifest.json"
    _copy_file(profile_manifest_path, local_profile_manifest, changed_files)

    resolved_image_name = image_name or _default_image_name(profile)
    image_path = f"/images/{profile}/{resolved_image_name}"
    checksum_required = bool(profile_manifest.get("checksum_required", False))
    checksum_state = "provided"
    if not checksum and checksum_required:
        checksum_state = "required-unset"
        notes.append("profile requires checksum; none provided")
    elif not checksum:
        checksum_state = "optional-unset"

    profile_entry_path = resolved_stick_root / "config" / "profiles" / f"{profile}.json"
    existing_entry = _load_json(profile_entry_path, default={}) if profile_entry_path.exists() else {}

    profile_entry: Dict[str, Any] = {
        "profile": profile,
        "display_name": profile_manifest.get("display_name", profile),
        "modes": profile_manifest.get("modes", []),
        "image": {
            "path": image_path,
            "checksum_algorithm": checksum_algorithm,
            "checksum": checksum,
            "checksum_required": checksum_required,
            "checksum_status": checksum_state,
        },
        "source": {
            "ventoy_profile_manifest": str(profile_manifest_path),
            "ubuntu_repo": str(resolved_ubuntu_repo),
        },
        "updated_at": _utc_now(),
    }

    if existing_entry and not replace:
        merged_entry = dict(existing_entry)
        merged_entry.update(profile_entry)
        profile_entry = merged_entry

    _write_json(profile_entry_path, profile_entry)
    changed_files.append(str(profile_entry_path))

    (resolved_stick_root / "images" / profile).mkdir(parents=True, exist_ok=True)

    ventoy_config = _load_json(ventoy_config_path)
    menu_class = [item for item in (ventoy_config.get("menu_class") or []) if isinstance(item, dict)]
    menu_alias = [item for item in (ventoy_config.get("menu_alias") or []) if isinstance(item, dict)]
    menu_tip = [item for item in (ventoy_config.get("menu_tip") or []) if isinstance(item, dict)]

    menu_class = _merge_entries(
        menu_class,
        [{"dir": f"/images/{profile}", "class": profile.replace("-", "_")}],
        _menu_class_identity,
    )
    menu_alias = _merge_entries(
        menu_alias,
        [{"image": image_path, "alias": f"{profile_entry['display_name']} - Base System"}],
        _path_identity("image"),
    )
    menu_tip = _merge_entries(
        menu_tip,
        [{"image": image_path, "tip": "Primary image profile managed by sonic-screwdriver."}],
        _path_identity("image"),
    )

    ventoy_config["menu_class"] = menu_class
    ventoy_config["menu_alias"] = menu_alias
    ventoy_config["menu_tip"] = menu_tip
    _write_json(ventoy_config_path, ventoy_config)
    changed_files.append(str(ventoy_config_path))

    return {
        "action": "add",
        "stick_root": str(resolved_stick_root),
        "profile": profile,
        "image": image_path,
        "changed_files": sorted(set(changed_files)),
        "notes": notes,
    }


def refresh_ventoy_templates(
    repo_root: Path,
    stick_root: Path,
    *,
    profile: str = "udos-ubuntu",
    ventoy_repo: Optional[Path] = None,
    theme: Optional[str] = None,
) -> Dict[str, Any]:
    resolved_repo_root = repo_root.resolve()
    resolved_stick_root = _resolve_local_path(resolved_repo_root, stick_root)
    resolved_ventoy_repo = _resolve_repo_path(resolved_repo_root, ventoy_repo, "uDOS-ventoy")

    template_root, template_config = _load_template_assets(resolved_ventoy_repo)
    ventoy_config_path = resolved_stick_root / "ventoy" / "ventoy.json"

    existing_config = _load_json(ventoy_config_path, default={}) if ventoy_config_path.exists() else {}
    chosen_theme = _normalize_theme(theme) if theme else _selected_theme_from_config(existing_config) or "modern"

    changed_files: List[str] = []
    notes: List[str] = []

    merged_config: Dict[str, Any] = dict(template_config)
    merged_config["menu_class"] = _merge_entries(
        [item for item in (existing_config.get("menu_class") or []) if isinstance(item, dict)],
        [item for item in (template_config.get("menu_class") or []) if isinstance(item, dict)],
        _menu_class_identity,
    )
    merged_config["menu_alias"] = _merge_entries(
        [item for item in (existing_config.get("menu_alias") or []) if isinstance(item, dict)],
        [item for item in (template_config.get("menu_alias") or []) if isinstance(item, dict)],
        _path_identity("image"),
    )
    merged_config["menu_tip"] = _merge_entries(
        [item for item in (existing_config.get("menu_tip") or []) if isinstance(item, dict)],
        [item for item in (template_config.get("menu_tip") or []) if isinstance(item, dict)],
        _path_identity("image"),
    )
    for key, value in existing_config.items():
        if key not in merged_config:
            merged_config[key] = value

    merged_config = _with_theme(merged_config, chosen_theme)

    _copy_tree(template_root / "grub", resolved_stick_root / "ventoy" / "grub", changed_files)
    _copy_tree(template_root / "theme", resolved_stick_root / "ventoy" / "theme", changed_files)
    _write_json(ventoy_config_path, merged_config)
    changed_files.append(str(ventoy_config_path))

    profile_manifest_path, profile_manifest = _load_profile_manifest(resolved_ventoy_repo, profile)
    local_profile_manifest = resolved_stick_root / "profiles" / profile / "profile-manifest.json"
    _copy_file(profile_manifest_path, local_profile_manifest, changed_files)

    profile_entry_path = resolved_stick_root / "config" / "profiles" / f"{profile}.json"
    if profile_entry_path.exists():
        profile_entry = _load_json(profile_entry_path)
        image = dict(profile_entry.get("image") or {})
        checksum_required = bool(profile_manifest.get("checksum_required", False))
        image["checksum_required"] = checksum_required
        if checksum_required and not image.get("checksum"):
            image["checksum_status"] = "required-unset"
            notes.append("checksum requirement remains unsatisfied for registered profile")
        profile_entry["image"] = image
        profile_entry["updated_at"] = _utc_now()
        _write_json(profile_entry_path, profile_entry)
        changed_files.append(str(profile_entry_path))

    update_stamp_path = resolved_stick_root / "config" / "global" / "sonic-update.json"
    _write_json(
        update_stamp_path,
        {
            "updated_at": _utc_now(),
            "profile": profile,
            "theme": chosen_theme,
            "action": "refresh-ventoy-templates",
        },
    )
    changed_files.append(str(update_stamp_path))

    return {
        "action": "update",
        "stick_root": str(resolved_stick_root),
        "theme": chosen_theme,
        "profile": profile,
        "changed_files": sorted(set(changed_files)),
        "notes": notes,
    }


def set_boot_theme(
    repo_root: Path,
    stick_root: Path,
    *,
    theme: str,
    ventoy_repo: Optional[Path] = None,
) -> Dict[str, Any]:
    resolved_repo_root = repo_root.resolve()
    resolved_stick_root = _resolve_local_path(resolved_repo_root, stick_root)
    resolved_ventoy_repo = _resolve_repo_path(resolved_repo_root, ventoy_repo, "uDOS-ventoy")
    normalized_theme = _normalize_theme(theme)

    ventoy_config_path = resolved_stick_root / "ventoy" / "ventoy.json"
    if not ventoy_config_path.exists():
        raise ValueError(f"missing generated ventoy config: {ventoy_config_path}. Run sonic init first.")

    changed_files: List[str] = []

    source_theme_dir = (
        resolved_ventoy_repo
        / "templates"
        / "ventoy"
        / "theme"
        / THEME_FOLDERS[normalized_theme]
    )
    destination_theme_dir = (
        resolved_stick_root
        / "ventoy"
        / "theme"
        / THEME_FOLDERS[normalized_theme]
    )
    _copy_tree(source_theme_dir, destination_theme_dir, changed_files)

    ventoy_config = _load_json(ventoy_config_path)
    ventoy_config = _with_theme(ventoy_config, normalized_theme)
    _write_json(ventoy_config_path, ventoy_config)
    changed_files.append(str(ventoy_config_path))

    return {
        "action": "theme",
        "stick_root": str(resolved_stick_root),
        "theme": normalized_theme,
        "changed_files": sorted(set(changed_files)),
        "notes": [],
    }
