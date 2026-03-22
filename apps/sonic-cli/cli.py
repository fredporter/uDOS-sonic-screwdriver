"""uDOS-sonic-screwdriver CLI.

Usage:
  python3 apps/sonic-cli/cli.py plan --usb-device /dev/sdb
"""

from __future__ import annotations

import argparse
import shlex
import subprocess
import sys
from pathlib import Path

if __package__ in {None, ""}:  # pragma: no cover - direct script execution
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

try:
    from services.os_limits import detect_platform, support_message, is_supported
    from services.http_api import serve as serve_api
    from services.mcp_server import SonicMcpServer
    from services.planner import write_plan
    from services.sonic_stick_integration import (
        initialize_sonic_stick,
        refresh_ventoy_templates,
        register_ubuntu_profile,
        set_boot_theme,
    )
except ImportError:  # pragma: no cover - fallback for direct execution
    from services.os_limits import detect_platform, support_message, is_supported
    from services.http_api import serve as serve_api
    from services.mcp_server import SonicMcpServer
    from services.planner import write_plan
    from services.sonic_stick_integration import (
        initialize_sonic_stick,
        refresh_ventoy_templates,
        register_ubuntu_profile,
        set_boot_theme,
    )


def _print_integration_result(result: dict) -> None:
    print(f"Action complete: {result.get('action')}")
    print(f"Stick root: {result.get('stick_root')}")
    changed_files = list(result.get("changed_files") or [])
    if changed_files:
        print("Updated files:")
        for file_path in changed_files:
            print(f"- {file_path}")
    for note in result.get("notes") or []:
        print(f"NOTE {note}")


STARTER_COMMANDS = (
    "help",
    "commands",
    "start",
    "status",
    "test",
    "doctor",
    "clear",
    "exit",
)


def _normalize_argv(argv: list[str]) -> list[str]:
    if not argv:
        return argv
    normalized = list(argv)
    normalized[0] = normalized[0].lower()
    if len(normalized) > 1 and normalized[0] in {"help", "commands", "start", "test"}:
        normalized[1] = normalized[1].lower()
    return normalized


def _print_starter_help() -> None:
    print("Welcome to Sonic")
    print("")
    print("Starter commands:")
    print("  help          Show starter help")
    print("  commands      List available commands")
    print("  start         Launch the Sonic ThinUI/browser surface")
    print("  status        Show local runtime status")
    print("  test          Show test targets")
    print("  doctor        Check local environment")
    print("  exit          Quit")
    print("")
    print("Examples:")
    print("  sonic start")
    print("  sonic test repo")
    print("  sonic help start")


def _print_command_list(include_advanced: bool = False) -> None:
    print("Starter commands")
    print("")
    print("Discovery:")
    print("  help")
    print("  help <command>")
    print("  commands")
    print("  commands list")
    print("")
    print("Launch:")
    print("  start")
    print("  start thinui")
    print("  start gui")
    print("")
    print("Validation:")
    print("  test")
    print("  test repo")
    print("  test thinui")
    print("  test all")
    print("  doctor")
    print("")
    print("Session:")
    print("  status")
    print("  clear")
    print("  exit")
    if include_advanced:
        print("")
        print("Advanced commands")
        print("  plan")
        print("  init")
        print("  add")
        print("  update")
        print("  theme")
        print("  run")
        print("  serve-api")
        print("  serve-mcp")


def _print_help_topic(topic: str | None) -> None:
    if topic in {None, "help"}:
        _print_starter_help()
        return
    if topic == "commands":
        print("commands")
        print("")
        print("Use `commands` for the starter surface.")
        print("Use `commands list` to include the deeper provisioning/runtime commands.")
        return
    if topic == "start":
        print("start")
        print("")
        print("Launch the Sonic GUI lane.")
        print("`start`, `start thinui`, and `start gui` all bootstrap the local API and browser UI.")
        print("This delegates to scripts/first-run-launch.sh.")
        return
    if topic == "status":
        print("status")
        print("")
        print("Report repo-root, venv, UI dependency, and ThinUI sibling availability.")
        return
    if topic == "test":
        print("test")
        print("")
        print("Use `test repo` for repo validation, `test thinui` for the ThinUI launcher demo, and `test all` for both.")
        return
    if topic == "doctor":
        print("doctor")
        print("")
        print("Checks local toolchain requirements: python3, node, npm, bash, venv, and UI package metadata.")
        return
    print(f"Unknown help topic: {topic}")
    print("Try `commands` or `commands list`.")


