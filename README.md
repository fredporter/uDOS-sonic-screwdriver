# sonic-screwdriver

Sonic Screwdriver is the deployment layer of the uDOS v2 architecture.

It is responsible for:

- hardware-aware planning
- USB and image deployment
- manifest generation and verification
- device catalog and compatibility guidance
- portable provisioning and rescue workflows

It is not the canonical owner of the `uHOME` runtime contract.

## Repo Family Boundary

The current repo split is:

- `uDOS-core` = deterministic runtime contracts and execution semantics
- `uDOS-shell` = interactive shell and workspace interaction surfaces
- `uDOS-wizard` = network, provider, MCP, and assist surfaces
- `sonic-screwdriver` = deployment, provisioning, hardware bootstrap
- `uHOME-server` = canonical `uHOME` runtime, bundle, preflight, and install-plan contracts

For `uHOME`-specific contracts, the source of truth is the sibling
`uHOME-server` repository, not this one.

## What Sonic Owns

Sonic owns the deployment lane that takes a reviewed profile and applies it to
real hardware:

`take profile -> generate manifest -> verify -> stage payloads -> apply to device`

Current active surfaces in this repo:

- USB plan and run CLI
- standalone HTTP API
- MCP facade over the same service layer
- browser UI for planning and catalog inspection
- device catalog and manifest validation
- explicit live/install/recovery product docs and demo surfaces

## What Sonic Does Not Own

Sonic does not own:

- the long-running `uHOME` runtime
- `uHOME` bundle/preflight/install-plan source of truth
- Wizard-managed beacon, Home Assistant, or network control surfaces

This repo no longer carries local `uHOME` bundle contract code. Use the sibling
`uHOME-server` repo directly for `uHOME` bundle, preflight, and install-plan
work.

## First-Run Preflight (Any OS)

Run the repo preflight entrypoint first:

```bash
bash scripts/first-run-preflight.sh
```

This command performs four checks:

- repo validation (`scripts/run-sonic-checks.sh`)
- v2 canonical root structure check
- quickstart probe
  - Linux: CLI `sonic plan --dry-run`
  - macOS/Windows: API health probe (`/api/sonic/health`)
- cross-repo `uHOME` contract conformance probe (when sibling repos exist)
  - `scripts/smoke/uhome-contract-conformance.sh`

## Starter CLI

Sonic now starts from the CLI surface first, then hands off to the browser GUI.

Run the installable starter CLI with:

```bash
sonic
```

Starter commands:

- `help`
- `commands`
- `start`
- `status`
- `test`
- `doctor`
- `exit`

GUI handoff:

```bash
sonic start
```

That bootstraps the local API and browser UI, then opens the Sonic surface on
`http://127.0.0.1:5173`.

One-command macOS/bootstrap launcher:

```bash
bash scripts/first-run-launch.sh
open ./scripts/first-run-launch.command
```

## Quick Start (Linux)

After preflight passes, run the Linux deployment quickstart:

Install editable CLI entrypoints:

```bash
bash installers/setup/install-sonic-editable.sh
```

This repo currently supports editable installation from source, not a
self-contained wheel. That keeps the CLI aligned to the tracked repo assets in
`config/`, `datasets/`, `distribution/`, and `scripts/`.

Generate a plan:

```bash
sonic plan \
  --usb-device /dev/sdb \
  --out memory/sonic/sonic-manifest.json
```

Run a dry-run first:

```bash
sonic plan \
  --usb-device /dev/sdb \
  --dry-run \
  --out memory/sonic/sonic-manifest.json

bash scripts/sonic-stick.sh \
  --manifest memory/sonic/sonic-manifest.json \
  --dry-run
```

Apply the manifest:

```bash
bash scripts/sonic-stick.sh --manifest memory/sonic/sonic-manifest.json
```

Serve the local API directly:

```bash
sonic-api
```

Serve the MCP facade directly:

```bash
sonic-mcp
```

Run the Linux smoke workflow:

```bash
bash scripts/smoke/linux-runtime-smoke.sh
```

## Ubuntu And Ventoy Integration (v2.0.6 Round B)

Sonic now exposes an explicit integration lane for the `uDOS-ubuntu` profile
and `uDOS-ventoy` boot templates.

Initialize a stick workspace from `uDOS-ventoy` templates:

```bash
sonic init \
  --stick-root memory/sonic/artifacts/sonic-stick \
  --theme modern \
  --profile udos-ubuntu
```

Register image metadata and checksum assumptions from the profile manifest:

```bash
sonic add udos-ubuntu \
  --stick-root memory/sonic/artifacts/sonic-stick \
  --image-name udos-ubuntu-22.04.iso \
  --checksum <sha256>
```

Refresh boot templates and profile metadata without deleting user images/config:

```bash
sonic update \
  --stick-root memory/sonic/artifacts/sonic-stick \
  --profile udos-ubuntu
```

