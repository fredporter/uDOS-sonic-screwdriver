# Sonic v1.6 Binder Breakdown and Task Planning

**Created**: 2026-03-10  
**Status**: Development workflow planning  
**Parent Roadmap**: [docs/ROADMAP-v1.6.md](ROADMAP-v1.6.md)

---

## Binder Structure for v1.6 Development

Each objective from the roadmap should be tracked as a dedicated `#binder` in the @dev workspace. This document breaks down the specific tasks, dependencies, and handoff criteria for each binder.

---

## #binder/sonic-education-pathway (v1.6.1)

**Objective**: Make the learner journey explicit and organized.

**Milestone**: v1.6  
**Priority**: P0 (blocker for learner adoption)  
**Owner**: TBD  
**State**: Not started

### Tasks

- [ ] **Task 1.1**: Analyze `docs/01-09.md` series and categorize by lesson/flow
  - Input: Current docs files
  - Output: Learning model proposal
  - Effort: 3 hours
  - Dependency: None

- [ ] **Task 1.2**: Create `courses/01-sonic-screwdriver/` directory structure
  - Input: Learning model from 1.1
  - Output: Course skeleton with README and module files
  - Effort: 2 hours
  - Dependency: Task 1.1

- [ ] **Task 1.3**: Convert first 3 docs modules into course format
  - Input: Course structure from 1.2
  - Output: `lesson-01-*.md`, `lesson-02-*.md`, `lesson-03-*.md`
  - Effort: 8 hours
  - Dependency: Task 1.2

- [ ] **Task 1.4**: Move reference docs to `docs/architecture/`
  - Input: All current docs
  - Output: Separated reference docs, updated links
  - Effort: 4 hours
  - Dependency: Task 1.3

- [ ] **Task 1.5**: Create `courses/02-deployment-patterns/` outline
  - Input: Operational examples from docs
  - Output: Course structure + stub lessons
  - Effort: 3 hours
  - Dependency: Task 1.2

### Completion Criteria

- Course material compiles without broken links
- Learner can complete first course in <2 hours
- Docs separation verified (no reference content in courses/)
- README guides to correct entry point

### Blockers

- None identified

### Risks

- Documentation scatter across multiple locations
- Mitigation: Update all cross-repo docs index after completion

---

## #binder/sonic-uhome-boundary (v1.6.2)

**Objective**: Phase down local uHOME compatibility code; clarify boundary with uHOME-server.

**Milestone**: v1.6  
**Priority**: P0 (blocks external integration)  
**Owner**: TBD  
**State**: Not started

### Tasks

- [ ] **Task 2.1**: Audit all local uHOME modules
  - Input: `installers/bundles/uhome/*` + `distribution/launchers/uhome/`
  - Output: Module inventory with ownership classification (canonical vs shim)
  - Effort: 3 hours
  - Dependency: None

- [ ] **Task 2.2**: Create uHOME-server bridge import pattern
  - Input: Inventory from 2.1
  - Output: Import shim proposal with example
  - Effort: 4 hours
  - Dependency: Task 2.1, requires uHOME-server repo access

- [ ] **Task 2.3**: Implement first bridge import (bundle module)
  - Input: Bridge pattern from 2.2
  - Output: Working `from uhome_server.sonic import uhome_bundle`
  - Effort: 3 hours
  - Dependency: Task 2.2

- [ ] **Task 2.4**: Test bundle/preflight/install-plan flow
  - Input: Bridge implementation from 2.3
  - Output: Integration test suite
  - Effort: 6 hours
  - Dependency: Task 2.3

- [ ] **Task 2.5**: Update integration docs for uHOME-server dependency
  - Input: Test results from 2.4
  - Output: `docs/architecture/uhome-integration.md`
  - Effort: 2 hours
  - Dependency: Task 2.4

### Completion Criteria

- All uHOME ownership documented and validated
- At least one module imports successfully from uHOME-server
- Integration tests pass
- No breaking changes to Sonic public API

### Blockers

- ⚠️ Requires uHOME-server release with public imports
- Contact uHOME-server maintainers for release timeline

### Risks

- uHOME-server API may change
- Mitigation: Use version pinning, document API contract

---

## #binder/sonic-vault-templates (v1.6.3)

**Objective**: Create a public template and example collection.

**Milestone**: v1.6  
**Priority**: P1 (improves onboarding)  
**Owner**: TBD  
**State**: Not started

### Tasks

- [ ] **Task 3.1**: Create `vault/` directory structure
  - Input: Roadmap specification
  - Output: Directories + READMEs for templates/, manifests/, deployment-notes/
  - Effort: 1 hour
  - Dependency: None

- [ ] **Task 3.2**: Collect example device profiles
  - Input: Current `config/` + `memory/sonic/user/` profiles
  - Output: 5+ reference profiles in `vault/templates/device-profiles/`
  - Effort: 4 hours
  - Dependency: Task 3.1

- [ ] **Task 3.3**: Create reference deployment manifests
  - Input: Generated manifests from test deployments
  - Output: 3+ reference manifests in `vault/manifests/`
  - Effort: 3 hours
  - Dependency: Task 3.1

- [ ] **Task 3.4**: Document vault structure and use
  - Input: Vault contents from 3.2 + 3.3
  - Output: `vault/README.md` + usage guide in docs
  - Effort: 2 hours
  - Dependency: Task 3.3

### Completion Criteria

- Templates are referenced in course material (1.3)
- Examples are runnable/verifiable
- Documentation is clear to new user

### Blockers

- None identified

### Risks

- Template data may become stale
- Mitigation: Document refresh cadence

---

## #binder/sonic-services-architecture (v1.6.4)

