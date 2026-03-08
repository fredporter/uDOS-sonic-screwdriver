# uHOME Bundle Module

This module exists as a boundary marker, not as a local implementation root.

Canonical ownership lives in `uHOME-server`.

Sonic may:

- reference bundle descriptors
- stage launch assets
- hand off deployment outputs

Sonic does not locally own:

- bundle schema
- preflight rules
- staged install-plan semantics

Use this module page to explain the boundary, not to reintroduce duplicate
contract code into `uDOS-sonic`.
