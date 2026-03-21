#!/usr/bin/env bash

set -eu

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
THINUI_DEMO="$REPO_ROOT/../uDOS-thinui/scripts/demo-thinui.js"

cat <<'EOF'
{
  "runtime": "thinui",
  "entryView": "boot-loader",
  "mode": "windowed",
  "themeId": "thinui-nes-sonic",
  "title": "sonic utility",
  "subtitle": "device diagnostics"
}
EOF
echo ""

if command -v node >/dev/null 2>&1 && [ -f "$THINUI_DEMO" ]; then
  echo "[sonic-screwdriver] Launching ThinUI NES demo"
  node "$THINUI_DEMO" --theme thinui-nes-sonic --view boot-loader --title "sonic utility" --subtitle "device diagnostics"
else
  echo "[sonic-screwdriver] ThinUI sibling demo not available; payload emitted only."
fi