**Objective**: Make service boundaries and integration points explicit.

**Milestone**: v1.6  
**Priority**: P1 (improves extensibility)  
**Owner**: TBD  
**State**: Not started

### Tasks

- [ ] **Task 4.1**: Document planner service interface
  - Input: `services/` code + integration examples
  - Output: `docs/architecture/services-planner.md` with API and lifecycle
  - Effort: 3 hours
  - Dependency: None

- [ ] **Task 4.2**: Document manifest service interface
  - Input: Manifest generation code
  - Output: `docs/architecture/services-manifest.md` with contract and format
  - Effort: 3 hours
  - Dependency: None

- [ ] **Task 4.3**: Document device-catalog service
  - Input: `datasets/sonic-devices.schema.json` + catalog code
  - Output: `docs/architecture/services-catalog.md` with schema and queries
  - Effort: 2 hours
  - Dependency: None

- [ ] **Task 4.4**: Create service integration diagram
  - Input: Services from 4.1-4.3
  - Output: Mermaid diagram in `docs/architecture/services-overview.md`
  - Effort: 2 hours
  - Dependency: Task 4.1-4.3

- [ ] **Task 4.5**: Add service testing patterns
  - Input: Existing test suite
  - Output: `docs/architecture/services-testing.md` with examples
  - Effort: 3 hours
  - Dependency: Task 4.4

### Completion Criteria

- All service API surfaces documented
- Testing patterns are clear and repeatable
- Integration diagram shows data flow
- Examples are runnable

### Blockers

- None identified

### Risks

- Services may evolve after documentation
- Mitigation: Schedule documentation refresh in v1.7

---

## #binder/sonic-packaging-finalization (v1.6.5)

**Objective**: Solidify public-facing install and import paths.

**Milestone**: v1.6  
**Priority**: P1 (impacts distribution)  
**Owner**: TBD  
**State**: Not started

### Tasks

- [ ] **Task 5.1**: Test `pip install udos-sonic` on clean venv
  - Input: Current `pyproject.toml` + build config
  - Output: Test report + any packaging fixes
  - Effort: 2 hours
  - Dependency: None

- [ ] **Task 5.2**: Verify import paths work correctly
  - Input: Public API definition from roadmap
  - Output: Test suite for `from udos_sonic import ...` patterns
  - Effort: 2 hours
  - Dependency: Task 5.1

- [ ] **Task 5.3**: Add service module public API
  - Input: Service docs from binder 4
  - Output: `__init__.py` exports for `services/` modules
  - Effort: 2 hours
  - Dependency: Task 5.2

- [ ] **Task 5.4**: Create extension example (custom build engine)
  - Input: Service layer architecture
  - Output: `examples/custom-build-engine/` with runnable example
  - Effort: 4 hours
  - Dependency: Task 5.3

- [ ] **Task 5.5**: Document dev vs production install workflows
  - Input: Local development patterns + CI/CD setup
  - Output: `docs/howto/development-install.md` + `docs/howto/production-install.md`
  - Effort: 2 hours
  - Dependency: Task 5.4

### Completion Criteria

- `pip install` succeeds on three OS targets (macOS, Linux, Windows/WSL)
- All documented import paths work
- Extension example is runnable
- Installation guide is clear

### Blockers

- May need to update GitHub Actions for multi-OS testing

### Risks

- Platform-specific issues in packaging
- Mitigation: Test on each platform early in cycle

---

## Binder Advancement Workflow

For each binder, follow this progression:

1. **Open** → Define scope and objectives (done above)
2. **Hand off** → Assign owner, schedule in sprint
3. **Advance** → Work through tasks incrementally, commit progress
4. **Review** → Inspect work, verify completion criteria
5. **Commit** → Merge advances to main branch
6. **Complete** → Milestone reached, compile outputs
7. **Compile** → Clean up temporary work, prepare for promotion
8. **Promote** → Include in release, update CHANGELOG

---

## Prioritization and Sequencing

### Phase 1 (Weeks 1-2): Foundation
- Start **#binder/sonic-education-pathway** (1.1-1.2)
- Start **#binder/sonic-vault-templates** (3.1-3.2) in parallel
- These enable other work

### Phase 2 (Weeks 3-4): Integration
- Complete **#binder/sonic-education-pathway** (1.3-1.5)
- Begin **#binder/sonic-services-architecture** (4.1-4.3)
- Begin **#binder/sonic-uhome-boundary** (2.1-2.2)

### Phase 3 (Weeks 5-6): Testing and Hardening
- Complete **#binder/sonic-services-architecture**
- Complete **#binder/sonic-uhome-boundary**
- Complete **#binder/sonic-vault-templates**

### Phase 4 (Week 7): Packaging
- Begin **#binder/sonic-packaging-finalization**

### Phase 5 (Week 8): Integration and Release Prep
- Complete **#binder/sonic-packaging-finalization**
- Compile all binder outputs
- Prepare v1.6 release notes

---

## Tracking and Communication

- Weekly binder review: Check each binder's progress against completion criteria
- Blockers: Escalate immediately (e.g., uHOME-server availability)
- Outputs: Verify each task produces its specified artifact
- Cross-binder dependencies: Coordinate between teams if parallel work streams

---

## Success Metrics for v1.6

| Metric | Target | Measurement |
|--------|--------|-------------|
| Learner onboarding time | < 2 hours | Time to complete course 1 |
| API stability | Zero breaking changes | Semantic versioning maintained |
| Service documentation | > 80% API coverage | Lines of public API documented |
| Test coverage | > 85% | Code coverage report |
| Packaging reliability | 100% success on three OS | CI/CD multi-OS test results |

