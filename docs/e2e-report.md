# E2E Behavior Report

> Generated: 2026-06-20  
> Mechanism: mixed (pytest T0/T1, Playwright T2, HTTP + browser MCP T3)  
> Branch: `main`  
> Journeys tested: 7 (UJ-001–003, UJ-DEV-001–003, UJ-OPS-001)

## Summary

| # | Journey | Feature | Mechanism | T0 | T2 | T3 | Status |
|---|---------|---------|-----------|----|----|-----|--------|
| 1 | Convert METAR via UI | F1 | browser | — | PASS (5/5 specs) | BLOCKED | **PARTIAL** |
| 2 | Validate IWXXM output | F2 | API | — | PASS (7/7) | NOT RUN | **PASS (T2)** |
| 3 | Register and login | F1 (auth) | browser | — | PARTIAL (2 pass, 1 skip) | PARTIAL | **PARTIAL** |
| 4 | Clone and run monorepo | M1, M5 | shell/pytest | PASS | — | — | **PASS** |
| 5 | Sync vendor schemas | M2, M6 | pytest | PASS (14/14) | — | — | **PASS** |
| 6 | Merge GIFTs upstream | M3 | pytest | PASS (TC-M003) | — | — | **PASS** |
| 7 | Deploy Render stack | M4 | HTTP + browser | — | — | PARTIAL | **PARTIAL** |

**Overall: FAIL** — T2 product journeys green locally; T3 blocked on staging auth deployment gap and legacy schema path regression.

### Connectivity tiers (stage 10)

| Tier | Scope | Result |
|------|-------|--------|
| T0 | Migration gates, vendor integrity, workspace smoke | **PASS** (41+ tests) |
| T1 | H0i integration (`apps/backend/tests/integration/test_h0i_connectivity.py`) | **PASS** (7/7) |
| T2 | Playwright `make test-e2e-t2-product` | **PASS** (8 passed, 1 skipped) |
| T2 connectivity | H0c + H4 + H5 via `scripts/deploy/verify_connectivity.sh` | **PASS** |
| T3 browser | Staging frontend login shell + validation | **PARTIAL** |
| T3 API | Staging health + convert (no auth) | **PASS** (3/5 live pytest; auth route missing) |

---

## Commands run

```bash
# T0 — migration + vendor
uv run pytest tests/migration/test_m7_t2_product_e2e.py tests/vendor/ -v --no-cov
uv run pytest tests/migration/test_tc_m003_golden_conversion.py \
  tests/migration/test_tc_m004_no_submodule_refs.py \
  tests/migration/test_tc_m005_auth_merge.py -v --no-cov
uv run pytest tests/migration/test_m7_e2e_layout.py \
  tests/migration/test_workspace_import_smoke.py -v --no-cov

# T1 — H0i
cd apps/backend && uv run pytest tests/integration/test_h0i_connectivity.py -v --no-cov

# UJ-002 validation
cd apps/backend && uv run pytest tests/validation/test_validation_e2e.py -v --no-cov

# T2 — Playwright product journeys
make test-e2e-t2-product

# T2/T3 connectivity
STAGING_API_URL=https://metar-to-iwxxm-api.onrender.com \
STAGING_FRONTEND_ORIGIN=https://metar-to-iwxxm-frontend-v4-web.onrender.com \
STAGING_FRONTEND_URL=https://metar-to-iwxxm-frontend-v4-web.onrender.com \
VITE_API_BASE_URL=https://metar-to-iwxxm-api.onrender.com \
  bash scripts/deploy/verify_connectivity.sh

# T3 — live API smoke
uv run pytest tests/test_playwright_e2e.py -v --tb=short
```

Staging URLs: API `https://metar-to-iwxxm-api.onrender.com`, frontend `https://metar-to-iwxxm-frontend-v4-web.onrender.com`.

---

## Journey details

### UJ-001: Convert METAR via UI (F1)

- **Mechanism**: browser (Playwright T2); browser MCP (T3 partial)
- **T2 steps**:
  1. Dev stack starts via Playwright `webServer` — **PASS**
  2. Manual METAR input converts to IWXXM — **PASS** (`tac-file-conversion.e2e.spec.ts`)
  3. COR METAR produces correction output — **PASS**
  4. Clear removes manual input — **PASS**
  5. Mocked success/error/auth notifications — **PASS** (3 specs)
- **T3 steps**:
  1. Staging frontend loads login gate — **PASS** (browser MCP)
  2. Full conversion journey — **BLOCKED** (requires authenticated session; staging API has no `/auth/*` routes)
- **Note**: Dev server logs Schematron warnings — schema resolver still points at `apps/backend/schemas/` instead of `vendor/schemas/` (see E2E-001).

### UJ-002: Validate IWXXM Output (F2)

- **Mechanism**: API (pytest)
- **T2 steps**:
  1. Validation workflow with valid ICAO — **PASS**
  2. Invalid ICAO blocked — **PASS**
  3. Evaluation/XML comparison — **PASS**
  4. Edge-case TAC syntax — **PASS**
  5. Airport data loading — **PASS**
- **Result**: 7/7 in `apps/backend/tests/validation/test_validation_e2e.py`

### UJ-003: Register and Login (F1 auth)

