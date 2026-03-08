# Sonic Standalone Release and Install Guide

This repository is the standalone Sonic guide.

For `uHOME` contract details, treat `uHOME-server` as the canonical owner.
This guide is about Sonic-owned release, staging, and deployment surfaces.

Use it for:

- release artifacts
- signature and readiness checks
- seeded catalog plus local user overlay rules
- editable install entrypoints for operators
- current-machine bootstrap evidence
- open-box `DESTROY`/`RESTORE` reinstall proof

See also:

- `docs/howto/quickstart.md`
- `docs/howto/build-usb.md`
- `docs/howto/dry-run.md`
- `docs/integration-spec.md`

## Current Setup Path

Sonic is currently packaged for editable installation from the repo root.

Operator entrypoints are defined in:

- `pyproject.toml`
- `installers/setup/install-sonic-editable.sh`

Installed commands:

- `sonic`
- `sonic-api`
- `sonic-mcp`

This setup mode is intentional. Sonic still depends on tracked repo assets such
as `config/`, `datasets/`, `distribution/`, and `scripts/`, so editable install
is the honest supported path today.
