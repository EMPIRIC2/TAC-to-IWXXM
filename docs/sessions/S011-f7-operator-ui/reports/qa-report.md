# QA Report — S011 M6 / T6.2 (09-qa)

> **Generated**: 2026-07-14  
> **Skill**: 09-qa (delta — EV-008 / F7)  
> **Session**: S011-f7-operator-ui / EV-008  
> **Branch**: `evolve/S011-f7-operator-ui`  
> **Mode**: report-only (+ one fix-in-place for blocking typecheck from T6.1 tip)

```text
QA Results:
  Lint:           PASS — 0 issues (ruff + eslint)
  Format:         PASS — 0 files (ruff + prettier)
  Typecheck:      PASS — 0 errors (after fix-in-place; see QA-001)
  Tests (Python): PASS — backend 1162; auth 228 (+31 skip); workspace/packages/bugs/worker green
  Tests (FE):     PASS — 590 passed; branches 88.88% (gate 88)
  Security:       PASS tree secrets; npm audit ENDPOINT 410 (advisory); pip-audit env noise (advisory)
  Cross-file:     PASS (ruff clean)
  Dependencies:   advisory — npm audit API retired; pip-audit scanned host env pkgs
  Template:       PASS — apps/packages layout; no Modal DATABASE_URL path change
  Data / Modal:   N/A (Render + Supabase BYO); H0c PASS; H4–H5 deferred T6.4
  Integration:    SKIPPED — ports 18000/18001 held by vecinita-*; disk ~686MB free (100%)
```

**Overall: pass_with_advisories**

## Executive summary

| Check | Blocking? | Status | Notes |
|-------|-----------|--------|-------|
| Format | Yes | PASS | `make format-check` |
| Lint | Yes | PASS | `make lint` |
| Typecheck | Yes | PASS | Was FAIL on tip; fixed narrowing in `api.py` (QA-001) |
| Unit tests | Yes | PASS | Full `make test-unit*` families used in CI |
| H0c CORS | Yes | PASS | 6 passed |
| Secrets (tree) | Yes | PASS | `make secrets-check` / gitleaks |
| Frontend vitest | Yes | PASS | coverage thresholds met |
| Compose / H0i | Yes* | SKIPPED | Host ports + Docker disk — not a product defect |
| npm `audit:ci` | No | ADVISORY | registry 410 Gone |
| H4–H5 staging | No | DEFERRED | T6.4 / `verify_connectivity.sh` |

\* Treated as non-blocking when host-envSKIP with documented reason (same as T6.1).

## Fix-in-place during T6.2

| ID | Change |
|----|--------|
| QA-001 | `apps/backend/src/api.py` — assign `request_body.product` / `.profile` via locals so `str \| None` is narrowed before assignment to `str` (introduced in T6.1 soft-preview JSON path). **Uncommitted** until user asks to commit. |

## Commands run

```bash
make format-check
make lint
make typecheck-py   # after QA-001
make typecheck-js
make secrets-check
make validate-yaml
make config-guard
make env-check
make test-unit-backend
make test-unit-auth
make test-unit-workspace
make test-bugs
make test-unit-tac2iwxxm
make test-unit-iwxxm-validate
make test-unit-tac-validate
make test-unit-worker
pnpm --filter @metar/frontend run test:coverage
uv run pytest tests/unit/test_cors_policy.py -v --no-cov
make audit-frontend   # failed: npm audit endpoint 410
```

## Findings for 11-verify-impl

| ID | Severity | Finding | Suggested action |
|----|----------|---------|------------------|
| QA-001 | Resolved (local) | Typecheck FAIL on T6.1 tip (`product`/`profile` Optional) | Commit QA-001 with T6.2 closeout |
| QA-002 | Advisory | `pnpm audit` returns HTTP 410 | Track npm audit migration; do not block deploy |
| QA-003 | Advisory | Host disk full (~686MB); compose SKIPPED | Free disk before local compose/Playwright; rely on CI + T6.4 |
| QA-004 | Advisory | Ports 18000/18001 owned by `vecinita-*` | Do not AUTO_KILL for metar e2e on this host; free ports or use CI |
| QA-005 | Advisory | `env-check` WARN: `SUPABASE_SERVICE_ROLE_KEY` without `SUPABASE_SECRET_KEY` | Migrate canonical name when convenient |
| QA-006 | Advisory | Stale Playwright admin narratives still present (`auth.e2e.spec.ts` admin login, `workflow-theme-persistence` admin view) | Retire/skip before relying on full `tests:e2e` suite |

## Connectivity (Stage 09)

- [x] H0c `tests/unit/test_cors_policy.py` PASS  
- [ ] H0i compose SKIPPED (QA-003/004)  
- [ ] H4–H5 staging deferred to T6.4  

## Phase alignment

- C→D passed (`D-S011-EV008-c-to-d-pass`).  
- T6.2 consumes this report + `e2e-report.md`.  
- Next: T6.3 `11-verify-impl` (F7 acceptance 1–8).
