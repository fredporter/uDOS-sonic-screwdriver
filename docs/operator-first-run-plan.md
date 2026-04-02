# Operator first-run plan — simpler setup, launcher, deps, health

## Problem

Today operators must discover **multiple** entrypoints (`first-run-preflight.sh`,
`first-run-launch.sh`, `run-sonic-checks.sh`, venv `PATH`, `sonic` install,
README sections). That is correct for **developers** but too heavy for **users**
who want: *install what I need → prove it works → open Sonic*.

## Goals (what “easy” means)

| Need | Operator expectation |
| --- | --- |
| **First-time setup** | One obvious command from a fresh clone (no prior `pip` / `sonic` on PATH). |
| **Requirement installer** | Script checks **Python 3**, **Node**, **npm**; prints **copy-paste** install lines for their OS when missing; optionally runs safe installs where policy allows. |
| **Launcher** | Same command (or a sibling `open` command) starts **API + UI** and opens the browser when possible. |
| **Health on startup** | Before saying “ready”, hit **API health** and **UI HTTP** (already partially in `scripts/first-run-launch.sh`); show a **short OK / FAIL** summary with log paths on failure. |
| **Repeat runs** | Second and later launches are **fast**: skip reinstall unless `--repair` or version bump. |

Non-goals for this pass: replacing Linux-only USB apply flows; running full `pytest` on every GUI open (keep that under **`sonic test`** / CI).

## What already exists (reuse, don’t rewrite blindly)

- **`scripts/first-run-launch.sh`** — Already: creates/uses **`~/.udos/venv/sonic-screwdriver`**, `pip install -e '.[dev]'`, `npm install` in `apps/sonic-ui`, starts **sonic-api**, **waits on `/api/sonic/health`**, starts **Vite** UI, **waits on UI port**, **opens browser**. This is the core **installer + launcher + health gate**; it is just **not marketed** as the one true path and it **hard-fails** if `node`/`npm` are missing without friendly guidance.
- **`apps/sonic-cli/cli.py`** — **`start`** → delegates to **`scripts/sonic-open.sh`**; **`doctor`** → environment/repo checks — but **`sonic`** must already be on PATH (venv/chicken-and-egg).
- **`scripts/first-run-preflight.sh`** — Valuable for **CI / developers** (pytest, structure, optional sibling smokes); **too heavy** as the default “first open” for casual operators.

## Proposed operator model

### Single entry (names TBD)

1. **Repo root wrapper (recommended)**  
   - Add **`./sonic-open`** (or **`open-sonic.sh`**) at repo root: thin script that only does `exec bash scripts/sonic-open.sh` so users see one file in the clone root.  
   - Implement **`scripts/sonic-open.sh`** as the **canonical** path (can start as a rename + doc of `first-run-launch.sh` behaviour, then evolve).

2. **Phases inside `sonic-open.sh` (ordered, printed in plain language)**  
   - **(1) Requirements** — Check `python3`, `node`, `npm` (and on Linux note for USB). If missing: print **one** OS-specific block (e.g. macOS Homebrew / Ubuntu apt) and exit non-zero with clear “install these, then re-run”.  
   - **(2) First-time install** — If no marker file (e.g. **`.run/sonic-setup-complete`**) or **`--repair`**: venv + `pip install -e '.[dev]'` + `npm install` in UI (same as today). Else skip pip/npm unless lockfile/package.json changed (optional later).  
   - **(3) Start services** — Start API + UI (reuse current PID/log logic from `first-run-launch.sh`).  
   - **(4) Health** — GET health URL + UI URL; print **`Sonic OK — UI … API …`** or **`FAILED — see …log`**.  
   - **(5) Open** — `open` / `xdg-open` UI URL.

3. **After first success**  
   - Write marker + short **`docs/operator-quickstart.md`** with literally **one** command and screenshots/URLs.

4. **`sonic` CLI**  
   - Keep for power users. Document: *“If `sonic` is not found, run `./sonic-open` once; then optionally add venv `bin` to PATH.”*  
   - Optional: `sonic open` alias to same script.

### Health on every startup

- **Always** run the same HTTP checks before printing success (already there; tighten messages).  
- Optional **`--no-open`** for headless / SSH.  
- Optional future: **`sonic status`** reads PID files and re-checks health (partially exists).

### Developer / CI path (unchanged in spirit)

- **`bash scripts/first-run-preflight.sh`** — Remains the **full** gate (tests, structure, siblings).  
- **`bash scripts/run-sonic-checks.sh`** — CI and **`sonic test repo`**.

## Documentation changes (when implemented)

- **`README.md`** — Top: **“Start Sonic (first time)”** → single command + 2-sentence prerequisite (Python + Node). Move preflight to **“Developers”**.  
- **`docs/getting-started.md`** — Align with **main**-only promotion wording; step 1 = **`./sonic-open`** (or chosen name).  
- **`docs/operator-quickstart.md`** (new, short) — Only operator-facing; link from README.

## Rollout phases

| Phase | Deliverable |
| --- | --- |
| **A** | Add **`scripts/sonic-open.sh`** = current `first-run-launch.sh` + friendlier requirement checks + **setup marker** + unified stdout messages. Add repo-root **`sonic-open`**. README “Start here” box. **Done** (includes **`scripts/sonic-open.command`** for macOS Finder). |
| **B** | Wire **`sonic start`** / CLI to call **`sonic-open.sh`** only (one implementation). Deprecate duplicate paths in docs. **Done** (`first-run-launch.sh` is a thin compat wrapper). |
| **C** | **`doctor`** improvements: same requirement checks as `sonic-open` so `sonic doctor` and launcher stay consistent. |
| **D** | Optional: detect outdated venv (hash `pyproject.toml` / `package-lock`) and suggest `--repair`. |

## Acceptance criteria

- New operator with clone + Python + Node installed succeeds with **one** documented command and sees the UI without reading the full README.  
- Missing deps → **one** screen of instructions, no stack trace as the first impression.  
- Failure after start → **explicit** log path and which step failed (deps / pip / npm / API / UI).  
- Developers can still run **preflight** / **pytest** without the operator path running tests on every launch.

## Related

- `scripts/sonic-open.sh` — canonical operator launcher (+ `first-run-launch.sh` compat wrapper)  
- `scripts/first-run-preflight.sh` — deep validation (not default operator path)  
- `uDOS-dev/docs/foundation-distribution.md` — family install order around Sonic
