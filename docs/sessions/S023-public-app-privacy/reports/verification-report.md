# Verification Report

> Generated: 2026-07-28  
> Scope: **Phase C / M7 complete** — S023 / EV-017 (F21 public app + F22 privacy)  
> Branch: `main` @ `aaf2aee` (#786/#787/#788)  
> Stage: **08-verify-build**

## Summary

| Check | Status | Findings | Auto-Fixed | Tool |
|-------|--------|----------|------------|------|
| Format | PASS | 0 | 0 | ruff format + prettier |
| Lint | PASS | 0 | 0 | ruff + eslint |
| Typecheck | PASS | 0 | — | basedpyright + tsc |
| Unit tests | PASS | 0 failed | — | `make test-unit` |
| Bugs | PASS | 32 passed, 5 skipped | — | `make test-bugs` |
| H0c CORS | PASS | 6/6 | — | `tests/unit/test_cors_policy.py` |
| H0i + F21 auth-gone | PASS | 14/14 | — | CI-parity pytest |
| Root integration | PASS | 23/23 | — | `tests/test_*integration*` |
| Live H4–H5 | PASS | H0c+H4+H5 | — | `verify_connectivity.sh` |
| Secrets | PASS | 0 | — | gitleaks |
| pip-audit | PASS | 0 known vulns | — | `uvx pip-audit` |
| Frontend audit | PASS* | 1 high ignored | — | `audit:ci` (brace-expansion GHSA pinned) |
| Template | PASS | auth package deleted; layout OK | — | static+api+worker |
| Docker compose integration | SKIPPED | no local `docker` | — | `make test-integration` |
| Main CI | PASS | Deploy + Test (integration) green | — | [run 30396669779](https://github.com/EMPIRIC2/TAC-to-IWXXM/actions/runs/30396669779) |

\* Known accepted ignore: `GHSA-mh99-v99m-4gvg` (brace-expansion via eslint/minimatch@3); documented in `audit-ci.sh`.

**Overall: PASS**

## Unit suite highlights (`make test-unit`)

| Package | Result |
|---------|--------|
| Workspace / shared (py+js) | pass (coverage gates met) |
| Backend unit | **1199** passed (98%+ cov) |
| Frontend Vitest | **698** passed (80 files) |
| tac2iwxxm / iwxxm-validate / tac-validate / dissemination | pass |
| Worker | 11 passed |
| Bugs (non-live) | 32 passed |

## Connectivity (stage 08 blocking)

| Artifact | Present |
|----------|---------|
| `tests/unit/test_cors_policy.py` | yes |
| `tests/smoke/test_staging_connectivity.py` | yes |
| `scripts/deploy/verify_connectivity.sh` | yes |
| `configure_cors` / `CORSMiddleware` on API | yes |

Live: `/auth/login` 404, public convert OK, FE `/config.json` omits `disableAuth` (post-#787).

## F21 / F22 delta focus

| Suite | Result |
|-------|--------|
| `test_tc_f21_auth_gone_unit` + abuse controls | 10/10 |
| FE `tc-f21-auth-gone` + privacy + localWorkSessionStore | 34/34 |
| H0i public conversion + Auth/work-sessions gone | included in 14/14 |

## Notes

- Local `make test-integration` (compose stack) skipped — Docker CLI unavailable on this host; CI **Test (integration)** succeeded on `main`.
- Full `apps/backend/tests/integration/` beyond H0i not required for 08 (Auth-era e2e stack / phenomenon corpus — out of CI matrix).
- Security WIP (static analysis skill) remains **unstaged** on `evolve/EV-017-public-app-privacy` — not part of this verify.

## Next

Phase C checkpoint → routing **09-qa** + **10-e2e** (Standard) → **11-verify-impl**.
