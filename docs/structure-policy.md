# uDOS-sonic-screwdriver Structure Policy

`uDOS-sonic-screwdriver` is a packaging and deployment-specialized repo with a broader public structure than a minimal package repo.

## Canonical Public Roots

These roots are part of the intended public structure for Sonic:

- `apps/`
- `build/`
- `config/`
- `core/`
- `courses/`
- `datasets/`
- `distribution/`
- `docs/`
- `examples/`
- `installers/`
- `library/`
- `memory/`
- `modules/`
- `payloads/`
- `scripts/`
- `services/`
- `tests/`
- `ui/`
- `vault/`
- `wiki/`

## Why This Repo Is Wider

Sonic owns:

- deployment planning and apply tooling
- package and installer metadata
- operator-facing validation surfaces
- educational and example material for deployment workflows

That means `config/`, `examples/`, and `tests/` are legitimate public roots here, not drift.

## Boundary Rule

The wider structure does not change ownership boundaries.

Sonic still does not own:

- canonical runtime semantics
- `uHOME-server` contract ownership
- `uDOS-wizard` provider or network ownership

Use this policy when evaluating Sonic in family structure sweeps.
