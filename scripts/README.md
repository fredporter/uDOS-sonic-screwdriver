# Scripts

`scripts/` is the checked-in execution lane for Sonic-owned deployment helpers.

Current script surfaces include:

- `sonic-stick.sh` for device-apply execution
- `validate-packaging.sh` for packaging verification
- `smoke/linux-runtime-smoke.sh` for Linux runtime smoke coverage
- `smoke/uhome-contract-conformance.sh` for cross-repo `uHOME-server` and Wizard contract conformance checks
- `run-sonic-checks.sh` for repo activation validation
- `first-run-preflight.sh` for first-run validation, v2 root checks, and OS-aware quickstart probes
- `first-run-launch.sh` for bootstrap plus Sonic GUI launch from the starter CLI
- `first-run-launch.command` as the macOS Finder wrapper for the launcher script
- `demo-live-install-recovery.sh` for the active live/install/recovery product lane

Boundary rule:

- keep device-apply, packaging, and machine-profile helpers here
- keep canonical runtime semantics in `uDOS-core`
- keep persistent local-service runtime ownership in `uHOME-server`
