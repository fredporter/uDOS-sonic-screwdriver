# uDOS-sonic-screwdriver Architecture

uDOS-sonic-screwdriver owns packaging, bootstrap, install, update, and managed environment tooling for the public family.

## Main Areas

- `apps/`, `services/`, and `core/` support provisioning and operator tooling
- `distribution/`, `installers/`, and `payloads/` hold release and install surfaces
- `modules/` marks extension and boundary lanes
- `docs/` explains deployment ownership and family alignment
- `scripts/run-sonic-checks.sh` is the activation validation entrypoint
- `sonic init/add/update/theme` commands integrate `uDOS-ventoy` templates and `uDOS-ubuntu` profile metadata

## Design Rule

Sonic is a deployment and managed-environment owner, not a semantic runtime owner.

See also:

- `ARCHITECTURE.md`
- `DEPLOYMENT_MODEL.md`
- `REPO_FAMILY.md`
- `structure-policy.md`
