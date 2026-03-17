"""uDOS-sonic-screwdriver CLI.

Usage:
  python3 apps/sonic-cli/cli.py plan --usb-device /dev/sdb
"""

import argparse
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


def main() -> int:
    parser = argparse.ArgumentParser(description="uDOS-sonic-screwdriver CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)
    default_repo_root = str(Path(__file__).resolve().parents[2])

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

    args = parser.parse_args()

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


if __name__ == "__main__":
    raise SystemExit(main())
