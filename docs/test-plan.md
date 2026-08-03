# Test Plan

> **Project**: METAR to IWXXM Converter
> **Repository**: https://github.com/EMPIRIC2/TAC-to-IWXXM
> **Last updated**: 2026-08-02 (S037 / EV-030 — TC-EV030 / TC-F29 #831/#829/#820)

## Scope

**In scope**: Product features F1–F27 (F1 superseded by F6 engine; F7 Planned — workbench
smoke under F15/F20/F23–F27; **F7.g** golden examples #780 / UJ-032; **F7.h** IndexedDB sessions;
F8–F15 as prior cycles; **F16–F19 Done** dissemination epic; **F20** TAF+SPECI quality;
**F21** public unauthenticated app; **F22** privacy preference center; **F23** SIGMET family
quality bar; **F24** AIRMET; **F25** WMO METAR/SPECI/TAF parity; **F26** VAA; **F27** TCA);
monorepo migration validation M1–M6 (M3 deprecated at F6 cutover); connectivity tiers
**H0c–H7** (local + live Render); tac2iwxxm + `tac-validate` + `iwxxm-validate` metrics
(library/CI); backend thin wrappers; F7 decode/spans/soft-preview/workbench/unified sessions;
admin-route negative tests; **F15** issue registry + METAR golden/negative packs (UJ-024);
**F16–F19** dissemination drawer, multi-DB upload, WIS2, EDIS, AMHS/SWIM/AFS (UJ-027–030);
**F20** TAF + SPECI quality bar (UJ-031; #735/#734); **F23** SIGMET + VA SIGMET quality bar
(UJ-034; #733/#739); **F26/F27** VAA + TCA quality (UJ-037/038; #736/#737).

**Out of scope**: Performance/load testing; wmo-im / IWXXM-US schema correctness beyond our fixtures;
scheduled CI live jobs (manual/Makefile only); **convert-response metrics fields** (F6-R11);
teaching CMS; saved/encrypted destination profiles; in-app paste of **Supabase auth** keys
(destination BYOC paste is **in scope** for F16–F19); sibling product-quality tickets beyond
#736/#737 this cycle (TC SIGMET #738, SWX #740, VONA #741).

### Live harness (delta 2026-06-22; H7 2026-07-12)

Unified manual live test harness against Render staging:

| Tier | Scope | Makefile target |
|------|-------|-----------------|
| H3 | Live API pytest (health, convert, validate; **no auth login**) | `make test-live-api` |
| H4–H5 | CORS preflight + frontend bundle URLs | `make test-live-connectivity` |
| H6 | Playwright UJ-001–007 (+ UJ-008 smoke) + F7 smokes UJ-013/015–019 + **UJ-027–030** (H6′ when F16–F19 ships) | `make test-live-e2e` |
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
| UJ-003 | Auth | **Superseded F21** — negative Auth-gone tests | H6 optional negative | TC-003 retired / TC-F21-auth-gone |
| UJ-004 | F5+F7+F21 | IndexedDB history Playwright | H6 UJ-004 | TC-004 (local store) |
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
| UJ-024 | F15 | METAR/SPECI registry + convert→validate golden | H4–H5 if FE | TC-F15-001..005 |
| UJ-025 | F7 | Manual TAC Input modes (ADR-024 / #730) | H6′ | TC-F7-007 |
| UJ-027 | F16 | `apps/e2e/uj027-030-dissemination-drawer.e2e.spec.ts` | H6′ | TC-F16-001..005 |
| UJ-028 | F17 | `apps/e2e/uj027-030-dissemination-drawer.e2e.spec.ts` | H6′ | TC-F17-001..002 |
| UJ-029 | F18 | `apps/e2e/uj027-030-dissemination-drawer.e2e.spec.ts` (UI smoke; live BYOC cycle-close) | live BYOC | TC-F18-001..002 |
| UJ-030 | F19 | `apps/e2e/uj027-030-dissemination-drawer.e2e.spec.ts` | H6′ | TC-F19-001..003 |
| UJ-031 | F20 | TAF/SPECI registry + convert→validate golden | H4–H5 if FE | TC-F20-001..006 |
| UJ-032 | F7 | Golden examples load (convert + validate) | H4–H5 if FE | TC-F7-008 |
| UJ-033 | F22 | Privacy notice + settings + GPC | H4–H5 if FE | TC-F22-001..003 |
| UJ-034 | F23 | SIGMET/VA SIGMET registry + convert→validate golden | H4–H5 if FE | TC-F23-001..006 |
| UJ-035 | F24 | AIRMET registry + WMO golden (defaults) | H4–H5 if FE | TC-F24-001..005 |
| UJ-036 | F25 | WMO-passing Examples + METAR/SPECI/TAF goldens | H4–H5 if FE | TC-F25-001..004 |
| UJ-037 | F26 | VAA registry + WMO golden (defaults) | H4–H5 if FE | TC-F26-001..006 |
| UJ-038 | F27 | TCA registry + WMO golden (defaults) | H4–H5 if FE | TC-F27-001..006 |
| UJ-039 | F25/F7.g deepen | Load official WMO examples from sample menu | H4–H5 if FE | TC-EV024-004..006 |
| UJ-040 | F6.b deepen | Structured iwxxm-us REMARKS encode pack | — (API T3 optional) | TC-EV025-001..007 |
| UJ-041 | F23 deepen | sigmet-multi-location-VA ADR-032 equality / wmoPass (EV-026) | — | TC-EV025-008..009 |
| UJ-042 | F25/F9/F7.g deepen | Official WMO TAC peers decode empty/allowlisted residuals | H4–H5 if FE | TC-EV027-001..005 |
| UJ-043 | F28 + F6/F12/F2/F13/F15/F20/F23/F24/F26/F27 deepen | Eight-family lint/convert/validate + SWXA bar (#823) | H4–H5 if FE | TC-EV029-001..008; TC-F28-001..006 |
| UJ-044 | F29 + F23/F12/F2/F13/F9/F26/F27 deepen | Rule matrices (#831) + TC SIGMET deepen (#829) + VAA/TCA decode (#820) | H4–H5 if FE | TC-EV030-001..006; TC-F29-001..007 |

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
| H6 | Live Playwright UJ-001–007 (+ UJ-008) + F7 UJ-013/015–019 + **UJ-025** + **UJ-027–030** (H6′ when F16–F19 ships) | `make test-live-e2e` |
| **H7** | Live bulletin → split → convert → Schematron (UJ-011) | `make test-live-bulletin` (planned) |

**Post-migration / F21**: Single API origin for `/api/v1/*` only — operator `/auth/*` removed.
**H7** is a dedicated connectivity gate for bulletin ingest path (not F8 worker); see
[connectivity-gates.md](../.cursor/skills/connectivity-gates.md).

**Env wiring** (see [config-spec.md](config-spec.md); env-contract **stale-until-F21** banner):

- `config.*.api.baseUrl` — API URL (replaces `VITE_API_BASE_URL`)
- `config.*.api.corsOrigins` — backend allowed origins (replaces `METAR_CORS_ORIGINS`)
- `LIVE_API_URL` / `LIVE_FRONTEND_URL` — from `config.prod.liveE2e` or env override
- ~~`E2E_USER_EMAIL` / `E2E_USER_PASSWORD`~~ — **retired for operator path (F21)**; negative
  Auth-gone coverage uses `TC-F21-auth-gone` (no login fixture)
- F8 worker secrets remain server-only (`SUPABASE_SERVICE_ROLE_KEY`, poller URL)
- `make env-check` — validates canonical names and config JSON before integration/live runs
  (full rewrite in 04/12)

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

### TC-M005: Auth Merge Behavior — **Superseded (F21)**

- **Status**: **Superseded** by F21 / `TC-F21-auth-gone`. Historical: Auth endpoints on backend.
- **Historical objective**: Auth endpoints available on backend; separate auth service removed.
- **Source**: M4, REQ-004 (historical); S023 / EV-017

## Product Test Cases

### TC-001: File Conversion E2E

- **Objective**: UJ-001 happy path
- **Input**: Sample `.tac` in test-data
- **Pass criteria**: IWXXM XML returned; HTTP 200 (**no JWT** — F21)
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
  - The custom name round-trips through the converter snapshot / `conversion_params` and survives
    reload (guest sessionStorage + **IndexedDB** work session — F7.h) — no API/schema change
  - ~~logged-in work session~~ superseded by F21 / IndexedDB
- **Source**: `apps/frontend/src/utils/*filename*.test.ts`, `apps/frontend/src/app/components/FileConverter.test.tsx`, `apps/e2e/tac-file-conversion.e2e.spec.ts`

### TC-002: Validation Pass

- **Objective**: UJ-002 for known-good output
- **Pass criteria**: validation status `pass` or equivalent

### TC-003: Auth Gate — **Retired (F21)**

- **Status**: **Retired** — operator Auth removed (F21). Negative coverage → **TC-F21-auth-gone**.
- **Historical objective**: UJ-003 — unauthorized blocked, authorized allowed
- **Historical pass criteria**: 401 without token; 200 with valid JWT
- **Source**: UJ-003 (superseded); S023 / EV-017

### TC-004: Local work session lifecycle (F5 / UJ-004) — IndexedDB

- **Objective**: Draft auto-save → convert → WIP → send → Finished in **browser IndexedDB**;
  resume after reload **without login**; My METARs filters METAR/SPECI locally (F7.h / F21)
- **Steps**:
  1. Public user creates draft via local upsert (`product` = metar|speci) — **no**
     `/api/v1/work-sessions`
  2. Convert success moves to WIP (reject second WIP — one WIP per browser profile total)
  3. Partial convert failure sets Failed; edit + re-convert transitions appropriately
  4. Dissemination success sets Finished with `kv_upload_key` (local only; no dest secrets)
  5. Soft-delete + restore within local trash policy
  6. My METARs does **not** list non-METAR products; workbench history may (TC-F7-005)
  7. Clearing site data loses history (disclosed in F22)
- **Pass criteria**: Status rules enforced locally; **no** JWT / RLS / server session calls
- **Source**: UJ-004; F7.h / F21; ADR-020 historical; FE IndexedDB unit + Playwright T2

### TC-F21-auth-gone: Operator Auth removed (UJ-003 superseded)

- **Level**: T2 / T3 (optional negative)
- **Objective**: `/auth/*` and JWT gates are gone from the public product surface
- **Pass criteria**:
  - `POST /auth/login` (and sibling Auth routes) → **404** (or equivalent not-found)
  - `POST /api/v1/convert` (and lint/decode/validate/preview) succeed **without** Authorization
  - Frontend has no login/register UX; no JWT bootstrap for convert path
  - `DISABLE_AUTH` dual path absent from runtime config contract (after 04 rewrite)
- **Source**: UJ-003 superseded; F21 / S023 / EV-017 / #783

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

### TC-F7-005: Unified local sessions + My METARs filter (UJ-018)

- **Level**: T2 / T3
- **Objective**: IndexedDB CRUD for non-METAR; My METARs METAR/SPECI filter (F7.h)
- **Pass criteria**: TAF (or other) Draft survives reload **without login**; My METARs filter
  correct; METAR session resumes (UJ-004); **no** `/api/v1/work-sessions`
- **Source**: UJ-018; F7.h / F21; ADR-020 historical

### TC-F7-006: Admin routes removed (UJ-019)

- **Level**: T2 / T3
- **Objective**: `/admin` and legacy admin deep links are gone
- **Pass criteria**: Not-found / no AdminDashboard; **public** convert still works (no JWT)
- **Source**: UJ-019; F7.a / #697; F21

### TC-F7-007: Manual TAC Input modes (UJ-025 / #730)

- **Level**: T2 (Vitest + Playwright) / T3 (H6′ / staging smoke)
- **Objective**: Validate FileConverter Manual TAC Input modes per ADR-024 matrix
- **Matrix**:

  | Case | Input | Mode | Expect |
  | ---- | ----- | ---- | ------ |
  | T1 | Single METAR TAC | TAC report | Convert OK; Product Auto-detect |
  | T2 | Multi-report WMO AHL | AHL bulletin | `/convert-bulletin` + summary/results |
  | T3 | AHL or COLLECT pasted in TAC mode | (auto-switch) | Switches mode + toast (**required**) |
  | T4 | COLLECT XML (fixture) | IWXXM COLLECT | `/ingest-collect` → **501** placeholder UX |
  | T5 | `.gz` COLLECT/bulletin if accepted | matching | Inflate + same as T2/T4 |
  | T6 | Read-only finished session | any | Mode buttons disabled |

- **Pass criteria**:
  1. Vitest: `inputKind`, `api` (convert-bulletin + ingest-collect 501), `FileConverter` mode group
  2. Playwright (`apps/e2e/`): **T1–T6 all green** (hard gate — S2.2)
  3. No silent AHL fall-through to single `/convert`; COLLECT 501 not treated as success
  4. Staging (13): H4–H5 + authenticated AHL happy path + COLLECT 501 notice
  5. H7 (`make test-live-bulletin` / UJ-011) remains API gate — not replaced by this TC
- **Source**: UJ-025; ADR-024; [#730](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/730);
  S016 / EV-012 (E12-1..E12-4; S2.2 = T1–T6 hard)

### TC-F7-008: Golden examples load (UJ-032 / #780)

- **Level**: T0 / T2 (Vitest hard) / H4–H5 when FE deploys
- **Objective**: Frontend static example catalog loads into FileConverter correctly
- **Matrix**:

  | Case | Action | Expect |
  | ---- | ------ | ------ |
  | C1 | Catalog completeness | ≥2 TAC/product **or** documented 1-fixture gap; ≥1 AHL; ≥1 happy-path IWXXM |
  | C2 | Load TAC example | Editor body set; `product` set; toast; demo labeling |
  | C3 | Load AHL example | `inputMode` = `ahl_bulletin`; multi-report body |
  | C4 | Load IWXXM example | `inputMode` = `collect_iwxxm` (or validate path); happy-path XML |
  | C5 | Soft-fail / file-queue | **Out of v1** — not tested |

- **Pass criteria**:
  1. Vitest: catalog unit + FileConverter click-to-load green
  2. No backend / env / DB dependency
  3. Staging H4–H5 smoke when frontend ships (13-deploy-smoke)
- **Source**: UJ-032; [#780](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/780);
  S021 / EV-016 (E16-5..E16-9)

### F7 UI↔API connection integration

Cross-layer coverage for workbench connection points (not only isolated unit/TC modules):

| Connection | API path | Backend integration | Playwright |
|------------|----------|---------------------|------------|
| Live lint + spans | `POST /api/v1/lint-tac` | `apps/backend/tests/api/test_f7_ui_connection_integration.py` | `apps/e2e/f7-ui-api-connections.e2e.spec.ts` |
| Decode panel | `POST /api/v1/decode-tac` | same | same |
| Soft-preview / Failed-TAC | `POST /api/v1/convert` (`preview=true`) | same + `test_frontend_contract_integration.py` | same |
| My METARs / sessions | `/api/v1/work-sessions*` + `product` | same | same |
| Manual TAC Input modes | `/convert`, `/convert-bulletin`, `/ingest-collect` | existing convert/bulletin tests + 501 | TC-F7-007 e2e (S016) |
| Golden examples (static FE) | (none — client fixtures) | — | TC-F7-008 Vitest (S021) |
| Browser CORS (H0i) | OPTIONS on lint/decode/convert | same + `test_h0i_connectivity.py` | — |

### F7 verify/deploy gate

Before closing S011 / EV-008:

- [ ] TC-F7-001–006 green at T2
- [ ] F7 UI↔API connection integration green (table above)
- [ ] TC-004′ (unified) green
- [ ] H6′ live smokes for UJ-013/015–019 (or documented waiver)
- [ ] Admin E2E modules removed or converted to TC-F7-006
- [ ] Child issues #697/#702/#665/#666/#694 closed or linked; #5 remains open

### F7 input-modes validation gate (S016 / EV-012 / #730)

- [ ] TC-F7-007 green at T2 (Playwright **T1–T6** + Vitest anchors)
- [ ] H4–H5 + authenticated AHL + COLLECT 501 on staging (13-deploy-smoke)
- [ ] Auto-switch (T3) required — no waiver without AskQuestion
- [ ] T5 (`.gz`) and T6 (read-only disable) hard gates (S2.2)

### F7 golden-examples gate (S021 / EV-016 / #780)

- [ ] TC-F7-008 green at T0/T2 (Vitest catalog + click-to-load)
- [ ] F7.g acceptance in feature-list met (or documented 1-fixture gaps)
- [ ] No backend / env / DB changes
- [ ] H4–H5 when FE deploys (13-deploy-smoke)
- [ ] #730 checklist documented; defects filed as separate bugs
- [ ] F7 status remains **Planned** (no Implemented flip this cycle)

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
- **Objective**: OIDC trusted publishing on `{pkg}-v*` tags
- **Pass criteria**: Workflow pattern + smoke job for all three packages; Trusted Publisher
  points at `EMPIRIC2/TAC-to-IWXXM` + `pypi-publish.yml` (EV-028)
- **Source**: F14; E10-25; #781

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

### EV-028 / #781 — EMPIRIC2 Codecov purge + PyPI Trusted Publisher (S035)

#### TC-EV028-001: Codecov removed from product CI

- **Level**: CI / repo hygiene
- **Objective**: No Codecov badge, workflow steps, config, or `CODECOV_TOKEN` secret
- **Pass criteria**: `ci-cd.yml` has no `codecov/codecov-action`; README badges gone;
  `.codecov.yml` absent; `CODECOV_TOKEN` not in repo secrets; CI green without upload
- **Source**: #781; EV-028

#### TC-EV028-002: Trusted Publisher → EMPIRIC2

- **Level**: Ops
- **Objective**: All three PyPI projects trust `EMPIRIC2/TAC-to-IWXXM` + `pypi-publish.yml`
- **Pass criteria**: Publisher settings match deploy.md table; stale pre-transfer publishers removed
- **Source**: #781; EV-028; UJ-023

#### TC-EV028-003: Tag publish `0.1.1` ×3 (UJ-023)

- **Level**: CI / live PyPI
- **Objective**: OIDC publish `tac-validate`, `iwxxm-validate`, `tac2iwxxm` at `0.1.1`
- **Pass criteria**: Tags `*-v0.1.1` → `pypi-publish.yml` green; `pip install <pkg>==0.1.1`
  in clean venv; landings have no required ADR/Feature/E10 refs
- **Source**: #781; EV-028; F12–F14

### TC-F15-001: Issue registry completeness (UJ-024)

- **Level**: T0 / CI
- **Objective**: Every METAR/**SPECI** lint emission uses a registered code; catalog export in sync
- **Pass criteria**: CI fails on unknown codes; registry row required for new rules; no ad-hoc
  severity literals for registered issues (ADR-028)
- **Source**: F15; #732; E11-8..E11-10

### TC-F15-002: METAR/SPECI accept → convert → XSD+Schematron (UJ-024)

- **Level**: T0 / CI (`tac2iwxxm` + `iwxxm-validate`)
- **Objective**: Expanded METAR **and SPECI** golden packs convert and pass M-xsd / M-sch on
  pinned versions
- **Pass criteria**: `product_matrix` / golden fixtures green for annex3 for both products;
  `iwxxm_us` where fixtures exist or documented N/A
- **Source**: F15 + F6 deepen; #732

### TC-F15-003: METAR/SPECI negative fixtures → registry diagnostics (UJ-024)

- **Level**: T0 / CI (`tac-validate`)
- **Objective**: Rule-violating METAR/SPECI TAC never silent-succeeds
- **Pass criteria**: Each negative case asserts expected registry `code`(s); useful messages;
  at least one SPECI-specific negative (e.g. missing SPECI keyword when product=speci)
- **Source**: F15 + F12 deepen; #732

### TC-F15-004: Workbench METAR/SPECI lint+convert smoke (UJ-024)

- **Level**: T2 / T3 (H4–H5 when redeployed)
- **Objective**: Operator Product=METAR and Product=SPECI (and Auto-detect) lint + convert;
  catalog tooltips via `GET /api/v1/lint-issue-catalog`
- **Pass criteria**: Console shows registry codes; tooltips/catalog panel resolve codes;
  convert+strict validation path works for both
- **Source**: F15; #732; E11-29; E11-31; F7 remains Planned (smoke only)

### TC-F15-005: METAR↔SPECI adjacency (UJ-024)

- **Level**: T0 / T2
- **Objective**: Shared METAR/SPECI pack does not mis-route or silent-pass across products
- **Pass criteria**: Auto-detect / product hint selects SPECI for `SPECI …` TAC; bulletin or
  paired fixtures keep per-report product identity; lint codes remain registry-backed
- **Source**: F15; #732 known gap AHL+SPECI adjacency

### F15 verify/deploy gate

- [ ] TC-F15-001..005 green
- [ ] Coverage-matrix METAR/SPECI **R1–R8** closed (HARD); non–R gaps only with AskQuestion + note

### TC-F20-001: TAF/SPECI registry completeness (UJ-031)

- **Level**: T0 / CI
- **Objective**: Every TAF/**SPECI** lint emission uses a registered code; catalog export in sync
- **Pass criteria**: CI fails on unknown codes; registry row required for new rules; ADR-028
- **Status**: **green** (S020/EV-015 T4.4) —
  `packages/tac-validate/tests/test_tc_f20_001_registry_completeness.py`
- **Source**: F20; #735/#734; E15-5

### TC-F20-002: TAF accept → convert → XSD+Schematron (UJ-031)

- **Level**: T0 / CI (`tac2iwxxm` + `iwxxm-validate`)
- **Objective**: Expanded TAF golden pack converts; root `iwxxm:TAF`; M-xsd / M-sch on pinned versions
- **Pass criteria**: annex3 goldens green; `iwxxm_us` where fixtures exist or documented N/A;
  #735 exceptional rules covered or deferred with rationale
- **Source**: F20 + F6.c deepen; #735

### TC-F20-003: SPECI accept → convert → XSD+Schematron (UJ-031)

- **Level**: T0 / CI (`tac2iwxxm` + `iwxxm-validate`)
- **Objective**: Full #734 SPECI golden bar (not residual-only); root `iwxxm:SPECI`
- **Pass criteria**: annex3 (+ iwxxm_us where applicable) green; exceptional-rule table covered
  or deferred with rationale
- **Source**: F20 + F6.b deepen; #734

### TC-F20-004: TAF/SPECI negative fixtures → registry diagnostics (UJ-031)

- **Level**: T0 / CI (`tac-validate`)
- **Objective**: Rule-violating TAF/SPECI TAC never silent-succeeds
- **Pass criteria**: Each negative asserts expected registry `code`(s); useful messages
- **Source**: F20 + F12 deepen; #735/#734

### TC-F20-005: Workbench TAF/SPECI lint+convert smoke (UJ-031)

- **Level**: T2 / T3 (H4–H5 when redeployed)
- **Objective**: Operator Product=TAF and Product=SPECI (and Auto-detect) lint + convert;
  catalog via `GET /api/v1/lint-issue-catalog`
- **Pass criteria**: Console shows registry codes; convert+strict validation works for both
- **Status**: **green** (S020/EV-015 T5.3 API smoke) —
  `apps/backend/tests/integration/test_tc_f20_005_taf_speci_catalog_smoke.py`
  (FE catalog filters T5.1–T5.2; live H4–H5 at T5.7)
- **Source**: F20; E15-7; F7 remains Planned (smoke only)

### TC-F20-006: SPECI↔METAR mis-classification guards (UJ-031)

- **Level**: T0 / T2
- **Objective**: Full #734 adjacency — never silent-swap SPECI↔METAR on shared structure
- **Pass criteria**: Auto-detect / product hint selects SPECI for `SPECI …` TAC; bulletin or
  paired fixtures keep per-report product identity; lint codes registry-backed
- **Source**: F20; #734; complements TC-F15-005

### F20 verify/deploy gate

- [ ] TC-F20-001..006 green
- [ ] Coverage-matrix TAF + SPECI rows updated; guidance gaps filed or closed
- [ ] H1–H3 if API ships; H4–H5 when FE touched (E15-7)

## F23 Test Cases (S025 / EV-019) — SIGMET + VA SIGMET quality

### TC-F23-001: SIGMET/VA SIGMET registry completeness (UJ-034)

- **Level**: T0 / CI
- **Objective**: Every SIGMET / VA SIGMET lint emission uses a registered code; catalog export
  in sync
- **Pass criteria**: CI fails on unknown codes; registry row required for new rules; ADR-028
- **Source**: F23; #733/#739; E19-5

### TC-F23-002: General SIGMET accept → convert → XSD+Schematron (UJ-034)

- **Level**: T0 / CI (`tac2iwxxm` + `iwxxm-validate`)
- **Objective**: Expanded general SIGMET golden pack converts; root `iwxxm:SIGMET`; M-xsd /
  M-sch on pinned versions
- **Pass criteria**: annex3 goldens green; #733 exceptional rules covered or deferred with
  rationale (matrix G1–G3)
- **Source**: F23 + F6.d deepen; #733

### TC-F23-003: VA SIGMET accept → convert → XSD+Schematron (UJ-034)

- **Level**: T0 / CI (`tac2iwxxm` + `iwxxm-validate`)
- **Objective**: Full #739 VA SIGMET golden bar; root `iwxxm:VolcanicAshSIGMET` (not
  `iwxxm:SIGMET`, not VAA)
- **Pass criteria**: annex3 goldens green; exceptional-rule table covered or deferred
  (matrix V1–V3); still submitted with HTTP `product=sigmet`
- **Source**: F23 + F6.d deepen; #739; E19-13

### TC-F23-004: SIGMET/VA negative fixtures → registry diagnostics (UJ-034)

- **Level**: T0 / CI (`tac-validate`)
- **Objective**: Rule-violating SIGMET / VA SIGMET TAC never silent-succeeds
- **Pass criteria**: Each negative asserts expected registry `code`(s); useful messages
- **Source**: F23 + F12 deepen; #733/#739

### TC-F23-005: Workbench SIGMET (+ VA) lint+convert smoke (UJ-034)

- **Level**: T2 / T3 (H4–H5 when redeployed)
- **Objective**: Operator Product=SIGMET lint + convert for general and VA fixtures; catalog
  via `GET /api/v1/lint-issue-catalog`
- **Pass criteria**: Console shows registry codes; convert+strict validation works;
  **additive FE catalog filters/copy for SIGMET (+ VA) tags** (E19-17=B); H4–H5 after FE deploy
- **Source**: F23; E19-7; E19-17; F7 remains Planned (product-path smoke + catalog filters)

### TC-F23-006: SIGMET / VA SIGMET / VAA adjacency guards (UJ-034)

- **Level**: T0 / T2
- **Objective**: Never silent-swap roots or products — VA TAC → `VolcanicAshSIGMET`; general
  non-VA/TC → `SIGMET`; VAA advisory remains `product=vaa` / advisory root
- **Pass criteria**: Content-based root selection under `product=sigmet`; negative or
  mismatch fixtures keep identity; lint codes registry-backed
- **Source**: F23; #733/#739; complements TC-F20-006 / TC-F15-005 adjacency pattern

### F23 verify/deploy gate

- [ ] TC-F23-001..006 green
- [ ] Coverage-matrix themes G1–G3 / V1–V3 / C1 updated; guidance gaps filed or closed
- [ ] H1–H3 if API ships; H4–H5 when FE touched (E19-7)

## F24 Test Cases (S026 / EV-020) — AIRMET quality / WMO golden

> Golden equality uses `canonicalize_xml` under **default** convert settings only
> (`profile=annex3`, default pinned `iwxxm_version`). E20-D3.

### TC-F24-001: AIRMET registry completeness (UJ-035)

- **Level**: T0 / CI
- **Objective**: Every AIRMET lint emission uses a registered ADR-028 code
- **Pass criteria**: CI fails on unknown codes; catalog export in sync
- **Source**: F24; #731

### TC-F24-002: WMO airmet-A6-1a-TS → convert → M-golden (UJ-035)

- **Level**: T0 / CI
- **Objective**: Vendor TAC converts to XML equal to vendor `airmet-A6-1a-TS.xml` under defaults
- **Pass criteria**: `canonicalize_xml(result) == canonicalize_xml(vendor)`; root `iwxxm:AIRMET`;
  geometry not nil-only (`AirspaceVolume` / vertical / horizontal projection per WMO)
- **Source**: F24 + F6 deepen; E20-D3

### TC-F24-003: AIRMET accept → XSD+Schematron (UJ-035)

- **Level**: T0 / CI
- **Objective**: AIRMET goldens validate M-xsd / M-sch on pinned versions
- **Pass criteria**: no blocking errors (SCHEMATRON_SKIPPED allowed per project policy)
- **Source**: F24

### TC-F24-004: AIRMET negatives → registry diagnostics (UJ-035)

- **Level**: T0 / CI
- **Objective**: Rule-violating AIRMET never silent-succeeds
- **Pass criteria**: expected registry codes; useful messages
- **Source**: F24 + F12 deepen

### TC-F24-005: Workbench AIRMET lint+convert smoke (UJ-035)

- **Level**: T2 / T3 (H4–H5 when redeployed)
- **Objective**: Product=AIRMET path + Examples load when F24 golden passes
- **Pass criteria**: lint+convert+strict validation; H4–H5 after FE deploy
- **Source**: F24; F7 Planned (smoke)

### F24 verify/deploy gate

- [ ] TC-F24-001..005 green
- [ ] Coverage-matrix AIRMET themes updated
- [ ] H1–H3 if API ships; H4–H5 when FE touched

## F25 Test Cases (S026 / EV-020) — WMO METAR/SPECI/TAF parity + UI gate

### TC-F25-001: WMO METAR/SPECI/TAF defaults → M-golden (UJ-036)

- **Level**: T0 / CI
- **Objective**: Listed vendor TAC examples convert equal to vendor XML under **defaults**
- **Pass criteria**: `metar-A3-1`, `speci-A3-2`, **`taf-A5-1` and `taf-A5-2`** pass
  `canonicalize_xml` equality; translation-failed examples are **not** happy-path goldens
- **Source**: F25; E20-A; E20-D3; **E20-E1**

### TC-F25-002: XSD+Schematron on F25 goldens (UJ-036)

- **Level**: T0 / CI
- **Objective**: F25 golden XML validates
- **Pass criteria**: no blocking XSD/SCH errors
- **Source**: F25

### TC-F25-003: Examples catalog WMO-passers only (UJ-036 / deepen UJ-032)

- **Level**: T0 / T2 (Vitest)
- **Objective**: FE catalog lists only demos that pass the strict WMO bar for in-scope products
- **Pass criteria**: Non-passers removed/hidden; SIGMET keepers retained; AIRMET appears when
  F24 green; provenance points at vendor or mirrored fixture; deepen TC-F7-008
- **Source**: F25 + F7.g; E20-3

### TC-F25-004: Workbench load WMO example → convert smoke (UJ-036)

- **Level**: T2 / T3 / H4–H5
- **Objective**: Operator loads a catalog WMO example and converts successfully
- **Pass criteria**: editor+product set; convert ok; demo banner; H4–H5 when FE deploys
- **Source**: F25; UJ-032 deepen

### F25 verify/deploy gate

- [ ] TC-F25-001..004 green
- [ ] TC-F7-008 deepen green
- [ ] H4–H5 when FE touched

## F26 Test Cases (S027 / EV-021) — VAA quality / WMO golden

### TC-F26-001: VAA registry completeness (UJ-037)

- **Level**: T0
- **Objective**: All VAA lint codes registered (ADR-028); CI fails on unknown codes
- **Pass criteria**: registry export includes VAA product codes used by rules; drift check green
- **Source**: F26; #736; E21-D1

### TC-F26-002: WMO va-advisory-A7-2 → convert → M-golden (UJ-037)

- **Level**: T0 / T2
- **Objective**: Vendor `va-advisory-A7-2.tac` → convert under defaults → `canonicalize_xml`
  equal to vendor XML; root `iwxxm:VolcanicAshAdvisory` (includes `NO VA EXP` → forecast status)
- **Pass criteria**: golden assert; profile=annex3; default pinned iwxxm_version (ADR-032)
- **Source**: F26 + F6.f deepen; E21-2; E21-D3 **F26 theme V3**

### TC-F26-003: VAA accept → XSD+Schematron (UJ-037)

- **Level**: T0 / T2
- **Objective**: Golden / accept VAA IWXXM validates XSD+Schematron (`iwxxm-validate`)
- **Pass criteria**: M-xsd / M-sch pass on F26 goldens
- **Source**: F26

### TC-F26-004: VAA negatives → registry diagnostics (UJ-037)

- **Level**: T0 / T2
- **Objective**: Negative fixtures (missing DTG/VAAC; exceptional-rule violations) emit
  registry codes; translation-package TAC themes mined as accept/neg where useful (E21-D4)
- **Pass criteria**: no silent success; codes in ADR-028 catalog
- **Source**: F26 + F12 deepen; #736; E21-D3 **F26 themes V1–V2**

### TC-F26-005: Workbench VAA lint+convert smoke (UJ-037)

- **Level**: T2 / T3 / H4–H5
- **Objective**: Product=VAA path + Examples load when F26 golden passes; hide non-passers;
  unlock VAA catalog independently of TCA (**S02.M2** incremental)
- **Pass criteria**: lint+convert ok; catalog policy; H4–H5 when FE deploys
- **Source**: F26; F7 Planned (smoke); E21-3; S02.M2; deepen UJ-032 / TC-F7-008

### TC-F26-006: VAA / VA SIGMET adjacency guards (UJ-037)

- **Level**: T0 / T2
- **Objective**: VAA encode never emits `iwxxm:VolcanicAshSIGMET`; VA SIGMET path never emits
  `iwxxm:VolcanicAshAdvisory` (F23 keepers stay green)
- **Pass criteria**: adjacency fixtures; complements TC-F23-006
- **Source**: F26; #736/#739

### F26 verify/deploy gate

- [ ] TC-F26-001..006 green
- [ ] Coverage-matrix **F26 themes** V1–V3/C1 closed or deferred
- [ ] H4–H5 when FE touched

## F27 Test Cases (S027 / EV-021) — TCA quality / WMO golden

### TC-F27-001: TCA registry completeness (UJ-038)

- **Level**: T0
- **Objective**: All TCA lint codes registered (ADR-028); CI fails on unknown codes
- **Pass criteria**: registry export includes TCA codes; drift check green
- **Source**: F27; #737

### TC-F27-002: WMO tc-advisory-A2-2 → convert → M-golden (UJ-038)

- **Level**: T0 / T2
- **Objective**: Vendor `tc-advisory-A2-2.tac` → convert under defaults → `canonicalize_xml`
  equal to vendor XML; root `iwxxm:TropicalCycloneAdvisory` (RMK NIL → remarks inapplicable)
- **Pass criteria**: golden assert; defaults only (ADR-032)
- **Source**: F27 + F6.f deepen; E21-2; E21-D3 **F27 theme T3**

### TC-F27-003: TCA accept → XSD+Schematron (UJ-038)

- **Level**: T0 / T2
- **Objective**: Golden / accept TCA IWXXM validates XSD+Schematron
- **Pass criteria**: M-xsd / M-sch pass on F27 goldens
- **Source**: F27

### TC-F27-004: TCA negatives → registry diagnostics (UJ-038)

- **Level**: T0 / T2
- **Objective**: Negative fixtures + exceptional-rule table; translation-package TAC themes
  mined (E21-D4); no Amd79 XML byte-match under 2025-2
- **Pass criteria**: registry diagnostics; explicit deferrals allowed with rationale
- **Source**: F27 + F12 deepen; #737; E21-D3 **F27 themes T1–T2**

### TC-F27-005: Workbench TCA lint+convert smoke (UJ-038)

- **Level**: T2 / T3 / H4–H5
- **Objective**: Product=TCA path + Examples load when F27 golden passes; hide non-passers;
  unlock TCA catalog independently of VAA (**S02.M2** incremental)
- **Pass criteria**: lint+convert ok; catalog policy; H4–H5 when FE deploys
- **Source**: F27; E21-3; S02.M2; deepen UJ-032 / TC-F7-008

### TC-F27-006: TCA / TC SIGMET adjacency guards (UJ-038)

- **Level**: T0 / T2
- **Objective**: TCA encode never emits `iwxxm:TropicalCycloneSIGMET`; product=`tca` path
  stays advisory root
- **Pass criteria**: adjacency fixtures; #738 remains OOS for quality bar
- **Source**: F27; #737/#738

### F27 verify/deploy gate

- [ ] TC-F27-001..006 green
- [ ] Coverage-matrix **F27 themes** T1–T3/C1 closed or deferred
- [ ] H4–H5 when FE touched

## S030 / EV-023 — APAC FAQ + codes encode/validate deepen (#800)

> No new UJ — library/CI + existing convert/validate journeys (UJ-001/005/006/016 deepen).
> Runtime pin **v2025-2**. Informative sources do not replace Annex 3 / vendor XSD/SCH.

### TC-EV023-001: NSC without layered cloud (P0)

- **Level**: T0 / T2
- **Objective**: TAC with `NSC` encodes empty/nil cloud (`nothingOfOperationalSignificance`);
  must **not** emit layered `<iwxxm:cloud>` content; XSD/SCH **negative** fixtures; lint beyond
  research `NSC_PRESENT` if needed
- **Pass criteria**: convert + validate green; negative fixture fails when layers present with NSC
- **Source**: F6/F12/F2 deepen; #800 P0; FAQ §14.3

### TC-EV023-002: Missing WX / Guidance nils (P0)

- **Level**: T0 / T2
- **Objective**: Missing weather (and related TAC gaps) match `TAC-to-XML-Guidance.txt` +
  iwxxm-translation examples; `common/nil` vs `iwxxm/nil` per product/XSD vocabulary
- **Pass criteria**: fixtures assert correct nil URI family under v2025-2
- **Source**: F6/F2; #800 P0; FAQ §3.2; WMO-306 D-1 lineage (corroborate only)

### TC-EV023-003: translationFailedTAC quarantine (P0)

- **Level**: T0 / T2
- **Objective**: Unreliable TAC → quarantine shape with original TAC on `translationFailedTAC`;
  no operational TAC-in-XML-comments; no partial translate; attr matrix vs official
  `*-translation-failed.xml`
- **Pass criteria**: regression fixtures; deepen UJ-016 soft-fail path consistency
- **Source**: F6/F2; #800 P0; FAQ §4.1 / §8.6

### TC-EV023-004: Dual-register colour + nil encode policy (P1)

- **Level**: T0
- **Objective**: Encode href policy for `49-2/AviationColourCode` vs `iwxxm/AviationColourCode`;
  dual nil SCH RDF (`common/nil` + `iwxxm/nil`); offline vendor RDF/CSV only
- **Pass criteria**: unit/integration tests; no live codes.wmo.int HTML dependency in CI
- **Source**: F6/F13; #800 P1

### TC-EV023-005: iwxxm-translation informative suite (P1)

- **Level**: T0 / CI or nightly
- **Objective**: Amd79-80-2023 METAR/TAF/VAA/TCA **TAC** → our 2025-2 → XSD+SCH; mark
  **informative**; do not fail on 2023-1 XML byte diffs (`gml:id`, translation* attrs, clocks)
- **Pass criteria**: suite wired; SIGMET/AIRMET remain on official schemas.wmo.int examples
- **Source**: F6/F2; #800 P1

### TC-EV023-006: translationCentre* gate (P1)

- **Level**: T0 / T2
- **Objective**: Default in-State convert omits `translationCentre*`; emit only when
  config/cross-State Translation Centre mode enabled
- **Pass criteria**: default omit; config-on emits designator/name
- **Source**: F6; config-spec; #800 P1; FAQ §14.5

### TC-EV023-007: SIGMET FIR / “S OF” polygon helpers (P2)

- **Level**: T0
- **Objective**: Prefer polygon TAC; FIR-boundary intersection helpers; coordinate #738 / F23
- **Pass criteria**: helper unit tests; full TC SIGMET quality remains #738
- **Source**: F6 deepen; #800 P2; #738

### TC-EV023-008: COLLECT / multi-version namespaces (P2)

- **Level**: T0 / package
- **Objective**: AFS COLLECT mandate + per-group `http://icao.int/iwxxm/{version}` documented
  and hooked under F16–F19 / bulletin — not single-report convert SoT
- **Pass criteria**: tests or deferred-with-rationale on dissemination path; convert SoT unchanged
- **Source**: F16–F19 deepen; #800 P2

### TC-EV023-009: Optional #798 encode QA + coverage matrix (P2)

- **Level**: T0 / docs
- **Objective**: Only if gaps survive defer-to-latest (aviation nilReasons, VAA/VONA METCE,
  TCA METCE name-only); confirm `COVERAGE_MATRIX` / conversion citations after P0/P1
- **Pass criteria**: gaps closed or explicitly deferred; matrix accurate; no `.local/` in git
- **Source**: #800 P2; #798/#719

### EV-023 verify/deploy gate

- [ ] TC-EV023-001..006 green (P0+P1)
- [ ] TC-EV023-007..009 green or deferred with rationale (P2)
- [ ] Informative translation suite does not fail CI on 2023-1 XML byte diffs
- [ ] 13-deploy-smoke when convert/validate behavior ships (E23-4)

## EV-024 / S031 — IWXXM domain mine + WMO sample menu (#804 / #807 / #773)

### TC-EV024-001: #804 folder×relevancy + examples matrix

- **Level**: T0 (docs / mining)
- **Objective**: Every path under vendor/pin `IWXXM/` (+ sibling triage) has an explicit
  relevancy call; every official example stem has a surface decision
  (validate / convert / UI catalog / defer)
- **Pass criteria**: Mining notes exist and are indexed in `docs/domain/mining/README.md`
- **Source**: #804; E24-3=3a

### TC-EV024-002: #807 org / sibling refresh

- **Level**: T0 (docs / mining)
- **Objective**: wmo-im org ranking refreshed vs pin v2025-2; IWXXM family + encode-adjacent
  lineage re-checked; WIS2/#806 explicitly out
- **Pass criteria**: Org mining notes updated; durable rows promoted or deferred with rationale
- **Source**: #807; E24-x exclude #806

### TC-EV024-003: #773 IWXXM-US / MDL coverage checklist

- **Level**: T0 (docs / mining)
- **Objective**: METAR/SPECI (and TAF companion) model types mapped TAC×encode×validate×fixture;
  RULE_SOURCE_URLS rows for PDF + modelling + VLab
- **Pass criteria**: Mining notes + catalog rows; US examples not mixed into WMO catalog
- **Source**: #773; F6.b

### TC-EV024-004: Sample menu lists official WMO stems (UJ-039)

- **Level**: T0 / T2
- **Objective**: Product-in-scope official WMO stems with TAC peers appear in Examples /
  sample menu (strict passer **or** WMO reference tier per ADR-032 amend)
- **Pass criteria**: Catalog Vitest / `FIXTURE_GAPS.md` accurate; provenance to vendor paths;
  translation-failed excluded from happy-path
- **Source**: E24-C; UJ-039; #804

### TC-EV024-005: Load WMO sample into editor (UJ-039)

- **Level**: T0 / T2
- **Objective**: Selecting a registered WMO sample loads TAC into the workbench editor with
  correct product and non-operational provenance banner
- **Pass criteria**: Unit/smoke green for ≥1 stem per in-scope product that has a TAC peer
  (or documented defer + child issue)
- **Source**: UJ-039; F7.g deepen

### TC-EV024-006: Strict vs reference badge (UJ-039 / UJ-036 deepen)

- **Level**: T0
- **Objective**: UI/catalog metadata distinguishes `wmoPass` (ADR-032 equality) from WMO
  reference samples
- **Pass criteria**: Catalog tests assert both tiers; no silent demotion of strict bar
- **Source**: ADR-032 amend; E24-C

### TC-EV024-007: Validate/CI wire in-scope stems

- **Level**: T0 / T2
- **Objective**: In-scope WMO stems exercised on validate (and convert soft-compare where TAC
  exists) or explicitly deferred with child issue
- **Pass criteria**: Coverage report / pytest expands beyond prior subset; roadmap-only marked
- **Source**: #804; E24-C=C1 portion

### TC-EV024-008: Durable promotions + child issues

- **Level**: T0
- **Objective**: Durable findings promoted; ❌/⚠ encode/lint/SCH gaps filed as child issues
  (link #800 / quality tickets); no big-bang encode in this cycle
- **Pass criteria**: PR checklist + issue comments on #804/#807/#773 with links
- **Source**: E24-3=3a; discovery-first archetype

### EV-024 verify/deploy gate

- [ ] TC-EV024-001..003 mining deliverables complete
- [ ] TC-EV024-004..006 sample menu / UJ-039 green
- [ ] TC-EV024-007 validate/CI wire or deferrals with children
- [ ] TC-EV024-008 promotions + child issues filed

## EV-025 / S032 — iwxxm-us REMARKS encode + VA multi-location (#810–#812 / #809)

### TC-EV025-001: #810 Variable RVR / meanRVR withheld (UJ-040)

- **Given** METAR/SPECI TAC with variable RVR REMARKS (incl. meanRVR withheld / nilReason patterns from PDF)
- **When** convert `profile=iwxxm_us`
- **Then** `AerodromeVariableRVR` (or pin-equivalent) emitted; withheld patterns covered; annex3/`iwxxm_us` golden + validate smoke
- **Tier**: T0

### TC-EV025-002: #811 Lightning / VisuallyObservablePhenomena (UJ-040)

- **Given** TAC with lightning / VOP REMARKS (PDF sample pack; local `.local/` extract only)
- **When** lint (as needed) + convert `iwxxm_us`
- **Then** `ObservedLightning` / `VisuallyObservablePhenomena` (and frequency/type) encoded; fixture pack + combined-catalog expectations
- **Tier**: T0

### TC-EV025-003: #812 SnowIncrease + sensor outage (UJ-040)

- **Given** TAC with snow-increase and/or sensor-outage REMARKS
- **When** lint + convert `iwxxm_us`
- **Then** `SnowIncrease` and Failed/Inoperative/MeteorologicalSensors paths encoded; goldens/negatives as appropriate
- **Tier**: T0

### TC-EV025-004: Adjacent dig ❌ US types pack (UJ-040)

- **Given** remaining dig-checklist ❌/⚠ types (WindShift, sky/convective, hail, sector/obscuration, second-site/tower, variable CIG/SKY/VIS, max/min, ProcessedProperty, Addendum residuals, codelists, …)
- **When** convert `iwxxm_us` (parametrized matrix)
- **Then** each type encodes per pin XSD (dig ❌ encode residuals **block Gate C** — E25-T5=3)
- **Tier**: T0

### TC-EV025-005: US fixtures stay out of WMO sample menu (UJ-039 deepen)

- **Given** new US REMARKS goldens / fixtures from Lane A
- **When** examples catalog / sample menu is inspected
- **Then** no US-only examples appear in the WMO menu (UJ-039 rule)
- **Tier**: T0

### TC-EV025-006: Malformed US REMARKS diagnostics (UJ-010 deepen)

- **Given** malformed / unknown US REMARKS tokens alongside valid structured remarks
- **When** convert `iwxxm_us`
- **Then** diagnostics non-empty; no silent drop of failure path
- **Tier**: T0

### TC-EV025-007: Unparsed REMARKS retain in humanReadableText (UJ-026 deepen)

- **Given** mix of newly structured + still-unparsed REMARKS
- **When** convert `iwxxm_us`
- **Then** structured elements emitted; remainder retained in `iwxxm-us:humanReadableText`
- **Tier**: T0

### TC-EV025-008: #809 sigmet-multi-location-VA package golden (UJ-041)

- **Given** vendor `sigmet-multi-location-VA.{tac,xml}` under pin
- **When** convert annex3 (default settings)
- **Then** root `iwxxm:VolcanicAshSIGMET`; multi-location geometry / forecast collections;
  **`canonicalize_xml` equal to vendor XML** under ADR-032 defaults (EV-026 — soft-compare
  / inequality assert removed; `E26-TC=1` reuses this id)
- **Tier**: T0
- **History**: EV-025 shipped soft-compare gate; EV-026 requires strict equality

### TC-EV025-009: #809 catalog promote to wmoPass (UJ-041)

- **Given** equality from TC-EV025-008
- **When** catalog / Vitest assert under ADR-032 defaults
- **Then** catalog tier is `wmoPass` (`wmoPass: true`); FIXTURE_GAPS equality-pending note
  removed; sample-menu label is passer not reference
- **Tier**: T0
- **History**: EV-025 allowed `wmoReference` until equality; EV-026 requires promote

### TC-EV025-010: Combined-catalog validate smoke for US extension blocks (F2/F13)

- **Given** Lane A emitted iwxxm-us extension XML
- **When** `iwxxm-validate` with combined WMO + iwxxm-us catalogs
- **Then** smoke pass (or documented SCH deferral with child issue)
- **Tier**: T0

### EV-025 verify/deploy gate

- [x] TC-EV025-001..003 named tickets green (#816)
- [x] TC-EV025-004 adjacent ❌ pack green (#816)
- [x] TC-EV025-005..007 UJ-039/010/026 deepen green (#816)
- [x] TC-EV025-008 soft-compare green (#816); **strict** deferred → EV-026
- [x] TC-EV025-009 stayed `wmoReference` until equality (#816); promote → EV-026
- [x] TC-EV025-010 validate smoke green (#816)
- [ ] 13-deploy-smoke if API convert/validate behavior ships (waived at EV-025 close)

## EV-026 / S033 — #809 VA multi-location ADR-032 equality / wmoPass

Reuses **TC-EV025-008..009** with strict semantics (`E26-TC=1`). No new TC ids.

### EV-026 verify/deploy gate

- [x] TC-EV025-008 strict equality green (no soft_compare) (#817)
- [x] TC-EV025-009 catalog `wmoPass` + FIXTURE_GAPS cleared (#817)
- [x] #809 GitHub closed
- [x] 13-deploy-smoke PASS (S033 / EV-026)

## EV-027 / S034 — #815 official WMO decode residual matrix

New **TC-EV027-001..005** (`E27-TC=1`). Ties **UJ-042**; deepens UJ-039 / UJ-020.

### TC-EV027-001: Inventory of official WMO TAC peers (UJ-042)

- **Given** current `vendor/schemas` pin (`IWXXM/examples/` + annex3 goldens mirrored)
- **When** inventory is generated / checked in
- **Then** every in-scope official WMO stem with a TAC peer appears in catalog **or**
  `FIXTURE_GAPS` with rationale + child issue (no silent omissions)
- **Tier**: T0
- **Source**: #815; E27-1

### TC-EV027-002: Catalog ∪ FIXTURE_GAPS completeness (UJ-042 / UJ-039 deepen)

- **Given** inventory from TC-EV027-001
- **When** catalog Vitest / `FIXTURE_GAPS.md` assert
- **Then** set equality holds; US/quarantine/translation-failed stay out of WMO happy-path
- **Tier**: T0 / T2
- **Source**: #815; ADR-032; UJ-039

### TC-EV027-003: Decode residual matrix — empty or allowlisted (UJ-042)

- **Given** each registered official happy-path TAC peer (CI-mirrored fixture)
- **When** `decode_tac` runs
- **Then** `residuals == []` **or** residual text matches documented expected-residual
  allowlist (G4 best-effort / deferred token / linked child issue); unexpected leftovers fail
- **Tier**: T0 / T2
- **Source**: #815; ADR-025; E27-4 triage

### TC-EV027-004: Load path for registered official stems (UJ-042 / UJ-039)

- **Given** a registered official stem in `examplesCatalog.ts`
- **When** sample is selected (unit/smoke)
- **Then** correct TAC body, product, and provenance banner (`wmoPass` vs `wmoReference`)
- **Tier**: T0 / T2
- **Source**: #815; ADR-032

### TC-EV027-005: Optional H4–H5 residual chrome smoke (UJ-042)

- **Given** deployed FE + API when catalog/decode chrome ships
- **When** operator loads one passer per product and opens decode panel
- **Then** no unexpected residual chrome for happy-path textbook peers
- **Tier**: H4–H5 / T3 (when_ships)
- **Source**: #815; connectivity gates

### EV-027 verify/deploy gate

- [x] TC-EV027-001..002 inventory + catalog∪gaps green
- [x] TC-EV027-003 residual matrix green (allowlist documented; VAA/TCA → #820)
- [x] TC-EV027-004 load path green (catalog Vitest)
- [x] TC-EV027-005 **waived** at close (`D-S034-gate-c` — no FE deploy)
- [ ] #815 GitHub closed on PR merge (deferral child #820)
- [x] 13-deploy-smoke **waived** (`D-S034-gate-c`)

## S036 / EV-029 — Eight-family AHL / lint / convert / validate (#823)

### TC-EV029-001: Coverage matrix eight-family × roles (UJ-043)

- **Given** `docs/domain/rules/COVERAGE_MATRIX.md` + canonicals after Phase A
- **When** audit runs for METAR/SPECI/TAF/SIGMET×3/AIRMET/VAA/TCA/SWXA × lint/convert/IWXXM-validate
- **Then** every cell is pass, explicit N/A, or defer+child issue (no silent blanks)
- **Tier**: T0 / docs CI
- **Source**: #823; E29-2 Phase A

### TC-EV029-002: TAC input-shape + IWXXM example inventory (UJ-043)

- **Given** inventory of standalone / AHL / multi-report TAC fixtures + official IWXXM peers
- **When** catalog ∪ FIXTURE_GAPS ∪ test fixtures assert
- **Then** each family has ≥1 shape covered or gap-documented; SIGWX/VONA/QVACI marked OOS
- **Tier**: T0
- **Source**: #823; UJ-043

### TC-EV029-003: Shared AHL / BBB / T1T2 map (UJ-043)

- **Given** AHL fixtures for each TAC `T1T2` in #823 B1 table
- **When** parse + convert (or lint) runs
- **Then** IWXXM `T1T2` + root type agree; `AAx`→AMENDMENT, `CCx`→CORRECTION, `RRx`→NORMAL
  (bulletin subsequent); invalid BBB rejected
- **Tier**: T0 / T2
- **Source**: #823 B1–B3; F6.bulletin

### TC-EV029-004: TC SIGMET root + quality path (#738)

- **Given** TC SIGMET accept TAC (`WC` / tropical-cyclone SIGMET form)
- **When** convert (defaults) + validate
- **Then** root `iwxxm:TropicalCycloneSIGMET`; XSD+Schematron pass; not `iwxxm:SIGMET` /
  not TCA advisory root
- **Tier**: T0 / T2
- **Source**: #738; F23 deepen; #823 B5

### TC-EV029-005: VAA/TCA bulletin + encode/decode residuals (#820 / #823 B4)

- **Given** multi-report VAA/TCA and #823 B4 / #820 residual cases
- **When** split + convert + decode
- **Then** `=`-terminator split (not blank-line-only); encode gaps closed or child-issued;
  decode residuals empty or allowlisted with child link
- **Tier**: T0 / T2
- **Source**: #820; #823 B2/B4; F26/F27 deepen

### TC-EV029-006: Report-state matrix (Normal/AMD/COR/CNL/NIL)

- **Given** fixtures per family where schema/TAC permits each state
- **When** lint + convert
- **Then** cancellation/NIL are not `reportStatus`; AMD/COR map correctly; CNL/NIL use
  product-specific or nilReason paths
- **Tier**: T0
- **Source**: #823 B3; COM-010..014

### TC-EV029-007: Product-order regression smoke (UJ-043)

- **Given** one accept fixture per family in Phase B order
- **When** lint → convert → validate pipeline runs in CI
- **Then** all green or explicitly skipped with child issue id in skip reason
- **Tier**: T0 / T2
- **Source**: #823; E29-3 order

### TC-EV029-008: Optional H4–H5 when FE Examples unlock (UJ-043)

- **Given** FE catalog changes for SWXA / TC SIGMET passers
- **When** operator loads one new passer
- **Then** workbench lint+convert smoke passes
- **Tier**: H4–H5 / T3 (when_ships)
- **Source**: connectivity gates; F7.g

### TC-F28-001: SWXA registry completeness (UJ-043)

- **Level**: T0 / CI
- **Objective**: Every SWXA lint emission uses a registered code
- **Pass criteria**: CI fails on unknown codes; ADR-028 registry row for new rules
- **Source**: F28; #740

### TC-F28-002: SWXA accept → convert → XSD+Schematron (UJ-043)

- **Level**: T0 / T2
- **Objective**: Happy-path SWXA TAC converts to `iwxxm:SpaceWeatherAdvisory` and validates
- **Pass criteria**: root + XSD+SCH pass under defaults
- **Source**: F28; #740/#823

### TC-F28-003: SWXA golden / official peer (UJ-043)

- **Level**: T0 / T2
- **Objective**: When a vendor/official peer exists, convert matches policy (ADR-032 equality
  or documented `wmoReference`)
- **Pass criteria**: peer fixture green or explicit defer+child
- **Source**: F28; ADR-032

### TC-F28-004: SWXA negative fixtures → registry diagnostics (UJ-043)

- **Level**: T0
- **Objective**: Malformed / incomplete SWXA TAC yields registry diagnostics (not crash)
- **Pass criteria**: negative pack; codes registered
- **Source**: F28; #740

### TC-F28-005: SWXA product-path smoke (UJ-043)

- **Level**: T2; H4–H5 if FE
- **Objective**: API (and Examples when unlocked) SWXA lint+convert path works
- **Pass criteria**: smoke green; catalog only lists passers when unlocked
- **Source**: F28; F7.g

### TC-F28-006: SWXA / COM adjacency + AHL FN→LN (UJ-043)

- **Level**: T0 / T2
- **Objective**: SWXA never mis-rooted as SIGMET/VAA/TCA; AHL `FN` maps to IWXXM `LN`;
  API accepts `product=swxa` (reject `swx` / unknown)
- **Pass criteria**: adjacency + AHL fixtures; convert/lint/decode accept `swxa`
- **Source**: F28; #823 B1; api-contract EV-029

### EV-029 verify/deploy gate

- [ ] TC-EV029-001..007 green (or deferred with child issues)
- [ ] TC-F28-001..006 green (or deferred with child issues)
- [ ] TC-EV029-008 when FE ships / else waive
- [ ] Coverage matrix + canonicals updated
- [ ] #823 / #738 / #820 / #740 closed or children linked
- [ ] 12/13 per Standard when behavior deploys

## S037 / EV-030 — Quality residuals (#831 / #829 / #820)

### TC-EV030-001: Harness design note answers #831 eval questions (UJ-044)

- **Level**: T0 (doc gate)
- **Objective**: Case storage, rule SoT, granularity, assertions, product scope, CI cost,
  fixture-fill policy documented with recommendation
- **Pass criteria**: Session design note (or ADR-lite) exists and is cited from F29
- **Source**: #831; F29

### TC-EV030-002: Lint + convert + validate runners land (UJ-044)

- **Level**: T0 / T2
- **Objective**: Shared runners execute RuleCase fixtures for three engines
- **Pass criteria**: Pilot rules run; `needs-fixture` skip/xfail policy documented
- **Source**: F29; TC-F29-002

### TC-EV030-003: Inventory gate for in-scope rules (UJ-044)

- **Level**: T0 / T2
- **Objective**: Every registered in-scope rule has 20 slots or explicit TODO
- **Pass criteria**: Gate test fails on silent gaps
- **Source**: F29; TC-F29-004

### TC-EV030-004: TC SIGMET tac-validate pack + STNR/geometry (#829)

- **Level**: T0 / T2
- **Objective**: Dedicated TC lint accept/negatives; STNR/exceptional shapes or OOS cite
- **Pass criteria**: #829 AC1–AC2 met
- **Source**: #829; F23 deepen

### TC-EV030-005: A6-2-TC catalog / menu tier decision (#829)

- **Level**: T0; H4–H5 if FE unlock
- **Objective**: Unlock `wmoPass`/`wmoReference` or defer with recorded reason (ADR-032)
- **Pass criteria**: #829 AC3 met; H4–H5 only if FE ships
- **Source**: #829; UJ-039; ADR-032

### TC-EV030-006: VAA/TCA decode residual deepen (#820)

- **Level**: T0 / T2
- **Objective**: Structured decode for major labels/forecast hours; shrink allowlist/matrix
- **Pass criteria**: #820 AC met or child-issued with cite
- **Source**: #820; F9/F26/F27 deepen

### TC-F29-001: Harness recommendation written (UJ-044)

- **Level**: T0
- **Objective**: #831 evaluation questions answered with recommendation
- **Pass criteria**: Design note approved in 04/07 spike
- **Source**: F29; #831

### TC-F29-002: Three-engine runners (UJ-044)

- **Level**: T2
- **Objective**: Lint + convert + validate parameterized runners
- **Pass criteria**: At least pilot rules execute via runners
- **Source**: F29

### TC-F29-003: Pilot METAR/SPECI matrices (UJ-044)

- **Level**: T2
- **Objective**: Pilot product set filled or explicit `needs-fixture`
- **Pass criteria**: Inventory shows no silent empty slots for pilot rules
- **Source**: F29

### TC-F29-004: Inventory gate CI (UJ-044)

- **Level**: T0 / T2
- **Objective**: New rule without matrix slots fails gate
- **Pass criteria**: Gate test/docs checklist in CI
- **Source**: F29

### TC-F29-005: Node ids encode rule/bucket/case (UJ-044)

- **Level**: T0 / T2
- **Objective**: Failures name `RULE_ID/bucket/NN`
- **Pass criteria**: Pytest node ids match convention
- **Source**: F29

### TC-F29-006: CI smoke + optional full matrix (UJ-044)

- **Level**: T2 / CI
- **Objective**: PR-smoke subset; full matrix optional/nightly; no network
- **Pass criteria**: CI wiring documented and green for smoke
- **Source**: F29

### TC-F29-007: Authoring docs for new rules (UJ-044)

- **Level**: T0
- **Objective**: Definition of done for rule PRs includes matrix slots
- **Pass criteria**: Docs path cited from package README or CONTRIBUTING
- **Source**: F29

### EV-030 verify/deploy gate

- [ ] TC-EV030-001..006 green (or deferred with child issues)
- [ ] TC-F29-001..007 green (or deferred with child issues)
- [ ] #831 / #829 / #820 closed or children linked
- [ ] H4–H5 when FE menu unlock ships / else waive
- [ ] 12/13 per Standard when behavior deploys

## F9 deepen (S026 / EV-020) — glossary registry

### TC-F9-003: Seven-product glossary meanings (UJ-020 deepen)

- **Level**: T0 / T2
- **Objective**: Token explanations use plain-English **meanings** from official/near-official
  sources first (e.g. `OBSC`→obscured, `TS`→thunderstorm), with YAML **overrides** where
  present; not category-only labels; optional F3/OpenAIP names
- **Pass criteria**: SIGMET/AIRMET sample tokens match expected strings; METAR/SPECI/TAF keep
  value-aware quality; VAA/TCA keywords expanded where sourced; missing OpenAIP → ICAO
  designator only (no fail); YAML override wins when set
- **Source**: F9 deepen; E20-B; E20-E2; ADR-032

### TC-F9-004: Official sources + YAML override load (UJ-020 deepen)

- **Level**: T0
- **Objective**: Official/near-official tables load; YAML overlay merges; unknown tokens remain
  residual or generic fallback
- **Pass criteria**: unit tests for merge order (official → YAML override); no LLM
- **Source**: F9 deepen; E20-E2; ADR-032

## F21 / F22 Test Cases (S023 / EV-017) — stubs

> Detailed steps finalize in **04-tech-plan**. Objectives and pass criteria locked at 02
> (`D-S023-02-C-EV017-A`).

### TC-F22-001: First-visit privacy notice (UJ-033)

- **Level**: T2 / T3
- **Objective**: First visit shows Solution A privacy notice disclosing IndexedDB work history /
  preference storage; dismiss/ack persists preference
- **Pass criteria**: Notice visible once per preference scope; no CMP/analytics scripts; copy
  matches F22 acceptance
- **Source**: UJ-033; F22 / E17-7 / E17-9

### TC-F22-002: Privacy settings preference center (UJ-033)

- **Level**: T2 / T3
- **Objective**: Settings UI lets user view/change privacy preferences (Solution A)
- **Pass criteria**: Preferences read/write in client storage only; no server PII endpoints;
  clearing site data resets prefs (disclosed)
- **Source**: UJ-033; F22

### TC-F22-003: Global Privacy Control (GPC) honor (UJ-033)

- **Level**: T2 / T3
- **Objective**: When browser signals GPC, app treats preference as opt-out of non-essential
  client storage beyond disclosed IndexedDB work history (per F22 scope)
- **Pass criteria**: GPC signal detected; preference center reflects GPC; no marketing/analytics
  scripts introduced
- **Source**: UJ-033; F22 / E17-9

### TC-F16-001: Drawer preflight schema diff (UJ-027)

- **Level**: T0 / T2
- **Objective**: One-shot URI preflight returns structured schema/permission/auth diffs; Send blocked until green
- **Pass criteria**: Missing column / no INSERT / auth fail messages actionable; secrets redacted
- **Source**: F16; #729; Q7=A

### TC-F16-002: SSRF + allowlist (UJ-027)

- **Level**: T0 / T2
- **Objective**: Private/metadata IPs rejected; empty `DISSEMINATION_EGRESS_ALLOWLIST` blocks user-URI egress
- **Pass criteria**: DNS-rebinding and RFC1918 targets fail closed; allowlisted public host proceeds
- **Source**: F16; Q11=A+B; ADR-029

### TC-F16-003: Multi-DB engines + DDL (UJ-027)

- **Level**: T0 / T2
- **Objective**: Postgres, MySQL/MariaDB, SQL Server, SQLite writer-contract + create-if-missing path
- **Pass criteria**: Contract tests per engine; DDL migrates to versioned shape when opted
- **Source**: F16; Q20=A,C; Q23=A–D

### TC-F16-004: Drag-drop + convert-then-send (UJ-027)

- **Level**: T2 / T3 (H6′)
- **Objective**: Both entry paths reach same preflight→send; local history may store `kv_upload_key` only
- **Pass criteria**: No destination secrets in IndexedDB/session JSON; Finished after success
- **Source**: F16; Q19=A; Q20=B

### TC-F16-005: Multi-file export selection (UJ-027 / #785)

- **Level**: T0 (Vitest drawer) / T2 / T3 (H6′)
- **Objective**: When >1 candidate (current-session + drops), operator multi-selects; Disseminate
  runs interleaved preflight→send per file; per-file progress + results visible
- **Pass criteria**:
  1. Select-all / clear / individual checkboxes work
  2. Empty selection disables Disseminate and Preflight-only with clear message
  3. Selection >20 rejected with clear error (E18-6)
  4. Partial failure: failed files show red mark; remaining continue and are reported (E18-11)
  5. Finished IndexedDB history items are **not** listed as candidates (E18-4)
  6. No destination secrets persisted; no batch API required (E18-5)
  7. Progress row: mail→destination animation (or text-only under reduced-motion); Playwright
     `toHaveScreenshot` for in-flight + failed states (E18-13/14/16)
- **Source**: F16 deepen; S024 / EV-018; #785; E18-4..E18-6; E18-9..E18-16

### TC-F17-001: Staging wis2box publish (UJ-028)

- **Level**: T2 / staging
- **Objective**: Publish IWXXM to project wis2box Compose harness (E14-04; not Render)
- **Harness (T3.3)**: `docker-compose.wis2box.yml` profile `wis2box` — MQTT + HTTP dataset
  stand-in; CI hook `scripts/ci/run_wis2box_harness.sh` (up + health + PUT/GET smoke)
- **Pass criteria**: MQTT notify + HTTP dataset retrievable (publish path = T3.4 —
  `packages/dissemination/tests/test_wis2_harness_publish.py` via
  `scripts/ci/run_wis2box_harness.sh`)
- **Source**: F17; #2; Q12=B / Q17

### TC-F17-002: Live WIS2 BYOC close gate (UJ-028)

- **Level**: T3 (live BYOC)
- **Objective**: User-supplied WIS2 node demo before EV-014 close
- **Pass criteria**: Live green recorded in deploy/evolve report (Q15=A / Q21=A)
- **Source**: F17; Q16

### TC-F18-001: EDIS message format (UJ-029)

- **Level**: T0 / T2
- **Objective**: ASCII-only message + correct WMO abbreviated headers
- **Pass criteria**: Format fixtures pass; non-ASCII rejected
- **Source**: F18; #6

### TC-F18-002: Live EDIS → RTH Washington BYOC (UJ-029)

- **Level**: T3 (live BYOC)
- **Objective**: Real gateway submission with user-pasted SMTP/gateway settings
- **Pass criteria**: Live green before cycle close; secrets not persisted
- **Source**: F18; Q13=A; Q18≈A

### TC-F19-001..003: AMHS / SWIM / AFS adapters (UJ-030)

- **Level**: T2 / T3
- **Objective**: Each adapter preflight + send with BYOC params under SSRF/allowlist
- **Pass criteria**: One TC per adapter with staging/test path green; F19 **live** demo
  optional (evidence or AskQuestion waive) — does not block EV-014 close (Q15=A hard gate
  is Postgres + WIS2 + EDIS only; S-EV014-M2)
- **Source**: F19; Q20=D; 02-verify-plan Q28=A

### F16–F19 verify/deploy gate

- [ ] TC-F16-001..005 green (multi-DB + SSRF + drawer + multi-select)
- [ ] TC-F17-001 staging wis2box green; TC-F17-002 live BYOC before cycle close
- [ ] TC-F18-001 format green; TC-F18-002 live BYOC before cycle close
- [ ] TC-F19-001..003 staging/test green; live F19 optional (evidence or waive id)
- [ ] H4–H5 after API/FE dissemination routes ship; H0c on CORS/env changes; H6′ UJ-027–030
- [ ] `DISSEMINATION_EGRESS_ALLOWLIST` in config-spec / env-contract / deploy / staging-secrets-matrix
      (S-EV014-L1 **resolved** at 04; matrix row added at 05-verify-tech)

## Live Test Cases (T3 / H3–H6)

Manual signoff before release — not a PR merge gate. Developer runs `make test-live` from repo root with `.env` populated.

### TC-LIVE-001: Live Health & Convert

- **Objective**: H3 — API health and METAR conversion against Render
- **Preconditions**: E2E-001 schema path fixed; `LIVE_API_URL` set; **no JWT** (F21 public)
- **Steps**:
  1. `curl -sf "${LIVE_API_URL}/health"` — expect 200, `tac2iwxxm_available: true`
  2. `pytest apps/backend/tests/infrastructure/test_live_api_health.py -m live_api`
- **Pass criteria**: All live_api tests green; cold-start retries (3×, 30s backoff) succeed
- **Resilience**: Exponential backoff on HTTP 429
- **Source**: UJ-001, H3

### TC-LIVE-002: Live Validation

- **Objective**: H3 — validation endpoint against Render
- **Preconditions**: E2E-001 resolved; **no JWT**; sample IWXXM from convert step
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
- **Preconditions**: `PLAYWRIGHT_BASE_URL=${LIVE_FRONTEND_URL}`; **no** Auth login fixture
  (F21 public); IndexedDB available in browser context
- **Steps**:
  1. Run `00-preflight.e2e.spec.ts` first (wake + health)
  2. `make test-live-e2e` — public METAR convert, F6 product/profile matrix (UJ-005),
     validation (UJ-002/007), UJ-008 smoke; **skip** retired Auth bootstrap
  3. Playwright config disables local `webServer` when base URL is remote
- **Pass criteria**: UJ-001–007 specs green against live URLs (UJ-003 = Auth-gone negative only)
- **Resilience**: Cold-start retry in preflight; serial execution (no parallel live requests)
- **Source**: UJ-001–007, H6; F21

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

### TC-F6-013: METAR REMARKS retain / exclusion (#667 / UJ-026)

- **Objectives**: annex3 `REMARKS_EXCLUDED`; iwxxm_us `humanReadableText` for unparsed RMK; T/P IR
- **Pass criteria**: `packages/tac2iwxxm/tests/test_issue_667_metar_remarks.py` green
- **Source**: S018 / EV-013

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
- S016 / EV-012 (2026-07-20): TC-F7-007 / UJ-025 Manual TAC Input modes (#730 / ADR-024);
  H6′ + staging gate; F7 stays Planned

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

**Policy (EV-002)**: Single workflow file for PR/push; dual-run locally via husky + pre-commit.
Scheduled workflows (`vendor-sync`, load/e2e) unchanged.

GitHub `ci-cd.yml` runs **validate**, then **test** / **tac2iwxxm-native** / **e2e-smoke**.
Husky **pre-push** mirrors validate + unit/matrix locally. **Deploy** on `main` needs
`test` + `tac2iwxxm-native`, and skips when GHCR or Render hook credentials are missing.

| Trigger | Workflow | Jobs | Checks |
|---------|----------|------|--------|
| PR / push `main`, `dev` | `ci-cd.yml` | **validate** | ruff format/check, prettier, eslint, basedpyright, tsc, gitleaks, actionlint/yamllint, config-guard (`tests/test_config_placeholders.py`), frontend npm audit |
| PR / push `main`, `dev` | `ci-cd.yml` | **test**, **tac2iwxxm-native**, **e2e-smoke** | package unit/integration matrix, PyO3 smoke, Playwright smoke |
| push `main` only | `ci-cd.yml` | **deploy** | needs test + native; Docker build/push GHCR, Render deploy hooks — **skip** if credentials incomplete |
| Local (husky pre-push) | `.husky/pre-push` | — | `make validate-ci` + `make ci-prepush` (unit/matrix @ package coverage gates) |
| Schedule | `vendor-sync.yml` | vendor-sync | wmo-im schema sync PR (M6) |
| Manual / schedule | `load-tests.yml`, `e2e-tests.yml` | — | out of EV-002 scope |

### Pre-commit / husky (local gates)

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
| husky pre-push | `make validate-ci` + `make ci-prepush` | local parity with CI **test** matrix |

Slow Compose integration (`make ci`) stays local/manual — needs free ports 18000/18001.

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
