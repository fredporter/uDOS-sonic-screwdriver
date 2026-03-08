"""Installable console entrypoint for the Sonic CLI."""

from __future__ import annotations

import importlib.util
from pathlib import Path


_CLI_PATH = Path(__file__).resolve().parent / "apps" / "sonic-cli" / "cli.py"
_CLI_SPEC = importlib.util.spec_from_file_location("sonic_repo_cli", _CLI_PATH)
if _CLI_SPEC is None or _CLI_SPEC.loader is None:  # pragma: no cover
    raise RuntimeError(f"Unable to load Sonic CLI from {_CLI_PATH}")
_CLI_MODULE = importlib.util.module_from_spec(_CLI_SPEC)
_CLI_SPEC.loader.exec_module(_CLI_MODULE)


def main() -> int:
    return _CLI_MODULE.main()
