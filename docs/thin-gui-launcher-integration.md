# Sonic Thin GUI Launcher Integration

This document defines the v2.1 Round C integration path from Sonic launcher lanes into ThinUI.

## Purpose

Enable Sonic utility/kiosk launch surfaces to invoke ThinUI using a stable launcher contract.

## Referenced Contract

- ../../uDOS-thinui/contracts/sonic-thin-gui.md

## Launch Payload Shape

```json
{
  "runtime": "thinui",
  "entryView": "utility-panel",
  "mode": "windowed",
  "themeId": "thinui-c64",
  "title": "sonic utility",
  "subtitle": "device diagnostics"
}
```

## Integration Sequence

1. Sonic launcher builds payload from manifest/profile context.
2. ThinUI runtime hydrates state and resolves view + theme adapter.
3. Themed frame renders locally.
4. Events return through ThinUI event channel to Sonic caller.

## Validation

```bash
bash scripts/run-sonic-checks.sh
bash scripts/demo-thinui-launch.sh
```

## Boundary Rules

- Sonic hosts launch/orchestration only.
- ThinUI owns render loop behavior.
- Themes own visual tokens and adapter output.
- Core owns semantic state and command authority.

## Demo Entry

- `scripts/demo-thinui-launch.sh`
- theme target: `thinui-nes-sonic`
