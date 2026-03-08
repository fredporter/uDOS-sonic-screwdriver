# Quickstart (Linux)

Status: active how-to

Install editable Sonic entrypoints from the repo root:

```bash
bash installers/setup/install-sonic-editable.sh
```

Generate a plan:

```bash
sonic plan \
  --usb-device /dev/sdb \
  --out memory/sonic/sonic-manifest.json
```

Safe first run:

```bash
sonic plan \
  --usb-device /dev/sdb \
  --dry-run \
  --out memory/sonic/sonic-manifest.json

bash scripts/sonic-stick.sh \
  --manifest memory/sonic/sonic-manifest.json \
  --dry-run
```

Serve Sonic locally:

```bash
sonic-api
sonic-mcp
```

Linux release-gate smoke:

```bash
bash scripts/smoke/linux-runtime-smoke.sh
```

Repo-local fallback without installation:

```bash
python3 apps/sonic-cli/cli.py plan --usb-device /dev/sdb --dry-run
```
