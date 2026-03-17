# uDOS-sonic-screwdriver Boundary

## Owns

- bootstrap and install flows
- packaging and update surfaces
- managed environment provisioning
- deployment and machine-profile guidance
- orchestration of `uDOS-ubuntu` profile registration and `uDOS-ventoy` template consumption

## Does Not Own

- canonical runtime semantics
- public provider and MCP ownership
- persistent local-service ownership
- private OMD product behavior
- base image composition ownership (owned by `uDOS-ubuntu`)
- Ventoy template policy ownership (owned by `uDOS-ventoy`)

## Platform Rule

- Linux is required for full stick initialization and creation flows
- macOS is maintenance-only for profile metadata, template refresh, and theme switching

See also:

- `REPO_BOUNDARY.md`
- `UDOS_V2_ALIGNMENT.md`
- `structure-policy.md`