- **Mechanism**: browser + API
- **T2 steps**:
  1. Login page loads — **PASS** (`auth.e2e.spec.ts`)
  2. Empty login validation messages — **PASS**
  3. Admin login reaches dashboard — **SKIPPED** (requires `ADMIN_EMAIL`/`ADMIN_PASSWORD` in CI/local env)
- **T3 steps**:
  1. Staging login page renders (“METAR Converter” heading) — **PASS** (browser MCP)
  2. Empty submit shows “Email is required” / “Password is required” — **PASS** (browser MCP)
  3. `POST /auth/login` on staging API — **FAIL** (404; auth routers not in deployed OpenAPI)
  4. Legacy `metar-to-iwxxm-auth-v2` service — **FAIL** (503 Service Suspended; `tests/test_playwright_e2e.py`)

### UJ-DEV-001: Clone and Run Monorepo (M1, M5)

- **Mechanism**: pytest layout + import smoke
- **Steps**:
  1. Workspace members importable (backend, auth, gifts, shared) — **PASS**
  2. pnpm workspace discovers `@metar/shared` — **PASS**
  3. E2E specs relocated to `apps/e2e/` — **PASS** (M7 layout gate, 17 checks)
- **TC-M001**: Covered by workspace import smoke; full `make test-unit` not re-run in this stage (09-qa reported flaky in full migration collection).

### UJ-DEV-002: Sync Vendor Schemas (M2, M6)

- **Mechanism**: pytest (`tests/vendor/`)
- **Steps**:
  1. Manifest integrity — **PASS**
  2. Required schema bundles present (2025-2, 2023-1, codelists, modelling, translation) — **PASS**
- **Result**: 14/14 (TC-M002)

### UJ-DEV-003: Merge GIFTs Upstream (M3)

- **Mechanism**: pytest golden conversion
- **Steps**:
  1. Golden fixture set converts with zero unexpected diffs — **PASS** (TC-M003, 6 fixtures)
  2. TC-M004 no submodule refs — **PASS**
  3. TC-M005 auth merge in-process — **PASS** (3 integration checks)

### UJ-OPS-001: Deploy Two-Service Render Stack (M4)

- **Mechanism**: HTTP + browser
- **Steps**:
  1. H1 health — **PASS** (`GET /health` → 200, `gifts_available: true`)
  2. H4 CORS preflight — **PASS** (`tests/smoke/test_staging_connectivity.py`)
  3. H5 bundle embeds `VITE_API_BASE_URL` — **PASS** (no deprecated auth URLs)
  4. UJ-001 against staging — **BLOCKED** (auth routes absent on deployed API)
  5. OpenAPI on staging lists 17 paths — **PASS** (no `/auth/*`)

---

## Failures and advisories

### E2E-001 — Schema path regression (blocking for full UJ-002 schematron)

**Tests**: `tests/integration/test_product_regression_smoke.py` (2 failed)

```
FileNotFoundError: Schema file not found:
  apps/backend/schemas/iwxxm/2025-2/IWXXM/iwxxm.xsd
```

Post-migration schemas live under `vendor/schemas/`; resolver still references legacy `apps/backend/schemas/`. Dev Playwright run also logged Schematron/WMO codelist setup warnings. Conversion succeeds but validation layers fail.

**Impact**: UJ-001 T2 passes conversion UI; schema/schematron validation incomplete until paths fixed.

### E2E-002 — Staging auth not deployed (blocking T3 UJ-001/003)

Deployed API OpenAPI has no `/auth/login`. Frontend login UI renders but cannot complete session against staging. Legacy separate auth service is suspended (503).

**Impact**: T3 full product journeys cannot pass until backend redeploy includes merged auth routes (M4 / TC-M005 behavior on Render).

### E2E-003 — Admin login Playwright skip (advisory)

`auth.e2e.spec.ts` admin dashboard test skipped when credentials absent. Local `.env` has credentials; spec skips in default Playwright run — verify env propagation in CI.

---

## Journey → test file matrix

| Journey | Test module | T0 | T2 | T3 |
|---------|-------------|----|----|-----|
| UJ-001 | `apps/e2e/tac-file-conversion.e2e.spec.ts` | — | ✓ | blocked |
| UJ-002 | `apps/backend/tests/validation/test_validation_e2e.py` | — | ✓ | — |
| UJ-003 | `apps/e2e/auth.e2e.spec.ts` | — | partial | partial |
| UJ-DEV-001 | `tests/migration/test_workspace_import_smoke.py` | ✓ | — | — |
| UJ-DEV-002 | `tests/vendor/test_manifest_integrity.py` | ✓ | — | — |
| UJ-DEV-003 | `tests/migration/test_tc_m003_golden_conversion.py` | ✓ | — | — |
| UJ-OPS-001 | `scripts/deploy/verify_connectivity.sh` + `tests/smoke/` | — | — | partial |

**Waiver**: No `tests/e2e/test_uj*.py` pytest modules — project uses Playwright in `apps/e2e/` per test-plan.md (M7 layout). T0 pytest UJ mapping satisfied via migration/vendor gates.

---

## Handoff to 11-verify-impl

1. **Blockers**: E2E-001 (schema path), E2E-002 (staging auth deploy).
2. **Green locally**: T2 Playwright product suite, H0i, validation E2E, migration TC-M003–M005.
3. **Green on staging**: H1, H4, H5 connectivity; anonymous convert API smoke.
4. **Not re-run**: Full Playwright suite (12 specs), docker integration matrix, live authenticated browser UJ-001.
