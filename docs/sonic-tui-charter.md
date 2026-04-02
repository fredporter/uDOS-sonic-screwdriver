# Sonic Screwdriver — TUI Charter

**Canonical pack (Classic Modern + ThinUI + Sonic alignment):** when you have **`uDOS-docs`** checked out, see **`docs/classic-modern-mvp-0.1/`** (README + `docs/sonic-tui-charter.md` there). This file is the same charter, kept in-repo so Sonic implementation work cannot drift without touching the boundary.

---

## One-line charter

sonic-screwdriver is a terminal-only fixer/installer/setup tool; it must never require or open a browser for its core job.

---

## Scope

### In

- install
- repair
- environment setup
- health checks
- guided fixes
- clear logs + next steps

### Out

- browser GUI
- visual dashboards
- sonic-db GUI

These belong in uDOS (ThinUI or other surfaces)

---

## Stack

Preferred:

- Go + Bubble Tea + Lip Gloss

Reason:

- single binary
- fast
- interactive
- SSH-safe

---

## User flows

### 1. First run

Input:

- `sonic`

Output:

- setup complete
- clear summary
- exit success

### 2. Repair

Input:

- broken env

Output:

- detected issue
- fixed or instructions

### 3. Doctor

Input:

- `sonic doctor`

Output:

- system health summary

---

## Failure handling

- human-readable messages
- no stack traces by default
- always provide next action

---

## Deprecation

- remove browser-based UI from this repo
- move UI to uDOS layer if needed

---

## Acceptance criteria

- no browser launched
- works over SSH
- no GUI dependency
- single command entry
- deterministic output

---

## Principle

Sonic is a tool, not a product surface.
