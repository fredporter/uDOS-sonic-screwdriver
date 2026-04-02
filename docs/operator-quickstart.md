# Sonic — operator quickstart

From a fresh clone, with **Python 3**, **Node.js**, and **npm** installed:

```bash
./sonic-open
```

Same thing:

- `bash scripts/sonic-open.sh`
- macOS Finder: double-click `scripts/sonic-open.command`

The first successful run creates **`~/.udos/venv/sonic-screwdriver`**, installs Python and UI dependencies, starts the API and UI, waits for health checks, and opens **http://127.0.0.1:5173** when a browser is available.

Later runs skip `pip` / `npm` unless you pass **`--repair`** (or remove **`.run/sonic-setup-complete`**). Use **`--no-open`** on headless systems.

After that, add **`~/.udos/venv/sonic-screwdriver/bin`** to your `PATH` if you want the **`sonic`** CLI, or keep using **`./sonic-open`**.

Developers: **`bash scripts/run-sonic-checks.sh`** and **`bash scripts/first-run-preflight.sh`** remain the deeper validation paths.
