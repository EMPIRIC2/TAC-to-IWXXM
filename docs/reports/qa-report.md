# QA Report — Stage 09 (live environment focus)

> Generated: 2026-06-22  
> Scope: Live Render stack + full-repo spot checks  
> Branch: `main`  
> Targets:
> - API: `https://metar-to-iwxxm-api.onrender.com`
> - Frontend: `https://metar-to-iwxxm-frontend-v4-web.onrender.com`

```text
QA Results (live focus):
  H0c CORS unit:     PASS — 6/6
  H4 live CORS:      PASS — preflight from frontend origin
  H5 bundle URL:     PASS — bundle embeds LIVE_API_URL host
  H3 live API:       PASS — 21/21 pytest (apps/backend/tests/infrastructure/test_live_api_health.py)
  Live integration:  PASS — 6/6 (tests/integration/test_live_stack.py)
  H6 Playwright:     PASS — 27 passed, 2 skipped (TAC fixture upload)
  Lint:              FAIL — 11 issues (backend scripts only; advisory)
  Format:            PASS — 388 files
  Typecheck (shared): PASS — 0 errors
  Security (pip-audit): PASS — 0 CVEs
```

**Overall: pass_with_advisories** — live H3–H6 green; ruff script advisories non-blocking for release signoff.

---

## Executive summary

| Category | Status | Blocking |
|----------|--------|----------|
| H0c CORS policy (unit) | PASS | — |
| H4 live CORS preflight | PASS | — |
| H5 frontend bundle API URL | PASS | — |
| H3 live API pytest | PASS (21/21) | — |
| Live integration stack | PASS (6/6) | — |
| H6 Playwright live E2E | PASS (27/29; 2 skipped) | — |
| pip-audit | PASS | — |
| ruff (apps/packages/tests) | FAIL (11) | Advisory (QA-008) |

**Key finding:** Live e2e and integration tests **already exist** and pass against the documented Render URLs. No new harness code required for H3–H6 signoff.

---

## Live test harness (existing)

| Tier | Makefile target | Test location |
|------|-----------------|---------------|
| H4–H5 | `make test-live-connectivity` | `scripts/deploy/verify_connectivity.sh`, `tests/smoke/test_staging_connectivity.py` |
| H3 | `make test-live-api` | `apps/backend/tests/infrastructure/test_live_api_health.py` |
| Integration | `make test-live-integration` | `tests/integration/test_live_stack.py` |
| H6 | `make test-live-e2e` | `apps/e2e/*.e2e.spec.ts` (Playwright, `PLAYWRIGHT_BASE_URL` = frontend) |
| All | `make test-live` | Sequential H4–H5 → H3 → integration → H6 |

**Env vars** (canonical):

```bash
LIVE_API_URL=https://metar-to-iwxxm-api.onrender.com
LIVE_FRONTEND_URL=https://metar-to-iwxxm-frontend-v4-web.onrender.com
RUN_LIVE_TESTS=1                    # required for pytest live integration
ADMIN_EMAIL=...                       # from .env — JWT via POST /auth/login
ADMIN_PASSWORD=...
```

Defaults in `tests/live_fixtures.py` and `Makefile` match the URLs above when `LIVE_*` are unset.

**Opt-in guard:** `tests/integration/conftest.py` skips live integration unless `RUN_LIVE_TESTS=1` (set automatically by `make test-live-*`).

---

## Commands run (2026-06-22)

```bash
# Connectivity (H0c + H4 + H5)
LIVE_API_URL=https://metar-to-iwxxm-api.onrender.com \
LIVE_FRONTEND_URL=https://metar-to-iwxxm-frontend-v4-web.onrender.com \
VITE_API_BASE_URL=https://metar-to-iwxxm-api.onrender.com \
bash scripts/deploy/verify_connectivity.sh

# Live integration (6 tests — frontend shell, CORS, health, convert+validate, auth reject, defaults)
make test-live-integration

# Live API (21 tests — health, versions, convert, validate, auth, performance)
make test-live-api

# Live Playwright (29 tests — UJ-001–003 + workflows; DISABLE_AUTH=false)
make test-live-e2e

# Spot checks
uv run ruff check apps packages tests
uv run ruff format --check apps packages tests
uv run basedpyright packages/shared/src
uv run pip-audit
```

---

## Live results detail

### H4–H5 connectivity — PASS

```
Live API awake: https://metar-to-iwxxm-api.onrender.com
H0c: 6 passed (tests/unit/test_cors_policy.py)
H4: test_staging_cors_preflight_allows_frontend_origin PASSED
H5: OK: deployed bundle references VITE_API_BASE_URL=https://metar-to-iwxxm-api.onrender.com
```

### Live integration — PASS (6/6)

| Test | Result |
|------|--------|
| `test_live_frontend_serves_app_shell` | PASS |
| `test_live_cors_preflight_from_frontend_origin` | PASS |
| `test_live_api_public_health_path` | PASS |
| `test_live_convert_then_validate_round_trip` | PASS (requires `.env` admin creds) |
| `test_live_auth_login_rejects_bad_credentials` | PASS |
| `test_live_env_defaults_match_render_stack` | PASS |

### H3 live API — PASS (21/21)

All classes in `test_live_api_health.py` green including authenticated convert/validate, concurrent health, and response-time thresholds.

### H6 Playwright — PASS (27 passed, 2 skipped)

| Spec | Result |
|------|--------|
| `00-preflight.e2e.spec.ts` | PASS — admin login against live stack |
| `tac-file-conversion.e2e.spec.ts` (UJ-001) | PASS — manual + COR METAR conversion |
| `auth.e2e.spec.ts` (UJ-003) | PASS |
| Workflow specs (theme, logout, full journey) | PASS |
| `tac-file-upload-database.e2e.spec.ts` | 2 **skipped** — no TAC fixture dir from `apps/e2e` cwd (QA-009) |

Cold-start handling: API wake retries (3×, 30s) in `tests/live_fixtures.py` and `00-preflight.e2e.spec.ts`.

---

## Findings for 11-verify-impl

| ID | Severity | Finding | Suggested action |
|----|----------|---------|------------------|
| QA-008 | Advisory | 11 ruff errors in `apps/backend/scripts/*` (E402, F841) | Fix or exclude scripts from lint scope |
| QA-009 | Advisory | Live E2E upload tests skip without `PLAYWRIGHT_TAC_FIXTURES_DIR` | Set fixture path or `PLAYWRIGHT_REQUIRE_TAC_FIXTURES=0` for upload coverage on live |
| QA-006 | **Resolved** | H4/H5 previously skipped locally | Re-verified green against Render URLs (this run) |

Prior findings from 2026-06-20 run (QA-001–QA-005, QA-007): see git history of this file; **msgpack CVE (QA-004) resolved** — pip-audit now reports no known vulnerabilities.

---

## Handoff notes

1. **Live signoff ready** — run `make test-live` from repo root with `.env` populated before release.
2. **CI policy** — live tests remain manual/Makefile-only per `docs/test-plan.md` (Render cold-start + secrets).
3. **No new test files needed** for H3–H6; harness maps to `docs/test-plan.md` §Live Test Cases.
4. For credential-free smoke against live frontend only: `make test-e2e-playwright-smoke` with `PLAYWRIGHT_BASE_URL` set still uses mock auth — use `make test-live-e2e` for real auth + API wiring.
