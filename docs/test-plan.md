# Test Plan

> **Project**: METAR to IWXXM Converter
> **Repository**: https://github.com/joseph-c-mcguire/metar-to-IWXXM
> **Last updated**: 2026-07-13 (S011 / EV-008 — F7 operator UI test plan)

## Scope

**In scope**: Product features F1–F8 (F1 superseded by F6 engine; **F7 built this cycle**
S011 / EV-008; F8 Implemented); monorepo migration validation M1–M6 (M3 deprecated at
F6 cutover); connectivity tiers **H0c–H7** (local + live Render); tac2iwxxm + `tac-validate` +
`iwxxm-validate` metrics (library/CI); backend thin wrappers; F7 decode/spans/soft-preview/
workbench/unified sessions; admin-route negative tests.

**Out of scope**: Performance/load testing; wmo-im / IWXXM-US schema correctness beyond our fixtures;
scheduled CI live jobs (manual/Makefile only); **convert-response metrics fields** (F6-R11);
teaching CMS; AMHS/SWIM/AFS; push sinks; in-app paste-keys UI.

### Live harness (delta 2026-06-22; H7 2026-07-12)

Unified manual live test harness against Render staging:

| Tier | Scope | Makefile target |
|------|-------|-----------------|
| H3 | Live API pytest (health, convert, validate, auth) | `make test-live-api` |
| H4–H5 | CORS preflight + frontend bundle URLs | `make test-live-connectivity` |
| H6 | Playwright UJ-001–007 (+ UJ-008 smoke) + F7 smokes UJ-013/015–019 | `make test-live-e2e` |
| **H7** | Live bulletin gate: multi-report AHL → split → convert → Schematron | `make test-live-bulletin` (planned) |
| All | Sequential H4–H5 → H3 → H6 → H7 | `make test-live` (extend when H7 lands) |

**Prerequisite**: E2E-001 schema path regression must be resolved before H3 validate and full H6 UJ-002 pass (see [e2e-report.md](reports/e2e-report.md)).

**CI policy**: Manual/local only — no GitHub Actions live job (Render cold-start + secrets).

**Canonical URLs** (see [staging-secrets-matrix.md](ops/staging-secrets-matrix.md)):

- `LIVE_API_URL` — `https://metar-to-iwxxm-api.onrender.com`
- `LIVE_FRONTEND_URL` — `https://metar-to-iwxxm-frontend-v4-web.onrender.com`

## User Journeys (E2E)

| Journey | Feature | Local E2E module | Live E2E | Test plan TC |
|---------|---------|------------------|----------|--------------|
| UJ-001 | F6 | `apps/e2e/tac-file-conversion.e2e.spec.ts`, `apps/e2e/tac-file-upload-database.e2e.spec.ts` | `make test-live-e2e` (H6) | TC-001, TC-LIVE-001 |
| UJ-002 | F2+F6 | backend validation tests + UI Strict Validation → `validate_output` (ADR-023) | H3 validate + H6 where exposed | TC-002, TC-LIVE-002 |
| UJ-003 | Auth | `apps/e2e/auth.e2e.spec.ts` | `make test-live-e2e` (H6) | TC-003, TC-LIVE-003 |
| UJ-004 | F5+F7 | `apps/e2e/metar-work-history.e2e.spec.ts` (unified filter) | H6 UJ-004 | TC-004, TC-LIVE-006 |
| UJ-005 | F6 | F6 product-matrix Playwright (planned) | H6 | TC-F6-001, TC-LIVE-F6-001 |
| UJ-006 | F6 | API product-matrix pytest | H3 live | TC-F6-002, TC-LIVE-F6-002 |
| UJ-007 | F2+F6 | US-profile validate | H3 / H6 | TC-F6-003, TC-LIVE-F6-003 |
| UJ-008–010 | F6 | error/edge specs | T2 (+ T3 smoke UJ-008) | TC-F6-010–012 |
| UJ-011 | F6 | bulletin split API (T2) | **H7** live | TC-F6-030, TC-LIVE-F6-030 |
| UJ-012 | F6 | tac-validate fail API (T2) | H3 optional smoke | TC-F6-031 |
| UJ-013 | F7 | workbench shell Playwright | H6′ | TC-F7-001 |
| UJ-014 | F8 | worker unit + T7.4 staging | staging | (F8 plan / ADR-018) |
| UJ-015 | F7 | decode-tac API + decode panel | H6′ | TC-F7-002 |
| UJ-016 | F7 | Failed-TAC + soft-preview | H6′ | TC-F7-003 |
| UJ-017 | F7 | live workbench debounce/spans | H6′ | TC-F7-004 |
| UJ-018 | F7 | unified sessions + migrate smoke | H6′ | TC-F7-005 |
| UJ-019 | F7 | `/admin` negative | H6′ | TC-F7-006 |
| UJ-020 | F9 | decode values + summary (unit/API/Vitest/Playwright) | H6′ | TC-F9-001, TC-F9-002 |
| UJ-021 | F10 | preview pane + terminator quick fix | H6′ | TC-F10-001, TC-F10-002 |
| UJ-022 | F11 | operator convert/validate after msgspec | H6′ | TC-F11-001 |
| UJ-023 | F12–F14 | PyPI tag → install smoke | CI | TC-F14-001 |
| UJ-DEV-005 | F12–F14 | pip install packages | CI | TC-F12-001, TC-F13-001, TC-F14-002 |
| UJ-DEV-004 | F2/F6/M5 | `tac-validate` + `iwxxm-validate` package CI | — | TC-F6-032 |

