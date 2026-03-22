# Lesson 01 - Extension Model and Ownership Boundaries

Status: Active

## Why This Lesson Exists

Extension work fails when ownership boundaries are unclear. This lesson maps
what can be extended safely and what should remain stable core behavior.

## Extension Point Taxonomy

- service extension points add behavior behind documented contracts
- packaging extension points reshape artifacts, metadata, or install surfaces
- installer extension points prepare environment-specific handoff logic
- documentation extension points explain capability and compatibility deltas

Every extension proposal should name which of these lanes it touches and which
lanes remain unchanged.

## Ownership Rules

- do not move canonical ownership out of Sonic just to make an extension easier
- prefer additive hooks over shadowing an existing build or service path
- document non-goals so reviewers can reject accidental boundary drift
- require contract checks before merging any extension that changes inputs,
  outputs, or lifecycle ordering

## Anti-Patterns

- undocumented overrides of core package behavior
- extension code that reaches across repo boundaries for private state
- customization flags that silently change default release behavior
- “temporary” compatibility breaks without a declared migration path

## Hands-On

- classify three candidate extension ideas by ownership boundary
- write one proposal with explicit goals, non-goals, and rollback path
- list the checks needed to prove the extension remains boundary-safe

## Recommended Outputs

- `extension-boundary-matrix.md`
- `extension-proposal.md`
