# Contributing to Sonic

Sonic is the deployment and hardware-bootstrap repo in the wider repo family.

Use this repository when the work belongs to:

- deployment planning
- manifest generation and verification
- USB and image provisioning
- Sonic-owned UI, API, CLI, and hardware bootstrap surfaces

Do not use this repository as the source of truth for external runtime
contracts that belong elsewhere, especially `uHOME-server`.

## Before You Open A Change

- keep standalone docs and examples rooted in this repository
- document breaking behavior in `README.md` and the relevant files under `docs/`
- preserve the current repo boundary between `uDOS`, `uDOS-sonic`, and
  `uHOME-server`
- prefer small, reviewable changes over broad speculative edits

## Public Governance

- participation rules: [CODE_OF_CONDUCT.md](/Users/fredbook/Code/uDOS-sonic/CODE_OF_CONDUCT.md)
- contributor record: [CONTRIBUTORS.md](/Users/fredbook/Code/uDOS-sonic/CONTRIBUTORS.md)
- legal summary: [LEGAL.md](/Users/fredbook/Code/uDOS-sonic/LEGAL.md)

## Local Development Lane

Sonic follows the same broad `@dev` and binder-driven working model used across
the repo family, but this public repository remains the curated output surface.

In practice:

- local experiments, scratch notes, binder state, and review staging should stay
  outside the distributable repo content
- those local dev artifacts are gitignored by default
- public repo changes should be the reviewed outputs of bounded work, not the
  raw workspace trail
- only approved contributors should promote changes into the public Sonic repo

## Notes

- Sonic currently installs as an editable repo toolchain through
  `installers/setup/install-sonic-editable.sh`
- runtime state under `memory/sonic/` is local operational state, not canonical
  tracked source