**Admin dashboard E2E**: **Retired** (S011 / #697). Replace prior admin panel locator guidance with
**TC-F7-006** — assert `/admin` and legacy admin deep links return not-found; delete/skip old
admin suite modules.

| UJ-DEV-001 | M1,M5 | CI monorepo-smoke job | — | TC-M001 |
| UJ-DEV-002 | M2,F6 | vendor manifest integrity tests | — | TC-M002 |
| UJ-DEV-003 | M3 | ~~gifts + conversion regression~~ | — | **TC-M003 deprecated** → TC-F6-020–022 |
| UJ-DEV-003b | F6 | tac2iwxxm + iwxxm-us pin | — | TC-F6-M001 |
| UJ-OPS-001 | M4 | deploy smoke H1–H5 | Render staging | TC-OPS-001 |

## Connectivity & Wiring

| Tier | Scope | Command |
|------|-------|---------|
| H0e | Env contract sync (`.env` + config JSON) | `make env-check` |
| H0c | CORS policy (in-process) | `pytest apps/backend/tests/unit/test_cors_policy.py` |
| H0i | Cross-service integration | `pytest apps/backend/tests/integration` |
| H3 | Live API smoke (pytest) | `make test-live-api` |
| H4 | Live CORS preflight | `make test-live-connectivity` |
| H5 | Frontend bundle URLs | `make test-live-connectivity` |
| H6 | Live Playwright UJ-001–007 (+ UJ-008) + F7 UJ-013/015–019 smokes | `make test-live-e2e` |
| **H7** | Live bulletin → split → convert → Schematron (UJ-011) | `make test-live-bulletin` (planned) |

**Post-migration**: Single API origin simplifies CORS — auth routes on same host as `/api/v1/*`.
**H7** is a dedicated connectivity gate for bulletin ingest path (not F8 worker); see
[connectivity-gates.md](../.cursor/skills/connectivity-gates.md).

**Env wiring** (see [config-spec.md](config-spec.md)):

- `config.*.api.baseUrl` — API URL (replaces `VITE_API_BASE_URL`)
- `config.*.api.corsOrigins` — backend allowed origins (replaces `METAR_CORS_ORIGINS`)
- `SUPABASE_PUBLISHABLE_KEY` / `SUPABASE_SECRET_KEY` — secrets in `.env` / Render only
- `LIVE_API_URL` / `LIVE_FRONTEND_URL` — from `config.prod.liveE2e` or env override
- `E2E_USER_EMAIL` / `E2E_USER_PASSWORD` — runtime JWT via `POST /auth/login` (local/CI; replaces deprecated `ADMIN_*`)
- `make env-check` — validates canonical names and config JSON before integration/live runs

## Test Strategy

| Level | Framework | Scope | Run Command | Location |
|-------|-----------|-------|-------------|----------|
| Unit | pytest / Vitest | packages/*, apps/backend, apps/frontend components | `make test-unit` | per workspace |
| Integration | pytest | API + auth + conversion | `make test-integration` | apps/backend/tests |
| E2E smoke (CI) | Playwright | Auth bootstrap + TAC conversion (mock session, no secrets) | `make test-e2e-playwright-smoke` | apps/e2e/ |
| E2E (T2) | Playwright | UJ-001–007 local stack | `make test-e2e-playwright` | apps/e2e/ |
| Live E2E (T3) | Playwright + pytest | UJ-001–007 on Render | `make test-live` | apps/e2e/ + live pytest |
| Vendor | pytest | manifest + schema presence | `pytest tests/vendor` | tests/vendor |
| CI | GitHub Actions | validate + test (matrix, incl. `bugs`) + e2e-smoke (Playwright) + deploy; path filters deferred (P2) | `.github/workflows/ci-cd.yml` | root |
| Pre-commit | pre-commit framework | fast gates (format/lint/typecheck/secrets/yaml) | `.pre-commit-config.yaml` | root |

**Coverage**: 95% on all packages and apps (ADR-007) — pytest for Python, Vitest for frontend.

## Migration Test Cases

### TC-M001: Monorepo Clone Smoke

- **Objective**: Verify single clone builds and tests without submodules.
- **Preconditions**: Clean environment; no `.gitmodules`.
- **Steps**:
  1. Clone repo.
  2. `make install && make test-unit`.
  3. `make dev` (or docker-compose) and hit `/health`.
- **Pass criteria**: Health 200; core unit tests green.
- **Source**: UJ-DEV-001

### TC-M002: Vendor Manifest Integrity

- **Objective**: `vendor/manifest.json` pins match checked-in tree checksums.
- **Steps**:
  1. Run manifest validation script/test.
  2. Confirm each schema bundle directory exists and matches pinned tag/SHA.
- **Pass criteria**: No drift between manifest and tree.
- **Source**: UJ-DEV-002

### TC-M003: GIFTs Conversion Regression — Deprecated

- **Status**: **Deprecated** (S008 / ADR-014). Ownership moved to **TC-F6-020–022**.
- **Historical objective**: Representative METAR set converts identically pre/post migration.
- **Source**: UJ-DEV-003 (deprecated)

### TC-M004: No Submodule References

- **Objective**: Big-bang PR removes all submodule machinery.
- **Steps**:
  1. Assert `.gitmodules` absent.
  2. Assert CI/docs contain no `git submodule` instructions.
  3. Grep for `.git/modules` paths in scripts.
- **Pass criteria**: All checks pass.
- **Source**: M1 layout / Phase 4 finalize (T11.1)

### TC-M005: Auth Merge Behavior

- **Objective**: Auth endpoints available on backend; separate auth service removed from compose.
- **Steps**:
  1. `POST /auth/login` (or equivalent) on backend port.
  2. Use JWT on `/api/v1/convert`.
  3. Confirm docker-compose has two app services (backend, frontend) not three.
- **Pass criteria**: UJ-003 passes; no auth container required.
- **Source**: M4, REQ-004

## Product Test Cases

### TC-001: File Conversion E2E

- **Objective**: UJ-001 happy path
- **Input**: Sample `.tac` in test-data
- **Pass criteria**: IWXXM XML returned; HTTP 200
- **Source**: apps/e2e/tac-file-conversion.e2e.spec.ts

### TC-001b: COR-after-time + TAC traceability (EV-003 / #594; UX hardening EV-007 / #655)

- **Objective**: ICAO COR placement and per-result TAC display
- **Input**: `METAR STID ddHHmmZ COR ...` manual TAC; multi-line manual input
- **Pass criteria**:
  - IWXXM contains `reportStatus="CORRECTION"` (no `translationFailedTAC`)
  - Results UI shows **Source TAC** panel with original input per result (always visible;
    client fallback when API omits `tac_input`)
  - Card title uses TAC-derived headline (e.g. `METAR KJFK 121251Z`); download name shown as
    subtitle when it differs (#664 preserved)
  - Multi-line manual input shows `Line N of M` chip per result
  - API `ConversionResult.tac_input` populated for manual and file conversions
- **Source**: `tests/bugs/test_bug_2026_06_22_issue_594_cor_after_time.py`, `packages/gifts/tests/test_metar_encoding.py::test_cor_after_time`, `apps/e2e/tac-file-conversion.e2e.spec.ts`, `apps/frontend/src/app/components/FileConverter.test.tsx`, `apps/frontend/src/utils/resultTraceability.test.ts`

### TC-001c: Custom output filename for manual input (EV-005 / #664)

- **Objective**: UJ-001 step 4/9 — manual-input downloads honor an optional custom filename and persist it
- **Input**: Manual TAC (single and multi-line) with and without an "Output filename" value; sanitizer
  inputs with path separators / illegal chars / a trailing extension
- **Pass criteria**:
  - Blank name ⇒ download is `manual_input.xml` (multi-line: `manual_input_N.xml`) — unchanged default
  - Non-blank `base` ⇒ single download `base.xml`; multi-line ⇒ `base_1.xml`, `base_2.xml`, …
  - Download All ZIP archive is named `base.zip` when a custom name is set; else `converted_files_<ts>.zip`
  - File-upload results keep their original filename (custom name not applied)
  - Sanitizer strips path/illegal chars + extension, trims; empty-after-sanitize ⇒ `manual_input`
  - The custom name round-trips through the converter snapshot / `conversion_params` and survives reload
    (guest sessionStorage + logged-in work session) — no API/schema change
- **Source**: `apps/frontend/src/utils/*filename*.test.ts`, `apps/frontend/src/app/components/FileConverter.test.tsx`, `apps/e2e/tac-file-conversion.e2e.spec.ts`

### TC-002: Validation Pass

- **Objective**: UJ-002 for known-good output
- **Pass criteria**: validation status `pass` or equivalent

### TC-003: Auth Gate

- **Objective**: UJ-003 — unauthorized blocked, authorized allowed
- **Pass criteria**: 401 without token; 200 with valid JWT

### TC-004: Work session lifecycle (F5 / UJ-004) — unified table

- **Objective**: Draft auto-save → convert → WIP → send → Finished; resume on login; My METARs
  filters METAR/SPECI on `tac_work_sessions` (ADR-020)
- **Steps**:
  1. Authenticated user creates draft via PATCH upsert (`product` = metar|speci)
  2. Convert success moves to WIP (reject second WIP — one WIP per user total)
  3. Partial convert failure sets Failed; edit + re-convert transitions appropriately
  4. Send success sets Finished with `kv_upload_key`
  5. Soft-delete + restore within 30 days
  6. My METARs does **not** list non-METAR products; workbench history may (TC-F7-005)
  7. ~~Admin GET lists all users~~ **Removed** — covered by TC-F7-006 negative
- **Pass criteria**: Status rules enforced; RLS isolates user data; no admin list
- **Source**: UJ-004; ADR-020; backend integration tests + Playwright T2

## F7 Test Cases (S011 / EV-008)

### TC-F7-001: Workbench shell + multi-product entry (UJ-013)

- **Level**: T2 / T3
- **Objective**: CodeMirror workbench loads; all seven products selectable; hard convert still works
- **Pass criteria**: Editor mounts; product matrix smoke; no METAR-only chrome blocking others
- **Source**: UJ-013

### TC-F7-002: Decode-tac API + decode panel (UJ-015)

- **Level**: T2 / T3
- **Objective**: `POST /api/v1/decode-tac` returns ordered segments; UI Code|Explanation panel
- **Pass criteria**: Golden METAR/SPECI/TAF segments non-empty; all 7 products return well-formed
  response; residuals explicit when undecoded
- **Source**: UJ-015; #702

### TC-F7-003: Failed-TAC + soft-preview (UJ-016)

- **Level**: T2 / T3
- **Objective**: Distinct Failed-TAC cue; soft-preview returns best-effort XML + failed spans
- **Pass criteria**: Cue visible for injected bad TAC; markers align to spans; hard convert
  failure semantics unchanged when preview not selected
- **Source**: UJ-016; #665/#666

### TC-F7-004: Live workbench debounce / spans / console (UJ-017)

- **Level**: T2 / T3
- **Objective**: Debounced lint/decode; AbortController; span highlight; console; optional live IWXXM
- **Pass criteria**: In-flight cancel on retype; spans match fixture issues; console shows structured
  messages without crashing editor
- **Source**: UJ-017; #694

### TC-F7-005: Unified sessions + F5 migrate smoke (UJ-018)

- **Level**: T2 / T3
- **Objective**: CRUD on `tac_work_sessions` for non-METAR; migrate smoke for legacy METAR rows
- **Pass criteria**: TAF (or other) Draft survives reload; My METARs filter correct; migrated METAR
  session resumes (UJ-004)
- **Source**: UJ-018; ADR-020

### TC-F7-006: Admin routes removed (UJ-019)

- **Level**: T2 / T3
- **Objective**: `/admin` and legacy admin deep links are not-found; old admin suite retired
- **Pass criteria**: Negative Playwright/API asserts; no AdminDashboard route registration
- **Source**: UJ-019; #697

### F7 UI↔API connection integration

Cross-layer coverage for workbench connection points (not only isolated unit/TC modules):

| Connection | API path | Backend integration | Playwright |
|------------|----------|---------------------|------------|
| Live lint + spans | `POST /api/v1/lint-tac` | `apps/backend/tests/api/test_f7_ui_connection_integration.py` | `apps/e2e/f7-ui-api-connections.e2e.spec.ts` |
| Decode panel | `POST /api/v1/decode-tac` | same | same |
| Soft-preview / Failed-TAC | `POST /api/v1/convert` (`preview=true`) | same + `test_frontend_contract_integration.py` | same |
| My METARs / sessions | `/api/v1/work-sessions*` + `product` | same | same |
| Browser CORS (H0i) | OPTIONS on lint/decode/convert | same + `test_h0i_connectivity.py` | — |

### F7 verify/deploy gate

Before closing S011 / EV-008:

- [ ] TC-F7-001–006 green at T2
- [ ] F7 UI↔API connection integration green (table above)
- [ ] TC-004′ (unified) green
- [ ] H6′ live smokes for UJ-013/015–019 (or documented waiver)
- [ ] Admin E2E modules removed or converted to TC-F7-006
- [ ] Child issues #697/#702/#665/#666/#694 closed or linked; #5 remains open

## F9/F10 Test Cases (S013 / EV-009)

### TC-F9-001: Value-aware decode explanations (UJ-020)

- **Level**: T0 / T2
- **Objective**: `decode_tac` explanations include parsed values, not only group labels
- **Pass criteria**:
  1. METAR fixture `METAR KJFK 121251Z 18004KT 10SM FEW250 24/18 A3011=`:
     `18004KT` explanation contains "180°" and "4 kt"; `24/18` contains "24 °C" and
     "dewpoint 18 °C"; `A3011` contains "30.11 inHg"; `121251Z` contains "day 12" and
     "12:51 UTC"
  2. Negative temps (`M05/M12`), gusts (`24012G22KT`), VRB wind, `Q1013`, metre visibility
     (`4000`) all produce value-aware text
  3. TAF change groups (`FM`, `TEMPO`, `BECMG`, `PROB`) include the parsed period/values
  4. SIGMET/AIRMET/VAA/TCA return best-effort value-aware segments; residuals unchanged
  5. Segment `start`/`end` offsets unchanged from pre-F9 behavior (contract additive)
- **Source**: UJ-020; F9 acceptance 1

### TC-F9-002: Plain-language summary live render (UJ-020)

- **Level**: T0 / T2 / T3
- **Objective**: Backend `summary` present and rendered live in the decode panel
- **Pass criteria**:
  1. decode-tac response includes `summary` for all seven products (best-effort where sparse,
     "partial decode" wording for sparse products)
  2. Summary is one flowing paragraph built deterministically from decoded values
  3. Residuals present → summary ends with "Not decoded: …" naming residual text
  4. Vitest: "Plain language" block renders at top of decode panel and updates on text change
     (debounce path); Playwright: typing updates the paragraph without manual refresh
- **Source**: UJ-020; F9 acceptance 2–3

### TC-F10-001: IWXXM preview pane (UJ-021)

- **Level**: T0 / T2 / T3
- **Objective**: Soft-preview / Live IWXXM output is anchored in a dedicated pane with status
- **Pass criteria**:
  1. Pane side-by-side ≥ `lg`, stacked < `lg`
  2. Soft-preview run lands pretty-printed XML in the pane with badge
     "Soft preview — not for publish" and plain-language soft-fail copy (no raw
     `LAYER12_SOFT_FAIL` code as primary text); passing preview shows "Passed"
  3. Failed-span count in pane links/scrolls to editor highlights
  4. Live IWXXM toggle output lands in the same pane
- **Source**: UJ-021; F10 acceptance 1–2

### TC-F10-002: Terminator info-level + quick fix (UJ-021)

- **Level**: T0 / T2
- **Objective**: `MISSING_TERMINATOR` is info severity with working one-click fix
- **Pass criteria**:
  1. `tac-validate`: `MISSING_TERMINATOR` severity `info`; `ok: true` for otherwise-clean
     single report without `=` (unit)
  2. Reworded copy: "Reports in bulletins end with '=' — add it before publishing"
  3. Console line renders info level (not warn/error styling) with "Add `=`" action;
     clicking appends `=` and the hint clears on next live pass
  4. Editor affordance on the hint span offers the same fix
- **Source**: UJ-021; F10 acceptance 3–4

### F9/F10 verify/deploy gate

Before closing S013 / EV-009:

- [ ] TC-F9-001/002 + TC-F10-001/002 green at T2
- [ ] Decode-tac contract remains backward-compatible (additive `summary` only)
- [ ] H6′ live smokes for UJ-020/021 (or documented waiver)

## F11–F14 Test Cases (S014 / EV-010)

### TC-F11-001: msgspec high-churn HTTP parity (UJ-022)

- **Level**: T0 / T2 / T3
- **Objective**: convert/validate/lint/decode usable by FE after msgspec move
- **Pass criteria**:
  1. Contract tests cover msgspec-backed routes; OpenAPI still generates for aliases
  2. Vitest + Playwright operator convert/validate/lint/decode green
  3. Bench: msgspec HTTP path ≤ prior pydantic map path (soft until publish; hard at cutover)
- **Source**: UJ-022; F11; ADR-026

### TC-F11-002: Layer cost matrix (#703)

- **Level**: T0
- **Objective**: Documented p50/p95 for TAC lint, convert IR, XSD, Schematron, HTTP DTO
- **Pass criteria**: Matrix committed under session reports; Schematron identified as dominant
  or contradicted with evidence
- **Source**: F11; #703

### TC-F12-001: tac-validate PyPI + domain rules (UJ-DEV-005)

- **Level**: T0 / CI
- **Objective**: Wheel installs; METAR/SPECI/TAF full rules; other products template+gates
- **Pass criteria**: Clean venv `pip install tac-validate==0.1.0`; fixture suite green
- **Source**: F12; #698

### TC-F13-001: iwxxm-validate Rust + Schematron parity (UJ-DEV-005)

- **Level**: T0 / CI
- **Objective**: Rust well-formed+XSD+Schematron; parity vs lxml; schemas bundled
- **Pass criteria**: `validate_iwxxm` on golden corpus; speedup vs baseline; wheel offline
- **Source**: F13; #699

### TC-F14-001: Tag → trusted publish (UJ-023)

- **Level**: CI
- **Objective**: OIDC trusted publishing on `*-v0.1.0` tags
- **Pass criteria**: Workflow pattern + smoke job for all three packages
- **Source**: F14; E10-25

### TC-F14-002: tac2iwxxm[validate] extras (UJ-DEV-005)

- **Level**: T0 / CI
- **Objective**: Convert-only wheel works; `[validate]` pulls both validators
- **Pass criteria**: Sample METAR → IWXXM; extras resolve tac-validate + iwxxm-validate
- **Source**: F14; #693

### F11–F14 verify/deploy gate

- [ ] TC-F11-001/002 + TC-F12-001 + TC-F13-001 + TC-F14-001/002 green
- [ ] Hard perf gates at publish (E10-24)
- [ ] H4–H5 + H6′ UJ-022 after Render redeploy
- [ ] PyPI install smokes for three packages

## Live Test Cases (T3 / H3–H6)

Manual signoff before release — not a PR merge gate. Developer runs `make test-live` from repo root with `.env` populated.

### TC-LIVE-001: Live Health & Convert

- **Objective**: H3 — API health and METAR conversion against Render
- **Preconditions**: E2E-001 schema path fixed; `LIVE_API_URL` set; JWT obtained via login fixture
- **Steps**:
  1. `curl -sf "${LIVE_API_URL}/health"` — expect 200, `gifts_available: true`
  2. `pytest apps/backend/tests/infrastructure/test_live_api_health.py -m live_api`
- **Pass criteria**: All live_api tests green; cold-start retries (3×, 30s backoff) succeed
- **Resilience**: Exponential backoff on HTTP 429
- **F6 note**: Health should report tac2iwxxm availability (not `gifts_available`) after cutover.
- **Source**: UJ-001, H3

### TC-LIVE-002: Live Validation

- **Objective**: H3 — validation endpoint against Render
- **Preconditions**: E2E-001 resolved; valid JWT; sample IWXXM from convert step
- **Steps**:
  1. POST `/api/v1/validation/validate` with converted XML
  2. Assert validation status pass for selected IWXXM version
- **Pass criteria**: HTTP 200; validation pass for known-good fixture
- **Source**: UJ-002, H3

### TC-LIVE-003: Live Connectivity (H4–H5)

- **Objective**: CORS preflight and frontend bundle embed correct API URL
- **Preconditions**: `LIVE_API_URL`, `LIVE_FRONTEND_URL` set
- **Steps**:
  1. `make test-live-connectivity` (wraps `verify_connectivity.sh` + CORS pytest)
  2. Confirm H4 preflight from frontend origin → API returns allowed headers
  3. Confirm H5 bundle contains `LIVE_API_URL` host
- **Pass criteria**: H0c-equivalent live checks pass (script exit 0)
- **Source**: UJ-OPS-001, H4–H5

### TC-LIVE-004: Live Playwright UJ-001–007

- **Objective**: H6 — product journeys against Render frontend (includes F6 matrix)
- **Preconditions**: `PLAYWRIGHT_BASE_URL=${LIVE_FRONTEND_URL}`; `DISABLE_AUTH=false`; admin credentials in `.env`
- **Steps**:
  1. Run `00-preflight.e2e.spec.ts` first (wake + health)
  2. `make test-live-e2e` — auth, METAR convert, F6 product/profile matrix (UJ-005), validation (UJ-002/007), UJ-008 smoke
  3. Playwright config disables local `webServer` when base URL is remote
- **Pass criteria**: UJ-001–007 specs green against live URLs
- **Resilience**: Cold-start retry in preflight; serial execution (no parallel live requests)
- **Source**: UJ-001–007, H6

### TC-LIVE-F6-001 / TC-LIVE-F6-002 / TC-LIVE-F6-003

- **Objective**: Live signoff for UJ-005 (UI 7 products annex3), UJ-006 (API matrix), UJ-007 (US validate)
- **Pass criteria**: All seven products annex3 convert; US-profile METAR/SPECI/TAF where schemas apply
- **Source**: F6 acceptance; H3/H6

## F6 Test Cases (`tac2iwxxm`)

### TC-F6-001: UI convert all 7 products annex3

- **Objective**: UJ-005 T2/T3 parametrize
- **Pass criteria**: Each product golden TAC → XML displayed; HTTP success
- **Source**: UJ-005

### TC-F6-002: API convert product matrix

- **Objective**: UJ-006
- **Pass criteria**: `POST /api/v1/convert` with `product`+`profile` succeeds for all seven annex3
- **Source**: UJ-006

### TC-F6-003: Validate iwxxm_us METAR/SPECI/TAF

- **Objective**: UJ-007
- **Pass criteria**: Combined catalog validation pass on fixtures
- **Source**: UJ-007

### TC-F6-010 / TC-F6-011 / TC-F6-012

- **Objectives**: UJ-008 unknown product; UJ-009 missing US pin fail-closed; UJ-010 malformed REMARKS diagnostics
- **Pass criteria**: Structured errors; no gifts fallback; no silent annex3 downgrade on US profile
- **Plan ownership**: T5.6 (API/package); UJ-008 live smoke in T8.4 (D-S008-05-batch2)

### TC-F6-020: M-parse / M-xsd / M-sch on golden pack

- **Level**: Package CI (`packages/tac2iwxxm` + **`packages/iwxxm-validate`** for M-xsd / M-sch)
- **Pass criteria**: Required metrics green on committed golden pack; **M-sch** executed via
  `iwxxm-validate`
- **Cutover gate**: Must pass for METAR/SPECI annex3 **and** iwxxm_us METAR/SPECI (T4.10–T4.11)
  on first gifts-delete PR (with UJ-001 E2E — T4.6)

### TC-F6-021: M-golden / M-field fixtures

- **Pass criteria**: Per-fixture golden/field equality where annotated

### TC-F6-022: Archive gifts goldens (post-delete)

- **Objective**: After gifts removal, freeze last gifts Annex-3 XML as archive goldens for M-parity-style diffs
- **Pass criteria**: Archive corpus present; diffs explained or zero vs tac2iwxxm annex3 METAR/SPECI

### TC-F6-030: Bulletin split (UJ-011)

- **Level**: T0 package + T2 API
- **Objective**: WMO AHL multi-report bulletin → N reports → convert each
- **Pass criteria**: Fixture yields expected report count; per-report IWXXM or structured errors
- **Source**: UJ-011; F6.bulletin

### TC-F6-031: TAC lint failure (UJ-012)

- **Level**: T0 `tac-validate` + T2 API wrapper
- **Objective**: Rule-pack / parse-gate failure returns structured issues
- **Pass criteria**: Non-empty issues; no silent success
- **Source**: UJ-012

### TC-F6-032: iwxxm-validate package suite (UJ-DEV-004)

- **Level**: T0 / CI
- **Objective**: XSD + Schematron package tests against vendor pins
- **Pass criteria**: CI green; M-sch ownership here
- **Source**: UJ-DEV-004; F2

### TC-F6-033: Backend thin wrappers

- **Level**: T2 integration
- **Objective**: Validation (and convert) routes call `iwxxm-validate` / `tac-validate` /
  `tac2iwxxm` — no inline duplicate Schematron engine
- **Pass criteria**: Wrapper smoke + import/SoC checks
- **Source**: Q30=B acceptance

### TC-LIVE-F6-030: H7 live bulletin gate

- **Tier**: **H7**
- **Objective**: Against live API — one committed multi-report bulletin fixture → split → convert
  → Schematron pass (or documented quarantine-style fail)
- **Command**: `make test-live-bulletin` (planned; wire in 04/07)
- **Pass criteria**: Exit 0; N IWXXM results or structured per-report errors; Schematron via
  `iwxxm-validate`
- **Source**: UJ-011; Q44b=B

### TC-F6-M001: tac2iwxxm workspace + iwxxm-us manifest

- **Objective**: UJ-DEV-003b
- **Pass criteria**: Package in uv workspace; `vendor/manifest.json` includes iwxxm-us pin; integrity tests pass;
  **also** `tac-validate` and `iwxxm-validate` workspace members

### F6 cutover PR gate

Before merging the PR that wires tac2iwxxm and deletes `packages/gifts`:

- [ ] TC-F6-020 / TC-F6-021 METAR/SPECI annex3 green
- [ ] TC-F6-003 METAR/SPECI `iwxxm_us` green (T4.10–T4.11)
- [ ] UJ-001 / TC-001 E2E green (T4.6 — Playwright or local equivalent)
- [ ] CI matrix uses `tac2iwxxm` (no `gifts` cell)
- [ ] No `packages/gifts` in tree; API does not import gifts

### F6 v1 done QA gate

- [ ] TC-F6-001 / TC-F6-002 (7 products)
- [ ] TC-F6-003 (US where applicable)
- [ ] TC-F6-010 / TC-F6-011 / TC-F6-012 (T5.6 + T8.4 UJ-008)
- [ ] TC-F6-020 / TC-F6-021
- [ ] TC-F6-030 / TC-F6-031 / TC-F6-032 / TC-F6-033
- [ ] Cutover complete (no gifts)
- [ ] H4–H5 green (T8.3)
- [ ] H6 UJ-001–007 (+ UJ-008 smoke) green (T8.4)
- [ ] **H7** TC-LIVE-F6-030 green (when bulletin API is live)

⚠️ **Resolved in 04/05**: PyO3 bench CI (T4.3–T4.5); `make test-live-bulletin` (T4.9).

### Session changelog

- S008 (2026-07-12): F6 test matrix, metrics gates, H6 expansion, TC-M003 deprecated
- S008 amend (2026-07-12): TC-F6-030–033; H7 bulletin gate; M-sch via iwxxm-validate; UJ-013/014 no TC
- S008 05 (2026-07-12): Cutover E2E ownership T4.6; TC-F6-010–012 → T5.6/T8.4; F6.b US in M4
- S011 / EV-008 (2026-07-13): TC-F7-001–006; TC-004 unified; admin E2E retired; H6′ F7 smokes;
  scope includes F7 build
  (D-S008-05-batch2)

### TC-LIVE-005: Stale Test Migration

- **Objective**: Remove auth-v2 references from legacy live Playwright
- **Steps**:
  1. Update `tests/test_playwright_e2e.py` to target merged API at `LIVE_API_URL`
  2. Deprecate `metar-to-iwxxm-auth-v2.onrender.com` references
- **Pass criteria**: No tests target suspended auth-v2 service
- **Source**: [Context: live-e2e-integration](context/live-e2e-integration.md)

### TC-LIVE-006: Live work history UJ-004 (F5)

- **Objective**: Persisted draft survives logout/login on Render
- **Steps**:
  1. Log in on live frontend
  2. Enter METAR text; wait for draft save
  3. Log out and back in; confirm resume
  4. Convert&Send; confirm Finished in My METARs
- **Pass criteria**: UJ-004 T3 steps green
- **Source**: UJ-004, H6; runs after S004 deploy

## CI/CD (Monorepo)

**Policy (EV-002)**: Single workflow file for PR/push; ≤3 jobs; all checks dual-run locally via
pre-commit fast hooks where applicable. Scheduled workflows (`vendor-sync`, load/e2e) unchanged.

| Trigger | Workflow | Jobs | Checks |
|---------|----------|------|--------|
| PR / push `main`, `dev` | `ci-cd.yml` | **validate** | ruff format/check, prettier, eslint, basedpyright, tsc, gitleaks, actionlint/yamllint, config-guard (`tests/test_config_placeholders.py`), frontend npm audit |
| PR / push `main`, `dev` | `ci-cd.yml` | **test** | matrix unit+coverage (backend, auth, **tac2iwxxm**, **tac-validate**, **iwxxm-validate**, frontend, shared @ 98% — **gifts removed at F6 cutover**), integration matrix (docker compose), Codecov upload (95% gate) |
| push `main` only | `ci-cd.yml` | **deploy** | Docker build/push GHCR, Render deploy hooks |
| Schedule | `vendor-sync.yml` | vendor-sync | wmo-im schema sync PR (M6) |
| Manual / schedule | `load-tests.yml`, `e2e-tests.yml` | — | out of EV-002 scope |

### Pre-commit (local fast gates)

| Hook | Tool | CI equivalent |
|------|------|---------------|
| Python format | `ruff format --check` | validate job |
| Python lint | `ruff check` | validate job |
| Python types | `basedpyright` | validate job |
| JS format | `prettier --check` | validate job |
| JS lint | `eslint` | validate job |
| JS types | `tsc --noEmit` | validate job |
| Secrets | `gitleaks` | validate job (replaces `secret-scan.yml`) |
| Workflow YAML | `actionlint`, `yamllint` | validate job (replaces `github-yaml-lint.yml`) |

Slow checks (`make ci` integration, full unit matrix) remain CI-only; optional via `pre-commit` `make-ci` hook.

### Removed workflows (EV-002)

- `secret-scan.yml` — merged into validate
- `github-yaml-lint.yml` — merged into validate
- `frontend-audit.yml` — merged into validate (monorepo `apps/frontend` paths)

## Test Data

| Dataset | Source | Location |
|---------|--------|----------|
| Sample METAR / multi-product TAC | repo fixtures | `test-data/` + `packages/tac2iwxxm/tests/` |
| IWXXM schemas | wmo-im + iwxxm-us vendored | `vendor/schemas/` |
| Golden XML | baseline + archive gifts goldens | `test-data/golden/` / package golden/ |

## Metrics & Thresholds

| Metric | Threshold | Context |
|--------|-----------|---------|
| Backend unit coverage | **95% all packages/apps** | ADR-007 universal gate |
| E2E pass rate | 100% on T2 before merge | Big-bang gate |
| Live E2E (T3) | Manual signoff before release | `make test-live` — not CI-gated |
| Vendor sync PR | human review required | No auto-merge to main |

## Big-Bang Merge Gate

All must pass before merging migration PR:

- [ ] TC-M001 through TC-M005
- [ ] TC-001 through TC-003 (full E2E suite in apps/e2e/)
- [ ] H0c CORS unit tests
- [ ] H4 CORS preflight + H5 bundle verification on staging
- [ ] CI green on PR branch
- [ ] render.yaml updated for two-service topology
