# Verification Report — S004 / EV-004 (08-verify-build)

> Generated: 2026-06-24  
> Scope: EV-004 delta (`feat/S004-issue-555-feedback`)  
> Branch: `feat/S004-issue-555-feedback`

## Summary

| Check | Status | Findings | Auto-Fixed | Tool |
|-------|--------|----------|------------|------|
| Lint (Python) | PASS | 0 | — | `ruff check` |
| Lint (JS) | **FAIL** | 4 errors | 1 (`prefer-const` in e2e spec) | `eslint` |
| Format | PASS | 2 (ruff) | 2 | `make format` |
| Typecheck | PASS | 0 | — | `basedpyright` + `tsc` |
| Tests (unit) | **FAIL** | 1 failed | — | `make test-unit` |
| CORS policy (H0c) | PASS | 6/6 | — | `tests/unit/test_cors_policy.py` |
| Integration (local) | PASS* | 6 pass, 7 skip | — | `tests/integration` |
| Connectivity artifacts | PASS | Present | — | See below |
| Security (secrets) | PASS | 0 | — | `gitleaks` |
| Security (pip-audit) | PASS | 0 on lockfile | — | `uv export` + `pip-audit` |
| Performance | SKIPPED | — | — | — |
| Data integrity | SKIPPED | — | — | — |
| Template conformance | PASS | `static+api` layout | — | manual |

**Overall: FAIL** — ESLint `react-hooks/*` violations and one Vitest regression block the gate.

## Auto-corrections applied

| Item | Action |
|------|--------|
| `apps/backend/src/services/work_session_service.py` | `ruff format` |
| `tests/integration/test_metar_work_sessions_migration.py` | `ruff format` |
| `apps/e2e/metar-work-history.e2e.spec.ts` | `prefer-const` via `eslint --fix` |
| Multiple frontend/e2e TSX | Prettier (work-session delta files) |

## Unit test matrix

| Target | Result | Notes |
|--------|--------|-------|
| Workspace pytest | PASS | 43/43 |
| `packages/shared` (py) | PASS | 57/57 |
| `packages/shared` (js) | PASS | 4/4 |
| `apps/backend` | PASS | 1143/1143, 98.01% cov |
| `packages/auth` | PASS | 223 passed, 31 skipped |
| `apps/frontend` | **FAIL** | 444 passed, **1 failed** |
| `packages/gifts` | **NOT RUN** | Blocked by frontend failure in `make test-unit` chain |

### Failed test

```
FileConverter.test.tsx > requires auth token for Convert&Send
Expected: mockToast.error('Authentication required. Please log in again.')
Actual: toast not called (0 calls)
```

**Likely cause:** `convert-and-send-button` is now `disabled={convertDisabled || !accessToken}` when unauthenticated, so the click never reaches the handler that calls `toast.error`. Test expects pre-disable behavior.

## Lint failures (manual)

| File | Rule | Issue |
|------|------|-------|
| `apps/frontend/src/app/App.tsx:114` | `react-hooks/set-state-in-effect` | `initializeWorkSessions` in `useEffect` |
| `apps/frontend/src/app/components/FileConverter.tsx:212` | `react-hooks/set-state-in-effect` | Hydrate loaded work session in `useEffect` |
| `apps/frontend/src/app/components/MyMetarsPage.tsx:57` | `react-hooks/set-state-in-effect` | `loadSessions()` in `useEffect` |
| `apps/frontend/src/hooks/useWorkSessionSync.ts:35` | `react-hooks/refs` | `sessionIdRef.current = sessionId` during render |

## Connectivity (stage 08 blocking)

| Artifact | Status |
|----------|--------|
| `tests/unit/test_cors_policy.py` | PASS (6/6) |
| `tests/smoke/test_staging_connectivity.py` | Present (not re-run live) |
| `scripts/deploy/verify_connectivity.sh` | Present |
| `apps/backend/src/api.py` `CORSMiddleware` | Configured via `get_cors_origins()` |

`tests/integration/test_live_stack.py` and migration smoke skipped without `RUN_LIVE_TESTS=1` — expected for local verify-build.

## Security

- **gitleaks:** PASS (no committed secrets).
- **pip-audit:** Raw `uv run pip-audit` audited system Python 3.11 (143 CVEs — unrelated packages). **Project lockfile** via `uv export --frozen --no-dev` → **0 known vulnerabilities**.

## EV-004 delta coverage (passing subsets)

Work-session backend unit tests all green:

- `test_work_session_service_unit.py` — 19/19
- `test_work_sessions_router_unit.py` — 9/9
- Included in backend 1143-pass run

## Advisory

- `make test-integration` (docker compose on 18000/18001) not run — prior sessions report port conflicts with `vecinita-*` stack; CI uses clean ports.
- `packages/gifts` unit suite should be re-run after frontend fix confirms full `make test-unit` chain.

## Required actions before 09-qa

1. Resolve ESLint `react-hooks/*` (suppress with justification, refactor, or eslint-disable per file with ADR note).
2. Fix `requires auth token for Convert&Send` — update test to assert disabled button **or** restore toast-on-click behavior.
3. Re-run `make lint` + `make test-unit` to confirm green.
