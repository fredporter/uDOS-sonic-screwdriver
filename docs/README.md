# Sonic Docs

This directory is the current reference surface for `sonic-screwdriver`.

## uDOS family doc layout (sibling checkout)

When you also have **`uDOS-dev`** cloned (same parent folder is typical), open
**`docs/family-documentation-layout.md`** in that repo for cross-repo rules:
what belongs in public **`docs/`**, **`@dev/`**, and **`wiki/`**. **Full index**
(reading order for host, Wizard, Sonic, first-run, health): **`uDOS-dev/docs/family-operator-organisation-map.md`**.

**Operator journey (Wizard-led, GUI-first, Sonic return path, device DB):**
**`uDOS-dev/docs/family-first-run-operator-flow.md`**.

**Offline-first:** Sonic aligns with **uDOS-host** on **prefetch / stage** while
online so **`~/.udos/library/`** and LAN installs survive **grid-down** — see
**`uDOS-dev/docs/udos-host-platform-posture.md`** § **Offline-first survival posture**.

Install and distribution topology (paths, `~/.udos/`, Sonic/Ventoy vs host):
**`uDOS-dev/docs/foundation-distribution.md`**. **OS naming:** **`uDOS-dev/docs/udos-host-platform-posture.md`**.

## Current v2 Docs

- [sonic-tui-charter.md](sonic-tui-charter.md) — **TUI-only utility boundary** (browser GUI out of scope; aligns with uDOS ThinUI)
- [architecture.md](architecture.md)
- [boundary.md](boundary.md)
- [getting-started.md](getting-started.md)
- [structure-policy.md](structure-policy.md)
- [UDOS_V2_ALIGNMENT.md](UDOS_V2_ALIGNMENT.md)
- [REPO_BOUNDARY.md](REPO_BOUNDARY.md)
- [REPO_FAMILY.md](REPO_FAMILY.md)
- [DEPLOYMENT_MODEL.md](DEPLOYMENT_MODEL.md)
- [MACHINE_PROFILES.md](MACHINE_PROFILES.md)
- [UBUNTU_VENTOY_SONIC_HANDOFF.md](UBUNTU_VENTOY_SONIC_HANDOFF.md)

## Legal And Public Positioning

- [../ABOUT.md](../ABOUT.md)
- [../LEGAL.md](../LEGAL.md)
- [../DISCLAIMER.md](../DISCLAIMER.md)
- [../TERMS.md](../TERMS.md)

## Archived v1 Reference

Historical material is retained under [`v1/`](v1/), including earlier how-to
guides, specs, and migration notes that still provide implementation context.
