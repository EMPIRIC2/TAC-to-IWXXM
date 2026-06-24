# QA Report — S004 / EV-004 (09-qa)

> Generated: 2026-06-24  
> Scope: Delta QA for GitHub [#555](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/555) UX + F5 work history + S003 config prerequisite  
> Branch: `feat/S004-issue-555-feedback`  
> Session: S004-issue-555-feedback | Evolve cycle: EV-004 | Features: F1, F5  
> Build status: **partial** — execution plan ~22/38 tasks; `07-build` still pending on routing plan

```text
QA Results (S004 delta + blocking connectivity):
  Lint (Python):  PASS — 0 issues
  Lint (JS):      FAIL — 4 errors (react-hooks/*)
  Format:         PASS — 404 files
  Typecheck:      PASS — 0 errors (basedpyright + tsc)
  Tests (Python): PASS — workspace 43, shared 57, backend 1143, auth 223, gifts 1010 (run separately)
  Tests (H0c):    PASS — 6/6 (tests/unit/test_cors_policy.py)
  Tests (H0i):    PASS — 8/8 (apps/backend/tests/integration/test_h0i_connectivity.py)
  Tests (FE):     FAIL — 444 passed, 1 failed (Vitest)
  Security:       PASS — 0 CVEs (lockfile); 0 tree leaks (gitleaks)
  Cross-file:     1 F841 (backend script); 0 cycles; 146 docstring gaps (advisory)
  Dependencies:   17 outdated (advisory); 0 missing
  Template:       PASS — static+api monorepo layout
  Config guard:   PASS — 8/8 (placeholders + H5 runtime config)
  env-check:      PASS with advisory (legacy SUPABASE_SERVICE_ROLE_KEY name)
  npm audit:      PASS — 0 vulnerabilities
  Connectivity:   H0c/H0i PASS; H4–H5 SKIPPED (no LIVE_* / staging URLs set)
  Live stack:     7 skipped (tests/integration — RUN_LIVE_TESTS unset)
```

**Overall: FAIL** — ESLint `react-hooks/*` violations and one Vitest regression block QA gate. Do not proceed to **11-verify-impl** sign-off until resolved.

---

## Executive summary

| Category | Status | Blocking |
|----------|--------|----------|
| Lint / format / typecheck (Python) | PASS | — |
| Lint (JS / ESLint) | **FAIL** | Yes |
| Unit tests (Python) | PASS | — |
| Unit tests (frontend Vitest) | **FAIL** | Yes |
| H0c CORS policy | PASS | Yes — green |
| H0i in-process connectivity | PASS | Yes — green |
| pip-audit (lockfile export) | PASS | — |
| gitleaks (pre-commit) | PASS | — |
| Config guard + env-check | PASS | — |
| npm audit (frontend) | PASS | — |
| Partial build scope | Advisory | QA-001 |
| H4–H5 live connectivity | SKIPPED | QA-002 |
| Live stack integration | SKIPPED | QA-003 |
| F841 unused variable (script) | Advisory | QA-004 |
| Public docstrings missing | Advisory | QA-005 |
| Outdated PyPI packages | Advisory | QA-006 |
| GIFTs tpg eval/exec | Advisory | QA-007 |
| Legacy env var name warning | Advisory | QA-008 |

---

## Blocking failures

### QA-BLK-001 — ESLint `react-hooks/*` (4 errors)

`make lint-js` fails with `react-hooks/set-state-in-effect` and `react-hooks/refs`:

| File | Line | Rule |
|------|------|------|
| `apps/frontend/src/app/App.tsx` | 110 | `set-state-in-effect` — `initializeWorkSessions` in `useEffect` |
| `apps/frontend/src/app/components/FileConverter.tsx` | 208 | `set-state-in-effect` — hydrate loaded work session |
| `apps/frontend/src/app/components/MyMetarsPage.tsx` | 57 | `set-state-in-effect` — `loadSessions()` in `useEffect` |
| `apps/frontend/src/hooks/useWorkSessionSync.ts` | 35 | `refs` — `sessionIdRef.current = sessionId` during render |

**Suggested action for 11:** Refactor to event-driven or layout-effect patterns, or narrowly scoped `eslint-disable` with ADR note per file.

### QA-BLK-002 — Vitest `requires auth token for Convert&Send`

```
FileConverter.test.tsx > requires auth token for Convert&Send
Expected: mockToast.error('Authentication required. Please log in again.')
Actual: toast not called (0 calls)
```

**Root cause:** `convert-and-send-button` is `disabled={convertDisabled || !accessToken}` when unauthenticated; click never reaches handler.

**Suggested action for 11:** Update test to assert disabled button + `aria-disabled`, **or** restore toast-on-click if product requires it.

---

## Commands run

```bash
# Lint / format / typecheck
uv run ruff check apps/backend/src apps/backend/tests packages/auth/src packages/auth/tests \
  packages/gifts/gifts packages/gifts/tests packages/shared packages/shared/tests tests
uv run ruff format --check apps packages tests
make typecheck
make lint-js

# Connectivity (blocking)
uv run pytest tests/unit/test_cors_policy.py -v
cd apps/backend && uv run pytest tests/integration/test_h0i_connectivity.py -v --no-cov

# Tests
make test-unit                    # fails at frontend; gifts blocked in chain
make test-unit-gifts              # 1010 passed separately

# Security
make secrets-check
uv export --frozen --no-dev -o /tmp/metar-deps.txt && uv run pip-audit -r /tmp/metar-deps.txt
uv run ruff check --select F401,F841 apps packages tests

# Config / audit
make config-guard env-check audit-frontend

# Integration (live — env-gated)
uv run pytest tests/integration -v
```

---

## Per-check details

### Python unit matrix

| Target | Result |
|--------|--------|
| Workspace pytest (`tests/migration`, `tests/unit`) | 43 passed |
| `packages/shared` (py) | 57 passed |
| `packages/shared` (js) | 4 passed |
| `apps/backend` | 1143 passed, 98.01% cov |
| `packages/auth` | 223 passed, 31 skipped |
| `packages/gifts` | 1010 passed, 1 skipped (not in `make test-unit` chain due to FE fail) |
| `apps/frontend` Vitest | **444 passed, 1 failed** |

### EV-004 delta coverage (passing subsets)

Work-session backend tests green when run as part of backend suite:

- `test_work_session_service_unit.py` — included in 1143-pass run
- `test_work_sessions_router_unit.py` — included in 1143-pass run

### Security

| Layer | Result |
|-------|--------|
| pip-audit (uv lockfile export) | 0 known vulnerabilities |
| gitleaks (pre-commit `--all-files`) | Passed |
| `pickle.loads` / `eval(` / `exec(` in `apps/` | None |
| `eval`/`exec` in `packages/gifts/gifts/common/tpg.py` | Present — upstream parser generator (advisory) |

### Template conformance (`static+api`)

| Criterion | Status |
|-----------|--------|
| Layout `apps/*`, `packages/*`, `tests/`, `vendor/` | PASS |
| No `import modal` outside infra | PASS (no Modal in this project) |
| Two deployables (API + static frontend) | PASS |
| CI `make validate-ci` parity paths | Matches Makefile targets |

### Data / deploy readiness

| Asset / gate | Status |
|--------------|--------|
| Supabase METAR project | present (per execution plan) |
| Local `supabase db reset` | verified (per execution plan) |
| Golden METAR fixtures | verified |
| `metar_work_sessions` migration | present; live migration test skipped without `RUN_LIVE_TESTS` |
| Phase 1 S003 gate (T1.1–T1.4) | **pending** — several M1 tasks still open |
| H4–H5 staging connectivity | SKIPPED — `METAR_STAGING_*` / `LIVE_*` not set this run |

---

## Findings for 11-verify-impl

| ID | Severity | Finding | Suggested action |
|----|----------|---------|------------------|
| QA-BLK-001 | **blocking** | 4 ESLint `react-hooks/*` errors in F5 work-session UI | Refactor effects/refs or scoped disable with justification |
| QA-BLK-002 | **blocking** | Vitest `requires auth token for Convert&Send` | Align test with disabled-button UX or restore toast behavior |
| QA-001 | advisory | Build ~22/38 tasks; `07-build` routing pending | Complete remaining milestones before full sign-off |
| QA-002 | advisory | H4–H5 live connectivity not exercised | Run `make test-live-connectivity` with staging URLs before deploy |
| QA-003 | advisory | `tests/integration` 7/7 skipped | Set `RUN_LIVE_TESTS=1` + credentials for live stack smoke |
| QA-004 | advisory | F841 in `apps/backend/scripts/generate_test_data.py:210` | Remove unused `test_cases` or use it |
| QA-005 | advisory | 146 Python files with public symbols lacking docstrings | Defer or scoped doc pass |
| QA-006 | advisory | 17 outdated PyPI packages (e.g. fastapi 0.137→0.138) | Intentional pins per dependency-inventory; bump via ADR if needed |
| QA-007 | advisory | `eval`/`exec` in GIFTs `tpg.py` | Upstream; document as accepted risk |
| QA-008 | advisory | `env-check` warns `SUPABASE_SERVICE_ROLE_KEY` without canonical `SUPABASE_SECRET_KEY` | Complete S003 M1 key migration |

---

## Phase / execution-plan alignment

| Phase | Gate | QA status |
|-------|------|-----------|
| Phase 1 S003 | T1.1–T1.4 pending | Not gated PASS — config tasks open |
| Phase 2 #555 UX | T2.1–T2.5 | Code present; blocked by QA-BLK-002 test |
| Phase 3 F5 backend | M3 tasks | Backend tests green |
| Phase 4 F5 frontend | M4 tasks | Blocked by QA-BLK-001 lint |
| Phase 5 E2E | M5 | Deferred to **10-e2e** after blocking fixes |

---

## Handoff

**11-verify-impl** should:

1. Walk user through **QA-BLK-001** and **QA-BLK-002** first — both must be green before feature approval.
2. Present advisories QA-001–QA-008 for approve / defer / fix-now.
3. Re-run `make lint` + `make test-unit` after fixes; QA re-run optional if only delta files touched.
