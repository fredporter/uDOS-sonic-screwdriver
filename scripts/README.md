# Scripts

`scripts/` is the checked-in execution lane for Sonic-owned deployment helpers.

Current script surfaces include:

- `sonic-stick.sh` for device-apply execution
- `linux-runner-validation.sh` for one-command Ubuntu/Alpine validation of the
  real Linux deployment lane
- `validate-packaging.sh` for packaging verification
- `smoke/linux-runtime-smoke.sh` for Linux runtime smoke coverage
- `smoke/uhome-contract-conformance.sh` for cross-repo `uHOME-server` and Wizard contract conformance checks
- `run-sonic-checks.sh` for repo activation validation
- `first-run-preflight.sh` for first-run validation, v2 root checks, and OS-aware quickstart probes
- `sonic-open.sh` as the canonical bootstrap + GUI launcher (repo root `sonic-open` execs this)
- `sonic-open.command` as the macOS Finder wrapper for the launcher
- `first-run-launch.sh` / `first-run-launch.command` as compatibility wrappers to `sonic-open.sh`
- `demo-live-install-recovery.sh` for the active live/install/recovery product lane

Boundary rule:

- keep device-apply, packaging, and machine-profile helpers here
- keep dry-run validation broadly portable, but keep destructive device writes
  Linux-only
- keep canonical runtime semantics in `uDOS-core`
- keep persistent local-service runtime ownership in `uHOME-server`