def _print_status(repo_root: Path) -> None:
    print("Sonic Status")
    print("")
    print(f"Repo Root: {repo_root}")
    print(f"Python Venv: {'ready' if (repo_root / '.venv' / 'bin' / 'python').exists() else 'missing'}")
    print(f"Sonic API Entrypoint: {'ready' if (repo_root / '.venv' / 'bin' / 'sonic-api').exists() else 'missing'}")
    print(f"Sonic UI Deps: {'ready' if (repo_root / 'apps' / 'sonic-ui' / 'node_modules').exists() else 'missing'}")
    print(f"ThinUI Sibling: {'available' if (repo_root.parent / 'uDOS-thinui').exists() else 'missing'}")
    print(f"Launcher Script: {'ready' if (repo_root / 'scripts' / 'first-run-launch.sh').exists() else 'missing'}")


def _run_doctor(repo_root: Path) -> int:
    checks = (
        ("python3", ["python3", "--version"]),
        ("node", ["node", "--version"]),
        ("npm", ["npm", "--version"]),
        ("bash", ["bash", "--version"]),
    )
    failed = False
    print("Sonic Doctor")
    print("")
    for label, cmd in checks:
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            print(f"[ok] {label}")
        except (FileNotFoundError, subprocess.CalledProcessError):
            print(f"[missing] {label}")
            failed = True
    metadata_checks = (
        ("apps/sonic-ui/package.json", repo_root / "apps" / "sonic-ui" / "package.json"),
        ("scripts/first-run-launch.sh", repo_root / "scripts" / "first-run-launch.sh"),
    )
    for label, path in metadata_checks:
        if path.exists():
            print(f"[ok] {label}")
        else:
            print(f"[missing] {label}")
            failed = True
    return 1 if failed else 0


def _print_test_help() -> None:
    print("Test Targets")
    print("")
    print("  test repo    Run repo validation")
    print("  test thinui  Run ThinUI launcher demo")
    print("  test all     Run repo validation and ThinUI demo")


def _run_test(repo_root: Path, target: str | None) -> int:
    if target is None:
        _print_test_help()
        return 0
    scripts = {
        "repo": [str(repo_root / "scripts" / "run-sonic-checks.sh")],
        "thinui": [str(repo_root / "scripts" / "demo-thinui-launch.sh")],
    }
    if target == "all":
        for name in ("repo", "thinui"):
            result = subprocess.call(["bash", *scripts[name]])
            if result != 0:
                return result
        return 0
    return subprocess.call(["bash", *scripts[target]])


def _launch_gui(repo_root: Path) -> int:
    launcher = repo_root / "scripts" / "first-run-launch.sh"
    if not launcher.exists():
        print(f"ERROR Missing launcher: {launcher}")
        return 1
    return subprocess.call(["bash", str(launcher)])


def _run_repl(repo_root: Path) -> int:
    _print_starter_help()
    while True:
        try:
            raw = input("SONIC> ")
        except EOFError:
            print("")
            return 0
        except KeyboardInterrupt:
            print("")
            return 0
        command = raw.strip()
        if not command:
            continue
        try:
            argv = shlex.split(command)
        except ValueError as exc:
            print(f"ERROR {exc}")
            continue
        exit_code = _dispatch(argv, repo_root, interactive=True)
        if exit_code == -1:
            return 0


