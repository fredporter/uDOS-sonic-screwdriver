# Tests

`tests/` is the current validation lane for `uDOS-sonic-screwdriver`.

Current coverage includes:

- installable CLI entrypoints
- packaging setup and editable install expectations
- deployment planner and runtime service helpers
- Linux smoke workflow path references
- lightweight HTTP API behavior

Phase 1 rule:

- keep tests focused on Sonic-owned deployment and packaging behavior
- do not re-own `uHOME-server` runtime behavior here
