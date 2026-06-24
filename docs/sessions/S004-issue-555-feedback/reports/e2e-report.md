# E2E Behavior Report — S004 / EV-004 (10-e2e delta)

> Generated: 2026-06-24  
> Session: S004-issue-555-feedback  
> Branch: `feat/S004-issue-555-feedback`  
> Mechanism: mixed (pytest T0 + Playwright T2 + live HTTP T3)  
> Scope: UJ-001 delta (#555 replace results + error log), UJ-004 work history (F1, F5)

## Summary

| # | Journey / gate | Mechanism | T0 | T2 connectivity | T3 browser/live | Status |
|---|----------------|-----------|----|-----------------|-----------------|--------|
| 1 | H0e env-check | shell | — | — | — | **PASS** (legacy key WARN) |
| 2 | H0i in-process wiring | pytest | ✓ | — | — | **PASS** (8/8) |
| 3 | UJ-001 core conversion | Playwright | — | ✓ | — | **PASS** (tac-file-conversion 8/8 subset) |
| 4 | UJ-003 auth API integration | Playwright | — | ✓ | — | **PASS** (4/4) |
| 5 | UJ-001 delta — replace results | Playwright | — | partial | — | **FAIL** (locator strict mode; behavior likely OK) |
| 6 | UJ-001 delta — error log panel | Playwright | — | partial | — | **FAIL** (locator strict mode; panel visible) |
| 7 | UJ-004 — auto-save indicator | Playwright | — | ✓ | — | **PASS** |
| 8 | UJ-004 — finished read-only | Playwright | — | ✗ | — | **FAIL** (buttons disabled for empty input; banner absent) |
| 9 | H4 staging CORS | pytest live | — | ✗ | — | **FAIL** (400 Disallowed CORS origin) |
| 10 | H5 runtime config | curl | — | — | skipped | **SKIP** (H4 gate aborted script) |
| 11 | H3 live API | pytest live | — | — | partial | **BLOCKED** (8 skipped — legacy Supabase keys) |

**Overall (S004 delta)**: **FAIL** — core UJ-001 conversion and UJ-004 auto-save pass locally; delta Playwright specs need locator/session-load fixes; staging H4 CORS and live auth remain blocked pending deploy.

---

## Journey Details

### H0e — Env contract (`make env-check`)

- **Feature**: F3
- **Result**: **PASS** — `config/local.json` valid; advisory WARN for legacy `SUPABASE_SERVICE_ROLE_KEY`.

### H0i — In-process connectivity (`test_h0i_connectivity.py`)

- **Feature**: M4, F5
- **Mechanism**: TestClient
- **Result**: **8/8 PASS** — CORS preflight (convert, auth, work-sessions PATCH/DELETE), auth+convert wiring, health, versions.

### UJ-001 — Core TAC conversion (`tac-file-conversion.e2e.spec.ts` + `auth-service-integration.e2e.spec.ts`)

- **Feature**: F1
- **Command**: `PLAYWRIGHT_BASE_URL=http://localhost:18000 PLAYWRIGHT_API_BASE_URL=http://localhost:18001 METAR_CONFIG_ENV=local playwright test tac-file-conversion.e2e.spec.ts auth-service-integration.e2e.spec.ts`
- **Result**: **11/11 PASS**
- **Note**: Work-session API calls return 502 (mock JWT vs Supabase) during guest convert paths — conversion UX unaffected with `disableAuth:true`.

### UJ-001 delta — #555 replace results (`issue-555-ux-delta.e2e.spec.ts`)

- **Feature**: F1 (EV-004)
- **Steps**:
  1. Convert METAR A (KJFK) — results region visible — **PASS**
  2. Convert METAR B (KDEN) — KJFK absent from results — **PASS** (`toHaveCount(0)`)
  3. Assert KDEN visible in results region — **FAIL** (Playwright strict mode: 2 elements match `/KDEN/i` — TAC pre + IWXXM XML)
- **Assessment**: Product behavior matches #555 (replace, not append). Failure is test locator specificity, not functional regression.

### UJ-001 delta — error log panel (`issue-555-ux-delta.e2e.spec.ts`)

- **Feature**: F1 (EV-004)
- **Steps**:
  1. Mock `/api/v1/convert` with `errors: ['Invalid METAR syntax']` — **PASS**
  2. Error log region (`aria-label` Conversion error log) visible — **PASS**
  3. `getByText(/Invalid METAR syntax/)` — **FAIL** (strict mode: 3 elements — panel list, inline error, toast)
- **Assessment**: Error log UX present; narrow locator to panel region.

### UJ-004 — Auto-save indicator (`metar-work-history.e2e.spec.ts`)

- **Feature**: F5
- **Mechanism**: Playwright with mocked `work-sessions` API
- **Result**: **PASS** — `autosave-indicator` visible with "saved" text after debounce.

### UJ-004 — Finished session read-only (`metar-work-history.e2e.spec.ts`)

- **Feature**: F5
- **Steps**:
  1. Mock list with `status: finished` session — **PASS** (route)
  2. `convert-button` disabled — **PASS**
  3. `convert-and-send-button` disabled — **PASS**
  4. Read-only banner (`/read-only/i`) — **FAIL** (not in DOM)
- **Root cause**: Test opens converter without loading the mocked finished session into `loadedWorkSession`. Buttons disabled because `!hasInput` (`convertDisabled = isBusy || !hasInput || isReadOnly`), not because `isReadOnly` is true. Vitest coverage (`FileConverter.work-session.test.tsx`) asserts banner when session status is `finished`.

### T3 — Staging connectivity (H4)

- **Command**: `make test-live-connectivity`
- **H0c**: **PASS** (6/6 unit CORS policy)
- **H4**: **FAIL** — `OPTIONS /health` and `OPTIONS /api/v1/work-sessions` return `400 Disallowed CORS origin` for `https://metar-to-iwxxm-frontend-v4-web.onrender.com`
- **H5**: **SKIP** — script exits on H4 failure (`set -e`)
- **Likely cause**: Render API `METAR_CORS_ORIGINS` / `config.prod.json` not deployed or stale vs v4 frontend URL.

### T3 — Live API (H3 subset)

- **Command**: `make test-live-api`
- **Result**: **13 passed, 8 skipped**
- **Blocker**: `POST /auth/login` → `Legacy API keys are disabled` (unchanged from S003; publishable/secret keys not on Render).

---

## Tier matrix (connectivity gates)

| Tier | Command | Result | Notes |
|------|---------|--------|-------|
| T0 / H0i | `pytest apps/backend/tests/integration/test_h0i_connectivity.py` | PASS | 8/8 |
| H0e | `make env-check` | PASS | Legacy key WARN |
| T2 product | `tac-file-conversion` + `auth-service-integration` | PASS | 11/11 (pre-started dev stack) |
| T2 delta UJ-001 | `issue-555-ux-delta.e2e.spec.ts` | FAIL | 0/2 — locator strict mode |
| T2 delta UJ-004 | `metar-work-history.e2e.spec.ts` | PARTIAL | 1/2 — auto-save PASS |
| T2 webServer cold start | `playwright test` with `webServer` | FAIL | 180s timeout (DB init); use pre-started stack or increase timeout |
| T2 connectivity H4 | `make test-live-connectivity` | FAIL | Staging CORS origin rejected |
| T3 live auth | `make test-live-api` auth cases | BLOCKED | Legacy keys on Render |

---

## Findings for 11-verify-impl

1. **E2E-S004-001** — `issue-555-ux-delta.e2e.spec.ts`: use `.first()` or scope assertions to results region / error log panel (strict mode violations; product behavior appears correct).
2. **E2E-S004-002** — `metar-work-history.e2e.spec.ts` finished-session test must load mocked finished session (sidebar click or direct hydrate) before asserting read-only banner.
3. **E2E-S004-003** — Playwright `webServer` 180s timeout insufficient when Supabase DB init runs on cold start; document pre-start via `start-dev-servers.sh` or extend timeout.
4. **E2E-S004-004** — Staging H4 CORS fail blocks F5 browser auto-save against live API until Render redeploy with v4 frontend origin.
5. **E2E-S004-005** — T3 UJ-001–004 deferred until S003 key rotation + H4 green (carried from prior sessions).
6. **Positive** — #555 replace-results behavior verified (KJFK cleared on second convert); error log region renders; UJ-004 auto-save indicator works with mocked API.

## Waivers

None recorded for S004 delta. T3 full browser UJ suite remains deferred per prior staging auth/CORS blockers.

## Related reports

- `docs/sessions/S004-issue-555-feedback/reports/qa-report.md` — ESLint + Vitest still blocking upstream gates
- `docs/sessions/S003-supabase-keys-config/reports/e2e-report.md` — live auth baseline
