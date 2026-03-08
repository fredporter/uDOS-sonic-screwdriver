# Lesson 02 - Rescue And Recovery

Sonic is not only an installer. It is also a rescue lane.

Typical rescue tasks include:

- inspect a failed or half-finished deployment
- verify layout and boot assets
- collect logs and device evidence
- reuse staged payloads without rebuilding everything

Important scripts:

- `scripts/collect-logs.sh`
- `scripts/verify-usb-layout.sh`
- `scripts/tinycore-bootlog.sh`

Educational rule:

- gather evidence first
- repair second
- rewrite only after you understand the current state

That is the same safety habit Sonic teaches for planning and apply workflows.
