# Execution plan — EV-002 CI consolidation

**Stage**: 04-tech-plan  
**Cycle**: EV-002 / M5  
**Branch**: `evolve/EV-002-ci-consolidation`

## Goal

Reduce PR CI from 13 jobs / 4 workflow files to **3 jobs / 1 workflow file** without dropping checks.

## Tasks

| ID | Task | Depends | Spec source | Status |
|----|------|---------|-------------|--------|
| T1 | Add `validate-fast` Makefile target mirroring CI validate checks | — | test-plan §Pre-commit | pending |
| T2 | Rewrite `.pre-commit-config.yaml` — fast hooks only; demote `make ci` to manual stage | T1 | pre-commit-tooling-plan | pending |
| T3 | Consolidate `ci-cd.yml` → 3 jobs: `validate`, `test`, `deploy` | T1 | test-plan §CI/CD | pending |
| T3a | validate job: all static analysis + config-guard + pnpm audit | T3 | evolve-decisions R6 | pending |
| T3b | test job: matrix (backend, auth, gifts, frontend, shared) + integration + Codecov | T3 | evolve-decisions R5,R7 | pending |
| T3c | deploy job: merge detect-changes + build-and-push + deploy-render; drop redundant summary jobs | T3b | ci-cd.yml current | pending |
| T4 | Delete `secret-scan.yml`, `github-yaml-lint.yml`, `frontend-audit.yml` | T3a | evolve-decisions | pending |
| T5 | Update `docs/dependency-inventory.md` pre-commit entry | T2 | product-audit C1 | pending |
| T6 | Update `docs/DEVELOPMENT.md` — pre-commit install + CI job layout | T3 | test-plan | pending |
| T7 | Run `make ci` + local pre-commit smoke on evolve branch | T2,T3 | EV-002 acceptance | pending |

## CI job design (T3 detail)

### Job 1: `validate` (~1 runner)

Single checkout; uv + pnpm setup once.

Steps (sequential):
1. `make validate-fast` (or inline equivalent)
2. gitleaks (redundant if pre-commit ran — still run in CI per dual-run)
3. actionlint + yamllint on `.github/`
4. `pytest tests/test_config_placeholders.py`
5. `pnpm --filter @metar/frontend run audit:ci`

### Job 2: `test` (~1 runner + matrix)

`needs: validate`

Strategy matrix:
```yaml
matrix:
  package: [shared, backend, auth, gifts, frontend]
```

Each matrix cell runs that package's unit+coverage target (extract from current per-job steps).

After matrix completes:
- Single integration step (docker compose + pytest integration suite)
- Codecov uploads per matrix artifact (preserve 5 flags)

Remove: `coverage-enforcement`, `test-summary` as separate jobs — fold into test job `if: always()` summary step.

### Job 3: `deploy` (main push only)

`needs: test`  
Unchanged logic from current build-and-push + deploy-render.

## Verification (08-verify-build)

- `make validate-fast`
- `make ci`
- `pre-commit run --all-files` (fast hooks only)
- Push branch → watch CI (3 jobs on PR)

## Acceptance mapping (11-verify-impl)

| Criterion | Task |
|-----------|------|
| ≤3 jobs on PR | T3 |
| All checks preserved | T3a,T3b |
| Pre-commit fast = validate | T2 |
| make ci unchanged | T1,T2 (no change to `ci:` target) |
| CI green | T7 |

## Git strategy

One task per commit:
- `[T1] chore: add validate-fast Makefile target`
- `[T2] chore: split pre-commit fast hooks from make ci`
- `[T3] ci: consolidate ci-cd.yml to validate/test/deploy jobs`
- `[T4] ci: remove redundant workflow files`
- `[T5] docs: update dependency inventory for pre-commit tiers`
- `[T6] docs: update DEVELOPMENT.md CI section`
