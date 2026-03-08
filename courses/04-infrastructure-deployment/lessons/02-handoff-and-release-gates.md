# Lesson 02 - Handoff And Release Gates

Infrastructure deployment is not complete when a manifest is written.

Sonic teaches a release gate model:

1. plan
2. inspect
3. dry-run
4. execute on Linux
5. hand off to the owning runtime

Current release-gate smoke:

- `bash scripts/smoke/linux-runtime-smoke.sh`

Current handoff boundaries:

- Sonic plans and stages the deployment
- Wizard-owned surfaces take over network-aware control
- `uHOME-server` remains the owner of `uHOME` runtime contracts

This is how Sonic stays useful without turning into an unbounded control-plane
repo.
