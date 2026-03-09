# uDOS-sonic Development Roadmap v1.6+

**Current Release**: v1.5.5 (2026-03-09)  
**Planning Date**: 2026-03-10  
**Status**: Post-release planning for next development cycle

---

## Overview

v1.5.5 completed the major structural refactor of Sonic into a deployable, education-facing toolkit with clean runtime boundaries and separation from uDOS core and uHOME-server ownership.

v1.6 and beyond focus on refinement, education pathway clarity, and phased reduction of internal technical debt while maintaining API stability and deployment reliability.

---

## v1.6 Objectives (Q2 2026)

### 1. Education Pathway Clarity

**Objective**: Make the learner journey explicit and organized.

**Work**:
- [ ] Convert `docs/01-09` series into structured `courses/01-sonic-screwdriver/` modules
- [ ] Separate reference docs from tutorial flows in `docs/`
- [ ] Create `docs/architecture/` for service boundary documentation
- [ ] Add `courses/02-deployment-patterns/` for advanced operational scenarios
- [ ] Publish `vault/templates/` with example profiles and manifests

**Blockers**: None identified  
**Outputs**: Three structured courses, reduced doc confusion

---

### 2. uHOME Ownership Resolution

**Objective**: Phase down local uHOME compatibility code; clarify boundary with uHOME-server.

**Work**:
- [ ] Document which uHOME modules are compatibility shims vs canonical
- [ ] Create import bridge from `uHOME-server` where available
- [ ] Deprecate local copies not provided externally
- [ ] Update integration guide for uHOME-server dependency
- [ ] Test bundle/preflight/install-plan flow against imported contracts

**Blockers**: Requires uHOME-server release with public imports  
**Outputs**: Clear ownership boundaries, reduced duplication

---

### 3. Vault and Templates Surface

**Objective**: Create a public template and example collection.

**Work**:
- [ ] Populate `vault/templates/` with example device profiles
- [ ] Add `vault/manifests/` with reference deployment manifests
- [ ] Create `vault/deployment-notes/` deployment logs and diagnostics examples
- [ ] Document vault structure and use cases

**Outputs**: Clear template/example library, improved onboarding

---

### 4. Services Architecture Documentation

**Objective**: Make service boundaries and integration points explicit.

**Work**:
- [ ] Document `services/planner/` interface and lifecycle
- [ ] Document `services/manifest/` contract and output format
- [ ] Document `services/device-catalog/` schema and extension points
- [ ] Create service integration diagram
- [ ] Add service testing patterns and examples

**Outputs**: Maintainable service layer, clear extension points

---

### 5. Packaging and Installation Entrypoints

**Objective**: Solidify public-facing install and import paths.

**Work**:
- [ ] Verify `pip install udos-sonic` works cleanly
- [ ] Test `from udos_sonic import *` import patterns
- [ ] Add service module public API (`from udos_sonic.services import ...`)
- [ ] Create extension example for custom build engines
- [ ] Document development vs production install workflows

**Outputs**: Clear packaging story, repeatable install

---

## v1.7 Objectives (Q3 2026)

### 1. Internal Folder Reorganization (non-breaking)

**Objective**: Align folder structure with education-facing IA without breaking APIs.

**Work**:
- [ ] Create shims or symlinks from old paths to new locations (backwards compat)
- [ ] Migrate code gradually to education-facing roots
- [ ] Move `installers/usb/` content into `modules/usb-installer/` and `services/`
- [ ] Reorganize `distribution/` into narrower purpose

**Outputs**: Cleaner structure, backwards-compatible transition

---

### 2. Extension Framework

**Objective**: Enable custom module development and deployment.

**Work**:
- [ ] Document module development pattern
- [ ] Create extension test harness
- [ ] Add discovery mechanism for third-party modules
- [ ] Publish reference extension (dualboot, rescue, etc.)

**Outputs**: Third-party extensibility, clear patterns

---

## Known Gaps / Always-On

- **Test coverage**: Add integration tests for multi-service flows
- **CI/CD**: Strengthen Linux smoke workflow, add deployment sandbox tests
- **Documentation**: Keep architecture docs in sync with code changes
- **Dependency updates**: Maintain Python and Node.js dependency freshness
- **Security**: Regular audit of deployment surface and permissions model

---

## Milestone Completion Criteria

**v1.6 "Complete"** when:
- Education pathway is clear (courses + docs separation)
- uHOME boundary is resolved (imports working or plan drafted)
- Services are documented
- Vault templates exist and are used in examples
- Packaging story is solid

**v1.7 "Complete"** when:
- Folder structure reorganization is complete (with backwards-compat)
- Extension framework is published with example usage
- Internal technical debt is understood and tracked

---

## Integration with @dev Workspace

Development work on these objectives should be tracked as individual `#binders`:

- `#binder/sonic-education-pathway` (v1.6.1)
- `#binder/sonic-uhome-boundary` (v1.6.2)
- `#binder/sonic-vault-templates` (v1.6.3)
- `#binder/sonic-services-architecture` (v1.6.4)
- `#binder/sonic-packaging-finalization` (v1.6.5)
- `#binder/sonic-refactor-structure` (v1.7.1)
- `#binder/sonic-extension-framework` (v1.7.2)

Each binder should be reviewed, advanced, and compiled according to the @dev workflow defined in `docs/uDOS-sonic-dev-brief.md`.

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| uHOME-server not ready | Medium | High | Define graceful fallback, document transition period |
| Breaking API changes | Low | High | Maintain `pyproject.toml` semantic versioning strictly |
| Education pathway too complex | Low | Medium | Iterate based on learner feedback |
| Test coverage gaps | Medium | Medium | Add integration suite early in v1.6 |

---

## Success Metrics

- Learner onboarding time < 2 hours (measured)
- Zero breaking changes in v1.6.x (maintains 1.x.y API)
- Service documentation covers >80% of public API
- Zero reported security issues related to permissions
- Deployment success rate >95% on tested hardware

