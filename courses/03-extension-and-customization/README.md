# Sonic Course 03 - Extension and Customization

Status: Active

Course 03 teaches how to extend Sonic safely without breaking repository
boundaries, API contracts, or release workflows.

The course is written as an operator-to-maintainer transition lane. It focuses
on bounded extension work: adding hooks, services, and packages without
silently changing ownership or compatibility guarantees.

## Purpose

- introduce extension points in services and packaging surfaces
- teach safe customization patterns with compatibility discipline
- provide a path from operator workflows to contributor workflows
- prepare maintainers for sustainable extension lifecycle management

## Entry Conditions

Complete these first:
- [Course 01 - Universal Sonic Screwdriver](../01-sonic-screwdriver/README.md)
- [Course 02 - Deployment Patterns](../02-deployment-patterns/README.md)

Then review:
- [Overview](overview.md)
- [Objectives](objectives.md)
- [Prerequisites](prerequisites.md)

## Lessons

1. [Lesson 01 - Extension Model and Ownership Boundaries](lessons/01-extension-model-and-ownership-boundaries.md)
2. [Lesson 02 - Custom Build Engines and Package Hooks](lessons/02-custom-build-engines-and-package-hooks.md)
3. [Lesson 03 - Service Contracts and Integration Testing](lessons/03-service-contracts-and-integration-testing.md)
4. [Lesson 04 - Packaging, Distribution, and Compatibility Policy](lessons/04-packaging-distribution-and-compatibility-policy.md)

## Project

- [Project Overview](project/README.md)
- [Project Phases](project/PHASES.md)

## Completion Criteria

By the end of this course, the learner should be able to:

- identify safe extension boundaries in Sonic service surfaces
- implement a small customization without API regressions
- design integration tests for extension behavior
- package and document extension compatibility expectations
