# Scripts

`scripts/` is the checked-in execution lane for Sonic-owned deployment helpers.

Current script surfaces include:

- `sonic-stick.sh` for device-apply execution
- `validate-packaging.sh` for packaging verification
- `smoke/linux-runtime-smoke.sh` for Linux runtime smoke coverage
- `run-sonic-checks.sh` for repo activation validation

Boundary rule:

- keep device-apply, packaging, and machine-profile helpers here
- keep canonical runtime semantics in `uDOS-core`
- keep persistent local-service runtime ownership in `uHOME-server`
