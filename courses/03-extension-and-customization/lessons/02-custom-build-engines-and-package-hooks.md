# Lesson 02 - Custom Build Engines and Package Hooks

Status: Active

## Why This Lesson Exists

Custom build behavior should be pluggable, testable, and reversible. This
lesson outlines a safe hook model for extending build and packaging steps.

## Hook Lifecycle

Treat hooks as explicit lifecycle steps:

- preflight validation before mutable work begins
- bounded build or packaging customization
- artifact verification after the hook runs
- rollback or cleanup when the hook fails

## Hook Design Rules

- hooks must be idempotent or document why they are single-use
- inputs and outputs must be visible to the base pipeline
- failure handling must stop promotion, not hide partial artifacts
- hooks should prefer composition over replacing the base engine

## Package Hook Checklist

- state trigger conditions
- define success and failure signals
- record produced files and directories
- declare cleanup expectations
- document which compatibility promises remain unchanged

## Hands-On

- draft a custom hook flow for one payload type
- define pass/fail conditions for that hook
- write rollback notes for partial artifact creation

## Recommended Outputs

- `custom-hook-design.md`
- `hook-contract.md`
