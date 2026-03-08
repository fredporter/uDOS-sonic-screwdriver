# Sonic Dev Workflow

Status: active how-to

Sonic development follows a local `@dev` and binder-style workflow, while the
repository itself stays a curated public surface.

## Principles

- do active exploration locally first
- keep scratch notes, experiments, and binder state out of tracked repo content
- promote bounded, reviewable outputs into the repo
- do not use this repo as the source of truth for `uHOME-server` contracts

## Local-Only Artifacts

Examples of local-only dev materials:

- `@dev/`
- `binders/`
- `.local-extension/`
- `review-staging/`
- `workspace-state/`

These are gitignored by default in Sonic.

## Public Repo Outputs

Changes promoted here should usually be one of:

- runtime code under `apps/`, `services/`, `scripts/`, or `config/`
- learner-facing material under `wiki/`, `courses/`, `vault/`, and `docs/`
- tracked distribution descriptors under `distribution/`

## Typical Flow

1. define a bounded Sonic objective locally
2. do active dev work in the local workspace lane
3. compile the result into reviewed repo-ready changes
4. update docs and tests together
5. promote only the public result into this repository
