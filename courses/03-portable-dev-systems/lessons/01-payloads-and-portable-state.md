# Lesson 01 - Payloads And Portable State

Portable Sonic work starts with one core distinction:

1. tracked repo assets
2. local runtime artifacts

Tracked assets live under:

- `config/`
- `distribution/`
- `datasets/`
- `vault/`

Local runtime artifacts live under:

- `memory/sonic/artifacts/`
- `memory/sonic/logs/`
- generated manifests and device DBs

This separation matters because portable systems are assembled from tracked
definitions plus machine-local staged payloads.

Key habit:

- keep templates and definitions in the repo
- keep downloaded media and generated state in `memory/sonic/`

That makes Sonic teachable, auditable, and safer to reuse across machines.
