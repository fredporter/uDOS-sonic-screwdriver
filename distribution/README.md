# Sonic Distribution

`distribution/` holds tracked release descriptors, packaging metadata, launcher
artifacts, and small distributable manifests that define how Sonic artifacts
are assembled.

Large generated outputs and downloaded media do not belong here. Put those
under `memory/sonic/artifacts/`.

Key subdirectories:
- `distribution/launchers/` contains launcher source assets staged onto target systems.
- `distribution/installers/` contains standalone installer descriptors for USB and bundle lanes.

Operator setup helpers live outside this tree under `installers/setup/` because
they install repo-local entrypoints rather than distribution payloads.
