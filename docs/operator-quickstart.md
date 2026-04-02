# Sonic — operator quickstart

From a fresh clone, with **Python 3**, **Node.js**, and **npm** installed:

```bash
./sonic-open
```

Same thing:

- `bash scripts/sonic-open.sh`
- macOS Finder: double-click `scripts/sonic-open.command`

The first successful run creates **`~/.udos/venv/sonic-screwdriver`**, installs Python and UI dependencies, starts the API and UI, waits for health checks, and opens **http://127.0.0.1:5173** when a browser is available.

That URL is a **browser UI** (Svelte + Vite), not a terminal (TUI) app. The page talks to the local API via **`/api`** (proxied to port **8991**). If you see a dark page with almost no text, ensure JavaScript is on and the API is up; you should at least see a header, connection status, and explanatory copy. A **Bubble Tea / pure-TUI** Sonic is not implemented in this repo today; the supported “in terminal” path is the **`sonic`** starter CLI.

Later runs skip `pip` / `npm` unless you pass **`--repair`** (or remove **`.run/sonic-setup-complete`**). Use **`--no-open`** on headless systems.

After that, add **`~/.udos/venv/sonic-screwdriver/bin`** to your `PATH` if you want the **`sonic`** CLI, or keep using **`./sonic-open`**.

Developers: **`bash scripts/run-sonic-checks.sh`** and **`bash scripts/first-run-preflight.sh`** remain the deeper validation paths.