Switch the active boot theme:

```bash
sonic theme retro --stick-root memory/sonic/artifacts/sonic-stick
```

OS boundary:

- `sonic init` is Linux-only (full creation path)
- `sonic add`, `sonic update`, and `sonic theme` are Linux/macOS maintenance commands
- Windows remains unsupported for Sonic build operations

Run the Ubuntu/Ventoy integration smoke workflow (Linux, sibling repos required):

```bash
bash scripts/smoke/ubuntu-ventoy-integration-smoke.sh
```

## Learning Surfaces

There are now three ways to enter this repo:

- student-facing wiki: [wiki/Home.md](wiki/Home.md)
- Sonic course: [courses/README.md](courses/README.md)
- reference docs: [docs/README.md](docs/README.md)

Use the wiki for orientation, the Sonic course for the deployment lane, and
`docs/` for implementation details and active contracts.

## Activation

The v2 repo activation path is documented in `docs/activation.md`.

Run the current repo validation entrypoint with:

```bash
scripts/run-sonic-checks.sh
```

Run the current ThinUI NES launcher demo with:

```bash
bash scripts/demo-thinui-launch.sh
```

Run the current live/install/recovery product demo with:

```bash
bash scripts/demo-live-install-recovery.sh
```

For broader platform learning, use the wider uDOS v2 family docs instead of
duplicating the same pathway structure in Sonic. Start with `uDOS-docs`,
`uDOS-core`, and `uDOS-wizard`.

If you prefer repo-local execution without installing entrypoints, the direct
CLI path remains `python3 apps/sonic-cli/cli.py`, and the starter launch path is
`python3 apps/sonic-cli/cli.py start`.

## Current Runtime Layout

The active runtime now aligns to the public repo structure:

- `apps/sonic-cli/` = operator CLI
- `apps/sonic-ui/` = browser UI
- `services/` = planner, manifest, API, MCP, and runtime service layer
- `installers/setup/` = editable install helpers
- `modules/` = install-domain architecture surfaces
- `vault/` = tracked templates, manifests, and deployment notes for learners
- `scripts/` = Linux-side execution steps
- `config/` = layout and manifest defaults
- `distribution/` = tracked packaging descriptors and launch assets
- `memory/sonic/` = local runtime state and generated artifacts
- `datasets/` = device catalog sources
- `tests/` = verification coverage

The earlier structure review is kept as a baseline record in
[docs/v1/sonic-structure-assessment-2026-03-08.md](docs/v1/sonic-structure-assessment-2026-03-08.md).

## Current Default Deployment Story

The default standalone profile currently produces a dual-boot disk with:

- a Linux-side `uHOME` surface and handoff path
- a Windows 10 gaming surface
- controller-first launch metadata for both sides

That is one active deployment profile, not the whole identity of the repo.
The broader Sonic role is deployment infrastructure and portable provisioning.

## Key Docs

- docs index: [docs/README.md](docs/README.md)
- v2 architecture: [docs/architecture.md](docs/architecture.md)
- v2 boundary: [docs/boundary.md](docs/boundary.md)
- live/install/recovery product: [docs/LIVE_INSTALL_RECOVERY_PRODUCT.md](docs/LIVE_INSTALL_RECOVERY_PRODUCT.md)
- Ubuntu/Ventoy/Sonic handoff: [docs/UBUNTU_VENTOY_SONIC_HANDOFF.md](docs/UBUNTU_VENTOY_SONIC_HANDOFF.md)
- release policy: [docs/release-policy.md](docs/release-policy.md)
- archived provisioning contract: [docs/v1/specs/sonic-screwdriver.md](docs/v1/specs/sonic-screwdriver.md)
- archived integration boundary: [docs/v1/integration-spec.md](docs/v1/integration-spec.md)
- archived structure assessment: [docs/v1/sonic-structure-assessment-2026-03-08.md](docs/v1/sonic-structure-assessment-2026-03-08.md)
- setup helper: [installers/setup/README.md](installers/setup/README.md)

## Project Governance

- license: [LICENSE](LICENSE)
- legal summary: [LEGAL.md](LEGAL.md)
- contributing: [CONTRIBUTING.md](CONTRIBUTING.md)
- contributors: [CONTRIBUTORS.md](CONTRIBUTORS.md)
- conduct: [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)

## Development Lane

Sonic uses a local `@dev` / binder-style development lane for in-progress work,
but this repository remains the curated public output surface. Local binder
state, scratch material, and review staging are ignored by default so dev-mode
work does not leak into tracked repo content.

## OS Support

- Supported: Linux
- Unsupported for build operations: macOS, Windows

## Safety

- destructive steps require explicit execution
- always verify the target block device
- run dry-run before any real apply
- treat `memory/sonic/` as local runtime state, not canonical tracked source
