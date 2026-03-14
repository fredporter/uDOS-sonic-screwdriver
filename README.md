# uDOS-sonic-screwdriver

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

- `uDOS` = shared architecture language, Wizard integration, family coordination
- `uDOS-sonic` = deployment, provisioning, hardware bootstrap
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

## What Sonic Does Not Own

Sonic does not own:

- the long-running `uHOME` runtime
- `uHOME` bundle/preflight/install-plan source of truth
- Wizard-managed beacon, Home Assistant, or network control surfaces

This repo no longer carries local `uHOME` bundle contract code. Use the sibling
`uHOME-server` repo directly for `uHOME` bundle, preflight, and install-plan
work.

## Quick Start (Linux)

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

Serve the local API:

```bash
sonic-api
```

Serve the MCP facade:

```bash
sonic-mcp
```

Run the Linux smoke workflow:

```bash
bash scripts/smoke/linux-runtime-smoke.sh
```

## Learning Surfaces

There are now three ways to enter this repo:

- student-facing wiki: [wiki/Home.md](<local-project-root>/uDOS-sonic/wiki/Home.md)
- Sonic course: [courses/README.md](<local-project-root>/uDOS-sonic/courses/README.md)
- reference docs: [docs/README.md](<local-project-root>/uDOS-sonic/docs/README.md)

Use the wiki for orientation, the Sonic course for the deployment lane, and
`docs/` for implementation details and active contracts.

For broader platform learning, use the sibling `uDOS` course ladder instead of
duplicating the same pathway structure in Sonic:

- [uDOS Courses README](<local-project-root>/uDOS/courses/README.md)
- [uDOS Education Pathways](<local-project-root>/uDOS/wiki/Education-Pathways.md)

If you prefer repo-local execution without installing entrypoints, the direct
CLI path remains `python3 apps/sonic-cli/cli.py`.

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
[docs/sonic-structure-assessment-2026-03-08.md](<local-project-root>/uDOS-sonic/docs/sonic-structure-assessment-2026-03-08.md).

## Current Default Deployment Story

The default standalone profile currently produces a dual-boot disk with:

- a Linux-side `uHOME` surface and handoff path
- a Windows 10 gaming surface
- controller-first launch metadata for both sides

That is one active deployment profile, not the whole identity of the repo.
The broader Sonic role is deployment infrastructure and portable provisioning.

## Key Docs

- provisioning contract: [docs/specs/sonic-screwdriver.md](<local-project-root>/uDOS-sonic/docs/specs/sonic-screwdriver.md)
- integration boundary: [docs/integration-spec.md](<local-project-root>/uDOS-sonic/docs/integration-spec.md)
- structure assessment: [docs/sonic-structure-assessment-2026-03-08.md](<local-project-root>/uDOS-sonic/docs/sonic-structure-assessment-2026-03-08.md)
- USB build how-to: [docs/howto/build-usb.md](<local-project-root>/uDOS-sonic/docs/howto/build-usb.md)
- dry-run how-to: [docs/howto/dry-run.md](<local-project-root>/uDOS-sonic/docs/howto/dry-run.md)
- quickstart: [docs/howto/quickstart.md](<local-project-root>/uDOS-sonic/docs/howto/quickstart.md)
- setup helper: [installers/setup/README.md](<local-project-root>/uDOS-sonic/installers/setup/README.md)

## Project Governance

- license: [LICENSE](<local-project-root>/uDOS-sonic/LICENSE)
- legal summary: [LEGAL.md](<local-project-root>/uDOS-sonic/LEGAL.md)
- contributing: [CONTRIBUTING.md](<local-project-root>/uDOS-sonic/CONTRIBUTING.md)
- contributors: [CONTRIBUTORS.md](<local-project-root>/uDOS-sonic/CONTRIBUTORS.md)
- conduct: [CODE_OF_CONDUCT.md](<local-project-root>/uDOS-sonic/CODE_OF_CONDUCT.md)

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
