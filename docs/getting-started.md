# uDOS-sonic-screwdriver Getting Started

1. Read `README.md` for the public role of Sonic.
2. Review `docs/boundary.md` and `docs/architecture.md`.
3. Review `docs/activation.md`.
4. Run `scripts/first-run-preflight.sh`.
5. Use the repo-specific test and release workflows for packaging validation.
6. Promote public changes through `develop -> main` in line with the family workflow.
7. For v2.0.6 Ubuntu/Ventoy wiring, use `sonic init`, `sonic add`, `sonic update`, and `sonic theme`.
8. On Linux, run `scripts/smoke/ubuntu-ventoy-integration-smoke.sh` to verify end-to-end template/profile wiring.

For deeper deployment material, continue with:

- `DEPLOYMENT_MODEL.md`
- `MACHINE_PROFILES.md`
- `v1/howto/quickstart.md`
