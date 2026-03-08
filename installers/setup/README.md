# Sonic Setup

`installers/setup/` contains repo-local setup helpers for installing Sonic's
editable operator entrypoints.

Current setup path:

- `installers/setup/install-sonic-editable.sh`

That script installs:

- `sonic`
- `sonic-api`
- `sonic-mcp`

It also upgrades the local packaging toolchain first so editable install works
from a clean virtual environment that may still have an older `pip`.

The install mode is intentionally editable so the entrypoints continue to use
the repo's tracked `config/`, `datasets/`, `distribution/`, and `scripts/`
assets rather than pretending Sonic is a self-contained wheel.
