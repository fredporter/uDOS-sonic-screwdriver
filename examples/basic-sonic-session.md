# Basic Sonic Session

This is the smallest v2-local walkthrough for validating
`uDOS-sonic-screwdriver` as a deployment and packaging surface.

## Validate The Repo

```bash
scripts/run-sonic-checks.sh
```

## Install Editable Entrypoints

```bash
.venv/bin/python -m pip install -e .[dev]
```

## Generate A Dry-Run Plan

```bash
.venv/bin/sonic plan \
  --usb-device /dev/sdb \
  --dry-run \
  --out memory/sonic/sonic-manifest.json
```

Expected outcome:

- the validation suite passes
- Sonic stays inside deployment and packaging ownership
- `uHOME-server` remains the persistent runtime owner
- `uDOS-core` remains the semantic owner