def _dispatch(argv: list[str], repo_root: Path, interactive: bool = False) -> int:
    normalized_argv = _normalize_argv(argv)
    if not normalized_argv:
        if interactive:
            _print_starter_help()
        elif sys.stdin.isatty():
            return _run_repl(repo_root)
        else:
            _print_starter_help()
        return 0

    starter = normalized_argv[0]
    if starter == "exit":
        return -1 if interactive else 0
    if starter == "clear":
        print("\033[2J\033[H", end="")
        return 0

    parser = argparse.ArgumentParser(description="uDOS-sonic-screwdriver CLI")
    sub = parser.add_subparsers(dest="cmd")
    default_repo_root = str(repo_root)

    help_cmd = sub.add_parser("help", help="Show starter help")
    help_cmd.add_argument("topic", nargs="?")

    commands_cmd = sub.add_parser("commands", help="List starter commands")
    commands_cmd.add_argument("scope", nargs="?", choices=["list"])

    start_cmd = sub.add_parser("start", help="Launch the Sonic GUI lane")
    start_cmd.add_argument("target", nargs="?", default="thinui", choices=["thinui", "gui"])

    sub.add_parser("status", help="Show local runtime status")

    test_cmd = sub.add_parser("test", help="Show or run test targets")
    test_cmd.add_argument("target", nargs="?", choices=["repo", "thinui", "all"])

    sub.add_parser("doctor", help="Check local environment")

    plan_cmd = sub.add_parser("plan", help="Generate ops manifest")
    plan_cmd.add_argument("--repo-root", default=default_repo_root)
    plan_cmd.add_argument("--usb-device", default="/dev/sdb")
    plan_cmd.add_argument("--dry-run", action="store_true")
    plan_cmd.add_argument("--out", default="memory/sonic/sonic-manifest.json")
    plan_cmd.add_argument("--layout-file", default="config/sonic-layout.json")
    plan_cmd.add_argument(
        "--payloads-dir",
        default=None,
        help="Override payloads root directory (defaults to repo_root/memory/sonic/artifacts/payloads)",
    )
    plan_cmd.add_argument(
        "--format-mode",
        default=None,
        choices=["full", "skip"],
        help="Formatting mode for partitions (full|skip). Defaults to layout file or full.",
    )

    init_cmd = sub.add_parser("init", help="Initialize sonic-stick templates from uDOS-ventoy")
    init_cmd.add_argument("--repo-root", default=default_repo_root)
    init_cmd.add_argument("--stick-root", default="memory/sonic/artifacts/sonic-stick")
    init_cmd.add_argument("--ventoy-repo", default=None)
    init_cmd.add_argument("--theme", default="modern", choices=["modern", "retro"])
    init_cmd.add_argument("--profile", default="udos-ubuntu")
    init_cmd.add_argument("--stick-size", default="128gb", choices=["64gb", "128gb"])
    init_cmd.add_argument("--without-persist", action="store_true")

    add_cmd = sub.add_parser("add", help="Register image metadata from uDOS-ubuntu profile assumptions")
    add_cmd.add_argument("profile", nargs="?", default="udos-ubuntu")
    add_cmd.add_argument("--repo-root", default=default_repo_root)
    add_cmd.add_argument("--stick-root", default="memory/sonic/artifacts/sonic-stick")
    add_cmd.add_argument("--ventoy-repo", default=None)
    add_cmd.add_argument("--ubuntu-repo", default=None)
    add_cmd.add_argument("--image-name", default=None)
    add_cmd.add_argument("--checksum", default=None)
    add_cmd.add_argument("--checksum-algorithm", default="sha256")
    add_cmd.add_argument("--replace", action="store_true")

    update_cmd = sub.add_parser("update", help="Refresh Ventoy templates and profile metadata")
    update_cmd.add_argument("--repo-root", default=default_repo_root)
    update_cmd.add_argument("--stick-root", default="memory/sonic/artifacts/sonic-stick")
    update_cmd.add_argument("--ventoy-repo", default=None)
    update_cmd.add_argument("--profile", default="udos-ubuntu")
    update_cmd.add_argument("--theme", default=None, choices=["modern", "retro"])

    theme_cmd = sub.add_parser("theme", help="Switch the active boot theme")
    theme_cmd.add_argument("theme", choices=["modern", "retro"])
    theme_cmd.add_argument("--repo-root", default=default_repo_root)
    theme_cmd.add_argument("--stick-root", default="memory/sonic/artifacts/sonic-stick")
    theme_cmd.add_argument("--ventoy-repo", default=None)

    run_cmd = sub.add_parser("run", help="Execute bash entrypoint")
    run_cmd.add_argument("--manifest", default="memory/sonic/sonic-manifest.json")
    run_cmd.add_argument("--dry-run", action="store_true")
    run_cmd.add_argument("--v2", action="store_true", help="Use v2 partition layout pipeline")
    run_cmd.add_argument("--skip-payloads", action="store_true")
    run_cmd.add_argument("--payloads-only", action="store_true")
    run_cmd.add_argument("--payloads-dir", default=None)
    run_cmd.add_argument("--no-validate-payloads", action="store_true")

    api_cmd = sub.add_parser("serve-api", help="Serve the local Sonic HTTP API")
    api_cmd.add_argument("--repo-root", default=default_repo_root)
    api_cmd.add_argument("--host", default="127.0.0.1")
    api_cmd.add_argument("--port", type=int, default=8991)

    mcp_cmd = sub.add_parser("serve-mcp", help="Serve the Sonic MCP facade over stdio")
    mcp_cmd.add_argument("--repo-root", default=default_repo_root)

    args = parser.parse_args(normalized_argv)

    if args.cmd == "help":
        _print_help_topic(args.topic)
        return 0

    if args.cmd == "commands":
        _print_command_list(include_advanced=args.scope == "list")
        return 0

    if args.cmd == "start":
        return _launch_gui(repo_root)

    if args.cmd == "status":
        _print_status(repo_root)
        return 0

    if args.cmd == "test":
        return _run_test(repo_root, args.target)

    if args.cmd == "doctor":
        return _run_doctor(repo_root)

    if args.cmd == "plan":
        print(support_message())
        if not is_supported():
            print("ERROR Unsupported OS for build operations. Use Linux.")
            return 1
        try:
            write_plan(
                repo_root=Path(args.repo_root),
                usb_device=args.usb_device,
                dry_run=args.dry_run,
                layout_path=Path(args.layout_file) if args.layout_file else None,
                format_mode=args.format_mode,
                payload_dir=Path(args.payloads_dir) if args.payloads_dir else None,
                out_path=Path(args.out),
            )
        except ValueError as exc:
            print(f"ERROR {exc}")
            return 1
        print(f"Plan written: {args.out}")
        if args.dry_run:
            print("Dry run enabled. No destructive operations should be executed.")
        return 0

    if args.cmd == "serve-api":
        return serve_api(host=args.host, port=args.port, repo_root=Path(args.repo_root))

    if args.cmd == "serve-mcp":
        return SonicMcpServer(repo_root=Path(args.repo_root)).run()

    if args.cmd == "init":
        print(support_message())
        if not is_supported():
            print("ERROR sonic init requires Linux. macOS is maintenance-only for add/update/theme.")
            return 1
        try:
            result = initialize_sonic_stick(
                repo_root=Path(args.repo_root),
                stick_root=Path(args.stick_root),
                ventoy_repo=Path(args.ventoy_repo) if args.ventoy_repo else None,
                theme=args.theme,
                profile=args.profile,
                stick_size=args.stick_size,
                include_persist=not args.without_persist,
            )
        except ValueError as exc:
            print(f"ERROR {exc}")
            return 1
        _print_integration_result(result)
        return 0

    if args.cmd in {"add", "update", "theme"}:
        if detect_platform() not in {"alpine", "ubuntu", "macos"}:
            print("ERROR Sonic maintenance commands support Linux and macOS only.")
            return 1
        try:
            if args.cmd == "add":
                result = register_ubuntu_profile(
                    repo_root=Path(args.repo_root),
                    stick_root=Path(args.stick_root),
                    profile=args.profile,
                    image_name=args.image_name,
                    checksum=args.checksum,
                    checksum_algorithm=args.checksum_algorithm,
                    ventoy_repo=Path(args.ventoy_repo) if args.ventoy_repo else None,
                    ubuntu_repo=Path(args.ubuntu_repo) if args.ubuntu_repo else None,
                    replace=args.replace,
                )
            elif args.cmd == "update":
                result = refresh_ventoy_templates(
                    repo_root=Path(args.repo_root),
                    stick_root=Path(args.stick_root),
                    profile=args.profile,
                    ventoy_repo=Path(args.ventoy_repo) if args.ventoy_repo else None,
                    theme=args.theme,
                )
            else:
                result = set_boot_theme(
                    repo_root=Path(args.repo_root),
                    stick_root=Path(args.stick_root),
                    theme=args.theme,
                    ventoy_repo=Path(args.ventoy_repo) if args.ventoy_repo else None,
                )
        except ValueError as exc:
            print(f"ERROR {exc}")
            return 1
        _print_integration_result(result)
        return 0

    print(support_message())
    if not is_supported():
        print("ERROR Unsupported OS for build operations. Use Linux.")
        return 1

    script = Path(__file__).resolve().parents[2] / "scripts" / "sonic-stick.sh"
    cmd = ["bash", str(script), "--manifest", args.manifest]
    if args.dry_run:
        cmd.append("--dry-run")
    if args.v2:
        # v2 is now always on; accept flag for compatibility.
        pass
    if args.skip_payloads:
        cmd.append("--skip-payloads")
    if args.payloads_only:
        cmd.append("--payloads-only")
    if args.payloads_dir:
        cmd.extend(["--payloads-dir", args.payloads_dir])
    if args.no_validate_payloads:
        cmd.append("--no-validate-payloads")
    return subprocess.call(cmd)


def main() -> int:
    repo_root = Path(__file__).resolve().parents[2]
    return _dispatch(sys.argv[1:], repo_root)


if __name__ == "__main__":
    raise SystemExit(main())
