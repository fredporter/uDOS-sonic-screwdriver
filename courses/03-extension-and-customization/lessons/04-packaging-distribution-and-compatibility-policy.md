# Lesson 04 - Packaging, Distribution, and Compatibility Policy

Status: Active

## Why This Lesson Exists

Good extension code still fails adoption if packaging and compatibility promises
are vague. This lesson sets expectations for versioning and distribution.

## Packaging Rules

- package names, install locations, and runtime entrypoints must stay explicit
- extension-facing artifact changes need an upgrade note, not just a version bump
- distribution metadata should tell operators which base surfaces are required

## Compatibility Policy Frame

- define which inputs, outputs, and commands are stable
- tie versioning policy to user-visible compatibility, not only internal code
- announce deprecations with a stated removal window
- provide migration notes whenever an extension-facing surface changes

## Distribution Notes

- include install and rollback instructions with distributed artifacts
- note environment prerequisites that affect extension behavior
- publish compatibility statements beside the package, not only in source docs

## Hands-On

- write a compatibility policy draft for one extension
- create a release note skeleton with upgrade notes
- define a deprecation timeline for a hypothetical change

## Recommended Outputs

- `compatibility-policy.md`
- `extension-release-notes-template.md`
