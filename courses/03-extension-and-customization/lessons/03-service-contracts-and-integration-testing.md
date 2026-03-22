# Lesson 03 - Service Contracts and Integration Testing

Status: Active

## Why This Lesson Exists

Extensions are only safe if contracts remain explicit and testable. This lesson
focuses on test strategy for extension behavior at service boundaries.

## Contract-First Testing

Write extension tests from the service contract outward:

- start with the request and response contract
- define fixture inputs that represent real extension scenarios
- assert stable behavior before asserting implementation detail
- keep diagnostics rich enough to explain rollback decisions

## Suggested Test Matrix

- base behavior without the extension enabled
- expected behavior with the extension enabled
- invalid input or contract mismatch handling
- compatibility checks across supported versions or package shapes

## Evidence Capture

- record the contract version under test
- keep sample payloads or fixture manifests
- save error output needed to diagnose boundary regressions
- note whether a failed test requires rollback, patch, or migration work

## Hands-On

- define one contract test matrix for an extension scenario
- write a minimal integration test plan
- map likely failures to rollback and repair actions

## Recommended Outputs

- `extension-test-matrix.md`
- `integration-test-plan.md`
