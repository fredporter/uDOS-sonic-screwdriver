# uDOS-sonic-screwdriver Activation

## Purpose

This document marks the first active implementation tranche for
`uDOS-sonic-screwdriver`.

The activation goal is to make Sonic runnable, testable, and teachable as the
deployment and packaging owner without broadening its ownership beyond:

- packaging and bootstrap flows
- managed environment provisioning
- deployment planning and manifest verification
- hardware-aware install and machine-profile tooling

## Activated Surfaces

- `sonic_cli.py` as the installable CLI entrypoint
- `services/` as the deployment planner, API, and runtime service lane
- `scripts/` as the checked-in Linux-side execution lane
- `tests/` as the packaging and smoke validation lane
- `scripts/run-sonic-checks.sh` as the repo validation entrypoint
- `examples/basic-sonic-session.md` as the smallest operator walkthrough

## Current Validation Contract

Run:

```bash
scripts/run-sonic-checks.sh
```

This command:

- bootstraps a local `.venv` only when needed
- installs the editable Sonic package with test dependencies
- runs the current packaging, launcher, service, and smoke-path tests

## Boundaries

This activation does not move ownership into Sonic for:

- canonical runtime semantics
- persistent local-service ownership
- provider and MCP control-plane ownership outside Sonic's deployment facade
- private OMD product behavior
