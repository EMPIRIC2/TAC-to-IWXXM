# 03-plan-tooling report — S014 / EV-010

**Date**: 2026-07-18  
**Mode**: delta (PyPI / release / msgspec HTTP guardrails)  
**User plan**: **D** — full set + release-tag hook + `pypi-release-checklist` skill

## Installed

### Rules (3)

| Artifact | Scope | Spec trace |
|----------|-------|------------|
| `core/plan-adherence.mdc` (updated) | always-apply | Feature table F7–F14 status corrected; F9–F14 added |
| `core/pypi-package-publish.mdc` (new) | packages + `.github/workflows` | F12–F14 OIDC, tags, boundaries, copyright |
| `optional/msgspec-http-boundary.mdc` (new) | backend/FE/packages/api-contract | ADR-026 / E10-28 |

### Hooks (3)

| Artifact | Event | Notes |
|----------|-------|-------|
| `scope_check.py` (patched) | preToolUse Write | + `tac2iwxxm`, `tac-validate`, `iwxxm-validate`, `apps/worker` |
| `feature_drift.py` (patched) | afterFileEdit | F11–F14 package mappings; F1–F14 messaging |
| `pypi_release_guard.py` (new) | beforeShellExecution `git tag`; preToolUse Shell; afterFileEdit | Advisory OIDC/tag/workflow reminders |
| `hooks.json` (updated) | bindings for above | Valid JSON |

### Skills (1 new + 1 delta)

| Artifact | Trigger |
|----------|---------|
| `pypi-release-checklist/SKILL.md` | Before tag / publish workflow / 12-verify-deploy |
| `api-contract-validator/SKILL.md` | §3b msgspec HTTP boundary checks |

### Agents (1)

| Artifact | Change |
|----------|--------|
| `scope-reviewer.md` | Checklist F1–F14, PyPI, ADR-026; refs updated |

## Verification

| Check | Result |
|-------|--------|
| Rule frontmatter | PASS (3) |
| hooks.json parse | PASS |
| scope_check → `packages/tac-validate` | PASS (maps to F12; git-root fix) |
| feature_drift → `iwxxm-validate/pyproject.toml` | PASS (F2, F13; git-root fix) |
| find_repo_root prefers `.git` over nested pyproject | PASS (fixed in 3 hooks) |
| pypi_release_guard → publish workflow path | PASS (advisory context) |
| pypi_release_guard → `git tag tac-validate-v0.1.0` | PASS (advisory context) |
| pypi_release_guard → unrelated shell | PASS (empty `{}`) |
| Skill YAML frontmatter | PASS |

## Phase A gate

- [x] Spec documents generated and audited (01 + 02 PASS)
- [x] Plan tooling installed (this stage)
- → Ready for Phase B: **04-tech-plan**
