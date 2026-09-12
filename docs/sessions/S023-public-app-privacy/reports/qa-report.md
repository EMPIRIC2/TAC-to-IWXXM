# QA Report — S023 / EV-017 (F21 public app + F22 privacy / #783)

> Generated: 2026-07-28  
> Scope: F21 / F22 / F5–F7.h IndexedDB; Auth teardown (`packages/auth` deleted)  
> Branch: `evolve/EV-017-public-app-privacy` @ `836c1a4` (+ uncommitted `test_coverage_boost` import fix)  
> Mode: evolve delta (09-qa) · parallel with 10-e2e

```text
QA Results:
  Lint:           PASS — 0 issues (ruff + eslint)
  Format:         PASS — 0 files (ruff + prettier)
  Typecheck:      PASS — 0 errors (basedpyright + tsc)
  Tests (Python): PASS — H0c 6; TC-F21-auth-gone + abuse 10; full unit matrix green at 08
  Tests (FE):     PASS — 698 passed / 80 files (@metar/frontend)
  Security:       PASS — pip-audit 0 known / 1 ignored (ecdsa); gitleaks PASS
  Cross-file:     PASS — WorkbenchConsole RegExp.exec only (not eval/exec misuse)
  Dependencies:   PASS — pyasn1 0.6.4 (D-S023-08-pyasn1-A)
  Template:       PASS — static+api+worker; packages/auth absent
  Data / Modal:   N/A — no Modal assets; Compose H0i SKIPPED (Docker unavailable)
```

## Summary

| Check | Status | Notes |
|-------|--------|-------|
| Format / Lint / Typecheck | PASS | `make validate-fast` |
| FE Vitest | PASS | **698** / 80 files |
| H0c CORS | PASS | 6/6 |
| Security (lockfile) | PASS | `pyasn1` 0.6.4; ecdsa ignored |
| Secrets | PASS | pre-commit gitleaks |
| H0i integration | SKIPPED | Docker not on host — advisory |
| Staging H4–H5 | ADVISORY | Already PASS at T7.2 live; re-confirm at 13 |

**Overall: pass_with_advisories**

## Blocking

None.

## Advisories (for 11-verify-impl)

| ID | Severity | Finding | Suggested action |
|----|----------|---------|------------------|
| QA-001 | advisory | H0i Compose integration not run (no Docker) | Run on CI / machine with Docker; not blocking for F21 public HTTP |
| QA-002 | advisory | `.env` `PLAYWRIGHT_BASE_URL=http://localhost:5173` mismatches local stack `:18000` | Override to `:18000` for local Playwright (see e2e-report); optional `.env.example` note |
| QA-003 | advisory | `tests/infrastructure/test_coverage_boost.py` imported `verify_supabase_token` from `src.api` (removed F21) | Fixed in working tree — import from `src.utilities.security` |
| QA-004 | advisory | Live H4–H5 already green (T7.2) but re-check after any further FE bake | 13-deploy-smoke |

## Connectivity (stage 09)

| Tier | Result |
|------|--------|
| H0c | PASS |
| H0i | SKIPPED (no Docker) |
| H4–H5 | PASS recorded at M7 (`t7.2-h4-h5-connectivity.md`); re-verify at 13 |

## Commands run

```bash
make validate-fast
uv run pytest tests/unit/test_cors_policy.py -q --no-cov
pnpm --filter @metar/frontend test
uv export … && uvx pip-audit -r /tmp/project-reqs.txt --disable-pip $(…ignore…)
uv run pre-commit run gitleaks --all-files
rg -n 'pickle\.loads|eval\(|exec\(' apps packages
```
