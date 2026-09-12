# E2E Behavior Report — S006 / EV-005 (10-e2e delta)

> Generated: 2026-06-25  
> Session: S006-issue-664-output-filename  
> Branch: `feat/S006-issue-664-output-filename`  
> Mechanism: mixed (pytest T0/T1 + Playwright T2)  
> Scope: UJ-001 delta (#664 custom output filename for manual METAR input; F1 extended, F5 persist)

## Summary

| # | Journey / gate | Mechanism | T0 | T2 connectivity | T3 browser/live | Status |
|---|----------------|-----------|----|-----------------|-----------------|--------|
| 1 | H0c CORS policy | pytest | ✓ | — | — | **PASS** (6/6) |
| 2 | H0i in-process wiring | pytest | ✓ | — | — | **PASS** (8/8) |
| 3 | UJ-001 core conversion | Playwright | — | ✓ | — | **PASS** (8/8) |
| 4 | UJ-003 auth API integration | Playwright | — | ✓ | — | **PASS** (4/4) |
| 5 | UJ-001 delta — #664 custom filename | Playwright | — | ✓ | — | **PASS** (1/1) |
| 6 | H4–H5 live connectivity | pytest/curl | — | skipped | — | **SKIP** (no staging URLs) |
| 7 | T3 live UJ-001–004 | Playwright live | — | — | skipped | **SKIP** (deferred to deploy) |

**Overall (S006 delta)**: **PASS** — #664 custom output filename journey green in T2 Playwright; T0/T1 connectivity green; T3 deferred per routing plan.

---

## Journey Details

### H0c — CORS policy (`tests/unit/test_cors_policy.py`)

- **Feature**: M4
- **Mechanism**: pytest (in-process)
- **Result**: **6/6 PASS**

### H0i — In-process connectivity (`test_h0i_connectivity.py`)

- **Feature**: M4, F1, F5
- **Mechanism**: TestClient
- **Result**: **8/8 PASS** — CORS preflight, auth+convert wiring, health, versions.

### UJ-001 — Core TAC conversion (`tac-file-conversion.e2e.spec.ts`)

- **Feature**: F1
- **Command**:

```bash
# Pre-start dev stack (see infra note below), then:
cd apps/e2e && METAR_CONFIG_ENV=local \
  PLAYWRIGHT_API_BASE_URL=http://localhost:18001 \
  PLAYWRIGHT_BASE_URL=http://127.0.0.1:18000 \
  pnpm exec playwright test tac-file-conversion.e2e.spec.ts --reporter=list
```

- **Result**: **8/8 PASS** (39.9s)

| Step | Description | Status |
|------|-------------|--------|
| 1 | Manual METAR converts to IWXXM | PASS |
| 2 | COR METAR produces correction output | PASS |
| 3 | ICAO COR-after-time METAR produces correction | PASS |
| 4 | Clear removes manual input | PASS |
| 5 | Mocked success shows notification + results | PASS |
| 6 | **#664** custom output filename names manual results | **PASS** |
| 7 | Mocked empty conversion shows no-files notification | PASS |
| 8 | Mocked 401 shows authentication notification | PASS |

### UJ-001 delta — #664 custom output filename (`tac-file-conversion.e2e.spec.ts`)

- **Feature**: F1 (EV-005), F5 (persist via `conversion_params`)
- **Mechanism**: Playwright (mocked `/api/v1/convert`, mock session)
- **Steps**:
  1. Fill **Output filename** field with `report` — **PASS**
  2. Enter two-line manual METAR text — **PASS**
  3. Click Convert — results region visible — **PASS**
  4. Result cards show `report_1.txt` and `report_2.txt` — **PASS**
  5. Download button `download report_1.txt as xml` visible — **PASS**
- **Assessment**: Custom base name with `_1/_2` multi-line suffix applied to manual-result labels and download affordances per UJ-001 step 4/9.

### UJ-003 — Auth API integration (`auth-service-integration.e2e.spec.ts`)

- **Feature**: F1 (auth)
- **Result**: **4/4 PASS** (10.1s) — frontend boots, merged API health, auth routes on same host, no 400 bootstrap requests.

### T3 — Live Render stack

- **Status**: **SKIPPED** — `RUN_LIVE_TESTS` / `LIVE_*` not exercised in this session (optional `12-verify-deploy` / `13-deploy-smoke` per routing plan).
- **Handoff**: Run `make test-live` after frontend deploy for full T3 sign-off.

---

## Infrastructure note (Playwright webServer)

Playwright's bundled `webServer` (`start-dev-servers.sh --kill`) timed out after 300s when `PLAYWRIGHT_BASE_URL` defaulted to `http://localhost:18000`, even though Vite/Uvicorn logs showed startup complete. Pre-starting the dev stack with `nohup ./start-dev-servers.sh --kill` and setting `PLAYWRIGHT_BASE_URL=http://127.0.0.1:18000` allowed `reuseExistingServer` to skip webServer and all tests passed.

**Advisory for 11-verify-impl**: Document or fix localhost vs 127.0.0.1 webServer readiness in CI/dev environments if Playwright cold-start regressions recur.

---

## Feature traceability (EV-005)

| Requirement | E2E evidence |
|-------------|--------------|
| R1 — Frontend-only | Playwright exercises UI field + mocked convert (no API contract change) |
| R2 — Blank ⇒ `manual_input` | Covered in Vitest (`outputFilename.test.ts`); not re-asserted in this Playwright spec |
| R3 — Manual only | Playwright spec uses manual textarea path only |
| R4 — Multi-line `_1/_2` | **PASS** — `report_1.txt`, `report_2.txt` visible |
| R5 — Persist across reload | Vitest `FileConverter.test.tsx`; not in this Playwright spec |
| R7 — ZIP archive custom base | Vitest `outputArchiveName()`; download click not exercised in Playwright |

---

## Handoff

Proceed to **11-verify-impl**. No blocking E2E failures for S006. T3 live browser verification deferred until optional deploy stages.
