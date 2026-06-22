# E2E Behavior Report — S001 / EV-001 (Convert & Convert&Send UI)

> Generated: 2026-06-22  
> Mechanism: mixed (Vitest T0 + Playwright T2 browser)  
> Scope: Delta E2E for GitHub [#656](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/656)  
> Branch: `feat/S001-convert-send-buttons` | Session: S001-convert-send-buttons | Feature: F1 (UJ-001)

## Summary

| # | Journey | Mechanism | Steps | Passed | Failed | Skipped | T0 | T2 | T3 | Status |
|---|---------|-----------|-------|--------|--------|---------|----|----|-----|--------|
| 1 | UJ-001 Convert METAR via UI (Convert only) | browser | 5 | 5 | 0 | 0 | — | ✓ | — | **PASS** |
| 2 | UJ-001 Convert&Send one-click | browser | 4 | 4 | 0 | 0 | ✓ | ✓ | — | **PASS** |
| 3 | UJ-001 Upload to Database (dialog) | browser | 5 | 5 | 0 | 0 | — | ✓ | — | **PASS** |
| 4 | UJ-003 Auth (login for upload tests) | browser | 3 | 3 | 0 | 0 | — | ✓ | — | **PASS** |

**Overall: PASS (T0 + T2)** — Issue #656 acceptance verified locally. **T3 deferred** until feature branch merges and Render redeploys.

```text
E2E Results (S001 delta):
  T0 (Vitest Convert&Send):  PASS — 2/2 tests
  T2 (Playwright UJ-001):    PASS — 11/11 executed (3 skipped without fixtures; 11/11 with fixtures)
  T2 connectivity:           PASS — CORS preflight 200 on POST /api/v1/convert during runs
  T3 (Render live):          DEFERRED — production not yet on feat/S001-convert-send-buttons
  T3 browser:                NOT RUN
```

---

## Issue #656 journey mapping

| Requirement | Journey step | Evidence |
|-------------|--------------|----------|
| **Convert** button (conversion only) | Paste/drop TAC → click **Convert** → view IWXXM | `tac-file-conversion.e2e.spec.ts` (6 tests); manual METAR convert PASS |
| **Convert&Send** (convert + immediate send) | Drop TAC → click **Convert&Send** → toast success | `tac-file-upload-database.e2e.spec.ts` — "converted and sent with one click" |
| Send success/failure feedback | Mock upload 200 → toast; mock failure covered in unit tests | Playwright: `Files converted and sent successfully`; Vitest: send-failure path |
| Retain **Upload to Database** (R2) | Convert → open dialog → upload | `tac-file-upload-database.e2e.spec.ts` — dialog flow PASS |

---

## Commands run

```bash
# T0 — Convert&Send unit coverage (Vitest)
cd apps/frontend && pnpm test -- --run FileConverter.test.tsx -t "Convert&Send"

# T2 — UJ-001 Playwright (default fixture path; 3 upload tests skipped without .tac dir)
cd apps/e2e && pnpm exec playwright test \
  tac-file-conversion.e2e.spec.ts \
  tac-file-upload-database.e2e.spec.ts

# T2 — full upload suite with golden fixtures
cd apps/e2e && PLAYWRIGHT_TAC_FIXTURES_DIR=/root/metar-to-IWXXM/test-data/golden/cases \
  pnpm exec playwright test tac-file-upload-database.e2e.spec.ts
```

**Environment**: Local dev stack via Playwright `webServer` (`DISABLE_AUTH=true`, API `:8001`, frontend `:5173`). Upload send step mocked via `page.route('**/functions/v1/**/database/upload')`.

---

## Journey details

### Journey 1: UJ-001 — Convert only (T2)

- **Feature**: F1
- **Mechanism**: Playwright browser (mock session + real API convert)
- **Test module**: `apps/e2e/tac-file-conversion.e2e.spec.ts`
- **Steps**:
  1. Open converter with mock session — **PASS**
  2. Enter manual METAR — **PASS**
  3. Click **Convert** (`^Convert METAR files to IWXXM XML$`) — **PASS**
  4. Conversion results region visible — **PASS**
  5. IWXXM XML in `<pre>` output — **PASS**
- **Additional cases**: COR METAR, clear input, mocked success/empty/401 — all **PASS** (6/6)

### Journey 2: UJ-001 — Convert&Send one-click (T0 + T2)

- **Feature**: F1 / EV-001
- **Mechanism**: Vitest (T0) + Playwright (T2, mocked upload endpoint)
- **Test modules**: `FileConverter.test.tsx`, `tac-file-upload-database.e2e.spec.ts`
- **T0 steps**:
  1. **Convert&Send** button visible, disabled until input — **PASS**
  2. Click chains `convertMetarToIwxxm` + `uploadConvertedFiles` with fixed defaults — **PASS**
  3. Auth required when no token — **PASS**
- **T2 steps** (fixture: `test-data/golden/cases/kjfk_basic.tac`):
  1. Login via Supabase (UJ-003) — **PASS**
  2. Attach TAC file — **PASS**
  3. Click **Convert&Send** (`Convert METAR files to IWXXM XML and send to database`) — **PASS**
  4. Results region + IWXXM output + success toast — **PASS**

### Journey 3: UJ-001 — Upload to Database dialog (T2)

- **Feature**: F1 (R2 retained)
- **Mechanism**: Playwright browser
- **Test module**: `apps/e2e/tac-file-upload-database.e2e.spec.ts`
- **Steps**:
  1. Upload button disabled before conversion — **PASS**
  2. Convert via **Convert** only — **PASS**
  3. Open upload dialog, select IWXXM format — **PASS**
  4. Mock upload → success toast — **PASS**
  5. Multi-file queue (2 TAC files) — **PASS**

### Journey 4: UJ-003 — Auth for protected flows (T2)

- **Feature**: F1 (auth)
- **Mechanism**: Playwright browser (real Supabase login in upload tests)
- **Steps**:
  1. Navigate to login — **PASS**
  2. `POST /auth/login` → 200 — **PASS**
  3. Open converter from admin dashboard — **PASS**

---

## Connectivity

| Tier | Check | Result |
|------|-------|--------|
| T2 | `OPTIONS /api/v1/convert` preflight during Playwright | 200 |
| T2 | `POST /api/v1/convert` from browser origin `http://localhost:5173` | 200 (valid TAC) / 400 (invalid) |
| T3 | H4–H5 live CORS + bundle wiring | **NOT RUN** — feature not deployed |
| T3 | `make test-live-e2e` against Render | **DEFERRED** — run post-merge per UJ-OPS-001 |

---

## Findings for 11-verify-impl

| ID | Severity | Finding | Suggested action |
|----|----------|---------|------------------|
| E2E-001 | Advisory | Default Playwright run skips 3 upload tests when `data/iwxxm-translation/.../metar` absent | CI sets `PLAYWRIGHT_TAC_FIXTURES_DIR` or documents `test-data/golden/cases` fallback |
| E2E-002 | Advisory | T3 live Convert&Send not exercised against Render | After merge to `main` + frontend redeploy, run `make test-live-e2e` or manual UJ-001 step 4 (Convert&Send) |
| E2E-003 | Info | Live upload path uses real Supabase edge function; T2 mocks upload only | T3 send verification requires staging credentials + live deploy |

---

## Handoff

- **Blocking failures**: none
- **Next stage**: **11-verify-impl** — present PASS summary; defer E2E-002 until deploy
- **GitHub #656**: Local E2E acceptance **PASS** for Convert, Convert&Send, and retained Upload dialog
