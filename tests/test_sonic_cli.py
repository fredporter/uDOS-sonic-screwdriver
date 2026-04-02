from __future__ import annotations

import importlib.util
from pathlib import Path


CLI_PATH = Path(__file__).resolve().parents[1] / "apps" / "sonic-cli" / "cli.py"
CLI_SPEC = importlib.util.spec_from_file_location("sonic_cli_test_module", CLI_PATH)
assert CLI_SPEC is not None
assert CLI_SPEC.loader is not None
cli = importlib.util.module_from_spec(CLI_SPEC)
CLI_SPEC.loader.exec_module(cli)


def test_plan_command_rejects_unsupported_platform_for_non_dry_run(monkeypatch, capsys) -> None:
    monkeypatch.setattr(cli, "support_message", lambda: "WARN Linux only")
    monkeypatch.setattr(cli, "is_supported", lambda: False)
    monkeypatch.setattr(cli.sys, "argv", ["cli.py", "plan"])

    exit_code = cli.main()

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "WARN Linux only" in captured.out
    assert "ERROR Unsupported OS for build operations. Use Linux." in captured.out


def test_plan_command_allows_unsupported_platform_for_dry_run(monkeypatch, tmp_path: Path, capsys) -> None:
    calls: dict[str, object] = {}

    monkeypatch.setattr(cli, "support_message", lambda: "WARN Linux only")
    monkeypatch.setattr(cli, "is_supported", lambda: False)

    def fake_write_plan(**kwargs: object) -> dict[str, object]:
        calls.update(kwargs)
        return {"ok": True}

    monkeypatch.setattr(cli, "write_plan", fake_write_plan)
    monkeypatch.setattr(
        cli.sys,
        "argv",
        [
            "cli.py",
            "plan",
            "--repo-root",
            str(tmp_path),
            "--dry-run",
            "--out",
            "memory/sonic/test-manifest.json",
        ],
    )

    exit_code = cli.main()

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Plan written: memory/sonic/test-manifest.json" in captured.out
    assert "Dry run enabled. No destructive operations should be executed." in captured.out
    assert calls["dry_run"] is True


def test_plan_command_writes_plan_with_repo_root(monkeypatch, tmp_path: Path, capsys) -> None:
    calls: dict[str, object] = {}

    monkeypatch.setattr(cli, "support_message", lambda: "WARN Linux only")
    monkeypatch.setattr(cli, "is_supported", lambda: True)

    def fake_write_plan(**kwargs: object) -> dict[str, object]:
        calls.update(kwargs)
        return {"ok": True}

    monkeypatch.setattr(cli, "write_plan", fake_write_plan)
    monkeypatch.setattr(
        cli.sys,
        "argv",
        [
            "cli.py",
            "plan",
            "--repo-root",
            str(tmp_path),
            "--usb-device",
            "/dev/sdz",
            "--dry-run",
            "--layout-file",
            "config/test-layout.json",
            "--out",
            "memory/sonic/test-manifest.json",
            "--payloads-dir",
            "memory/sonic/artifacts/custom",
            "--format-mode",
            "skip",
        ],
    )

    exit_code = cli.main()

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Plan written: memory/sonic/test-manifest.json" in captured.out
    assert calls["repo_root"] == tmp_path
    assert calls["usb_device"] == "/dev/sdz"
    assert calls["dry_run"] is True
    assert calls["layout_path"] == Path("config/test-layout.json")
    assert calls["out_path"] == Path("memory/sonic/test-manifest.json")
    assert calls["payload_dir"] == Path("memory/sonic/artifacts/custom")
    assert calls["format_mode"] == "skip"


def test_init_command_rejects_non_linux_platform(monkeypatch, capsys) -> None:
    monkeypatch.setattr(cli, "support_message", lambda: "WARN Linux only")
    monkeypatch.setattr(cli, "is_supported", lambda: False)
    monkeypatch.setattr(cli.sys, "argv", ["cli.py", "init"])

    exit_code = cli.main()

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "ERROR sonic init requires Linux" in captured.out


def test_add_command_runs_on_macos_maintenance_lane(monkeypatch, capsys, tmp_path: Path) -> None:
    calls: dict[str, object] = {}

    def fake_register(**kwargs: object) -> dict[str, object]:
        calls.update(kwargs)
        return {
            "action": "add",
            "stick_root": str(tmp_path / "stick"),
            "changed_files": [str(tmp_path / "stick" / "config" / "profiles" / "udos-ubuntu.json")],
            "notes": [],
        }

    monkeypatch.setattr(cli, "detect_platform", lambda: "macos")
    monkeypatch.setattr(cli, "register_ubuntu_profile", fake_register)
    monkeypatch.setattr(
        cli.sys,
        "argv",
        [
            "cli.py",
            "add",
            "udos-ubuntu",
            "--repo-root",
            str(tmp_path),
            "--stick-root",
            "memory/sonic/artifacts/sonic-stick",
            "--image-name",
            "udos-ubuntu-22.04.iso",
        ],
    )

    exit_code = cli.main()

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Action complete: add" in captured.out
    assert calls["profile"] == "udos-ubuntu"
    assert calls["image_name"] == "udos-ubuntu-22.04.iso"


def test_no_args_prints_starter_help_when_not_interactive(monkeypatch, capsys) -> None:
    monkeypatch.setattr(cli.sys.stdin, "isatty", lambda: False)
    monkeypatch.setattr(cli.sys, "argv", ["cli.py"])

    exit_code = cli.main()

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Welcome to Sonic" in captured.out
    assert "sonic start" in captured.out


def test_start_command_delegates_to_sonic_open_launcher(monkeypatch, tmp_path: Path) -> None:
    launcher = tmp_path / "scripts" / "sonic-open.sh"
    launcher.parent.mkdir(parents=True)
    launcher.write_text("#!/usr/bin/env bash\n", encoding="utf-8")
    calls: list[list[str]] = []

    monkeypatch.setattr(cli.sys, "argv", ["cli.py", "start"])
    monkeypatch.setattr(cli.subprocess, "call", lambda cmd: calls.append(cmd) or 0)

    exit_code = cli._dispatch(["start"], tmp_path)

    assert exit_code == 0
    assert calls == [["bash", str(launcher)]]
