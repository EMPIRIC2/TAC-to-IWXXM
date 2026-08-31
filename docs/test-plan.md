# Test Plan

> **Project**: METAR to IWXXM Converter
> **Repository**: https://github.com/EMPIRIC2/TAC-to-IWXXM
> **Last updated**: 2026-08-25 (EV-084 — US_FAA_NWS M19 WAUS multi-section AIRMET)

## Scope

**In scope**: Product features F1–**F36** (F1 superseded by F6 engine; F7 Planned — workbench
smoke under F15/F20/F23–F27; **F7.g** golden examples #780 / UJ-032; **F7.h/i** hybrid sessions;
F8–F15 as prior cycles; **F16–F19 Done** dissemination epic; **F20** TAF+SPECI quality;
**F21 Amended** public convert + optional Auth for long-term storage; **F22** privacy preference
center (deepen F31); **F23** SIGMET family quality bar; **F24** AIRMET; **F25** WMO
METAR/SPECI/TAF parity; **F26** VAA; **F27** TCA; **F30** platform independence; **F31** hybrid
sessions; **F32** VONA quality bar; **F35** semantic vs exchange profile architecture;
**F36** national/exchange profile content); monorepo migration validation M1–M6 (M3 deprecated at F6 cutover; **M4 restore**);
connectivity tiers **H0c–H7** (local + live **DOKS** target; Render until cutover soak);
tac2iwxxm + `tac-validate` + `iwxxm-validate` metrics (library/CI); backend thin wrappers;
F7 decode/spans/soft-preview/workbench/unified sessions; admin-route negative tests; **F15**
issue registry + METAR golden/negative packs (UJ-024); **F16–F19** dissemination drawer,
multi-DB upload, WIS2, EDIS, AMHS/SWIM/AFS (UJ-027–030); **F20** TAF + SPECI quality bar
(UJ-031; #735/#734); **F23** SIGMET + VA SIGMET quality bar (UJ-034; #733/#739); **F26/F27**
VAA + TCA quality (UJ-037/038; #736/#737); **UJ-045–048** guest notice / login auto-upload /
privacy / DOKS cutover.

**Out of scope**: Performance/load testing; wmo-im / IWXXM-US schema correctness beyond our fixtures;
scheduled CI live jobs (manual/Makefile only); **convert-response metrics fields** (F6-R11);
teaching CMS; saved/encrypted destination profiles; in-app paste of **Supabase auth** keys
(destination BYOC paste is **in scope** for F16–F19); long-lived dual production hosts after
DOKS soak; Supabase hosted Postgres / PostgREST as product data plane.

### Live harness (delta 2026-06-22; H7 2026-07-12; **DOKS target S038 / EV-031**)

Unified manual live test harness against **DOKS** production endpoints after F30 cutover
(Render URLs remain valid only until soak + decommission — TC-F30-005):

| Tier | Scope | Makefile target |
|------|-------|-----------------|
| H3 | Live API pytest (health, convert, validate; convert **no JWT**) | `make test-live-api` |
| H4–H5 | CORS preflight + frontend bundle URLs — **required this cycle** (FE Auth + notice + DOKS) | `make test-live-connectivity` |
| H6 | Playwright UJ-001–007 (+ UJ-008) + F7 smokes + **UJ-045–047** + dissemination H6′ | `make test-live-e2e` |
| **H7** | Live bulletin gate: multi-report AHL → split → convert → Schematron | `make test-live-bulletin` (planned) |
| All | Sequential H4–H5 → H3 → H6 → H7 | `make test-live` (extend when H7 lands) |

**Prerequisite**: E2E-001 schema path regression must be resolved before H3 validate and full H6 UJ-002 pass (see [e2e-report.md](reports/e2e-report.md)).

**CI policy**: Manual/local only — no GitHub Actions live job (cold-start + secrets).

**Canonical URLs** (see [staging-secrets-matrix.md](ops/staging-secrets-matrix.md); update at F30 cutover):

- `LIVE_API_URL` — DOKS API origin: `https://api.tac-to-iwxxm.com`
- `LIVE_FRONTEND_URL` — DOKS static origin: `https://app.tac-to-iwxxm.com`
- Optional login fixtures for UJ-046 / H6 Auth path: `E2E_USER_EMAIL` / `E2E_USER_PASSWORD` (restored for session tests only — convert remains public)

## User Journeys (E2E)

| Journey | Feature | Local E2E module | Live E2E | Test plan TC |
|---------|---------|------------------|----------|--------------|
| UJ-001 | F6 | `apps/e2e/tac-file-conversion.e2e.spec.ts`, `apps/e2e/tac-file-upload-database.e2e.spec.ts` | `make test-live-e2e` (H6) | TC-001, TC-LIVE-001 |
| UJ-002 | F2+F6 | backend validation tests + UI Strict Validation → `validate_output` (ADR-023) | H3 validate + H6 where exposed | TC-002, TC-LIVE-002 |
| UJ-003 | Auth / F31 | **Restored** — see UJ-046; convert still public | H6 login path | TC-F31-003/004; TC-F21-auth-gone amended |
| UJ-004 | F5+F7+F31 | Hybrid history (guest IDB + logged-in server) | H6 UJ-004/045/046 | TC-004 + TC-F31-001..004 |
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
| UJ-DEV-006 | F13–F14 | Rust fmt/clippy/`cargo test` + maturin both crates | CI | TC-EV045-001..007 |
| UJ-024 | F15 | METAR/SPECI registry + convert→validate golden | H4–H5 if FE | TC-F15-001..005 |
| UJ-025 | F7 | Manual TAC Input modes (ADR-024 / #730) | H6′ | TC-F7-007 |
| UJ-027 | F16 | `apps/e2e/uj027-030-dissemination-drawer.e2e.spec.ts` (+ live local suite EV-039) | H6′ / live local | TC-F16-001..005; TC-F16-LIVE-001..004 |
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
| UJ-045 | F31+F21 | Guest convert + persistent loss-of-progress notice + local history | **H4–H5 required** | TC-F31-001/002/006 |
| UJ-046 | F31+F30 | Login → auto-upload drafts → DO Postgres sessions | **H4–H5 required** | TC-F31-003/004/006 |
| UJ-047 | F22+F31 | Privacy prefs ↔ IndexedDB / Auth cookies | **H4–H5 required** | TC-F31-005; TC-F22-* deepen |
| UJ-048 | F30 | DOKS cutover smoke (API + FE + worker) | **H0–H5 required** | TC-F30-004/005; TC-EV031-* |
| UJ-049 | F32 + F6/F7/F12/F2/F13 deepen | VONA quality bar + full F7 surface (#741); cycle also #835/#808/corpus | H4–H5 when FE | TC-EV032-001..008; TC-F32-001..006 |
| UJ-050 | F4+F7 deepen (EV-038) | IWXXM version picker Latest / Previous (#854) | H4–H5 when FE | TC-EV038-007 |
| UJ-051 | F33 | Secure mass file/folder ingest (auth + caps) | **H4–H5 required** | TC-F33-001..006 |
| UJ-052 | F7 deepen (EV-042) | Queue + keyboard/batch convert·validate | **H4–H5 required** | TC-EV042-003..004 |
| UJ-053 | F16–F19 deepen (EV-091) | Operator dissemination destinations visible | **H4–H5 required** | TC-EV091-001..002; TC-EV042-002 |
| UJ-054 | F7 deepen (EV-047) | Operator Help → one-pager / handbook (#956/#957) | T0/T2; H4–H5 when FE deploy | TC-EV047-009..011 |
| UJ-055 | F7+F21 deepen (EV-048) | Operator UI + OpenAPI free of internal planning vocabulary (#951) | T0/T2; T3 if UI hits | TC-EV048-001..005 |
| UJ-056 | F7.q deepen (EV-054 / EV-055 / EV-056 / EV-058) | Quality metrics primary tab — match/residuals/lint/validate; W3C C14N diffs (#982); 2025-2 validate disposition (#980/#979); dedicated `/quality/:stem` + collapsible hunks (#988); side-by-side vs inline XML diff (#983) | **H4–H5 required** | TC-EV054-001..008; TC-EV055-001..007; TC-EV056-001..005; TC-EV058-001..005 |
| UJ-057 | F7.r deepen (EV-057) | Accumulate conversions → Download all ZIP (#903) | **H4–H5 required** | TC-EV057-903-001..007 |
| UJ-058 | F7.s deepen (EV-057) | Validate existing IWXXM paste/upload (#838) | **H4–H5 required** | TC-EV057-838-001..005 |
| UJ-059 | F7/F6 deepen (EV-060) | AHL bulletin lint/validate without heading flood (#1001) | **H4–H5 required** | TC-EV060-1001-001..003 |
| UJ-060 | F7.t (EV-060) | IWXXM product pass-through lint+F2 (#1003) | **H4–H5 required** | TC-EV060-1003-001..004 |
| UJ-061 | F7/F6 deepen (EV-060) | Profile labeled at converter top (#1002) | **H4–H5 required** | TC-EV060-1002-001..003 |
| UJ-062 | F7/F6 deepen (EV-060) | Bulletin ID + Issuing Center applied (#1005) | **H4–H5 required** | TC-EV060-1005-001..003 |
| UJ-063 | F29 deepen (EV-060) | Conversion log_level sets logger verbosity (#1004) | T0/T2 | TC-EV060-1004-001..002 |
| UJ-003 / UJ-046 | F31 deepen (EV-060) | Auth register/login/logout/persist UAT (#1006) | **H4–H5 required** | TC-EV060-1006-001..004 |
| UJ-064 | F2/F9/F10 deepen (EV-061) | Validate IWXXM item-by-item readable decode (#1010) | **H4–H5 required** | TC-EV061-1010-001..003 |
| UJ-065 | F6/F7 deepen (EV-061) | AHL decode + convert-bulletin (#1012) | **H4–H5 required** | TC-EV061-1012-001..004 |
| UJ-066 / UJ-067 | F7.u (EV-061) | Product/Profile + param bars aligned (#1013) | **H4–H5 required** | TC-EV061-1013-001..003 |
| UJ-068 | F7.v/F15 (EV-061; EV-062) | Validation Issues Catalog (#1014; #1017 deepen) | **H4–H5 required** | TC-EV061-1014-001..004; TC-EV062-001..006 |
| UJ-069 | F35/F36 (EV-063/EV-090/EV-093) | Semantic convert → exchange package (`GLOBAL_AFS`) | T2 / **T3**; **H4–H5** (#1024 FE) | TC-EV063-001..006; TC-EV090-*; TC-EV093-* |
| UJ-DEV-009 | F34 deepen (EV-061) | stage→main full CI+E2E+lint+typecheck (#1015) | CI | TC-EV061-1015-001..002 |
| LIVE-F6-030 | F6 chore (EV-061) | Live bulletin multipart field `files` (#1011) | Live H7 | TC-LIVE-F6-030 (fix harness) |
| UJ-OPS-002 | F30 deepen (EV-057) | Prod apex → app redirect (#948) | ops / T3 | TC-EV057-948-001..003 |
| UJ-DEV-007 | M5 deepen (EV-047) | Slim husky lint commit + fast-unit push (#833) | — | TC-EV047-001..004 |
| UJ-DEV-008 | F6 deepen (EV-047) | Converter perf regression blocks PR (#834) | CI | TC-EV047-005..008 |

**Admin dashboard E2E**: **Retired** (S011 / #697). Replace prior admin panel locator guidance with
**TC-F7-006** — assert `/admin` and legacy admin deep links return not-found; delete/skip old
admin suite modules.

| UJ-DEV-001 | M1,M5 | CI monorepo-smoke job | — | TC-M001 |
| UJ-DEV-002 | M2,F6 | vendor manifest integrity tests | — | TC-M002 |
| UJ-DEV-003 | M3 | ~~gifts + conversion regression~~ | — | **TC-M003 deprecated** → TC-F6-020–022 |
| UJ-DEV-003b | F6 | tac2iwxxm + iwxxm-us pin | — | TC-F6-M001 |
| UJ-OPS-001 | F30 / M4 | deploy smoke H0–H5 | **DOKS** (Render until cutover) | TC-OPS-001; TC-F30-004 |

## Connectivity & Wiring

| Tier | Scope | Command |
|------|-------|---------|
| H0e | Env contract sync (`.env` + config JSON) | `make env-check` |
| H0c | CORS policy (in-process) | `pytest apps/backend/tests/unit/test_cors_policy.py` |
| H0i | Cross-service integration | `pytest apps/backend/tests/integration` |
| H3 | Live API smoke (pytest) | `make test-live-api` |
| H4 | Live CORS preflight | `make test-live-connectivity` |
| H5 | Frontend bundle URLs | `make test-live-connectivity` |
| H6 | Live Playwright UJ-001–007 (+ UJ-008) + F7 UJ-013/015–019 + **UJ-025** + **UJ-027–030** (H6′ when F16–F19 ships; **operator UI deferred #898 / EV-042**) + **UJ-051..053** (EV-042) | `make test-live-e2e` |

| **H7** | Live bulletin → split → convert → Schematron (UJ-011) | `make test-live-bulletin` (planned) |

**Post-migration / F21 Amended (EV-031)**: Single API origin serves `/api/v1/*` **and**
`/auth/*` (Supabase Auth verify only). Convert/lint/validate/disseminate stay **public** (no JWT).
JWT required only for `/api/v1/work-sessions*`. **H4–H5 required this cycle** (FE Auth + guest
notice + DOKS URLs — `D-S038-tp`). **H7** remains bulletin ingest path (not F8 worker); see
[connectivity-gates.md](../.cursor/skills/connectivity-gates.md).

**Env wiring** (see [config-spec.md](config-spec.md); [env-contract.md](env-contract.md)):

- `config.*.api.baseUrl` — API URL (includes `/api/v1` + `/auth`)
- `config.*.api.corsOrigins` — backend allowed origins (DOKS FE origin after cutover)
- `LIVE_API_URL` / `LIVE_FRONTEND_URL` — from `config.prod.liveE2e` or env override (DOKS after F30)
- `E2E_USER_EMAIL` / `E2E_USER_PASSWORD` — **restored** for UJ-046 / session CRUD live tests only
- `DATABASE_URL` — DigitalOcean Postgres (sessions + F8); required for F30/F31 server path
- Supabase: Auth URL + keys for JWT verify / FE Auth bootstrap — **not** product DB credentials
- F8 worker: `DATABASE_URL` + poller secrets (no Supabase DB / PostgREST product writes)
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

**Coverage**: **100%** line+branch on all packages and apps (ADR-007 / EV-080 / #1077) —
pytest for Python, Vitest for frontend/shared. Python also enforces **per-file ≥100%** via
`scripts/ci/check_per_file_coverage.py --min-pct 100`. Scripts: Python cov ≥100% +
**bats-core** for every `scripts/**/*.sh` (**TC-EV080-001..010**). Historical EV-052/053
retained **95%** TCs as prior-bar evidence. **F34** adds Schemathesis (path-filtered
required, tight budget) and mutation testing (nightly/manual only) — see **TC-F34-001..007** /
EV-059.

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

### TC-004: Local work session lifecycle (F5 / UJ-004) — guest IndexedDB (F31 deepen)

- **Objective**: Guest Draft auto-save → convert → WIP → send → Finished in **browser IndexedDB**;
  resume after reload **without login**; My METARs filters METAR/SPECI locally. Logged-in path
  covered by **TC-F31-003/004** (DO Postgres).
- **Steps**:
  1. Guest creates draft via local upsert (`product` = metar|speci) — **no**
     `/api/v1/work-sessions` while logged out
  2. Convert success moves to WIP (reject second WIP — one WIP per browser profile total)
  3. Partial convert failure sets Failed; edit + re-convert transitions appropriately
  4. Dissemination success sets Finished with `kv_upload_key` (local only; no dest secrets)
  5. Soft-delete + restore within local trash policy
  6. My METARs does **not** list non-METAR products; workbench history may (TC-F7-005)
  7. Clearing site data loses history (disclosed in F22); guest notice visible (TC-F31-002)
- **Pass criteria**: Status rules enforced locally for guests; **no** server session calls while
  logged out
- **Source**: UJ-004/045; F7.h / F31; ADR-031 guest path retained; ADR-033

### TC-F21-auth-gone: Public convert without JWT (UJ-003 / F21 Amended — EV-031)

- **Level**: T2 / T3
- **Objective**: Convert/lint/validate/disseminate remain **public** after Auth restore. Historical
  name retained; pass criteria **amended** — `/auth/*` may exist for long-term storage, but must
  not gate convert.
- **Pass criteria**:
  - `POST /api/v1/convert` (and lint/decode/validate/preview/dissemination) succeed **without**
    Authorization
  - `/auth/*` may return 200 for login/register/me when Auth is enabled (F31) — **not** required
    to be 404
  - Frontend may show optional login for long-term storage; convert path works logged-out
  - Abuse controls (rate limit / body) still apply
- **Source**: UJ-001/003; F21 Amended; TC-EV031-003; S038 / EV-031

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

### TC-EV040-001: Workbench lint UX + catalog source (S048 / EV-040)

- **Objective**: Lint console lists each issue on its own line; convert keeps TAC input;
  New TAC + action strip above selects; slim prefs; official AHL/Collect examples;
  catalog source attribution; A3-1/AHL FPs fixed.
- **Tier**: T0 unit (Vitest + pytest) + H4–H5 when UI ships
- **Source**: F7/F10/F15 deepen; [Corpus: product]; evolve-decisions §EV-040
- **Asserts**: AC1–AC7; `test_ev040_rvr_ahl_false_positives.py`; lint console Vitest;
  examplesCatalog Vitest; prefs slim Vitest

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

### EV-045 / #725 — Rust crate CI (S054; F13/F14 deepen)

CI must gate **both** `packages/tac2iwxxm/rust` and `packages/iwxxm-validate/rust`
with fmt, clippy, unit tests, and maturin/PyO3 integration smoke. Prefer extending
`.github/workflows/ci-cd.yml` (matrix) over a separate workflow unless latency requires
split. Tooling: `dtolnay/rust-toolchain@stable` + components `rustfmt,clippy`;
Cargo cache (`Swatinem/rust-cache` or equivalent). Local: `make rust-check`.
[Corpus: product §F13] [Corpus: product §F14] [Corpus: tests] [Corpus: adr/ADR-017]

| ID | Level | Assert |
|----|-------|--------|
| TC-EV045-001 | CI | `cargo fmt --check` fails on unformatted Rust in both crate trees |
| TC-EV045-002 | CI | `cargo clippy -- -D warnings` fails on warnings (documented allowlist only if needed) |
| TC-EV045-003 | CI | `cargo test` green for `tac2iwxxm` and `iwxxm-validate` Rust crates |
| TC-EV045-004 | CI | Maturin/PyO3 smoke for **both** packages (`TAC2IWXXM_REQUIRE_RUST` /
  `IWXXM_VALIDATE_REQUIRE_RUST` or equivalent) |
| TC-EV045-005 | T0 | `make rust-check` mirrors CI: fmt + clippy + `cargo test` **both** crates **and** both `test-*-native` maturin smokes (D-S054-04-local=2) |
| TC-EV045-006 | Ops | Required check name(s) **documented**; PRs cannot merge with red Rust CI **once rulesets applied** |
| TC-EV045-007 | CI | Jobs run on default `ci-cd.yml` PR/push (same as today’s native job; **not** path-filter-only — D-S054-04-trigger=1) |

**Required status check contexts** (must match `ci-cd.yml` job `name:` exactly; applied via
`scripts/deploy/apply_gh_branch_rulesets.sh` when repo admin is available):

| Context | Role |
|---------|------|
| `Rust crates (fmt/clippy/test)` | fmt + clippy + `cargo test` both crates (EV-045) |
| `tac2iwxxm PyO3 (maturin)` | existing maturin smoke |
| `iwxxm-validate PyO3 (maturin)` | EV-045 maturin smoke (new) |

Also retained from F30 script: `Test (backend)`, `Test (frontend)`, `Alembic migrations`;
`main` adds `Staging gate`.

**AC6 ops waiver (D-S054-ac6-waive=2 / EV-045):** docs + script updated this cycle; live
GitHub rulesets/required-check wiring deferred until an admin runs the apply script
(token `admin=false`; rulesets currently empty — same class as EV-043). Cycle close may
treat TC-EV045-006 as **docs/script met; ops deferred**. [Corpus: tests] [Corpus: decisions]

**UJ mapping**: UJ-DEV-006 (new); deepen UJ-DEV-004.

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

## S040 / EV-032 — Official IWXXM corpus quality (#846 / #835 / #741 / #808)

New **TC-EV032-001..008** and **TC-F32-001..006**. Ties **UJ-045**; deepens UJ-034/039/042.

### TC-EV032-001: Epic #846 children linked + scope locked (UJ-045)

- **Level**: T0 (docs)
- **Objective**: Epic lists #835/#741/#808 + corpus track; evolve-decisions EV-032 scope matches
- **Pass criteria**: #846 body + `evolve-decisions.md` §EV-032 + session-brief agree
- **Source**: #846; E32-*

### TC-EV032-002: #835 A6-2-TC canonicalize_xml equality (UJ-034/039 deepen)

- **Level**: T0 / T2
- **Objective**: `canonicalize_xml(convert(annex3 A6-2-TC)) == canonicalize_xml(vendor)` under default pin
- **Pass criteria**: ADR-032 equality green; deltas (coords / airspace / intensityChange / trailing zeros) resolved or waived with cite
- **Source**: #835; ADR-032

### TC-EV032-003: #835 catalog promote → wmoPass (UJ-039 deepen)

- **Level**: T0 / T2 (+ H4–H5 if FE)
- **Objective**: Catalog tier `sigmet_a6_2_tc` → `wmoPass`; FIXTURE_GAPS / inventory updated
- **Pass criteria**: Catalog metadata + gap notes match; FE badge if unlock ships
- **Source**: #835; ADR-032

### TC-EV032-004: #808 adopt/deprecate assessment written (docs)

- **Level**: T0 (docs)
- **Objective**: Maintainability report + adopt + deprecate checklists; blast-radius map; child issues
- **Pass criteria**: #808 AC1–5; no re-pin required to close
- **Source**: #808; VERSION_SUPPORT_POLICY

### TC-EV032-005: Corpus / WMO-source stance indexed (#846)

- **Level**: T0 (docs) / T2 as children land
- **Objective**: Durable notes for parity vs iwxxm / translation / codelists / codes.wmo.int / modelling
- **Pass criteria**: Session or domain index + #846 children for actionable gaps
- **Source**: #846; prior #804/#807/#815

### TC-EV032-006: F32 VONA encode + validate path (UJ-045)

- **Level**: T0 / T2
- **Objective**: VONA lint→convert→XSD+SCH; root `VolcanoObservatoryNoticeForAviation`
- **Pass criteria**: TC-F32-001..004 green (or child-issued)
- **Source**: F32; #741

### TC-EV032-007: F7 VONA picker + Examples unlock (UJ-045)

- **Level**: T2 / T3 / H4–H5
- **Objective**: Product picker includes VONA; Examples list passers when golden greens
- **Pass criteria**: TC-F32-005; H4–H5 when FE ships (`D-S040-E32-M` Q2=3)
- **Source**: F32; F7

### TC-EV032-008: Optional live smoke order #835→#741→#808 (deploy)

- **Level**: T3 / H1–H5
- **Objective**: Deployed API accepts `product=vona`; A6-2-TC path still healthy; docs #808 linked
- **Pass criteria**: Live convert/lint smoke; FE when shipped
- **Source**: EV-032 Standard 12/13

### TC-F32-001: VONA registry completeness (UJ-045)

- **Level**: T0
- **Objective**: Registry-backed VONA lint codes; CI fails on unknown codes
- **Pass criteria**: Catalog drift check includes VONA codes
- **Source**: F32; ADR-028; #741

### TC-F32-002: VONA encode cookbook from XSD+SCH+example (UJ-045)

- **Level**: T0 / T2
- **Objective**: Encode path not guidance-file-only; gaps vs silent guidance documented
- **Pass criteria**: Session/domain cookbook note + fixtures cite `vona-A7-1` / PANS-MET / XSD
- **Source**: F32; #741

### TC-F32-003: MeteorologicalFeature + colour codes (UJ-045)

- **Level**: T0 / T2
- **Objective**: Volcano/ash features + bounding period/volume/phenomena; AviationColourCode list
- **Pass criteria**: Convert XML asserts feature shape + vocabulary URIs
- **Source**: F32; #741; 2025-2 vona.xsd

### TC-F32-004: VONA accept/negative + golden (UJ-045)

- **Level**: T0 / T2
- **Objective**: Accept → convert → XSD+SCH; negatives → registry diagnostics; golden equality when peer exists
- **Pass criteria**: Fixture pack green; ADR-032 when vendor peer present
- **Source**: F32; ADR-032

### TC-F32-005: Workbench product-path + Examples (UJ-045)

- **Level**: T2 / T3 / H4–H5
- **Objective**: Full F7 surface for VONA
- **Pass criteria**: Picker + convert smoke; Examples unlock when passers exist
- **Source**: F32; F7; `D-S040-E32-M` Q2=3

### TC-F32-006: API product=vona enum (UJ-045)

- **Level**: T0 / T2
- **Objective**: Runtime accepts `vona`; rejects unknown aliases with `unknown_product` 400
- **Pass criteria**: Backend + package enum tests; OpenAPI/FE types updated same cycle
- **Source**: F32; api-contract S040 / EV-032

### EV-032 verify/deploy gate

- [ ] TC-EV032-001..008 green (or deferred with child issues)
- [ ] TC-F32-001..006 green (or deferred with child issues)
- [ ] #835 / #741 / #808 closed or children linked under #846
- [ ] H4–H5 when FE VONA surface / A6-2 catalog ships
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

## F30 / F31 / EV-031 Test Cases (S038) — platform independence

> Objectives and pass criteria locked at 01 (`D-S038-tp` = 1,1,1). Detailed steps / fixtures
> finalize in **04-tech-plan**. **Live H4–H5 required** this cycle (not waivable behind a flag).

### TC-F30-001: Boot without Supabase database credentials (UJ-048)

- **Level**: T0 / T2
- **Objective**: API + worker product path starts and smokes with **no** Supabase Postgres /
  PostgREST product credentials; only Auth JWT verify config when Auth is enabled
- **Pass criteria**: Health + public convert green; no runtime dependency on Supabase DB URL /
  service-role for default convert path; env-check fails closed if product DB is still pointed
  at Supabase when F30 cutover flag is on
- **Source**: F30 AC1; #830 amend; UJ-048

### TC-F30-002: Auth-only Supabase verify (UJ-046)

- **Level**: T0 / T2
- **Objective**: JWT verification uses Supabase Auth only; no Supabase DB writes on default
  session/convert path
- **Pass criteria**: Valid JWT accepted for work-sessions; invalid JWT rejected; instrumented
  tests assert zero Supabase PostgREST product writes on convert + session CRUD against DO
- **Source**: F30 AC2; M4 restore

### TC-F30-003: F8 store → DigitalOcean Postgres (UJ-014 deepen)

- **Level**: T0 / T2 (+ staging smoke)
- **Objective**: F8 worker persists store/quarantine via `DATABASE_URL` → DO Postgres
- **Pass criteria**: Unit/integration insert+read against DO schema; no Supabase service-role
  DB writer on default path; worker image/docs list `DATABASE_URL` as required
- **Source**: F30 AC3; F8 deepen; ADR-018 amend

### TC-F30-004: DOKS hosts API + worker + static; H0–H5 (UJ-048)

- **Level**: T3 / H0–H5
- **Objective**: After cutover, DOKS serves API, static FE, and worker; live harness points at
  DOKS URLs
- **Pass criteria**: `make test-live-connectivity` (H4–H5) + H0/H3 health/convert green against
  DOKS; worker store smoke recorded; cutover runbook steps checked
- **Source**: F30 AC4; #712; UJ-048

### TC-F30-005: Render decommission after soak (UJ-048)

- **Level**: Ops / checklist
- **Objective**: Render services retired after soak, or residual ticket with explicit checklist
- **Pass criteria**: Decommission checklist complete **or** open residual issue linking soak
  criteria + owners; dual-prod hosts not left long-lived without ticket
- **Source**: F30 AC5; `D-S038-doks-depth`=3

### TC-F30-006: Docs / env-contract Auth-only Supabase (corpus)

- **Level**: T0 (doc/contract)
- **Objective**: CORPUS + env-contract + deploy no longer require Supabase as **data** plane
- **Pass criteria**: env-check + doc grep gate: product DB = `DATABASE_URL` (DO); Supabase =
  Auth keys only; ADR-033 / deploy cutover referenced
- **Source**: F30 AC6; #830

### TC-F30-007: CD auto-rolls DOKS images (EV-034)

- **Level**: Ops / T3 (CD)
- **Objective**: After `main` GHCR push, Deploy pins DOKS `metar-api` / `metar-frontend` /
  `metar-worker` to the immutable `TIMESTAMP-SHA` tag without manual kubectl
- **Pass criteria**:
  1. Deploy job runs `scripts/deploy/doks_rollout_images.sh` (or equivalent) with `KUBE_CONFIG`
  2. Cluster Deployments show the pushed tag; `rollout status` succeeds
  3. Live smoke: `/health` 200; OpenAPI includes `/auth/*` when that tag includes Auth
  4. Missing `KUBE_CONFIG` fails Deploy; missing Render hooks do **not** fail Deploy
- **Source**: F30 AC7; S042 / EV-034; `E34-1..4`

### TC-F30-008: Staging cluster + isolated secrets (EV-043 / EV-044)

- **Level**: Ops / T0
- **Objective**: Staging DOKS cluster `metar-iwxxm-staging` (DO Project **Staging TAC-to-IWXXM**)
  has ns `metar-iwxxm-staging` with API/FE/worker; secrets and `DATABASE_URL` point at
  dedicated staging Postgres `metar-iwxxm-staging`, not prod `metar-iwxxm` / `defaultdb`.
  Prod cluster remains on DO Project **TAC-to-IWXXM**.
- **Pass criteria**: `doctl projects resources list` shows staging cluster+DB under Staging
  project and prod under TAC-to-IWXXM; `kubectl --context staging -n metar-iwxxm-staging get deploy`
  shows workloads; staging `DATABASE_URL` host/db ≠ prod
- **Source**: F30 AC8; S052 / EV-043; S053 / EV-044; #886

### TC-F30-009: Staging DNS + TLS

- **Level**: Ops / T3
- **Objective**: `https://api.staging.tac-to-iwxxm.com` and `https://app.staging.tac-to-iwxxm.com`
  resolve to the **staging** DOKS LB and serve valid TLS
- **Pass criteria**: DNS A/AAAA → staging LB EXTERNAL-IP (not necessarily prod `168.144.12.70`);
  `/health` 200 on API; FE returns 200; cert-manager Certificate Ready
- **Source**: F30 AC9; D-S052-dns; D-S053-dns

### TC-F30-010: Dual-branch CD (amended EV-051)

- **Level**: Ops / CI
- **Objective**: Push/merge to `stage` deploys **staging cluster** after full Deploy
  `needs` (incl. `e2e-smoke`). Push/merge to `main` runs full CI but **does not** Deploy
  prod (EV-051).
- **Pass criteria**: Staging Deploy bound to GH Environment `staging`; `main` push workflow
  has no successful prod Deploy job for that event; env-scoped kubeconfig + `DOKS_NAMESPACE`
  correct when Deploy runs
- **Source**: F30 AC10; #886; EV-044; **EV-051 / S060** (`D-S060-scope=1`)

### TC-F30-011: Branch protection on stage and main

- **Level**: Ops / T0
- **Objective**: `stage` and `main` require PR; force-push denied (rulesets or classic protection)
- **Pass criteria**: `gh api` rulesets/protection show required PR + block force push
- **Source**: F30 AC11; D-S052-gh

### TC-F30-012: staging-gate on PRs to main

- **Level**: CI
- **Objective**: PRs targeting `main` fail unless head branch is `stage` and tip has green
  **Staging smoke** (H0c/H1 + H4–H5 against staging DNS)
- **Pass criteria**: `staging-gate` job fails for non-`stage` heads; passes when Staging smoke
  succeeded for the SHA; documented in deploy.md
- **Source**: F30 AC12; D-S052-promote

### TC-F30-013: Shared-cluster staging ns teardown (EV-044)

- **Level**: Ops / T0
- **Objective**: After staging cluster cutover, prod cluster no longer hosts
  `metar-iwxxm-staging` workloads (EV-043 leftover removed)
- **Pass criteria**: `kubectl --context prod get ns metar-iwxxm-staging` is NotFound (or
  empty/terminating with no Deployments); staging smoke uses staging cluster context only
- **Source**: F30 AC13; D-S053-teardown

### TC-F30-014: Tag-driven prod Deploy (EV-051)

- **Level**: Ops / CI
- **Objective**: Prod Deploy runs only for `vYYYY.MM.DD-deploy` tag pushes (pattern
  `v*-*-deploy`) or `workflow_dispatch` targeting production — after Deploy `needs`
  including `e2e-smoke` pass. Solo-dev approval = tag/dispatch (no Environment reviewers).
- **Pass criteria**: Workflow `on.push.tags` / `workflow_dispatch` documented; Deploy job
  `if` excludes bare `main` push; `needs` includes `e2e-smoke`; ADR-034 + deploy.md match
- **Source**: F30 AC14; EV-051 / S060; TC-EV051-001..006

### TC-EV051-001: Deploy needs include e2e-smoke

- **Level**: T0 (workflow review)
- **Objective**: `deploy.needs` lists prior jobs plus `e2e-smoke`
- **Pass criteria**: `.github/workflows/ci-cd.yml` `deploy.needs` contains `e2e-smoke`
- **Source**: EV-051 AC1

### TC-EV051-002: stage push still auto-deploys staging

- **Level**: Ops / CI
- **Objective**: Unchanged staging path after needs widen
- **Pass criteria**: `deploy` `if` allows `refs/heads/stage` push; Environment `staging`
- **Source**: EV-051 AC2

### TC-EV051-003: main push does not Deploy prod

- **Level**: Ops / CI
- **Objective**: Bare `main` push is CI-only for Deploy purposes
- **Pass criteria**: `deploy` `if` excludes `refs/heads/main`
- **Source**: EV-051 AC3

### TC-EV051-004: deploy tag triggers prod Deploy

- **Level**: Ops / CI
- **Objective**: Tag `v*-*-deploy` triggers prod Deploy path
- **Pass criteria**: `on.push.tags` includes pattern; Deploy resolves `env_role=prod`
- **Source**: EV-051 AC4; TC-F30-014

### TC-EV051-005: workflow_dispatch prod escape hatch

- **Level**: Ops / CI
- **Objective**: Manual `workflow_dispatch` can Deploy production
- **Pass criteria**: `on.workflow_dispatch` present; Deploy `if` includes dispatch → production
- **Source**: EV-051 AC5

### TC-EV051-006: Docs / ADR / rule parity

- **Level**: T0
- **Objective**: Standing docs describe tag-driven prod + full CI needs
- **Pass criteria**: ADR-034, deploy.md §CD, doks-promote-from-stage.mdc, feature-list F30
  AC10/AC14 consistent
- **Source**: EV-051 AC6

### EV-052 / S061 — CI polish + quality PR stats + Sentry/Redis/Orval

- **Level**: T0 / CI
- **Objective**: Restore ≥95% coverage gates (#950); second sticky PR comment with
  golden/quality-matrix outcomes by product × profile; free Sentry + Upstash-backed
  slowapi + OpenAPI typed FE client (#900).
- **Pass criteria**: AC1–AC12 in evolve-decisions §EV-052; TC-EV052-001..012
- **Source**: F29/F6/F21/F30/M5 deepen; EV-052 / S061; [#950](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/950);
  [#900](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/900)

### TC-EV052-001: Coverage surface inventory

- **Level**: T0
- **Objective**: Document every coverage surface + threshold vs ≥95%
- **Pass criteria**: Session inventory table (or test-plan appendix) lists apps/packages/scripts
- **Source**: EV-052 AC1; #950

### TC-EV052-002: ≥95% enforced in CI

- **Level**: T0 / CI
- **Objective**: Soft/deferred gates removed; fail_under / Vitest thresholds ≥95
- **Pass criteria**: Frontend lines/statements/branches ≥95 (or justified exclude); auth and
  all packages use fail_under ≥95; CI runs fail when under
- **Source**: EV-052 AC2; ADR-007

### TC-EV052-003: Suite green with gates

- **Level**: T0
- **Objective**: Tests added so gates pass; no silent waive
- **Pass criteria**: `make coverage-*` / CI coverage jobs green at tip
- **Source**: EV-052 AC3

### TC-EV052-004: Quality sticky PR comment

- **Level**: T0 / CI
- **Objective**: Second sticky comment with match/soft-diff/fail/skip by product × profile
- **Pass criteria**: Workflow posts markdown with distinct sticky marker; tables cover
  quality-matrix + annex3/`iwxxm_us` golden outcomes
- **Source**: EV-052 AC4

### TC-EV052-005: Comment formatter + sticky idempotence

- **Level**: T0
- **Objective**: Formatter unit-tested; update-in-place sticky
- **Pass criteria**: pytest for formatter; github-script finds marker and updates
- **Source**: EV-052 AC5

### TC-EV052-006: Sentry optional init

- **Level**: T0
- **Objective**: API/FE/worker init when DSN set; no-op when unset
- **Pass criteria**: Unit tests mock SDK; docs cite Developer free tier
- **Source**: EV-052 AC6

### TC-EV052-007: Upstash-backed slowapi

- **Level**: T0
- **Objective**: Shared Redis URL enables distributed limits; unset → in-memory
- **Pass criteria**: `abuse_controls` / limiter factory branches covered
- **Source**: EV-052 AC7; `D-S061-redis=1`

### TC-EV052-008: Shared-store rate-limit tests

- **Level**: T0
- **Objective**: Fake Redis proves cross-"replica" shared counters
- **Pass criteria**: Unit/integration with fakeredis or equivalent
- **Source**: EV-052 AC8

### TC-EV052-009: OpenAPI typed FE client

- **Level**: T0
- **Objective**: Generated client/types for high-churn paths; drift policy
- **Pass criteria**: `openapi-typescript` wired (`D-S061-orval=1`); committed
  `apps/frontend/openapi/openapi.json` + `src/generated/openapi.d.ts`;
  `pnpm openapi:check` fails on drift; convert/validate use generated aliases
- **Source**: EV-052 AC9

### TC-EV052-010: Docs / ADR parity

- **Level**: T0
- **Objective**: feature-list, test-plan, env-contract, deploy, inventory, ADR-006/031
- **Pass criteria**: Corpus deltas match implementation
- **Source**: EV-052 AC10

### TC-EV052-011: Free-tier infra record

- **Level**: T0
- **Objective**: No new DOKS Redis; Upstash + Sentry secrets documented
- **Pass criteria**: infra-free-tier.md + deploy/env stubs; kustomization has no Redis Deployment
- **Source**: EV-052 AC11

### TC-EV052-012: PR CI green

- **Level**: CI
- **Objective**: Tip PR CI includes coverage gates + quality comment job + new unit tests
- **Pass criteria**: Required workflows SUCCESS on evolve PR
- **Source**: EV-052 AC12

### EV-053 / S062 — Vitest branches ≥95 (FileConverter / #968)

- **Level**: T0 / CI
- **Objective**: Close `D-S061-cov-branches` waiver — Vitest `branches` ≥95; re-include
  `FileConverter.tsx`; FileConverter itself ≥95% branches; inventory waiver resolved.
- **Pass criteria**: AC1–AC5 in evolve-decisions §EV-053; TC-EV053-001..005
- **Source**: F29/M5 deepen; EV-053 / S062; [#968](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/968);
  parent [#950](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/950) / EV-052

### TC-EV053-001: Vitest branches threshold ≥95

- **Level**: T0 / CI
- **Objective**: `apps/frontend/vitest.config.ts` enforces `branches: 95` (with lines /
  statements / functions still ≥95)
- **Pass criteria**: Config thresholds all ≥95; no branches floor of 84
- **Source**: EV-053 AC1; ADR-007; #968

### TC-EV053-002: FE coverage suite green under gates

- **Level**: T0 / CI
- **Objective**: Frontend Vitest coverage job green with FileConverter in the coverage set
- **Pass criteria**: `pnpm --filter @metar/frontend test:coverage` (or CI matrix equivalent)
  passes at tip
- **Source**: EV-053 AC2

### TC-EV053-003: Coverage inventory branch_waiver resolved

- **Level**: T0
- **Objective**: Inventory no longer records an open branches waiver for frontend
- **Pass criteria**: S061 inventory updated (or EV-053 successor) shows `branch_waiver`
  resolved / removed; intentional excludes listed without silent soft gate
- **Source**: EV-053 AC3

### TC-EV053-004: Standing docs + #968 closeout

- **Level**: T0
- **Objective**: feature-list / test-plan / evolve-decisions cite EV-053 close; #968 Done
- **Pass criteria**: Corpus deltas match; issue closable after merge
- **Source**: EV-053 AC4

### TC-EV053-005: FileConverter ≥95% branches when included

- **Level**: T0
- **Objective**: With `FileConverter.tsx` in coverage collection, that file’s branch
  coverage is ≥95% (not only aggregate)
- **Pass criteria**: Coverage report (json/html or per-file summary) shows FileConverter
  branches ≥95; documented in session verify report
- **Source**: EV-053 AC5 (`D-S062-01-ac` Q3=2)

### EV-080 / #1077 — Universal 100% unit coverage gate

- **Level**: T0 / CI
- **Objective**: Raise ADR-007 from ≥95% to **100%** line+branch for Python apps/packages,
  Vitest unit surfaces, and repo scripts (Python cov + bats-core for every `.sh`)
- **Pass criteria**: AC1–AC6 in [evolve-decisions.md](decisions/evolve-decisions.md) §EV-080;
  **TC-EV080-001..010**
- **Source**: EV-080; [#1077](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1077);
  [Corpus: adr/ADR-007]

### TC-EV080-001: Coverage surface inventory @ 100 floor

- **Level**: T0
- **Objective**: Document every coverage surface with `target_floor: 100` and approved omits only
- **Pass criteria**: Inventory YAML lists apps/packages/scripts; no unapproved excludes
- **Source**: EV-080 AC1; REQ-EV080-001

### TC-EV080-002: Python fail_under 100 in configs + CI

- **Level**: T0 / CI
- **Objective**: Every pyproject + matrix job uses fail_under / `--cov-fail-under` **100**; `branch = true`
- **Pass criteria**: Config + workflow grep/tests assert 100; `__init__.py` not omitted
- **Source**: EV-080 AC2; REQ-EV080-002..003

### TC-EV080-003: Python aggregate + per-file 100 green

- **Level**: T0 / CI
- **Objective**: Unit matrix green at 100%; per-file checker `--min-pct 100`
- **Pass criteria**: CI package coverage jobs green; checker fails when any file &lt;100
- **Source**: EV-080 AC2; REQ-EV080-004..005

### TC-EV080-004: Vitest thresholds 100 + executable excludes purged

- **Level**: T0
- **Objective**: FE + shared Vitest lines/statements/functions/branches = **100**; no executable excludes
- **Pass criteria**: vitest configs show 100; TacEditor/App/liveAssist/gunzip/etc. not excluded
- **Source**: EV-080 AC3; REQ-EV080-006..008

### TC-EV080-005: FE + shared coverage suites green

- **Level**: T0 / CI
- **Objective**: `pnpm … test:coverage` green under 100% thresholds
- **Pass criteria**: frontend + `@metar/shared` coverage jobs green
- **Source**: EV-080 AC3; REQ-EV080-009

### TC-EV080-006: Scripts Python coverage 100

- **Level**: T0 / CI
- **Objective**: Dedicated job/make target covers `scripts/**/*.py` at ≥100% line+branch
- **Pass criteria**: Job green; fail_under 100
- **Source**: EV-080 AC4; REQ-EV080-010

### TC-EV080-007: bats-core installed in CI

- **Level**: T0 / CI
- **Objective**: Workflow installs bats-core and runs bats suite
- **Pass criteria**: CI step succeeds; bats binary available
- **Source**: EV-080 AC5; REQ-EV080-011..012; D-EV080-bats

### TC-EV080-008: Every `.sh` has bats coverage

- **Level**: T0 / CI
- **Objective**: Each `scripts/**/*.sh` mapped to ≥1 bats test
- **Pass criteria**: Manifest count matches `find scripts -name '*.sh'`; bats job green
- **Source**: EV-080 AC5; REQ-EV080-011

### TC-EV080-009: Standing docs + ADR-007 at 100%

- **Level**: T0
- **Objective**: ADR-007, typing-policy, test-plan metrics cite **100%**
- **Pass criteria**: Docs greppable for 100% gate; CORPUS cites valid
- **Source**: EV-080 AC6; REQ-EV080-013

### TC-EV080-010: No silent excludes remain

- **Level**: T0
- **Objective**: Audit inventory vs configs — zero unapproved measurement omits
- **Pass criteria**: Diff/inventory audit passes in CI or unit guard test
- **Source**: EV-080 AC6; REQ-EV080-014..015

### EV-054 / S063 — Quality metrics tab (#836 / F7.q)

- **Level**: T0 / T2 / T3 / H4–H5
- **Objective**: Primary **Quality metrics** shell tab browses official WMO corpus by
  product with precomputed match / residuals / lint / validate and unified XML diff.
- **Pass criteria**: AC1–AC7 in evolve-decisions §EV-054; TC-EV054-001..008; **UJ-056**
- **Source**: F7.q deepen; EV-054 / S063; [#836](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/836);
  ADR-032; ADR-025

### TC-EV054-001: Quality metrics is a primary shell tab

- **Level**: T0 / T2
- **Objective**: App exposes a dedicated Quality metrics view peer to Convert / History
  (not a panel inside FileConverter)
- **Pass criteria**: Navigation reaches the tab; Vitest and/or Playwright assert shell route/view
- **Source**: EV-054 AC1; UJ-056; `D-S063-shell-tab`

### TC-EV054-002: Corpus listed by product / file type

- **Level**: T0 / T2
- **Objective**: Official corpus inventory grouped by product; ADR-032 tiers visible;
  FIXTURE_GAPS / deferred stems labeled
- **Pass criteria**: Catalog ∪ gaps completeness; no silent omission of in-scope pin stems
- **Source**: EV-054 AC1 / AC5; UJ-039 deepen

### TC-EV054-003: File detail — match + unified XML diff

- **Level**: T0 / T2
- **Objective**: Selecting a stem shows official + our XML/TAC, match status, and a
  **unified XML diff** (`D-S063-diff=2`)
- **Pass criteria**: Diff visible for a non-equal pair or documented equal/empty-diff state
  for a passer; raw panes remain inspectable
- **Source**: EV-054 AC2

### TC-EV054-004: Residuals / lint / validate panels

- **Level**: T0 / T2
- **Objective**: Detail pane surfaces decode residuals, tac-validate issues, and
  iwxxm-validate XSD/Schematron results (empty states when clean)
- **Pass criteria**: Clean passer shows empty/expected allowlisted diagnostics; dirty fixture
  (when present) shows non-empty panel content
- **Source**: EV-054 AC3; ADR-025

### TC-EV054-005: Product summary counts match precomputed fixture

- **Level**: T0
- **Objective**: Aggregate counts per product equal the precomputed metrics artifact
  served by `GET /api/v1/quality-metrics`
- **Pass criteria**: Backend unit/fixture test compares response summaries to golden artifact
- **Source**: EV-054 AC4; `D-S063-compute=1`; `D-S063-gateA=2`

### TC-EV054-006: No Supabase / no live upstream WMO fetch

- **Level**: T0 / T2
- **Objective**: Metrics routes and FE tab do not call Supabase or download upstream WMO
  trees; data comes from precomputed fixtures via our API
- **Pass criteria**: Tests assert handler reads local artifact only; no Supabase client on path
- **Source**: EV-054 AC7; `D-S063-gateA=2`

### TC-EV054-007: Playwright / H4–H5 smoke (UJ-056)

- **Level**: T2 / T3 / H4–H5
- **Objective**: Open Quality metrics tab → filter one product → open one passer → see
  clean or expected diagnostics (+ unified diff pane present); FE calls quality-metrics API
- **Pass criteria**: Playwright green locally/CI; H4–H5 after staging deploy (12/13)
- **Source**: EV-054 AC6; UJ-056; connectivity gates

### TC-EV054-008: Public quality-metrics HTTP API

- **Level**: T0 / T2 / H0i
- **Objective**: `GET /api/v1/quality-metrics` and `GET /api/v1/quality-metrics/{stem}` are
  public (no JWT), return msgspec JSON, 404 unknown stem, serve precomputed data
- **Pass criteria**: Backend tests + OpenAPI paths; CORS covered by existing H0c patterns
- **Source**: EV-054 AC4/AC7; [Corpus: api]; `D-S063-gateA=2`

### EV-055 / S064 — Quality metrics normalize + 2025-2 validate (#982 / #980 / #979)

- **Mode**: delta deepen F7.q + F2/F13
- **Pass criteria**: AC1–AC7 in evolve-decisions §EV-055; TC-EV055-001..007; **UJ-056** deepen
- **Source**: [#982](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/982),
  [#980](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/980),
  [#979](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/979); parent #836 / EV-054

### TC-EV055-001: Formatting-only diffs no longer dominate

- **Level**: T0 / T2
- **Objective**: For a representative stem whose official vs converted XML differ mainly in
  pretty-print/whitespace, unified line diff on **C14N** peers is empty or semantic-only
- **Pass criteria**: Fixture/unit assertion on C14N + diff; Vitest or generator test
- **Source**: EV-055 AC1; #982; UJ-056; `D-S064-c14n=1`

### TC-EV055-002: match_status uses C14N equality

- **Level**: T0 / H0i
- **Objective**: `match_status` on list/detail quality-metrics payloads equals when
  post–volatile-strip **C14N** official and converted XML are equal (even if raw bytes
  differ in formatting or `gml:id` / UUID attrs — `D-S064-c14n-volatile=1` / ADR-035)
- **Pass criteria**: Backend/generator tests; OpenAPI/docs state C14N + volatile-strip
  semantics
- **Source**: EV-055 AC2; [Corpus: api]; [Corpus: adr/ADR-035]; `D-S064-normalize=1`;
  `D-S064-c14n=1`; `D-S064-c14n-volatile=1`

### TC-EV055-003: C14N helper + golden stem (shared generator + FE)

- **Level**: T0
- **Objective**: Shared C14N helper covered by unit tests; ≥1 golden stem; vendor trees
  not rewritten in place; used by metrics generator and FE diff
- **Pass criteria**: Unit tests green; vendor/schemas read-only
- **Source**: EV-055 AC3; #982; `D-S064-gateA-M1=1`

### TC-EV055-004: SCHEMATRON enabled for 2025-2 (hard)

- **Level**: T0 / T2
- **Objective**: 2025-2 Schematron with xslt2 binding is **evaluated** (prefer native);
  `SCHEMATRON_SKIPPED` is not an acceptable close for this cycle
- **Pass criteria**: Engine tests assert evaluation path; matrix documented
- **Source**: EV-055 AC4; #980; `D-S064-sch-hard=1`; F2/F13

### TC-EV055-005: SCHEMA_IMPORT_WARNING fixed for 2025-2 (hard)

- **Level**: T0 / T2
- **Objective**: Root cause (file + import URI) fixed; strict XSD path no longer skipped for
  the resolved case
- **Pass criteria**: Regression test green; warning absent on representative stems
- **Source**: EV-055 AC5; #979; `D-S064-xsd-hard=1`; F2

### TC-EV055-006: corpus_metrics regen for C14N match

- **Level**: T0 / CI
- **Objective**: Regenerated `corpus_metrics.json` reflects C14N `match_status` counts after
  `make generate-quality-metrics`
- **Pass criteria**: Generator CI/job green; summary counts consistent with AC2
- **Source**: EV-055 AC7; `D-S064-regen=1`

### TC-EV055-007: UJ-056 smoke — C14N panes + validate chips

- **Level**: T2 / T3 / H4–H5
- **Objective**: Quality metrics detail defaults to normalized XML panes with override to
  un-normalized; quieter C14N diff; validate chips match enabled/fixed disposition
- **Pass criteria**: Local Playwright/Vitest green; H4–H5 after staging deploy (12/13)
- **Source**: EV-055 AC1 / AC6 / AC7; UJ-056; `D-S064-gateA-M2=override`

### EV-056 / S066 — Quality metrics detail page + collapsible diffs (#988 / F7.q)

- **Mode**: delta deepen F7.q (UX/docs/tests; C14N semantics unchanged)
- **Pass criteria**: AC1–AC5 in evolve-decisions §EV-056; TC-EV056-001..005; **UJ-056** deepen
- **Source**: [#988](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/988); S065 FOLLOWUP;
  parent EV-054 / EV-055; pretty-print hotfix #987

### TC-EV056-001: Dedicated `/quality/:stem` detail route

- **Level**: T0 / T2
- **Objective**: List row navigates to shareable `/quality/:stem` with back-to-list
  (`D-S066-route-shape=1` / `D-S066-list=1`)
- **Pass criteria**: Vitest and/or Playwright assert route + back navigation
- **Source**: EV-056 AC1; UJ-056

### TC-EV056-002: Pretty C14N panes preserved

- **Level**: T0 / T2
- **Objective**: Official/Converted/TAC panes remain; normalized = pretty C14N (S065 helpers)
- **Pass criteria**: FE unit asserts pretty multi-line display XML for C14N peers
- **Source**: EV-056 AC2; S065; UJ-056

### TC-EV056-003: Collapsible equal-context hunks (default 3)

- **Level**: T0 / T2
- **Objective**: Unified diff collapses unchanged context to GitHub-like expand controls;
  default **3** context lines; expand hunk / expand all (`D-S066-context-n=1`)
- **Pass criteria**: Unit test on `collapseEqualContext` (or equivalent); UI control smoke
- **Source**: EV-056 AC3; UJ-056

### TC-EV056-004: Unequal SIGMET stems remain readable

- **Level**: T2 / T3 / H4–H5
- **Objective**: Non-equal SIGMET (or other unequal) stems open on detail route with
  navigable collapsed hunks
- **Pass criteria**: Playwright or staging smoke opens an unequal stem; no single-line dump
- **Source**: EV-056 AC4; UJ-056

### TC-EV056-005: UJ-056 smoke — detail route + hunk fold

- **Level**: T2 / T3 / H4–H5
- **Objective**: Open Quality metrics → open stem → land on `/quality/:stem` → see
  collapsible unified diff; C14N/`match_status` unchanged
- **Pass criteria**: Local Playwright green; H4–H5 after staging deploy (13)
- **Source**: EV-056 AC5; UJ-056

### EV-058 / S068 — Quality metrics side-by-side vs inline XML diff (#983 / F7.q)

- **Mode**: delta deepen F7.q (FE-only UX/docs/tests; C14N semantics unchanged)
- **Pass criteria**: AC1–AC5 in evolve-decisions §EV-058; TC-EV058-001..005; **UJ-056** deepen
- **Source**: [#983](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/983); predecessor
  EV-056 / #988; parent EV-054 / #836

### TC-EV058-001: Layout segmented control on `/quality/:stem`

- **Level**: T0 / T2
- **Objective**: Detail page exposes Inline (unified) | Side-by-side control; switch
  without reload (`D-S068-01-control=3a`)
- **Pass criteria**: Vitest and/or Playwright assert control + both layouts render
- **Source**: EV-058 AC1; UJ-056

### TC-EV058-002: Default remains unified

- **Level**: T0 / T2
- **Objective**: First visit (no stored preference) shows unified/inline layout
- **Pass criteria**: Default view matches prior UJ-056 unified assertions
- **Source**: EV-058 AC2; UJ-056

### TC-EV058-003: Side-by-side uses existing line-diff helpers

- **Level**: T0 / T2
- **Objective**: Side-by-side highlights changed lines via `unifiedLineDiff` (or sibling
  helpers); no new npm `diff` package
- **Pass criteria**: FE unit asserts side-by-side changed-line markers; package.json
  unchanged for diff libs
- **Source**: EV-058 AC3; UJ-056

### TC-EV058-004: Preference persists in localStorage

- **Level**: T0 / T2
- **Objective**: Selected layout survives reload via localStorage
- **Pass criteria**: Vitest and/or Playwright set side-by-side → reload → still side-by-side
- **Source**: EV-058 AC4; UJ-056

### TC-EV058-005: UJ-056 smoke — both layout modes

- **Level**: T2 / T3 / H4–H5
- **Objective**: Open `/quality/:stem` → toggle Inline ↔ Side-by-side; TAC/diagnostics/
  collapse remain; C14N/`match_status` unchanged. Synced scroll best-effort only.
- **Pass criteria**: Local Playwright green; H4–H5 after staging deploy (13)
- **Source**: EV-058 AC5; UJ-056; `D-S068-01-ac=2b`

### EV-059 / S069 — F34 Contract + mutation quality gates (#841 / #727 / #874)

- **Mode**: new **F34** (Platform / CI·DX); no operator UJ; no H4–H5
- **Pass criteria**: AC1–AC7 in evolve-decisions §EV-059; **TC-F34-001..007**;
  optional cycle aliases **TC-EV059-001..007**
- **CI posture** (`D-S069-ci`):
  - **Schemathesis**: path-filtered **required** when `apps/backend/**` or OpenAPI-related
    paths change; Hypothesis **max-examples ≤ 25**; job timeout ≤ **10 min**.
    Workflow: `.github/workflows/schemathesis.yml`. Local: `make test-schemathesis`
    (override with `SCHEMATHESIS_MAX_EXAMPLES`, still capped at 25 in-suite).
  - **Mutation** (pytest-gremlins + Stryker): **nightly / `workflow_dispatch` only**;
    chunked matrix + hard timeouts; **not** required on every PR.
    Workflow: `.github/workflows/mutation.yml`. Local:
    `make test-mutation-poc` (narrow), `make test-mutation-python TARGET=…`,
    `make test-mutation-js TARGET=frontend|shared`.
    Excludes: e2e, Rust crates, generated `iwxxm_xsd` trees.
    Interpreting survivors: a surviving mutant means tests execute the line but do not
    assert behavior that would fail under the mutation — strengthen assertions or waive
    with rationale in the session build report / bug report (not a PR merge blocker).
- **Schemathesis exclusions** (explicit): `/api/v1/work-sessions*`, `/api/v1/eval/*`,
  `/auth/*` (Postgres / Supabase Auth — covered by unit/integration). Documented HTTP 501
  on `/api/v1/ingest-collect` is an allowed expected status.
- **Source**: [#841](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/841);
  [#727](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/727);
  [#874](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/874); [Corpus: product §F34]

### TC-F34-001: Schemathesis ASGI + auth

- **Level**: T0 / T2 (in-process ASGI; no external network)
- **Objective**: Suite loads OpenAPI from backend app; Bearer/test JWT (or dependency
  override) exercises protected routes; no unexpected 5xx; responses match schema
- **Pass criteria**: `make test-schemathesis` green locally; failures minimize to seed/cURL
- **Source**: F34 AC1; #727

### TC-F34-002: Path-filtered Schemathesis CI

- **Level**: CI
- **Objective**: Required job runs on PRs touching backend/OpenAPI paths; skipped otherwise
- **Pass criteria**: Workflow path filters documented; job respects max-examples ≤ 25 and
  timeout ≤ 10 min (**TC-F34-007**)
- **Source**: F34 AC2 / AC7; `D-S069-ci`

### TC-F34-003: pytest-gremlins Python mutation targets

- **Level**: T0 / nightly
- **Objective**: Config + `make` target(s) mutate
  `apps/backend`, `apps/worker`,
  `packages/{auth,shared,tac-validate,tac2iwxxm,iwxxm-validate,dissemination}`
- **Pass criteria**: Local/nightly run produces score + survivors report; exclusions
  (e2e, Rust) documented
- **Source**: F34 AC3; #874; `D-S069-tool`

### TC-F34-004: Stryker TypeScript mutation targets

- **Level**: T0 / nightly
- **Objective**: Stryker config + `make`/pnpm script for `apps/frontend` (+ shared JS if
  present)
- **Pass criteria**: Nightly/manual run produces mutation report; hard timeout enforced
- **Source**: F34 AC3; #874

### TC-F34-005: Nightly / manual mutation matrix

- **Level**: CI (non-PR-required)
- **Objective**: Chunked workflow covers full Python + TS matrix without blocking every PR
- **Pass criteria**: `workflow_dispatch` and/or schedule green or flaky survivors tracked;
  minutes bounded by per-chunk timeouts
- **Source**: F34 AC3; `D-S069-e4`

### TC-F34-006: Inventory, docs, findings, epic close path

- **Level**: Docs / process
- **Objective**: Deps in dependency-inventory; test-plan notes; findings fixed via
  bug-investigation or waived; two PRs; #841 closable when children Done
- **Pass criteria**: Inventory rows present; waivers recorded; #727/#874 Done ⇒ epic Done
- **Source**: F34 AC4–AC6

### TC-F34-007: Schemathesis budget ceilings documented

- **Level**: Docs / CI
- **Objective**: Standing test-plan (this section) + workflow comments state
  max-examples ≤ 25 and job timeout ≤ 10 min
- **Pass criteria**: Docs and CI config agree; Build does not raise budgets without
  AskQuestion
- **Source**: F34 AC7; `D-S069-01-ac=2b`

### TC-EV059-001..007

- Aliases of **TC-F34-001..007** for evolve-cycle traceability (EV-059 / S069).

### EV-060 / S070 — Converter operator bugs + IWXXM pass-through (#1000)

- **Mode**: delta deepen F7.t + F6/F2/F10/F29/F31
- **Pass criteria**: AC in evolve-decisions §EV-060; **UJ-059..063**; UJ-003/046 UAT
- **Source**: [#1000](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1000)–[#1006](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1006)

### TC-EV060-1001-001: AHL heading not product-syntax flood

- **Level**: T0 / T2
- **Objective**: Well-formed AHL METAR bulletin lint does not score AHL tokens as METAR syntax
- **Pass criteria**: Heading issues are bulletin-level (or none); contained METARs still linted
- **Source**: #1001; UJ-059

### TC-EV060-1001-002: Malformed AHL one bulletin error

- **Level**: T0
- **Objective**: Malformed AHL yields one bulletin-level error and still attempts split
- **Pass criteria**: Structured bulletin error; no opaque 5xx
- **Source**: #1001

### TC-EV060-1001-003: FileConverter + convert-bulletin parity

- **Level**: T2 / T3 / H4–H5
- **Objective**: Same AHL behavior on workbench, FileConverter, and `/convert-bulletin`
- **Pass criteria**: No heading flood on all three
- **Source**: #1001; `D-S070-e3c`

### TC-EV060-1003-001: Valid IWXXM product pass-through

- **Level**: T0 / T2
- **Objective**: `product=iwxxm` + valid XML → F2 result; no TAC convert
- **Pass criteria**: No TAC lint-as-METAR; F2 issues/pass shown
- **Source**: #1003; F7.t AC1

### TC-EV060-1003-002: TAC text under product=iwxxm is not-XML

- **Level**: T0
- **Objective**: TAC text with product=iwxxm returns structured not-XML error
- **Pass criteria**: Not METAR lint flood
- **Source**: #1003; F7.t AC2

### TC-EV060-1003-003: Convert disabled or no-op

- **Level**: T0 / T2
- **Objective**: Convert control disabled or no-ops with clear operator message
- **Pass criteria**: Message has no internal doc refs
- **Source**: #1003

### TC-EV060-1003-004: FileConverter / QM / accumulate honor IWXXM product

- **Level**: T2 / T3 / H4–H5
- **Objective**: Those surfaces honor product=iwxxm
- **Pass criteria**: Same pass-through semantics
- **Source**: #1003; `D-S070-e3c`

### TC-EV060-1002-001: Profile labeled at converter top

- **Level**: T0 / T2
- **Objective**: Profile control labeled at top; changing it is used on convert/lint/validate
- **Pass criteria**: Accessible name + visible label; API `profile=` matches
- **Source**: #1002; UJ-061

### TC-EV060-1002-002: Keyboard/accessible Profile

- **Level**: T0
- **Objective**: Profile has accessible name (not icon-only)
- **Pass criteria**: axe/vitest accessible name present
- **Source**: #1002; `D-S070-e3b`

### TC-EV060-1002-003: FileConverter / QM honor profile

- **Level**: T2
- **Objective**: Shared chrome or inherit; no QM redesign
- **Pass criteria**: Same profile value used
- **Source**: #1002

### TC-EV060-1005-001: Bulletin fields used on convert

- **Level**: T0 / T2
- **Objective**: Filled Bulletin ID + Issuing Center appear in output/API payload
- **Pass criteria**: Values round-trip
- **Source**: #1005; UJ-062

### TC-EV060-1005-002: Empty uses discover/defaults

- **Level**: T0
- **Objective**: Empty fields keep discover-from-AHL or current defaults
- **Pass criteria**: No silent drop of discovered AHL CCCC
- **Source**: #1005

### TC-EV060-1005-003: Invalid CCCC/ID field error

- **Level**: T0
- **Objective**: Invalid issuing center → one operator-visible field error
- **Pass criteria**: Not silent ignore
- **Source**: #1005

### TC-EV060-1004-001: DEBUG vs ERROR log verbosity differs

- **Level**: T0 / T2
- **Objective**: Same convert at DEBUG vs ERROR emits different log verbosity
- **Pass criteria**: Logger level applied in backend/packages
- **Source**: #1004; UJ-063

### TC-EV060-1004-002: DEBUG does not dump secrets

- **Level**: T0
- **Objective**: DEBUG logs omit JWTs, passwords, Authorization headers
- **Pass criteria**: Fixture/scan assertion
- **Source**: #1004; `D-S070-e6`

### TC-EV060-1006-001: Register happy path

- **Level**: T2 / T3
- **Objective**: Playwright register with test account
- **Pass criteria**: Account created; no production PII
- **Source**: #1006; UJ-003

### TC-EV060-1006-002: Login + session persist

- **Level**: T2 / T3 / H4–H5
- **Objective**: Login then reload still logged in
- **Pass criteria**: UJ-046 persist
- **Source**: #1006

### TC-EV060-1006-003: Logout

- **Level**: T2 / T3
- **Objective**: Logout returns to guest convert
- **Pass criteria**: Convert still works without JWT
- **Source**: #1006; F21

### TC-EV060-1006-004: Facilitated UAT sign-off

- **Level**: UAT
- **Objective**: `uat` Build checklist signed for register/login/logout/persist
- **Pass criteria**: Session UAT report
- **Source**: #1006; `D-S070-e4`

### EV-061 / S071 — Pre-promote UX + catalog + AHL + stage→main gate (#1009)

- **Mode**: delta deepen F7.u/F7.v + F2/F6/F9/F10/F15/F34
- **Pass criteria**: AC in evolve-decisions §EV-061; **UJ-064..068**; UJ-DEV-009; TC-LIVE-F6-030 `files`
- **Source**: [#1009](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1009)–[#1015](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1015)

### TC-EV061-1011 / TC-LIVE-F6-030: Live bulletin multipart `files`

- **Level**: Live H7
- **Objective**: Harness posts convert-bulletin multipart field **`files`**, not `file`
- **Pass criteria**: Request matches [Corpus: api] `/convert-bulletin`; fixture still converts
- **Source**: #1011; UJ-011

### TC-EV061-1012-001: Golden AHL multi-METAR decode rows

- **Level**: T0 / T2
- **Objective**: `SAUS31 KZNY` multi-report METAR AHL decodes with item-by-item rows per report
- **Pass criteria**: Bulletin framing + F9-shaped rows; not a raw dump
- **Source**: #1012; UJ-065

### TC-EV061-1012-002: Golden AHL convert-bulletin

- **Level**: T0 / T2
- **Objective**: Same golden bulletin succeeds on `/convert-bulletin`
- **Pass criteria**: Per-report IWXXM results (or structured per-report errors); HTTP not 5xx
- **Source**: #1012

### TC-EV061-1012-003: FileConverter / workbench AHL parity

- **Level**: T2 / T3 / H4–H5
- **Objective**: Decode + convert-bulletin behavior matches API on operator UI
- **Pass criteria**: Golden path works; product/profile/Bulletin ID context honored
- **Source**: #1012; UJ-065

### TC-EV061-1012-004: Malformed AHL clear error

- **Level**: T0
- **Objective**: Malformed heading/body yields `INVALID_AHL` and/or `empty_bulletin`
- **Pass criteria**: No silent success; operator-facing message has no internal doc refs
- **Source**: #1012; [Corpus: api]

### TC-EV061-1010-001: Validate IWXXM item-by-item decode

- **Level**: T0 / T2
- **Objective**: Validate IWXXM path that still produces decode shows F9 item rows
- **Pass criteria**: Same panel pattern as TAC products; not a raw XML/text dump
- **Source**: #1010; UJ-064

### TC-EV061-1010-002: Additive decode fields backward-compatible

- **Level**: T0
- **Objective**: `/validate` optional `segments`/`summary` (if added) do not break existing clients
- **Pass criteria**: Older clients ignore extras; OpenAPI documents additive fields
- **Source**: #1010; D-S071-api

### TC-EV061-1010-003: F7.s / F7.t still work

- **Level**: T2 / T3 / H4–H5
- **Objective**: Validate-only and IWXXM pass-through remain after decode-panel work
- **Pass criteria**: UJ-058 / UJ-060 still pass
- **Source**: #1010; F7.s / F7.t

### TC-EV061-1013-001: Product Type + Profile no-wrap ≥1024px

- **Level**: T0 / T2 / T3 / H4–H5
- **Objective**: Top Product Type + Profile stay on one bar without wrap at ≥1024px
- **Pass criteria**: No wrap; keyboard labels preserved
- **Source**: #1013; UJ-066

### TC-EV061-1013-002: Mode selects one aligned row

- **Level**: T0 / T2
- **Objective**: Mode selects share one aligned bar/row at ≥1024px
- **Pass criteria**: Visual alignment with Product/Profile chrome
- **Source**: #1013; UJ-066

### TC-EV061-1013-003: Conversion parameters one bar; stack below 1024px

- **Level**: T0 / T2 / T3 / H4–H5
- **Objective**: Parameters share one aligned bar ≥1024px; stacking OK below
- **Pass criteria**: UJ-067; a11y names unchanged
- **Source**: #1013; UJ-067

### TC-EV061-1014-001: Catalog tab reachable

- **Level**: T2 / T3 / H4–H5
- **Objective**: Top-level **Validation Issues Catalog** nav opens a page (EV-062 rename; was Lint & validation catalog)
- **Pass criteria**: Public/guest can open without JWT
- **Source**: #1014; #1017; UJ-068

### TC-EV061-1014-002: Rows include code, description, level, source

- **Level**: T0 / T2
- **Objective**: Catalog lists TAC lint **and** IWXXM validation checks
- **Pass criteria**: code, description, level, clickable source URL when status=verified
- **Source**: #1014; F7.v / F15

### TC-EV061-1014-003: Operator source hrefs resolve

- **Level**: T0 / T2
- **Objective**: Operator-visible `source_url` values are verified landings (HTTP 2xx/3xx)
- **Pass criteria**: Semantic `codes.wmo.int/49-2*` may be aliases, not hrefs (`D-S071-links-resolve`)
- **Source**: #1014; mining note

### TC-EV061-1014-004: No internal planning ids in catalog copy

- **Level**: T0
- **Objective**: Catalog attribution / OpenAPI / UI free of `[Corpus:]`, ADR, EV, UJ ids
- **Pass criteria**: EV-048 guards green
- **Source**: #1014; [Corpus: product §F7]

### TC-EV062-001: Catalog title is Validation Issues Catalog

- **Level**: T0 / T2 / T3 / H4–H5
- **Objective**: Nav + page title use **Validation Issues Catalog**
- **Pass criteria**: No operator-visible “Lint & validation catalog” title
- **Source**: #1017; UJ-068; FR1

### TC-EV062-002: issue_type present and filterable

- **Level**: T0 / T2 / T3 / H4–H5
- **Objective**: Each row has `issue_type`; UI filter narrows by type
- **Pass criteria**: Closed vocab; empty state when no matches
- **Source**: #1017; FR2

### TC-EV062-003: Descriptions explain what/why + locator or unavailable

- **Level**: T0 / T2
- **Objective**: No thin research-only stubs as sole description; section cite or unavailable marker
- **Pass criteria**: Spot-check former research codes (e.g. AMD_PRESENT); API `source_locator` or unavailable copy
- **Source**: #1017; FR3

### TC-EV062-004: source_access + public-prefer primary href

- **Level**: T0 / T2
- **Objective**: `source_access` exposed; public primary when lawful free cite exists; paywall labeled
- **Pass criteria**: Inventory + crawl after retarget; EV-048 clean attribution
- **Source**: #1017; FR4

### TC-EV062-005: Sort + multi-filter

- **Level**: T0 / T2 / T3 / H4–H5
- **Objective**: Sort by code/level/type/access; combine filters
- **Pass criteria**: Intersection semantics; keyboard accessible
- **Source**: #1017; FR5

### TC-EV062-006: Catalog regen / drift + OpenAPI additive

- **Level**: T0 / T2
- **Objective**: Registry/catalog drift green; OpenAPI includes new optional fields
- **Pass criteria**: TC-F15-001 family + OpenAPI internal-doc-ref guards
- **Source**: #1017; ADR-028; NFR1–NFR4

### EV-064 / F36 — CA_ECCC profile (#916)

- **Mode**: deepen F36; IWXXM 3.0.0 + `iwxxm-ca` line
- **Pass criteria**: AC in evolve-decisions §EV-064; TC-EV064-*
- **Source**: [#916](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/916); ADR-036;
  [domain/profiles/semantic/CA_ECCC.md](domain/profiles/semantic/CA_ECCC.md)

### TC-EV064-001: Vendor pin iwxxm-ca + IWXXM 3.0.0 core

- **Level**: T0
- **Objective**: `vendor/manifest.json` includes `iwxxm-ca`; core 3.0.0 refs resolve for CA XSD
- **Pass criteria**: Manifest checksum gate; sync script copies `iwxxm-ca` tree
- **Source**: EV-064 M1; R-EV064-01

### TC-EV064-002: Convert METAR CA_ECCC golden

- **Level**: T0 / T2
- **Objective**: `semantic_profile=CA_ECCC` converts MANOBS fixture to golden IWXXM
- **Pass criteria**: Profile fixture manifest green; not annex3 delegate for targeted rules
- **Source**: EV-064 M3; R-EV064-02

### TC-EV064-003: Validate CA extension XSD path

- **Level**: T0
- **Objective**: `validate_iwxxm(..., profile=ca_eccc)` uses CA catalog roots
- **Pass criteria**: Valid CA golden passes XSD; missing pin fails closed
- **Source**: EV-064 M2; R-EV064-05

### TC-EV064-004: API CA_ECCC wire matrix

- **Level**: T2 / T3
- **Objective**: `semantic_profile=CA_ECCC` on convert/validate; unknown id → 400
- **Pass criteria**: TC-EV063-003 pattern extended for `ca_eccc`
- **Source**: R-EV064-06

### TC-EV064-005: FE profile picker CA_ECCC

- **Level**: T2 / H4–H5
- **Objective**: FileConverter profile dropdown includes Canada (ECCC)
- **Pass criteria**: Workflow test sends `CA_ECCC` (or canonical wire id) on convert
- **Source**: #1024 slice; R-EV064-07

### TC-EV064-006: Forecast product E2E (TAF or AIRMET)

- **Level**: T0 / T2
- **Objective**: At least one MANAIR TAF or GFA AIRMET golden + API convert path
- **Pass criteria**: #916 acceptance “METAR + one forecast product”
- **Source**: EV-064 M4/M5; R-EV064-03/04

### EV-066 / #916 — CA_ECCC RMK + altimeter deepen

- **Mode**: deepen F36; IWXXM 3.0.0 + `iwxxm-ca` line
- **Pass criteria**: AC in evolve-decisions §EV-066; TC-EV066-*
- **Source**: [#916](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/916); EV-066;
  [domain/profiles/semantic/CA_ECCC.md](domain/profiles/semantic/CA_ECCC.md)

### TC-EV066-001: PRESRR remark golden

- **Level**: T0 / T2
- **Objective**: `CA_ECCC` converts METAR with `PRESRR` to golden with RISING pressureChangeIndicator
- **Pass criteria**: Manifest case `metar_rmk_presrr`; canonicalize diff empty
- **Source**: EV-066 M1/M2; FR-EV066-01

### TC-EV066-002: Altimeter not observable (`A////`)

- **Level**: T0 / T2
- **Objective**: Body `A////` → nil-reason QNH; no false altimeter_inhg
- **Pass criteria**: Golden + convert ok; nilReason notObservable on qnh
- **Source**: EV-066 M1/M2; FR-EV066-02

### TC-EV066-003: SLP + hourly T remark combo

- **Level**: T0 / T2
- **Objective**: Addendum encodes SLP; additive T preserved in humanReadableText
- **Pass criteria**: Golden diff empty; Addendum contains seaLevelPressure
- **Source**: EV-066 M2; FR-EV066-03

### TC-EV066-004: Canadian RMK lint deepen

- **Level**: T0
- **Objective**: `lint(..., profile=ca_eccc)` emits extended MANOBS remark codes
- **Pass criteria**: `CA_REMARK_PRESRR`, `CA_REMARK_NOSPECI`, `CA_REMARK_SECTOR_VIS`, `CA_ALTIMETER_NOT_OBS`
- **Source**: EV-066 M3; FR-EV066-04

### EV-068 / #1035 + #1027 — CA_ECCC layered validation stack

- **Mode**: deepen F2/F4/F13/F36; IWXXM 3.0.0 profile-pinned bundle + staged `ca_eccc` validate
- **Pass criteria**: AC in evolve-decisions §EV-068; TC-EV068-*
- **Source**: [#1035](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1035), [#1027](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1027); EV-068;
  [domain/IWXXM_VALIDATION.md](domain/IWXXM_VALIDATION.md) §CA_ECCC validation stages

### TC-EV068-001: Profile-pinned 3.0.0 bundle integrity

- **Level**: T0
- **Objective**: `vendor/manifest.json` + on-disk trees satisfy CA_ECCC bundle resolution
- **Pass criteria**: `iwxxm-ca` pin present; `3.0.0/IWXXM/iwxxm.xsd` exists; manifest integrity test green
- **Source**: EV-068 M1; #1027; R-EV068-001

### TC-EV068-002: Layered validate stages + product XSD selection

- **Level**: T0 / T2
- **Objective**: `validate(..., profile=ca_eccc)` returns per-stage issues; METAR uses `metar-speci-ca.xsd` at layer 4
- **Pass criteria**: Missing CA extension element fails at `ca_xsd` layer (not only `wmo_xsd`)
- **Source**: EV-068 M3/M4; #1035; R-EV068-002..003

### TC-EV068-003: EV-067 golden validate gate

- **Level**: T0 / T2
- **Objective**: `metar_lwis`, `metar_sawr`, `metar_rmk_icing` goldens pass layers 2–4 under `ca_eccc`
- **Pass criteria**: Replaces EV-064/067 XSD waive in `test_tc_ev064_002_ca_eccc_goldens.py`
- **Source**: EV-068 M6; R-EV068-007

### TC-EV068-004: API `extensions=IWXXM_CA` wire

- **Level**: T2 / H4
- **Objective**: Convert/validate accept `extensions` with `IWXXM_CA`; triggers full CA stack
- **Pass criteria**: OpenAPI + backend unit tests; backward compat when extensions omitted
- **Source**: EV-068 M5; #1027; R-EV068-005

### TC-EV068-005: Datamart METAR sample (informative)

- **Level**: T2
- **Objective**: Operational datamart METAR sample passes full CA stack when fixture available
- **Pass criteria**: Document pass/fail in test or mining notes — gate per feasibility decision
- **Source**: #1035 acceptance; R-EV068-NF-003

### EV-069 / #1035 follow-on — CA_ECCC validation deepen

- **Mode**: deepen F2/F13; layers 5–6 + TAF product XSD gate
- **Pass criteria**: AC in evolve-decisions §EV-069; TC-EV069-*
- **Source**: [#1035](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1035), [#1033](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1033), [#1032](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1032); EV-069

### TC-EV069-001: All CA stages implemented

- **Level**: T0
- **Objective**: `pending_ca_stages()` empty; registry matches catalog
- **Pass criteria**: `IMPLEMENTED_CA_STAGES == CA_VALIDATION_STAGES`
- **Source**: EV-069 M1

### TC-EV069-002: TAF NCLWS full stack

- **Level**: T0 / T2
- **Objective**: `taf_nclws.golden.xml` passes layers 1–6 under `ca_eccc` + `product=TAF`
- **Pass criteria**: All stage `ok`; `ca_xsd` validates NCLWS global element against `taf-ca.xsd`
- **Source**: EV-069 M2; #1035 TAF acceptance

### TC-EV069-003: code-ca membership gate

- **Level**: T0
- **Objective**: Unknown code-ca href fails at `code_ca` layer only
- **Pass criteria**: `CODE_CA_UNKNOWN` on bad href; known goldens pass
- **Source**: EV-069 M3; #1033

### TC-EV069-004: Layer attribution preserved with full stack

- **Level**: T0
- **Objective**: CA XSD failures still attributed to `ca_xsd`; later stages skipped on error
- **Pass criteria**: Monkeypatched `ca_xsd` failure; no `code_ca` stage appended
- **Source**: EV-069 M4

### EV-070 / #1041 — CA_ECCC TAF + AIRMET convert deepen

- **Mode**: deepen F6/F20/F36; `tac2iwxxm` national mappers
- **Pass criteria**: AC in evolve-decisions §EV-070; TC-EV070-*
- **Source**: [#1041](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1041); EV-069 follow-on

### TC-EV070-001: TAF present_and_forecast_weather encode

- **Level**: T0 / T2
- **Objective**: TAF golden with Canadian forecast weather encodes `code-ca/present_and_forecast_weather/` href
- **Pass criteria**: Convert matches golden; `code_ca` layer passes
- **Source**: EV-070 M1; #1041 TAF

### TC-EV070-002: TAF MANAIR amendment slice

- **Level**: T2
- **Objective**: At least one amendment/corrected TAF golden converts and validates
- **Pass criteria**: Layered `ca_eccc` layers 1–6 pass
- **Source**: EV-070 M1; #1041 TAF

### TC-EV070-003: AIRMET GFA structured fields

- **Level**: T0 / T2
- **Objective**: SFC_VIS* phenomenon golden includes `surfaceVisibility` / `cloudBase` / `surfaceWindSpeed` where applicable
- **Pass criteria**: Golden diff stable; `airmet-ca.xsd` layer passes
- **Source**: EV-070 M2; #1041 AIRMET

### TC-EV070-004: AIRMET phenomenon vocabulary

- **Level**: T0
- **Objective**: Root `phenomenon` xlink uses `airmet_weather_phenomena/` code-ca path
- **Pass criteria**: `code_ca` membership passes; unknown code fails closed
- **Source**: EV-070 M2

### TC-EV070-005: Convert → validate round-trip

- **Level**: T2
- **Objective**: All new EV-070 goldens convert then pass full `ca_eccc` stack
- **Pass criteria**: `report.valid` and per-stage `ok` for layers 1–6
- **Source**: EV-070 M3; FR6

### TC-EV070-006: Manifest rule_id promotion

- **Level**: T0
- **Objective**: New cases in `manifest.json` with `status: active` and unique `rule_id`
- **Pass criteria**: `test_tc_ev064_002` parametrization includes new case ids
- **Source**: EV-070 M3

### EV-071 / #1038 + #1032 + #1040 — CA_ECCC lint pack + exchange output (METAR)

- **Mode**: deepen F15/F6/F36; national lint pack + operational packaging
- **Pass criteria**: AC in evolve-decisions §EV-071; TC-EV071-*
- **Source**: [#1038](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1038),
  [#1032](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1032),
  [#1040](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1040); EV-070 follow-on

### TC-EV071-001: CA lint pack — ≥10 rules with fixtures

- **Level**: T0
- **Objective**: `profile=ca_eccc` lint returns ≥10 distinct CA rule codes on fixture matrix
- **Pass criteria**: Each code has accept/negative fixture; registry + catalog in sync
- **Source**: EV-071 M1; #1038

### TC-EV071-002: Profile isolation CA vs US

- **Level**: T0
- **Objective**: Same TAC under `ca_eccc` vs `iwxxm_us` emits profile-appropriate codes only
- **Pass criteria**: No cross-profile CA/US rule bleed
- **Source**: EV-071 M1; #1038 acceptance

### TC-EV071-003: API pre-convert CA lint wire

- **Level**: T2
- **Objective**: Convert with `semantic_profile=CA_ECCC` runs CA TAC lint before convert
- **Pass criteria**: Lint issues include CA codes when applicable TAC supplied
- **Source**: EV-071 M1; FR-L6

### TC-EV071-004: Quality matrix METAR (CA) rows

- **Level**: T0
- **Objective**: Quality matrix includes CA lint rows with working catalog links
- **Pass criteria**: Matrix CI passes; source links resolve
- **Source**: EV-071 M1; #1038

### TC-EV071-005: MSC METAR filename pattern

- **Level**: T0 / T2
- **Objective**: Convert/package with `CA_ECCC` emits `A_{TTAAiiCCCCYYGGggBBB}_C_{CCC}_{YYYYMMddhhmmss}.xml`
- **Pass criteria**: Filename matches mining/datamart pattern for METAR golden
- **Source**: EV-071 M2; #1032 acceptance

### TC-EV071-006: WMO header METAR (`A_LACN`)

- **Level**: T0
- **Objective**: CA profile validates METAR WMO header designator
- **Pass criteria**: Layer-6 exchange check passes; wrong designator fails closed
- **Source**: EV-071 M2; #1032

### TC-EV071-007: Translation centre metadata golden

- **Level**: T0 / T2
- **Objective**: CA convert populates translation centre attrs when profile requires
- **Pass criteria**: Golden XML includes configured translation metadata elements
- **Source**: EV-071 M2; #1040

### TC-EV071-008: API convert output spec exposure

- **Level**: T2
- **Objective**: Convert response includes operator-visible profile output spec fields
- **Pass criteria**: OpenAPI + integration test; no internal doc refs in strings
- **Source**: EV-071 M2; #1032 FR-E6

### TC-EV071-009: Datamart fixture round-trip

- **Level**: T2
- **Objective**: Operational datamart sample round-trips naming + header checks
- **Pass criteria**: Filename, header, and layer-6 validate pass on fixture
- **Source**: EV-071 M2; #1032 acceptance

### EV-072 / #1032 residual + #1036 — CA_ECCC exchange aerodrome products + ops corpus

- **Mode**: deepen F36/F6; complete exchange output + operational fixtures
- **Pass criteria**: AC in evolve-decisions §EV-072; TC-EV072-*
- **Source**: EV-071 deferred; [#1036](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1036)

### TC-EV072-001: SPECI exchange output (`A_LPCN`)

- **Level**: T0 / T2
- **Objective**: CA_ECCC SPECI convert returns MSC filename + `A_LPCN` WMO header in output_spec
- **Pass criteria**: Layer-6 validate passes; wrong designator fails closed
- **Source**: EV-072 M1; #1032 residual

### TC-EV072-002: TAF exchange output (`A_LTCN`)

- **Level**: T0 / T2
- **Objective**: CA_ECCC TAF convert returns MSC filename + `A_LTCN` WMO header in output_spec
- **Pass criteria**: Layer-6 validate passes; distribution path segment `taf`
- **Source**: EV-072 M1; #1032 residual

### TC-EV072-003: AIRMET exchange output (`A_LWCN`)

- **Level**: T0 / T2
- **Objective**: CA_ECCC AIRMET convert returns MSC filename + `A_LWCN` WMO header in output_spec
- **Pass criteria**: Layer-6 validate passes; distribution path segment `airmet`
- **Source**: EV-072 M1; #1032 residual

### TC-EV072-004: Layer-6 goldens per aerodrome product

- **Level**: T0
- **Objective**: `validate_ca_exchange_packaging` parametrized for METAR/SPECI/TAF/AIRMET goldens
- **Pass criteria**: Each product has accept/negative packaging fixture
- **Source**: EV-072 M1

### TC-EV072-005: API output_spec SPECI/TAF/AIRMET

- **Level**: T2
- **Objective**: `/api/v1/convert` with `semantic_profile=CA_ECCC` returns populated output_spec per product
- **Pass criteria**: No internal doc refs; product-appropriate designator and filename
- **Source**: EV-072 M1; FR-X6

### TC-EV072-006: Catalog exchange_output all products

- **Level**: T0
- **Objective**: `catalog.yaml` CA_ECCC exchange_output documents all four aerodrome products
- **Pass criteria**: No `ev071_slice`-only marker; docs match `exchange_output.py`
- **Source**: EV-072 M1; FR-X8

### TC-EV072-007: Ops harvest script pin-date reproducibility

- **Level**: T1
- **Objective**: Harvest script fetches MSC datamart tree for pin date without live CI dependency
- **Pass criteria**: Script documents rate limit + pin; manifest checksum stable
- **Source**: EV-072 M2; #1036

### TC-EV072-008: Ops METAR fixture count

- **Level**: T0
- **Objective**: ≥5 METAR ops fixtures under `CA_ECCC/METAR/ops/` in manifest
- **Pass criteria**: Manifest `tier: wmoReference`; CI collects fixtures
- **Source**: EV-072 M2; #1036 acceptance

### TC-EV072-009: Ops SPECI/TAF/AIRMET fixture counts

- **Level**: T0
- **Objective**: ≥2 ops fixtures each for SPECI, TAF, AIRMET
- **Pass criteria**: Manifest entries + layer-6 packaging check or documented waiver
- **Source**: EV-072 M2; #1036 acceptance

### TC-EV072-010: Ops IWXXM packaging checks

- **Level**: T2
- **Objective**: Ops IWXXM samples pass layer-6 filename/header checks where attrs present
- **Pass criteria**: Pass or explicit waiver row in manifest notes
- **Source**: EV-072 M2; FR-O5

### EV-073 / #1032 COLLECT + #1042 — CA_ECCC envelope + profile wiring

- **Mode**: deepen F36/F6/F7; COLLECT wrap + operator profile/extension wiring
- **Pass criteria**: AC in evolve-decisions §EV-073; TC-EV073-*
- **Source**: EV-072 deferred; [#1042](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1042)

### TC-EV073-001: COLLECT wrap idempotency

- **Level**: T0
- **Objective**: `wrap_ca_eccc_collect` returns input unchanged when already COLLECT
- **Source**: EV-073 M1

### TC-EV073-002: MSC bulletinIdentifier

- **Level**: T0
- **Objective**: Wrapped output sets `collect:bulletinIdentifier` to MSC filename from AHL
- **Source**: EV-073 M1; #1032

### TC-EV073-003: Inner product round-trip

- **Level**: T0
- **Objective**: `extract_iwxxm_from_collect(wrap(product))` equals inner product XML
- **Source**: EV-073 M1

### TC-EV073-004: Ops fixture shell parity

- **Level**: T2
- **Objective**: Single-member ops fixtures match COLLECT shell structure after wrap
- **Source**: EV-073 M1; FR-O5

### TC-EV073-005: Convert COLLECT output mode

- **Level**: T2
- **Objective**: CA_ECCC convert with packaging flag returns COLLECT-wrapped XML
- **Source**: EV-073 M1; FR-X6

### TC-EV073-006: FE IWXXM_CA auto-wire

- **Level**: T2
- **Objective**: Selecting `ca_eccc` sends `extensions=IWXXM_CA` on convert/validate
- **Source**: EV-073 M2; #1042

### TC-EV073-007: Profile metadata surfacing

- **Level**: T2
- **Objective**: UI shows IWXXM 3.0.0 pin + extension label when CA_ECCC selected
- **Source**: EV-073 M2; #1042

### TC-EV073-008: Fail-closed vendor pin

- **Level**: T2
- **Objective**: Missing CA vendor bundle blocks convert with operator help
- **Source**: EV-073 M2; #1042

### TC-EV073-009: E2E CA_ECCC convert + validate

- **Level**: T4 / H6
- **Objective**: Select CA_ECCC → convert Canadian METAR → validate pass with ca_xsd
- **Source**: EV-073 M2; #1042 acceptance

### EV-074 / #1043 — CA_ECCC SIGMET + VAA validate-first ops

- **Mode**: deepen F23/F26/F36; datamart ops IWXXM + WMO 3.0.0 validate; no TAC convert
- **Pass criteria**: AC in evolve-decisions §EV-074; TC-EV074-*
- **Source**: [#1043](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1043); playbook #1044 type P

### TC-EV074-001: Harvest script SIGMET/VAA pin URLs

- **Level**: T0
- **Objective**: Harvest plan includes SIGMET and VAA datamart entries; CI uses committed fixtures only
- **Source**: EV-074 M1; REQ-EV074-M1-001

### TC-EV074-002: Ops SIGMET fixture count

- **Level**: T1
- **Objective**: Manifest contains ≥2 SIGMET ops IWXXM; kinds recorded
- **Source**: EV-074 M1; REQ-EV074-M1-002

### TC-EV074-003: Ops VAA fixture count

- **Level**: T1
- **Objective**: Manifest VAA ≥1 Montreal VAAC TAC ops fixture; `vaa_harvest=vaac_tac_waived` (D-EV074-vaa-waiver-tac). Target ≥2 when VAAC 31-day index publishes more. Do not silent-fill encoder VAA.
- **Source**: EV-074 M1; EV-077; D-EV074-vaa-waiver-tac

### TC-EV074-004: SIGMET WMO 3.0.0 under CA profile

- **Level**: T1
- **Objective**: Harvested SIGMET fixtures pass wellformed + WMO 3.0.0 XSD+Schematron with `semantic_profile=CA_ECCC`
- **Source**: EV-074 M2; REQ-EV074-M2-001

### TC-EV074-005: VAA VAAC TAC validate-first

- **Level**: T1
- **Objective**: Montreal VAAC TAC ops fixtures pass annex3 VAA lint; IWXXM exchange packaging N/A (no datamart vaa/)
- **Source**: EV-077; D-EV074-vaa-waiver-tac

### TC-EV074-011: VAA VAAC TAC lint green

- **Level**: T1
- **Objective**: Each manifest VAA `ops_tac` passes `tac_validate.lint(product=VAA)` with no errors
- **Source**: EV-077; TC-EV074-005

### TC-EV074-006: ca_xsd skipped not-applicable

- **Level**: T0
- **Objective**: SIGMET/VAA CA layered validate skips `ca_xsd` as not-applicable (no `CA_PRODUCT_XSD_NOT_FOUND` error); mapped aerodrome products still fail-closed if XSD file missing
- **Source**: EV-074 M2; REQ-EV074-M2-002

### TC-EV074-007: Catalog lists SIGMET/VAA

- **Level**: T0
- **Objective**: `catalog.yaml` CA_ECCC products include SIGMET and VAA with validate-first status
- **Source**: EV-074 M2; REQ-EV074-M2-004

### TC-EV074-008: Coverage matrix CA SIGMET/VAA row

- **Level**: T0
- **Objective**: Coverage matrix documents validate-first ops slice + #1033 note-only
- **Source**: EV-074 M2; REQ-EV074-M2-004

### TC-EV074-009: Aerodrome CA regression

- **Level**: T1
- **Objective**: METAR/SPECI/TAF/AIRMET CA convert, exchange, COLLECT, and layered validate remain green
- **Source**: EV-074 M2; REQ-EV074-M2-005

### TC-EV074-010: code-ca SIGMET note-only

- **Level**: T0
- **Objective**: Catalog/coverage notes #1033 investigation without shipping SIGMET `code-ca` rules
- **Source**: EV-074; D-EV074-1033

### EV-075 / #1032 — CA_ECCC umbrella closeout audit

- **Mode**: doc audit + regression gate; no product code unless drift
- **Pass criteria**: AC in evolve-decisions §EV-075; TC-EV075-*
- **Source**: [#1032](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1032) (verify close); EV-071..074 on `stage`

### TC-EV075-001: #1032 aerodrome exchange output regression

- **Level**: T0
- **Objective**: TC-EV071-005..009 + TC-EV072-001..006 green on branch
- **Pass criteria**: All exchange-output tests pass; catalog `ev072_slice` documents four aerodrome products
- **Source**: EV-075 REQ-EV075-001

### TC-EV075-002: COLLECT + ops corpus regression

- **Level**: T0
- **Objective**: TC-EV073-001..005 + TC-EV072-007..010 green
- **Pass criteria**: COLLECT wrap + ops manifest counts unchanged
- **Source**: EV-075 REQ-EV075-002..003

### TC-EV075-003: SIGMET validate-first + waived residuals documented

- **Level**: T0 / docs
- **Objective**: TC-EV074-001..010 green; catalog/coverage note SIGMET/VAA exchange emit waived → #1061
- **Pass criteria**: `ev074_validate_first` documented; VAA harvest waiver cited
- **Source**: EV-075 REQ-EV075-004..005

### TC-EV075-004: Standing docs parity

- **Level**: Docs
- **Objective**: `catalog.yaml`, `COVERAGE_MATRIX.md`, `CA_ECCC.md`, `evolve-decisions.md` §EV-075 aligned
- **Pass criteria**: No stale “#1032 open” rows; acceptance checklist updated
- **Source**: EV-075 NFR-EV075-001

### EV-076 / #1061 — CA_ECCC SIGMET exchange output emit

- **Mode**: delta deepen F36 exchange output
- **Pass criteria**: AC in evolve-decisions §EV-076; TC-EV1061-*
- **Source**: [#1061](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1061); split from #1032 / EV-075

### TC-EV1061-001: Catalog SIGMET exchange slice

- **Level**: T0 / docs
- **Objective**: `ev076_slice: [SIGMET]`; VAA remains `ev074_validate_first`
- **Pass criteria**: catalog row matches implementation
- **Source**: EV-076 M2

### TC-EV1061-002: SIGMET WMO header designators

- **Level**: T0
- **Objective**: `A_LSCN` default; VA/TC via `sigmet_kind`
- **Pass criteria**: unit tests green
- **Source**: EV-076 M1

### TC-EV1061-003: Ops MSC filename output spec

- **Level**: T0
- **Objective**: SIGMET ops fixtures expand filename + WMO AHL via `build_ca_eccc_output_spec_from_msc_filename`
- **Pass criteria**: suggested_filename matches datamart source_filename
- **Source**: EV-076 M1

### TC-EV1061-004: SIGMET ops layer-6 packaging

- **Level**: T0
- **Objective**: Ops SIGMET IWXXM passes `validate_ca_exchange_packaging` with MSC context
- **Pass criteria**: no blocking exchange issues; TC-EV072-010 includes SIGMET
- **Source**: EV-076 M1

### EV-079 / #919 — US_FAA_NWS SIGMET/AIRMET national layer (M8)

- **Mode**: parser tokens + profile fixture pack + regression gate
- **Pass criteria**: AC in evolve-decisions §EV-079; TC-EV079-*
- **Source**: [#919](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/919); EV-063 M7 RMK matrix prior

### TC-EV079-001: SIGMET/AIRMET manifest rows

- **Level**: T0
- **Objective**: `fixtures/profiles/US_FAA_NWS/manifest.json` lists ≥2 SIGMET + ≥3 AIRMET with `US.*` rule ids
- **Pass criteria**: `test_tc_ev079_us_sigmet_airmet.py::test_tc_ev079_001_*`
- **Source**: EV-079 REQ-EV079-001

### TC-EV079-002: SIGMET phenomenon tokens

- **Level**: T1
- **Objective**: OBSC TS + SEV ICE parse to `OBSC_TS` / `SEV_ICE`; FL band geometry on SEV ICE
- **Pass criteria**: `test_tc_ev079_002_*`
- **Source**: EV-079 REQ-EV079-002

### TC-EV079-003: AIRMET US phenomenon tokens

- **Level**: T1
- **Objective**: IFR → `SFC_VIS`; MOD TURB → `MOD_TURB`; ISOL TS unchanged
- **Pass criteria**: `test_tc_ev079_003_*`
- **Source**: EV-079 REQ-EV079-003

### TC-EV079-004: SIGMET/AIRMET M-golden convert

- **Level**: T1
- **Objective**: `US_FAA_NWS` convert matches profile goldens; `iwxxm-us` namespace present
- **Pass criteria**: `test_tc_ev079_004_*`
- **Source**: EV-079 REQ-EV079-004

### EV-080 / #919 — US_FAA_NWS SIGMET VOR reference geometry (M9)

- **Mode**: `ReferencePointGeometryParser` + bundled VOR table + fixture pack
- **Pass criteria**: AC in evolve-decisions §EV-080; TC-EV080-*
- **Source**: [#919](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/919); EV-079 M8 prior

### TC-EV080-001: VOR offset math

- **Level**: T1
- **Objective**: `offset_nm` moves point north/east as expected
- **Pass criteria**: `test_tc_ev080_001_*`
- **Source**: EV-080 REQ-EV080-003

### TC-EV080-002: VOR chain parse

- **Level**: T1
- **Objective**: `FROM` chain yields closed polygon + `reference_points` audit
- **Pass criteria**: `test_tc_ev080_002_*`
- **Source**: EV-080 REQ-EV080-001

### TC-EV080-003: Unknown VOR fails closed

- **Level**: T1
- **Objective**: `UnknownVOR` raised for absent id
- **Pass criteria**: `test_tc_ev080_003_*`
- **Source**: EV-080 REQ-EV080-002

### TC-EV080-004: VOR fixture convert goldens

- **Level**: T1
- **Objective**: manifest rows convert to profile goldens
- **Pass criteria**: `test_tc_ev080_004_*`
- **Source**: EV-080 REQ-EV080-005

### TC-EV080-005: Bundled VOR table

- **Level**: T1
- **Objective**: EED/BZA/TRM resolve within CONUS bounds
- **Pass criteria**: `test_tc_ev080_005_*`
- **Source**: EV-080 REQ-EV080-002

### EV-081 / #919 — US_FAA_NWS M10–M13 (hazards, WST, VIS, TAF lint)

- **Mode**: iwxxm-us hazard emit + convective SIGMET parse/emit + M7 VIS assert + TAF overlay lint
- **Pass criteria**: AC in evolve-decisions §EV-081; TC-EV081-*
- **Source**: [#919](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/919); EV-080 M9 prior

### TC-EV081-001: AIRMET IFR weather hazards

- **Level**: T1
- **Objective**: IFR AIRMET emits `AIRMETWeatherHazards` with `causingIFRConditions`
- **Pass criteria**: `test_tc_ev081_001_*`
- **Source**: EV-081 REQ-EV081-001

### TC-EV081-002: Convective SIGMET (WST)

- **Level**: T1
- **Objective**: `CONVECTIVE SIGMET` parses and emits `SIGMETWeatherHazards` `AreaTS`
- **Pass criteria**: `test_tc_ev081_002_*`
- **Source**: EV-081 REQ-EV081-002

### TC-EV081-003: US TAF BECMG forbidden

- **Level**: T1
- **Objective**: `iwxxm_us` lint emits `US_TAF_BECMG_FORBIDDEN` for BECMG groups
- **Pass criteria**: `test_tc_ev081_003_*`
- **Source**: EV-081 REQ-EV081-006

### TC-EV081-004: US TAF TEMPO max 4h

- **Level**: T1
- **Objective**: `iwxxm_us` lint emits `US_TAF_TEMPO_MAX_4H` when TEMPO window > 4h
- **Pass criteria**: `test_tc_ev081_004_*`
- **Source**: EV-081 REQ-EV081-007

### TC-EV081-005: Structured visibility fixtures present

- **Level**: T1
- **Objective**: M7 `rmk_sector_vis` / `rmk_tower_vis` / `rmk_var_vis` remain in US_FAA_NWS manifest
- **Pass criteria**: `test_tc_ev081_005_*`
- **Source**: EV-081 REQ-EV081-005

### EV-082 / #919 — US_FAA_NWS M15–M16 (outlook / multi-area AIRMET)

- **Mode**: `OTLK VALID` outlook parse/emit + AND-joined multi-area members
- **Pass criteria**: AC in evolve-decisions §EV-082; TC-EV082-*
- **Source**: [#919](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/919); NWSI 10-811 §7.3 item 10; EV-081 prior

### TC-EV082-001: AIRMET outlook sub-period

- **Level**: T1
- **Objective**: Outlook emits forecast analysis + `validTimeSubPeriod` extension
- **Pass criteria**: `test_tc_ev082_001_*`
- **Source**: EV-082 REQ-EV082-001..005

### TC-EV082-002: Multi-area AIRMET

- **Level**: T1
- **Objective**: AND-joined areas emit multiple `AIRMETEvolvingCondition` members
- **Pass criteria**: `test_tc_ev082_002_*`
- **Source**: EV-082 REQ-EV082-006..007

### TC-EV082-003: EV-081 regression pack

- **Level**: T1
- **Objective**: EV-079..081 SIGMET/AIRMET manifest rows remain green
- **Pass criteria**: `test_tc_ev082_003_*`
- **Source**: EV-082 REQ-EV082-008

### EV-083 / #919 — US_FAA_NWS M17–M18 (CONUS UPDT + FRZLVL forecast)

- **Mode**: CONUS `UPDT` header parse + standalone `FRZLVL...` subsection emit
- **Pass criteria**: AC in evolve-decisions §EV-083; TC-EV083-*
- **Source**: [#919](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/919); NWSI 10-811 Appendix A2.1; EV-082 prior

### TC-EV083-001: CONUS UPDT header + inline FRZLVL

- **Level**: T1
- **Objective**: `AIRMET ZULU UPDT` header populates IR; `BTN FRZLVL` + inline levels emit
- **Pass criteria**: `test_tc_ev083_001_*`
- **Source**: EV-083 REQ-EV083-001..004

### TC-EV083-002: FRZLVL-only subsection

- **Level**: T1
- **Objective**: Standalone `FRZLVL...` emits `FreezingLevelForecast`
- **Pass criteria**: `test_tc_ev083_002_*`
- **Source**: EV-083 REQ-EV083-005..007

### TC-EV083-003: EV-082 regression pack

- **Level**: T1
- **Objective**: EV-079..082 US_FAA_NWS SIGMET/AIRMET manifest rows remain green
- **Pass criteria**: `test_tc_ev083_003_*`
- **Source**: EV-083 REQ-EV083-008

### EV-084 / #919 — US_FAA_NWS M19 (WAUS multi-section AIRMET)

- **Mode**: Full bulletin ICE + VOR `FROM` geometry + inline FRZLVL + `OTLK VALID` + FRZLVL subsection
- **Pass criteria**: AC in evolve-decisions §EV-084; TC-EV084-*
- **Source**: [#919](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/919); NWSI 10-811; EV-083 prior

### TC-EV084-001: WAUS multi-section convert golden

- **Level**: T1
- **Objective**: One bulletin emits polygon geometry, outlook member, and `FreezingLevelForecast`
- **Pass criteria**: `test_tc_ev084_001_*`
- **Source**: EV-084 REQ-EV084-001..004

### TC-EV084-002: VOR TO-chain parser

- **Level**: T1
- **Objective**: `FROM … TO …` chains and missing WSW cardinal coverage
- **Pass criteria**: `test_tc_ev084_002_*`
- **Source**: EV-084 REQ-EV084-005

### TC-EV084-003: EV-083 regression pack

- **Level**: T1
- **Objective**: EV-079..083 manifest rows remain green (incl. updated `airmet_zulu_updt_ice` geometry)
- **Pass criteria**: `test_tc_ev084_003_*`
- **Source**: EV-084 REQ-EV084-006

### EV-078 / #916 — CA_ECCC P1 closeout audit

- **Mode**: doc audit + regression gate; no product code unless drift
- **Pass criteria**: AC in evolve-decisions §EV-078; TC-EV078-*
- **Source**: [#916](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/916) (verify close); EV-071..077 on `stage`

### TC-EV078-001: SIGMET exchange + catalog slices documented

- **Level**: T0 / docs
- **Objective**: `ev076_slice: [SIGMET]`; `ev074_validate_first: [VAA]`; VAAC harvest script cited
- **Pass criteria**: catalog row matches EV-076/077 implementation
- **Source**: EV-078 REQ-EV078-001

### TC-EV078-002: VAA TAC + AIRMET ops regression

- **Level**: T1
- **Objective**: ≥1 VAA `ops_tac`; ≥4 AIRMET datamart ops; `vaa_harvest=vaac_tac_waived`
- **Pass criteria**: manifest fixtures on disk
- **Source**: EV-078 REQ-EV078-002

### TC-EV078-003: Coverage matrix residuals waived

- **Level**: T0 / docs
- **Objective**: X6 SIGMET emit met; X7 VAA emit waived; S2 EV-077 cited
- **Pass criteria**: `COVERAGE_MATRIX.md` acceptance checklist current
- **Source**: EV-078 REQ-EV078-003

### TC-EV078-004: Standing docs parity post EV-077

- **Level**: Docs
- **Objective**: `feature-list.md`, `CA_ECCC.md`, `evolve-decisions.md` §EV-078 aligned; no stale bare “VAA harvest deferred”
- **Pass criteria**: EV-077 / waiver cited; #916 closeout recorded
- **Source**: EV-078 NFR-EV078-001

### EV-063 / F35–F36 — Semantic vs exchange profiles (#912)

- **Mode**: new F35/F36; amends F6 wire
- **Pass criteria**: AC in evolve-decisions §EV-063; UJ-069; TC-EV063-*
- **Source**: [#912](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/912),
  [#914](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/914),
  [#1025](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1025); ADR-036

### TC-EV063-001: Alias annex3 ≡ ICAO_2025 convert parity

- **Level**: T0 / T2 / T3
- **Objective**: `annex3` alias produces same IWXXM as pre-migration goldens
- **Pass criteria**: Golden diff empty under defaults; deprecation signal present when implemented
- **Source**: UJ-069; FR-03; A1

### TC-EV063-002: US_FAA_NWS ≡ iwxxm_us RMK semantics

- **Level**: T0 / T2
- **Objective**: Canonical `US_FAA_NWS` matches current `iwxxm_us` RMK behavior
- **Pass criteria**: Existing iwxxm_us METAR RMK fixtures green
- **Source**: UJ-069; A2; #919

### TC-EV063-003: Unknown semantic or exchange profile → 400

- **Level**: T2 / T3
- **Objective**: Hard fail on invalid ids
- **Pass criteria**: `invalid_profile` or successor codes; no 5xx
- **Source**: UJ-069; FR-06

### TC-EV063-004: Exchange packaging default GLOBAL_AFS

- **Level**: T2
- **Objective**: Package path without explicit exchange profile uses `GLOBAL_AFS`
- **Pass criteria**: Deterministic packaging test artifact; no live sink
- **Source**: UJ-069; A4; #921

### TC-EV063-005: Exchange profile ≠ dissemination credentials

- **Level**: T0 / T2
- **Objective**: Selecting exchange profile does not persist or require BYOC secrets
- **Pass criteria**: F16–F19 regression suite green; explicit negative test in Spec/Build
- **Source**: UJ-069; A5; ADR-021/029

### TC-EV063-006: Profile id metrics + alias counters (Build)

- **Level**: T2 / observability
- **Objective**: Metrics emitted for semantic/exchange ids and alias use
- **Pass criteria**: Contract documented; smoke assert in integration test when implemented
- **Source**: EV-063 observability; NFR observability skill

### EV-065 / #921 — GLOBAL_AFS closure + APAC_ROBEX stub

- **Mode**: delta deepen F36 exchange overlays
- **Pass criteria**: TC-EV065-001..003; catalog + GLOBAL_AFS.md status updated
- **Source**: [#921](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/921); EV-065

### TC-EV065-001: GLOBAL_AFS fixture COLLECT golden

- **Level**: T0 / T2
- **Objective**: Profile fixture under `profiles/GLOBAL_AFS/` produces deterministic COLLECT wrap
- **Pass criteria**: `is_collect_bulletin`; `bulletinIdentifier` present
- **Source**: EV-065; FR-EV065-01

### TC-EV065-002: APAC_ROBEX registry + packaging stub

- **Level**: T0 / T2
- **Objective**: `APAC_ROBEX` resolves and COLLECT-wraps member IWXXM
- **Pass criteria**: Registry includes wire + canonical; packaging test green
- **Source**: EV-065; FR-EV065-02

### TC-EV065-003: convert-bulletin APAC_ROBEX API wire

- **Level**: T2 / T3
- **Objective**: `POST /api/v1/convert-bulletin` with `exchange_profile=APAC_ROBEX` returns COLLECT XML
- **Pass criteria**: HTTP 200; `exchange_profile` echoed; COLLECT root in result
- **Source**: EV-065; UJ-069

### EV-086 / #921 — EUR_RODEX + AFI + CAR_SAM stubs

- **Mode**: delta deepen F36 exchange overlays
- **Pass criteria**: TC-EV086-001..004; catalog + exchange stub docs
- **Source**: [#921](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/921); EV-086

### TC-EV086-001: Registry resolves regional stubs

- **Level**: T0 / T2
- **Objective**: `EUR_RODEX`, `AFI`, `CAR_SAM` resolve (wire + canonical)
- **Pass criteria**: `known_exchange_profile_ids` contains all three; `resolve_exchange_profile` non-None
- **Source**: EV-086; UJ-069

### TC-EV086-002: Packaging COLLECT for each stub

- **Level**: T0 / T2
- **Objective**: Each stub COLLECT-wraps member IWXXM via GLOBAL_AFS baseline
- **Pass criteria**: `is_collect_bulletin`; `bulletinIdentifier` preserved
- **Source**: EV-086; FR-EV086-01

### TC-EV086-003: Unknown exchange fail-closed

- **Level**: T0 / T2
- **Objective**: Garbage exchange id still rejected
- **Pass criteria**: `ValueError` from packaging / API 400
- **Source**: EV-086; ADR-036

### TC-EV086-004: EV-065 regression

- **Level**: T0 / T2
- **Objective**: GLOBAL_AFS + APAC_ROBEX paths unchanged
- **Pass criteria**: TC-EV065-001..002 green
- **Source**: EV-086

### EV-090 / #921+#913+#1024 — Exchange mining deepen + light picker

- **Mode**: delta deepen F36 exchange overlays + F7 light UI
- **Pass criteria**: TC-EV090-001..005; catalog/stub provenance deltas; UJ-069 FE steps
- **Source**: [#921](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/921), [#913](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/913), [#1024](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1024); EV-090; ADR-036

### TC-EV090-001: Catalog provenance for regional exchange stubs

- **Level**: T0
- **Objective**: Each exchange id (`GLOBAL_AFS`, `APAC_ROBEX`, `EUR_RODEX`, `AFI`, `CAR_SAM`) has promoted mining_notes and/or shared OPMET Guidelines source; ROBEX handbook durable file remains an explicit gap if unpinned
- **Pass criteria**: `catalog.yaml` + stub Owns/Gaps match; PROVENANCE_MAP digs where tickets apply
- **Source**: EV-090; D-EV090-req 2a; #913

### TC-EV090-002: Workbench Exchange profile control

- **Level**: T0 / T2 (browser unit)
- **Objective**: Labeled Exchange profile select lists registered ids; default `GLOBAL_AFS`; accessible name distinct from semantic Profile
- **Pass criteria**: `data-testid` exchange select visible; options include regional stubs; plain-language help without internal doc refs
- **Source**: EV-090; #1024; UJ-069; D-EV090-ui

### TC-EV090-003: FE sends exchange_profile on package/bulletin path

- **Level**: T0 / T2 (browser unit)
- **Objective**: Selecting a non-default exchange id sends `exchange_profile` on convert-bulletin / packaging request; convert-only path does not invent credentials
- **Pass criteria**: Form/JSON field matches API contract; unknown id rejected by API (existing fail-closed)
- **Source**: EV-090; api-contract; UJ-069

### TC-EV090-004: H4–H5 connectivity for exchange picker

- **Level**: T3 / H4–H5
- **Objective**: Live or staging workbench can select exchange overlay and complete package path without CORS failure
- **Pass criteria**: Connectivity gate scripts / Playwright e2e green for UJ-069 FE
- **Source**: EV-090; connectivity-gates; D-EV090-routing

### TC-EV090-005: EV-086 packaging regression

- **Level**: T0 / T2
- **Objective**: COLLECT baseline for all regional stubs unchanged
- **Pass criteria**: TC-EV086-001..004 green
- **Source**: EV-090

### EV-093 / #1024 — Semantic light picker deepen

- **Mode**: delta deepen F7/F35 FE semantic Profile wire + nationals
- **Pass criteria**: TC-EV093-001..006; UJ-069 FE semantic steps; preserve TC-EV060/064/090/091
- **Source**: [#1024](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1024); EV-093; ADR-036; D-EV093-*

### TC-EV093-001: Profile options = all canonicals + aliases

- **Level**: T0 / T2 (browser unit)
- **Objective**: `profile-type-select` lists `ICAO_2025`, `US_FAA_NWS`, `CA_ECCC`, `AU_BOM`,
  `NZ_CAA_MET`, thin packs, plus legacy `annex3` / `iwxxm_us`; default `ICAO_2025`
- **Pass criteria**: Options + default match FR-01/FR-02/FR-04; accessible name distinct from Exchange
- **Source**: EV-093; D-EV093-g2; UJ-069

### TC-EV093-002: FE sends semantic_profile uppercase

- **Level**: T0 / T2
- **Objective**: Convert / convert-bulletin FormData appends `semantic_profile` with uppercase
  OpenAPI ids (e.g. `ICAO_2025`), not only deprecated `profile=`
- **Pass criteria**: Client unit asserts field + value; API accepts
- **Source**: EV-093; D-EV093-wire; api-contract

### TC-EV093-003: Legacy aliases still convert

- **Level**: T0 / T2
- **Objective**: Selecting `annex3` or `iwxxm_us` resolves and converts; coerce helpers map stored prefs
- **Pass criteria**: Alias options present; convert path green; no unknown-profile 400
- **Source**: EV-093; #1025 window; FR-02

### TC-EV093-004: CA_ECCC pin / metadata unchanged

- **Level**: T0 / T2
- **Objective**: Choosing `CA_ECCC` still pins IWXXM 3.0.0, sends `IWXXM_CA` extensions, shows metadata / block notice
- **Pass criteria**: TC-EV064-005 behavior preserved under new option value
- **Source**: EV-093; FR-05

### TC-EV093-005: Profile trust copy

- **Level**: T0 / T2
- **Objective**: Plain-language Profile/Exchange trust model without bloating the control bar: (A) help icons + tooltips on Profile and Exchange labels; (B) one short always-visible summary under the bar; (C) collapsed “What’s this?” details with full copy (not destinations/credentials; not editable overlays)
- **Pass criteria**: `product-profile-bar` contains controls only (no help paragraphs); summary + details `data-testid`s present; full help visible after expand; no internal doc refs (EV-048)
- **Source**: EV-093; FR-06; #924; D-EV093-trust-layout

### TC-EV093-006: H4–H5 / e2e UJ-069 semantic + exchange

- **Level**: T3 / H4–H5
- **Objective**: Playwright (or live connectivity) selects canonical Profile + Exchange and completes convert/package path
- **Pass criteria**: Extend `tc-ev090-uj069-exchange-picker` or sibling TC-EV093 e2e green
- **Source**: EV-093; connectivity-gates; UJ-069

### EV-087 / #917+#918 — AU_BOM + NZ_CAA_MET P1 kickoff

- **Mode**: delta deepen F36 semantic nationals
- **Pass criteria**: TC-EV087-001..006; catalog P1 + stubs + mining notes; D-EV087-* locked
- **Source**: [#917](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/917), [#918](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/918); EV-087; ADR-036

### TC-EV087-001: Registry resolves AU_BOM and NZ_CAA_MET

- **Level**: T0 / T2
- **Objective**: Canonical wire ids resolve to emit keys `au_bom` / `nz_caa_met`
- **Pass criteria**: `resolve_semantic_profile` non-None; `known_semantic_profile_ids` contains both
- **Source**: FR-EV087-01; UJ-069

### TC-EV087-002: AU INTER parsed distinct from TEMPO

- **Level**: T0 / T2
- **Objective**: Under `AU_BOM`, `INTER` is a distinct IR change-group
- **Pass criteria**: Fixture with INTER does not collapse to TEMPO-only AST; `rule_id` AU.TAF.INTER
- **Source**: FR-EV087-02; D-EV087-inter-emit

### TC-EV087-003: AU INTER emit policy (no invented enum)

- **Level**: T0 / T2
- **Objective**: Converted IWXXM uses `TEMPORARY_FLUCTUATIONS` and preserves INTER provenance
- **Pass criteria**: No `changeIndicator="INTER"`; remarks/diagnostics/humanReadable retain INTER; XSD-valid under core pin
- **Source**: FR-EV087-03; D-EV087-inter-emit

### TC-EV087-004: AU TAF3 RMK flag

- **Level**: T0 / T2
- **Objective**: `TAF3` / `TAF3 VALID TL` detected under `product=TAF`
- **Pass criteria**: Profile flag / IR field set; API product remains TAF
- **Source**: FR-EV087-04; D-EV087-taf3

### TC-EV087-005: NZ domestic vs international TAF fixtures

- **Level**: T0 / T2
- **Objective**: Domestic extras parsed; international path remains Annex 3-shaped
- **Pass criteria**: ≥1 domestic + ≥1 international fixture; extras in IR and/or remarks
- **Source**: FR-EV087-06..07; D-EV087-nz-domestic

### TC-EV087-006: Unknown semantic profile fail-closed

- **Level**: T0 / T2
- **Objective**: Garbage semantic id still rejected after AU/NZ registration
- **Pass criteria**: API 400 / library reject; ICAO/US/CA paths unchanged
- **Source**: FR-EV087-01; ADR-036

### EV-088 / #1044 — National profile onboarding playbook

- **Mode**: engineering enablement (docs + scaffold; no #920/#921 feature content)
- **Pass criteria**: TC-EV088-001..006; playbook + `_template/`; ADR-036/README links
- **Source**: [#1044](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1044); EV-088; ADR-036

### TC-EV088-001: Playbook lists issue types A–P

- **Level**: T0 / Docs
- **Objective**: `NATIONAL_PROFILE_PLAYBOOK.md` documents child types A–P
- **Pass criteria**: Each `| A |` … `| P |` row present
- **Source**: #1044 §8

### TC-EV088-002: Template stubs present

- **Level**: T0 / Docs
- **Objective**: `_template/` holds catalog-row, semantic, mining, manifest stubs
- **Pass criteria**: Five required template files on disk
- **Source**: #1044 deliverables

### TC-EV088-003: Catalog YAML parses

- **Level**: T0
- **Objective**: `catalog.yaml` remains valid machine index
- **Pass criteria**: YAML loads; `CA_ECCC` and `ICAO_2025` present
- **Source**: [Corpus: domain-profiles]

### TC-EV088-004: README and ADR-036 link playbook

- **Level**: T0 / Docs
- **Objective**: Standing docs discoverable from hub + ADR
- **Pass criteria**: Playbook filename cited in README and ADR-036
- **Source**: #1044 AC

### TC-EV088-005: Scaffold dry-run

- **Level**: T0
- **Objective**: `scaffold_national_profile.py --dry-run` prints checklist without writes
- **Pass criteria**: Exit 0; checklist mentions `profile_registry.py`; no new semantic stub file
- **Source**: EV-088 Build M2

### TC-EV088-006: Scaffold rejects bad id

- **Level**: T0
- **Objective**: Malformed `--id` fails closed
- **Pass criteria**: Exit 2; stderr error
- **Source**: EV-088 Build M2

### EV-089 / #920 — Thin/compat national packs

- **Mode**: delta F36 — thin/compat semantic packs via EV-088 playbook thin path
- **Pass criteria**: TC-EV089-001..007; six catalog rows + stubs; GAMET parse-only spike; UK first Build PR
- **Source**: [#920](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/920); EV-089; ADR-036; [GAMET-spike.md](domain/profiles/GAMET-spike.md)

### TC-EV089-001: Catalog lists six #920 profile ids

- **Level**: T0 / Docs
- **Objective**: `catalog.yaml` contains UK_METOFFICE, BR_DECEA, KR_KMA, JP_JMA, IN_IMD, HK_HKO
- **Pass criteria**: YAML loads; each id `kind: semantic` and `issue: "#920"`
- **Source**: FR-EV089-01

### TC-EV089-002: Semantic stubs present

- **Level**: T0 / Docs
- **Objective**: `docs/domain/profiles/semantic/<ID>.md` exists for each #920 id
- **Pass criteria**: Six stub files on disk
- **Source**: FR-EV089-02

### TC-EV089-003: GAMET spike is parse-only

- **Level**: T0 / Docs
- **Objective**: Standing GAMET disposition forbids IWXXM emit
- **Pass criteria**: `GAMET-spike.md` states parse-only; no convert product enum for GAMET
- **Source**: D-EV089-gamet

### TC-EV089-004: Scaffold dry-run still works after #920 stubs

- **Level**: T0
- **Objective**: Scaffold checklist for a probe id that is not yet a standing stub
- **Pass criteria**: `scaffold_national_profile.py --id ZZ_SCAFFOLD_PROBE --dry-run` exit 0; no stub written (TC-EV088-005)
- **Source**: EV-088 playbook; FR-EV089-04

### TC-EV089-005: UK_METOFFICE registry + fixture smoke (Build)

- **Level**: T0 / T2
- **Objective**: First shippable thin pack converts METAR/SPECI/TAF under profile id
- **Pass criteria**: Fixtures under `profiles/UK_METOFFICE/`; convert or fixture-load tests green; ICAO/US/CA/AU/NZ unchanged
- **Source**: FR-EV089-02; FR-EV089-10

### TC-EV089-006: Remaining #920 packs smoke (Build, per PR)

- **Level**: T0 / T2
- **Objective**: Each subsequent profile PR adds fixtures + allowlist for its v1 products
- **Pass criteria**: Parameterized tests per id; BR excludes GAMET from convert allowlist
- **Source**: FR-EV089-05; FR-EV089-06

### TC-EV089-007: Unknown semantic id still rejected

- **Level**: T0 / T2
- **Objective**: Garbage semantic id rejected after #920 registration
- **Pass criteria**: API 400 / library reject; existing profiles unchanged
- **Source**: FR-EV089-10; ADR-036

### TC-EV061-1015-001: Promote PR required-check inventory

- **Level**: Docs / CI
- **Objective**: `stage`→`main` required checks include full unit, lint, typecheck, full E2E (not smoke-only), Staging gate
- **Pass criteria**: Names documented in deploy.md; match workflow `name:` fields
- **Source**: #1015; UJ-DEV-009

### TC-EV061-1015-002: Merge blocked when a required check is red/missing

- **Level**: CI
- **Objective**: Promote PR cannot merge without the stricter set
- **Pass criteria**: Branch protection (or equivalent) enforces the documented checks; no new app secrets
- **Source**: #1015; D-S071-ci

### EV-057 / S067 — M0 Ready: apex redirect + accumulate ZIP + validate-only (#948 / #903 / #838)

- **Mode**: delta deepen F7.r / F7.s + F30; F1/F6/F2/F4 notes as applicable
- **Pass criteria**: AC in evolve-decisions §EV-057; TC-EV057-*; **UJ-057** / **UJ-058** /
  **UJ-OPS-002**
- **Source**: [#948](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/948),
  [#903](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/903),
  [#838](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/838); S067 / EV-057

### TC-EV057-948-001: Apex HTTPS redirects to app

- **Level**: T3 / ops
- **Objective**: `https://tac-to-iwxxm.com` permanently redirects to
  `https://app.tac-to-iwxxm.com` (301 or equivalent)
- **Pass criteria**: Live curl/HEAD shows permanent redirect Location to app host
- **Source**: EV-057 #948 AC1; UJ-OPS-002; [Corpus: deploy]

### TC-EV057-948-002: Path and query preserved

- **Level**: T3 / ops
- **Objective**: `/foo?bar=1` on apex redirects to same path+query on app host
- **Pass criteria**: Location includes `/foo?bar=1` on `app.tac-to-iwxxm.com`
- **Source**: EV-057 #948 AC2; `D-S067-948-path=1`

### TC-EV057-948-003: www / HTTP / TLS + docs

- **Level**: T3 / ops / docs
- **Objective**: `www` covered when DNS/cert allows; HTTP ends on HTTPS app; TLS valid;
  deploy.md documents **prod FE Ingress** extension + permanent redirect
  (`D-S067-948-ingress=2a`)
- **Pass criteria**: Checklist in deploy-smoke / ops report; docs section present
- **Source**: EV-057 #948 AC3–AC5

### TC-EV057-903-001: Accumulate N≥2 successes

- **Level**: T0 / T2
- **Objective**: Two sequential successful converts leave both results visible
- **Pass criteria**: Vitest and/or Playwright assert N≥2 result cards after sequential converts
- **Source**: EV-057 #903 AC1; UJ-057

### TC-EV057-903-002: Download all ZIP contents

- **Level**: T0 / T2
- **Objective**: Download all produces one ZIP with one IWXXM per accumulated success
- **Pass criteria**: Unit/e2e asserts ZIP member count and names
- **Source**: EV-057 #903 AC2; UJ-057

### TC-EV057-903-003: Default ZIP stem from first TAC

- **Level**: T0
- **Objective**: Empty custom basename → `{stem}_{yyyyMMddHHmmss}.zip` with ≈8 sanitized
  chars from first success TAC
- **Pass criteria**: Unit test on `outputArchiveName` (or successor) helper
- **Source**: EV-057 #903 AC3; #664; `D-S067-903-stem=1`

### TC-EV057-903-004: Custom basename ZIP

- **Level**: T0
- **Objective**: Custom output name → `{base}.zip`
- **Pass criteria**: Unit test matches #664 rule
- **Source**: EV-057 #903 AC4

### TC-EV057-903-005: Clear + failed convert isolation

- **Level**: T0 / T2
- **Objective**: Clear empties batch; failed convert does not remove prior successes
- **Pass criteria**: Unit/UI tests for clear and failure paths
- **Source**: EV-057 #903 AC5–AC6

### TC-EV057-903-006: UJ-057 H4–H5 / Playwright smoke

- **Level**: T2 / T3 / H4–H5
- **Objective**: Accumulate two converts → Download all → named ZIP; soft cap **≤200**
  (`D-S067-903-cap=1c`) with clear over-cap error
- **Pass criteria**: Playwright green locally/CI; H4–H5 after staging deploy (13)
- **Source**: EV-057 #903 AC7–AC8; UJ-057

### TC-EV057-903-007: Soft accumulate cap ≤200

- **Level**: T0 / T2
- **Objective**: Attempting to accumulate beyond 200 results is blocked with a clear error
- **Pass criteria**: Unit/UI test asserts cap and message
- **Source**: EV-057 #903 AC7; `D-S067-903-cap=1c`

### TC-EV057-838-001: Paste IWXXM validate-only

- **Level**: T0 / T2
- **Objective**: Paste known-good IWXXM and validate without TAC convert
- **Pass criteria**: FE + API test; no convert call required
- **Source**: EV-057 #838 AC1; UJ-058

### TC-EV057-838-002: Upload single XML

- **Level**: T0 / T2
- **Objective**: Upload one `.xml` IWXXM file and show F2 results
- **Pass criteria**: Playwright/Vitest asserts upload → validate results
- **Source**: EV-057 #838 AC2; UJ-058

### TC-EV057-838-003: Broken XML structured fail

- **Level**: T0 / T2
- **Objective**: Invalid / non-IWXXM input returns structured fail (no opaque 5xx)
- **Pass criteria**: Backend/FE assert structured error body
- **Source**: EV-057 #838 AC3

### TC-EV057-838-004: F4 version/profile parity

- **Level**: T0 / T2
- **Objective**: Version/profile controls match convert/validate elsewhere
- **Pass criteria**: UI test asserts shared control behavior
- **Source**: EV-057 #838 AC4; F4

### TC-EV057-838-005: UJ-058 guest + H4–H5 smoke

- **Level**: T2 / T3 / H4–H5
- **Objective**: Guest paste good fixture → pass; broken → structured fail; no Supabase
- **Pass criteria**: Playwright green; H4–H5 after staging deploy (13)
- **Source**: EV-057 #838 AC5–AC6; UJ-058

### Live harness — staging (EV-043 / EV-044)

| Env | API | Frontend |
|-----|-----|----------|
| staging | `https://api.staging.tac-to-iwxxm.com` | `https://app.staging.tac-to-iwxxm.com` |
| prod | `https://api.tac-to-iwxxm.com` | `https://app.tac-to-iwxxm.com` |

CI **Staging smoke** sets `LIVE_API_URL` / `LIVE_FRONTEND_URL` to staging hosts after Deploy
staging. Prod smokes remain Makefile / 13-deploy-smoke against prod hosts.

## S043 / EV-035 — Rule-source provenance (deepen F6 / F12 / F15 / F2)

**No new Fn** (G1=2). Standing provenance map under `docs/domain/rules/` (path-cite; G3=1).
Full stack: ISSUE_CATALOG + encode/SCH + bulletin AHL. **Dense asserts** for every rule
cited or revisited. Raise unfindable sources — do not invent.

### TC-EV035-001: Dig inventory completeness

- **Level**: T0 / CI
- **Objective**: Every `docs/domain/mining/*-mining-notes.md` is indexed and linked from the
  provenance map (or explicitly retired with rationale)
- **Pass criteria**: Parametric assert — one case per dig file; map lists dig path + date mined
  + products/roles touched; orphan digs fail CI
- **Many asserts**: file exists · indexed · non-empty source URL or paywall landing · products
  non-empty · role label valid
- **Source**: S043; [docs/domain/mining/README.md](domain/mining/README.md)

### TC-EV035-002: ISSUE_CATALOG code ↔ provenance

- **Level**: T0 / CI (`tac-validate`)
- **Objective**: Every registry / ISSUE_CATALOG code in scope has a provenance row
- **Pass criteria**: Parametric over all catalog codes — status ∈ {ok, gap, paywall, N/A};
  `ok`/`paywall` rows have cite (RULE_SOURCE_URLS id or URL); `gap` rows have raise ticket /
  session note id; unknown status fails
- **Many asserts**: code present · status valid · cite shape · dig link when mined ·
  consumer ∈ {tac-validate, tac2iwxxm, iwxxm-validate, bulletin, UI-decode}
- **Source**: F15/F12 deepen; ADR-028; ISSUE_CATALOG

### TC-EV035-003: Coverage matrix cell ↔ source URL

- **Level**: T0 / docs CI
- **Objective**: Revisited COVERAGE_MATRIX product×role cells cite a catalog URL or
  explicit ⚠/❌ disposition
- **Pass criteria**: Parametric over F6 products × {validation, conversion, iwxxm-validation,
  bulletin} — no silent blanks; ✅ implies RULE_SOURCE_URLS hit; ⚠/❌ implies gap note
- **Many asserts**: cell parsed · disposition · URL or gap id · gate G1–G7 consistency
- **Source**: F6 deepen; COVERAGE_MATRIX; RULE_SOURCE_URLS

### TC-EV035-004: Encode / SCH / bulletin cite parity (full stack)

- **Level**: T0 / CI
- **Objective**: Encode playbook rules, Schematron assert themes, and AHL/bulletin rules
  revisited this cycle appear in the provenance map with sources
- **Pass criteria**: Inventory of in-scope encode/SCH/AHL rule ids each has provenance;
  SCH asserts cite vendored `rule/iwxxm.sch` pin path; AHL cites WMO AHL + OPMET Guidelines
  or gap
- **Many asserts**: per rule id — role · source · dig · status · pin version when schema
- **Source**: F6/F2 deepen; IWXXM_CONVERSION; IWXXM_VALIDATION; OPMET dig

### TC-EV035-005: Behavioral dense asserts for revisited executable rules

- **Level**: T0 / CI
- **Objective**: Every executable rule cited/revisited has **many** behavioral asserts
  (happy + sad + edge), not a single smoke — prefer F29 matrix slots when available
- **Pass criteria**: For each revisited executable rule_id: ≥3 distinct assert sites
  (or filled F29 happy/sad/edge slots); failures name rule_id in node id
- **Source**: F12/F15/F2/F6; F29 harness patterns; E35-5

### TC-EV035-006: Gap raise gate (no silent invent)

- **Level**: T0 / process CI
- **Objective**: Provenance rows with `gap` are listed in session gap report and raised
- **Pass criteria**: `docs/sessions/S043-rule-source-traceability/reports/provenance-gaps.md`
  exists when any `gap` row present; CI fails if `gap` count > 0 and report missing/stale
- **Source**: Phase 0 — raise unfindable rules to user

### EV-035 verify gate

- [ ] TC-EV035-001..006 green (or gaps explicitly raised + user disposition recorded)
- [ ] No new Fn in feature-list (deepen-only)
- [ ] Domain path-cites only (no CORPUS membership required this cycle)
- [ ] H4–H5 **N/A** (no UI)

## S045 / EV-037 — Matrix dispositions #869 / #870 / #872 (deepen F2 / F6 / F32)

**No new Fn.** Docs + `COVERAGE_MATRIX` / `PROVENANCE_MAP` dispositions for EV-035 remine
residuals. No UI — H4–H5 **N/A**. Corpus: `[Corpus: product]` · `[Corpus: tests]` ·
`[docs/domain/rules/COVERAGE_MATRIX.md]` · `[docs/domain/rules/PROVENANCE_MAP.md]`.

### TC-EV037-001: VONA SoT / Guidance silence (#869)

- **Level**: T0 / docs CI
- **Objective**: VONA conversion is defined without a Guidance section; cookbook is derived
- **Pass criteria**:
  - `COVERAGE_MATRIX` VONA convert cell documents SoT hierarchy (ICAO → FM205 → XSD/SCH →
    AHL → A7-1 → cookbook derived)
  - Guidance silence marked **non-blocking** ⚠ (not “undefined”)
  - Provenance `VONA_GUIDANCE_SILENT` disposition is upstream-gap / non-blocking (not
    encode-blocked); ticket #869 linked
- **Source**: F32 deepen; #869; vona remine dig

### TC-EV037-002: IWXXM-US Schematron N/A (#870)

- **Level**: T0 / docs CI
- **Objective**: Official US Schematron artifact documented **N/A / not published** without
  N/A-ing all US validation
- **Pass criteria**:
  - Validate classes split: WMO XSD ✅ · US XSD ✅ · WMO SCH ✅ · US SCH **N/A** ·
    semantic/fixtures tracked separately
  - Provenance `US_SCH_ABSENT` status ∈ {`N/A`} (not invent-as-gap for a missing official
    artifact the project must author)
  - METAR_US / iwxxm-us validate cell does not imply “entire US validation N/A”
- **Source**: F2 deepen; #870; iwxxm-us pin + NOAA publication

### TC-EV037-003: Bulletin AHL source vs impl columns (#872)

- **Level**: T0 / docs CI
- **Objective**: AHL **source** coverage is ✅ for all WMO-mapped families; impl gaps are
  separate columns / children
- **Pass criteria**:
  - Every family in the eight-family (+ SWXA/VONA) AHL map has `AHL source = ✅`
  - Former single **Bulletin AHL** cell redesigned into:
    `AHL source | T1T2 map | parser | BBB | body splitter | filename | COLLECT | fixtures | CI`
  - Stale `gap` cells that only meant “source missing” are cleared; residual `gap` rows
    name an implementation concern + child issue when still open
- **Source**: F6 deepen; #872; WMO AHL publication; `AHL.asciidoc`

### TC-EV037-004: GitHub ticket disposition closeout

- **Level**: T0 / process
- **Objective**: #869 / #870 / #872 closed or reworded to match locked dispositions; #846 linked
- **Pass criteria**: Issue bodies/comments cite EV-037 ACs; close when matrix+provenance+TCs
  green; children opened only for true #872 impl gaps
- **Source**: Phase 0 Q2; epic #846

### EV-037 verify gate

- [ ] TC-EV037-001..004 green (or disposition recorded)
- [ ] No new Fn in feature-list (deepen F2/F6/F32 only)
- [ ] H4–H5 **N/A** (no UI); deploy 12/13 waive expected
- [ ] Domain path-cites for matrix/provenance updates

## S046 / EV-038 — Epic #846 corpus residuals (#849–#861)

New **TC-EV038-001..014**. Deepens F2 / F4 / F6 / F7 / F32. Milestones M1→M2→M3→M4.

### TC-EV038-001: WAFS / QVACI / SIGWX XML-only OOS (G5 / #858)

- **Level**: T0 / docs
- **Objective**: Durable OOS row; cited from epic #846 + COVERAGE_MATRIX; no encode work
- **Pass criteria**: Matrix + epic note; #858 closable
- **Source**: #858; G5

### TC-EV038-002: iwxxm-modelling delta watch (G8 / #861)

- **Level**: T0 / docs
- **Objective**: Sync-PR checklist step for modelling deltas; no duplicate #807 mine
- **Pass criteria**: RELEASE_LINE_ADOPTABILITY (or peer) links watch note; #861 closable
- **Source**: #861; G8

### TC-EV038-003: Deprecation calendar / reminder template (#855)

- **Level**: T0 / process
- **Objective**: GitHub issue template (or runbook) for previous→warning window; dry-run doc
- **Pass criteria**: Template + VERSION_SUPPORT_POLICY / staff-guide links; #855 closable
- **Source**: #855

### TC-EV038-004: FE/OpenAPI IWXXM versions from single SoT (#851)

- **Level**: T0 / T1
- **Objective**: One SoT drives FE options + API enum; CI fails on drift
- **Pass criteria**: Drift test red→green; docs point to SoT
- **Source**: #851; RELEASE_LINE_ADOPTABILITY §Automation gaps

### TC-EV038-005: Sync-PR tip-diff summary (#852)

- **Level**: T0 / T1
- **Objective**: Script/job lists XSD/SCH/example stem deltas vs previous pin
- **Pass criteria**: Linked from adopt checklist; no vendor hand-edit
- **Source**: #852

### TC-EV038-006: iwxxm-us compatibility gate (#853)

- **Level**: T0 / T1
- **Objective**: Checklist (+ optional CI smoke) when WMO default moves; lag decision documented
- **Pass criteria**: RELEASE_LINE_ADOPTABILITY link; #853 closable
- **Source**: #853

### TC-EV038-007: Version picker Latest / Previous labels (#854)

- **Level**: T2 / T3 / H4–H5
- **Objective**: Picker or help shows Latest/Previous; syncs with SoT; no convert-semantics change
- **Pass criteria**: UI shows roles; Vitest/Playwright as applicable; local preview at M2
- **Source**: #854; **UJ-050**

### TC-EV038-008: codes.wmo.int vs vendor codelist drift (G6 / #859)

- **Level**: T0 / T1
- **Objective**: Cadence + failure disposition; optional non-flake CI
- **Pass criteria**: Documented check; #859 closable or CI green
- **Source**: #859; G6

### TC-EV038-009: iwxxm-translation failed-case parity (G7 / #860)

- **Level**: T0 / T1
- **Objective**: Inventory of failed-case stems vs soft path; fixtures or explicit deferral
- **Pass criteria**: Inventory + fixtures **or** deferral rationale; #860 closable/deferred
- **Source**: #860; G7

### TC-EV038-010: SWXA A7-4 / A7-5 sample-menu unlock (G4 / #857)

- **Level**: T0 / T1
- **Objective**: Inventory disposition; catalog only with vendor peers (no invented TAC)
- **Pass criteria**: Disposition documented; unlock when bar matches A7-3 policy
- **Source**: #857; G4; F28

### TC-EV038-011: VONA VolcanicAshCloudVerticalExtent (G-VONA-1 / #849)

- **Level**: T1
- **Objective**: Encode vertical extent when TAC supplies HGT SOURCE / MOV beyond A7-1 inapplicable
- **Pass criteria**: Accept + negative fixtures; SCH green; COVERAGE_MATRIX residual row
- **Source**: #849; F32 deepen

### TC-EV038-012: RESUSPENDED_VOLCANIC_ASH path (G-VONA-5 / #850)

- **Level**: T0 / T1
- **Objective**: Lint/encode when normative TAC known — else cite-only deferral documented
- **Pass criteria**: Fixtures **or** documented deferral; matrix row
- **Source**: #850; F32 deepen

### TC-EV038-013: Promote sigmet-VA-EGGX to wmoPass (G3 / #856)

- **Level**: T1
- **Objective**: ADR-032 equality vs vendor golden (or irreducible diffs documented); catalog tier flip
- **Pass criteria**: `wmoPass` **or** documented residual; FIXTURE_GAPS / matrix updated
- **Source**: #856; G3; ADR-032

### TC-EV038-014: Epic #846 residual roll-up

- **Level**: T0 / process
- **Objective**: #849–#861 closed or explicitly deferred; epic roll-up acceptance updated
- **Pass criteria**: Epic body reflects dispositions; no silent open children
- **Source**: #846 acceptance

### EV-038 verify gate

- [ ] TC-EV038-001..014 green (or explicit deferral recorded)
- [ ] No new Fn in feature-list (deepen F2/F4/F6/F7/F32 only)
- [ ] H4–H5 for #854 at deploy; M1 may waive 12/13 if docs-only ship alone
- [ ] Domain path-cites for matrix / RELEASE_LINE updates

## S055 / EV-046 — codes.wmo.int aviation registers (#889 Lean)

New **TC-EV046-001..006**. Deepens F6 / F12 / F15 / F20 / F23 / F24 / F26 / F27 / F28 / F32.
Docs/coverage only — no H4–H5. Complements **TC-EV038-008** / [#859](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/859)
(URI drift) — this cycle is TAC present/cite/cover + Validated waiver.

### TC-EV046-001: Present inventory (priority registers)

- **Level**: T0 / docs
- **Objective**: Inventory of 49-2, 306/4678, iwxxm, common/nil (and duals) vs vendor SoT;
  dual/404/obsolete dispositions recorded
- **Pass criteria**: Standing or session report lists depended-on notations + dispositions;
  offline SoT path cited
- **Source**: #889 Present; AC1; [Corpus: product] EV-046 deepen

### TC-EV046-002: Citations (docs + ISSUE_CATALOG)

- **Level**: T0 / docs
- **Objective**: RULE_SOURCE_URLS + mining notes + COVERAGE_MATRIX cite stable concept URIs;
  ISSUE_CATALOG / PROVENANCE_MAP rows that claim codes.wmo.int use concept URIs where available
- **Pass criteria**: Spot-check ≥ sample of weather/phenomena/nil-related catalog rows; no
  bare-root-only where concept URI exists (or explicit gap noted)
- **Source**: #889 Cited; AC2; `D-S055-cite=2`

### TC-EV046-003: Coverage % per F6 product family

- **Level**: T0 / docs
- **Objective**: % of priority-register members exercised by TAC fixtures for each supported
  F6 product (METAR, SPECI, TAF, SIGMET/VA, AIRMET, VAA, TCA, SWXA, VONA); exclusions with
  cite + reason
- **Pass criteria**: Coverage report committed; exclusions listed
- **Source**: #889 Cover; AC3; `D-S055-families=3`

### TC-EV046-004: Gap report / backlog children

- **Level**: T0 / process
- **Objective**: Notations with no fixture / lint / encode / citation → children or deferrals
  on #846 / #889
- **Pass criteria**: Gap list filed or deferred with rationale; epic/issue cross-links
- **Source**: #889 Gap report; AC4

### TC-EV046-005: Validated waiver + Standard follow-on

- **Level**: T0 / process
- **Objective**: Lean close records Validated waiver and opens/links Standard follow-on for
  harvest + automated TAC-token membership checks (vendor offline in PR CI)
- **Pass criteria**: Waiver in evolve-decisions §EV-046; follow-on issue or clearly titled
  child; no live HTML CI introduced
- **Source**: #889 Validated (waived); AC5; `D-S055-validated=1`

### TC-EV046-006: Harvest SoT + compose links (#859 / #882)

- **Level**: T0 / docs
- **Objective**: Document vendor RDF/CSV + manifest pin/cadence; keep compose links to #859
  (drift) and #882 (notify) current
- **Pass criteria**: SoT path + pin notes in mining/RULE_SOURCE_URLS; cross-links present
- **Source**: #889 bookkeeping; AC6

### EV-046 verify gate

- [ ] TC-EV046-001..006 green (or explicit deferral recorded)
- [ ] No new Fn (deepen only); Validated waived with follow-on
- [ ] No live `codes.wmo.int` HTML in PR CI
- [ ] Domain path-cites for RULE_SOURCE_URLS / COVERAGE_MATRIX / mining / ISSUE_CATALOG

## S059 / EV-050 — codes.wmo.int Validated harvest + membership (#959)

New **TC-EV050-001..008**. Deepens F6 / F12 / F15 / F20 / F23 / F24 / F28 (fixtures may touch
F6 packs). Completes Validated waived in EV-046 (`D-S055-validated=1`). Adds **annex3 vs
`iwxxm_us`** membership/lint compare + true-error fixes. No H4–H5 (no UI).
No live `codes.wmo.int` HTML in PR CI.

### TC-EV050-001: Offline harvest → membership sets

- **Level**: T0 / T1
- **Objective**: Standing harvest from `vendor/schemas/iwxxm-codelists` (+ pin RDF) produces
  machine-readable membership set(s) used by CI / `tac-validate`
- **Pass criteria**: Harvest path documented; CI consumes offline artifact only; no network
  fetch of codes.wmo.int HTML in PR CI
- **Source**: #959 §1; AC1; [Corpus: tech-spec] [Corpus: product §F12]

### TC-EV050-002: Membership happy + unknown/sad

- **Level**: T1
- **Objective**: Assert known-good tokens pass and unknown/sad tokens fail for v1 families:
  present/forecast weather, recent weather, cloud amount/type, SIGMET + AIRMET phenomena,
  nilReason where lint already checks URIs
- **Pass criteria**: Matrix or unit tests green for happy + sad per family; failures carry
  stable issue codes where applicable
- **Source**: #959 §2; AC2; `D-S059-families=1a`

### TC-EV050-003: Harvest cadence vs manifest pin

- **Level**: T0 / docs
- **Objective**: Document refresh cadence tied to `vendor/manifest.json` `iwxxm-codelists`
  pin (vendor sync PRs)
- **Pass criteria**: Standing docs (RULE_SOURCE_URLS / TAC_VALIDATION / mining) state pin +
  cadence; cross-link #859
- **Source**: #959 Acceptance; AC3

### TC-EV050-004: Aggressive fixture expansion (EV-046 gaps)

- **Level**: T0 / T1
- **Objective**: Add fixtures covering `RE*`, AIRMET underscore phenomena, SpaceWxPhenomena,
  TCU; update coverage notes; residual gaps deferred with cite
- **Pass criteria**: Fixtures land under `tac-validate` / product packs; coverage report or
  COVERAGE_MATRIX delta records uplift; deferrals listed
- **Source**: AC4; `D-S059-fixtures=2c`; EV-046 coverage gap table

### TC-EV050-005: #889 Validated satisfied

- **Level**: T0 / process
- **Objective**: Parent [#889](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/889) Validated
  triad element closed via this cycle’s membership CI (or explicit re-scope)
- **Pass criteria**: evolve-decisions §EV-050 AC5 + issue comments / close criteria met; no
  silent waiver without cite
- **Source**: #959 Acceptance; AC5

### TC-EV050-006: #882 design-only compose note

- **Level**: T0 / docs
- **Objective**: Short design note for optional scheduled live refresh **outside** PR CI
  composing with #882 — no job implementation
- **Pass criteria**: Note committed (session report or domain/ops pointer); states out of
  scope for notify pipeline and PR CI live HTML
- **Source**: AC6; `D-S059-882=3a`

### TC-EV050-007: annex3 vs iwxxm_us membership/lint compare

- **Level**: T0 / T1
- **Objective**: For **all supported F6 products**, same TAC corpus (or representative
  matrix) linted/membership-checked under `profile=annex3` and `profile=iwxxm_us`. Where
  `iwxxm_us` is unsupported for a product, row is **N/A** (not a fail). Where both apply,
  disposition: shared WMO expected · intentional L5 US overlay · suspect/true error
- **Pass criteria**: Report committed (session or domain) covering all F6 product families;
  N/A rows cited; CI or unit harness fails if an unclassified divergent outcome appears for
  dual-profile packs; WMO L3 SoT unchanged for both profiles; L5 only under `iwxxm_us`
- **Source**: AC7; `D-S059-profiles=1b`; [Corpus: product §F6];
  `docs/domain/TAC_VALIDATION.md` L3/L5

### TC-EV050-008: True-error profile fixes

- **Level**: T1
- **Objective**: Each **true error** from AC7 is fixed with a regression test (happy and/or
  sad); intentional diffs and N/A rows retain cited disposition
- **Pass criteria**: No open true-error rows without fix or explicit deferral+cite; no
  invented US weather tokens outside FMH-1 / NWS / iwxxm-us pins
- **Source**: AC8; `D-S059-profiles=1b`

### EV-050 verify gate

- [ ] TC-EV050-001..008 green (or explicit deferral recorded)
- [ ] No new Fn (deepen only); #889 Validated satisfied or re-scoped
- [ ] No live `codes.wmo.int` HTML in PR CI
- [ ] H4–H5 **N/A** (no UI); 12/13 waived per routing
- [ ] Aggressive fixture families present or deferred with cite
- [ ] annex3 vs iwxxm_us disposition table present; true errors fixed or deferred with cite

### TC-F31-001: Guest convert + local-only history (UJ-045)

- **Level**: T2 / T3
- **Objective**: Guest converts without login; work history stays in IndexedDB only
- **Pass criteria**: Convert 200 without Authorization; no `work-sessions` POST; local resume
  works after refresh
- **Source**: F31 AC1; UJ-045

### TC-F31-002: Persistent guest loss-of-progress notice (UJ-045)

- **Level**: T2 / T3 / H4–H5
- **Objective**: While guest **and** local/unsaved work exists, UI shows a **persistent**
  banner/callout that progress may be lost without login (`D-S038-uj`)
- **Pass criteria**: Notice visible across navigation while guest+local work; dismiss does not
  permanently hide while condition holds (or documented re-show rules); no notice required when
  logged in
- **Source**: F31 AC2; UJ-045

### TC-F31-003: Login enables DO session APIs; convert stays public (UJ-046)

- **Level**: T0 / T2 / T3
- **Objective**: After Supabase Auth login, JWT gates `/api/v1/work-sessions*`; convert/lint/
  validate remain JWT-free
- **Pass criteria**: Session CRUD 401 without JWT / 200 with JWT; convert without JWT still 200
- **Source**: F31 AC3; UJ-003 restore / UJ-046

### TC-F31-004: Auto-upload local drafts on login (UJ-046)

- **Level**: T2 / T3
- **Objective**: On login, all eligible local drafts auto-upload to DO Postgres (no merge prompt)
- **Pass criteria**: N local drafts → N server sessions (or structured per-item errors); local
  eligible drafts cleared/marked uploaded per 04 design; `D-S038-guest-merge`=2
- **Source**: F31 AC4; UJ-046

### TC-F31-005: Privacy prefs gate IndexedDB / disclose Auth cookies (UJ-047)

- **Level**: T0 / T2 / H4–H5
- **Objective**: F22 preference center gates guest work-history persistence and discloses Auth
  session cookies when login is used; GPC still honored
- **Pass criteria**: Declined non-essential storage ⇒ no IndexedDB work-history writes; Auth
  cookie category disclosed post-login; deepen TC-F22-001..003
- **Source**: F31 AC5; UJ-047; F22

### TC-F31-006: Live H4–H5 for Auth + notice + DOKS FE (UJ-045–047)

- **Level**: H4–H5 / T3
- **Objective**: Live connectivity proves FE Auth bootstrap URLs, guest notice surface, and
  DOKS (or pre-cutover staging) API/FE origins
- **Pass criteria**: `make test-live-connectivity` green; Playwright smokes for notice + login
  entry; **not waived** behind a feature flag this cycle (`D-S038-tp` Q2=1)
- **Source**: F31 AC6; UJ-045–047

## F33 / EV-042 — Mass ingest + destinations hide + churn (S050)

> Historical: Operator Dissemination destinations were **UI-hidden** under EV-042.
> **EV-091 / #898** restores destinations (`destinationsEnabled=true`) with URI-BYOC and
> connection-first preflight; #1089 adds drawer exchange overlay. Backend
> `/api/v1/dissemination/*` unchanged. Ops: [Corpus: ops] `docs/ops/operator-ui-runbook.md` §EV-091.

### TC-F33-001: Authenticated mass ingest accepts TAC / zip (UJ-051)

- **Level**: T0 / T2 / T3
- **Objective**: JWT bearer required; accepted text files land in work queue
- **Pass criteria**: POST `/api/v1/ingest/mass` 200 with JWT; per-file `accepted` + `content`;
  FE Folder/Zip → queue (Playwright `uj051-053-ev042-mass-queue.e2e.spec.ts`)
- **Source**: F33 AC4; UJ-051

### TC-F33-002: Caps 200 / 5 MiB / 50 MiB enforced (UJ-051)

- **Level**: T0
- **Objective**: Reject over-count, oversize file, or oversize total unzipped
- **Pass criteria**: Structured reject / 413-class errors; unit TC-F33 guards green
- **Source**: F33 R1; UJ-051

### TC-F33-003: Sniff + zip-bomb reject without aborting siblings (UJ-051)

- **Level**: T0
- **Objective**: Binary / zip-bomb entries rejected; other files in batch may still accept
- **Pass criteria**: Per-file `accepted=false` + reason; batch continues
- **Source**: F33 AC4; UJ-051

### TC-F33-004: Unauthenticated mass path denied (UJ-051)

- **Level**: T0 / T2 / T3
- **Objective**: No JWT → 401/403; guest UI prompts sign-in (does not open chooser)
- **Pass criteria**: API deny; Playwright guest Folder shows toast / login
- **Source**: F33 AC5 / R3; UJ-051

### TC-F33-005: Mass successes hand off to work queue (UJ-051/052)

- **Level**: T2 / T3
- **Objective**: Accepted mass items appear in operator work queue for convert/validate
- **Pass criteria**: Queue region visible with accepted names after mass ingest
- **Source**: AC6; UJ-051/052

### TC-F33-006: Live H4–H5 mass route + FE URLs (UJ-051)

- **Level**: H4–H5 / T3
- **Objective**: Browser CORS OPTIONS for `/api/v1/ingest/mass`; FE `/config.json` uses shared
  `api.baseUrl` (no separate mass URL)
- **Pass criteria**: `make test-live-connectivity` + H0i OPTIONS mass ingest; live
  `test_t83_h4_cors_preflight_mass_ingest` / staging smoke; H5 `massIngestUrl` absent
- **Source**: AC6; connectivity-gates H4–H5

### TC-EV042-001: Operator UI has no dissemination destinations (UJ-053) — **superseded**

- **Level**: T2 / T3 (historical EV-042)
- **Objective**: Convert&Send + Disseminate + **Upload to Database** absent; Convert/Validate remain
- **Pass criteria**: Vitest residual gate-off case still asserts hide when
  `destinationsEnabled=false`; production default is **enabled** (EV-091)
- **Source**: AC1; UJ-053; #897; superseded by **TC-EV091-001**

### TC-EV042-002: Dissemination API retained for harness (UJ-053)

- **Level**: T0 / T2
- **Objective**: `/api/v1/dissemination/preflight` + `/send` still mounted for tests/harness
- **Pass criteria**: Existing dissemination API tests green; operator Playwright UJ-027–030
  restored under EV-091 / #898
- **Source**: AC2; UJ-053

### TC-EV042-003: Work queue keyboard next/prev + Enter convert/validate (UJ-052)

- **Level**: T2 / T3
- **Objective**: Sticky queue; ArrowUp/Down focus; Enter convert; Shift+Enter validate
- **Pass criteria**: Vitest TC-EV042-003; Playwright queue focus + batch controls
- **Source**: AC3; UJ-052

### TC-EV042-004: Batch convert / batch validate (no disseminate) (UJ-052)

- **Level**: T2 / T3
- **Objective**: Multi-select → Batch Convert / Batch Validate; no batch disseminate
- **Pass criteria**: Buttons enabled with selection; no disseminate batch control
- **Source**: AC3 / R4; UJ-052

### EV-042 verify gate

- [x] TC-F33-001..006 + TC-EV042-001..004 green (or explicit deferral)
- [x] H4–H5 mass route wired (H0i + live smoke + Playwright UJ-051..053)
- [x] Operator destinations restore tracked in #898 → **delivered EV-091**

### TC-EV091-001: Operator dissemination destinations visible (UJ-053 restore / #898)

- **Level**: T2 / T3
- **Objective**: Convert&Send + Disseminate + Upload to Database visible; Convert remains
- **Pass criteria**: Vitest + Playwright assert `convert-and-send-button` /
  `open-dissemination-drawer` / `upload-to-database-button` present; preflight still gates Send
- **Source**: EV-091; #898; UJ-027–030 / UJ-053

### TC-EV091-002: Drawer exchange overlay on convert-before-send (#1089)

- **Level**: T2 / T3
- **Objective**: Dissemination drawer Exchange profile select (default `GLOBAL_AFS`); TAC
  candidates convert with `exchange_profile` before send
- **Pass criteria**: Vitest selects `APAC_ROBEX` and asserts convert called with that id;
  Playwright asserts select visible; Convert&Send continues to use workbench picker
- **Source**: EV-091; #1089; [Corpus: product §F36]

### EV-091 verify gate

- [ ] TC-EV091-001..002 green
- [ ] UJ-027–030 Playwright unskipped and green (stubbed BYOC)
- [ ] SSRF / memory-only BYOC invariants unchanged

### TC-EV031-001: One-time migrate legacy Supabase → DO Postgres

- **Level**: T0 / T2 (ops script + integration)
- **Objective**: Legacy product rows (e.g. `tac_work_sessions`) migrate once from Supabase DB
  into DO Postgres
- **Pass criteria**: Dry-run + apply documented; row counts / checksum sample; no dual-write
  requirement after cutover; idempotent or clearly one-shot
- **Source**: EV-031; `D-S038-spec-data` Q3=2

### TC-EV031-002: Alembic (or migration path) against DATABASE_URL

- **Level**: T0 / T2
- **Objective**: Schema migrations apply to DO Postgres via `DATABASE_URL` (not Supabase CLI
  as product SoT)
- **Pass criteria**: Upgrade/downgrade (or documented forward-only) green in CI/local against
  disposable DO-compatible Postgres
- **Source**: EV-031; F30 schema

### TC-EV031-003: Public convert without JWT after Auth restore

- **Level**: T0 / T2 / H3
- **Objective**: Restoring `/auth/*` does not re-gate convert APIs
- **Pass criteria**: Matrix of public routes succeed with no Authorization header; rate limits
  still apply (ADR-031 keep)
- **Source**: EV-031; F21 Amended; F30 convert public lock

### TC-EV031-004: Login session CRUD happy path

- **Level**: T2 / T3 / H6
- **Objective**: Register/login (or existing fixture user) → create/list/patch/delete (or soft-
  delete) work session on DO Postgres
- **Pass criteria**: Full CRUD green with JWT; owner isolation (user A cannot read user B);
  aligns UJ-046
- **Source**: EV-031; F31; M4

## F21 / F22 Test Cases (S023 / EV-017) — stubs (**amended EV-031**)

> Detailed steps finalize in **04-tech-plan**. Objectives and pass criteria locked at 02
> (`D-S023-02-C-EV017-A`). **EV-031**: Auth returns for long-term sessions; convert stays public;
> deepen privacy ↔ storage (TC-F31-005).

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

### TC-F16-LIVE-001: Live local Postgres upload (UJ-027 / EV-039)

- **Level**: T2 / T3 (local Compose — not production)
- **Objective**: Playwright live (no route mocks) preflight→send to Compose `byoc-postgres`
- **Pass criteria**: UI success; row/writer-contract write asserted; suite tears down containers
- **Harness**: `make compose-mock-byoc-up` / `compose-mock-byoc-down`; allowlist includes localhost
- **Source**: F16 deepen; S047 / EV-039; AC2/AC4; [Corpus: product §F16]

### TC-F16-LIVE-002: Live local MySQL upload (UJ-027 / EV-039)

- **Level**: T2 / T3 (local Compose)
- **Objective**: Same as LIVE-001 against Compose `byoc-mysql`
- **Pass criteria**: UI success + write assertion + teardown
- **Source**: F16 deepen; S047 / EV-039; AC2/AC4

### TC-F16-LIVE-003: Live local SQL Server upload (UJ-027 / EV-039)

- **Level**: T2 / T3 (local Compose; may be opt-in in CI if image is heavy)
- **Objective**: Same as LIVE-001 against Compose `byoc-sqlserver`
- **Pass criteria**: UI success + write assertion + teardown; documented skip/opt-in if CI-waived
- **Source**: F16 deepen; S047 / EV-039; AC2/AC4/AC7

### TC-F16-LIVE-004: Live local SQLite upload + teardown audit (UJ-027 / EV-039)

- **Level**: T2 / T3 (local file path)
- **Objective**: Live Playwright against disposable SQLite file URI; verify temp file removed
  after suite; integration Testcontainers fixtures tear down on pass/fail/skip (AC5/AC6)
- **Pass criteria**: Write asserted; no leftover `.db` from the live suite; teardown audit
  gaps fixed or waived in session report
- **Source**: F16 deepen; S047 / EV-039; AC2/AC4/AC5/AC6

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
- [ ] TC-F16-LIVE-001..004 green locally (or documented CI opt-in + local evidence) — S047 / EV-039
- [ ] Teardown: Compose down / Testcontainers stop / SQLite temp cleanup — no orphans (AC4–AC6)
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

- **Objective**: H6 — product journeys against live frontend (includes F6 matrix; Render
  transitional, then DOKS per F30 / UJ-048)
- **Preconditions**: `PLAYWRIGHT_BASE_URL=${LIVE_FRONTEND_URL}`; public convert needs **no**
  login; IndexedDB available for guest path; optional Auth fixtures only for UJ-046 / F31 cases
- **Steps**:
  1. Run `00-preflight.e2e.spec.ts` first (wake + health)
  2. `make test-live-e2e` — public METAR convert, F6 product/profile matrix (UJ-005),
     validation (UJ-002/007), UJ-008 smoke; Auth login covered by TC-F31 / UJ-046 (not
     “Auth-gone”)
  3. Playwright config disables local `webServer` when base URL is remote
- **Pass criteria**: UJ-001–007 specs green against live URLs; UJ-003 amended — convert stays
  public (no JWT), while `/auth/*` may exist for long-term sessions (F31)
- **Resilience**: Cold-start retry in preflight; serial execution (no parallel live requests)
- **Source**: UJ-001–007, H6; F21 amended F31; F30 DOKS URLs when cut over

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
  `iwxxm-validate`. Multipart field name is **`files`** (EV-061 / #1011; not `file`).
- **Source**: UJ-011; Q44b=B; #1011

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
- S047 / EV-039 (2026-08-06): TC-F16-LIVE-001..004 live local Compose multi-DB + teardown
  gates (F16 deepen; UJ-027)

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

**Policy (EV-002 → EV-036 → EV-047 amend)**: Single workflow file for PR/push. **EV-047
(#833)** restores a **slim developer hook path**: local commit = **lint/format only**;
local push = **fast unit subset only**. Heavier gates (typecheck, catalog/registry,
actionlint/yamllint, medium validate, full coverage matrix, Compose integration) stay on
**remote CI** and opt-in `make` targets — **not** on default husky. Remote CI **keeps**
merge strength (unit matrix + coverage + PR coverage comment + native/Rust/e2e/alembic as
wired). Scheduled workflows (`vendor-sync`, load/e2e) unchanged.

| Trigger | Workflow | Jobs | Checks |
|---------|----------|------|--------|
| Local commit | husky → pre-commit | lint | ruff / prettier / eslint (lint/format only; shape A) |
| Local push | husky pre-push | fast units | agreed fast unit subset only (not `validate-ci` / not Compose) |
| PR / push `main`, `stage`, `dev` | `ci-cd.yml` | **remote** | typecheck + catalog/registry + secrets/yaml as configured; unit matrix + coverage + PR coverage comment; `tac2iwxxm-native`; **Rust crate checks** (EV-045); **converter perf hard gate** (EV-047 / #834); `e2e-smoke`; `test-alembic` |
| push `main` / `stage` | `ci-cd.yml` | **deploy** | needs remaining remote jobs; GHCR + **DOKS**; Render optional |
| Schedule | `vendor-sync.yml` | vendor-sync | wmo-im schema sync PR (M6) |
| Manual / schedule | `load-tests.yml`, `e2e-tests.yml` | — | out of EV-002 / EV-036 / EV-047 day-to-day husky scope |

### Pre-commit / husky (local gates) — EV-047 (#833; supersedes EV-036 day-to-day)

| Hook | Tool | Role |
|------|------|------|
| husky pre-commit | lint/format only | ruff / prettier / eslint — **no** tsc/basedpyright/catalog/registry/actionlint/yamllint/medium validate on default path |
| husky pre-push | fast unit subset | explicit Makefile/pytest target — **not** full `ci-prepush` / Compose |
| Opt-in local | `make validate-*` / `ci-prepush` | full parity when contributor chooses |
| Remote PR coverage | `coverage-pr-comment` | sticky PR comment from unit coverage artifacts |
| Remote converter perf | hard gate job | EV-047 / #834 — fail on convert p95 regression |

Family `test-*-quality` packs stay path-filtered / opt-in — **not** on every commit/push.
Remote Playwright **e2e-smoke** stays on Actions (browser install cost; not every local push).

### TC-EV036 (M5 / S044) — local-first CI *(superseded for husky day-to-day by EV-047)*

| ID | Level | Assert |
|----|-------|--------|
| TC-EV036-001 | T0 | *(historical)* husky pre-commit ran fast + medium validate |
| TC-EV036-002 | T0 | *(historical)* `.husky/pre-push` ran `make ci` |
| TC-EV036-003 | T0 | `ci-cd.yml` — no `validate:` job; unit matrix + coverage + PR comment; no Compose integration; deploy `needs` includes `test` — **still relevant for remote graph** |

### TC-EV047 (M5 / F6 / F7 / S056) — slim husky + converter perf + operator docs

| ID | Level | Assert |
|----|-------|--------|
| TC-EV047-001 | T0 | `.husky/pre-commit` (via `make install-hooks`) runs lint/format only — does **not** invoke tsc, basedpyright, catalog-check, issue-registry-guard, actionlint, yamllint, or medium validate |
| TC-EV047-002 | T0 | `.husky/pre-push` runs agreed **fast unit** subset only — does **not** run `validate-ci` or Compose integration |
| TC-EV047-003 | T0 | `docs/ops/DEVELOPMENT.md` hook table matches shape A; opt-in `make` targets documented |
| TC-EV047-004 | T0/CI | Offloaded gates still present in CI (typecheck and/or catalog/registry/secrets/yaml/unit coverage as configured) — contract test or workflow assert |
| TC-EV047-005 | T0/CI | Artificial slowdown in `tac2iwxxm.convert` fails converter perf hard gate |
| TC-EV047-006 | T0/CI | Revert slowdown → gate green; baselines committed YAML with documented refresh (no silent auto-raise) |
| TC-EV047-007 | CI | Perf gate is required check (or merge-blocking job) on PR path to protected branches — job `name:` **`Converter perf (tac2iwxxm)`** must match `scripts/deploy/apply_gh_branch_rulesets.sh` (D-S056-gateA=2) |
| TC-EV047-008 | T0 | Flake policy documented (median-of-N / retry / tolerance); convert-only p95; METAR/SPECI/TAF + thin SIGMET-family; pure-Python first |
| TC-EV047-009 | T0 | `docs/guides/operator-one-pager.md` exists; one-page content checklist (convert→validate→download; version; soft preview); no internal citations |
| TC-EV047-010 | T0 | `docs/guides/operator-handbook.md` has required sections + ingest pointer; no internal citations; one-pager links here |
| TC-EV047-011 | T0/T2 | README Quick start links both docs; in-app Help entry reaches one-pager (UJ-054) |

### TC-EV048 (F7 / F21 / S057) — strip internal doc refs from UI + public API (#951)

**Guard patterns** (fail when found in scanned user-facing surfaces): `\[Corpus:`,
`docs/sessions/`, `docs/feature-list`, `\bADR-\d+\b`, `\bEV-\d+\b`, `\bS0\d+\b`,
`\bTC-[A-Z0-9-]+\b`, `\bE\d{2}-\d+\b`, `(?<!\w)#\d{3,}\b`, `\bF\d+\b`
(`D-S057-guard-s0=1`, `D-S057-04-guard-ext=1`, `D-S057-qa003=2`; `#NNN` uses
lookbehind because `\b#` misses `#702` after spaces/slashes). Allowlist only for
true domain false positives. Do **not** scan `docs/` standing text, source
comments-only, or `*.test.*` / pytest modules.

| ID | Tier | Criterion |
|----|------|-----------|
| TC-EV048-001 | T0 | PR (or session report) lists audit findings for UI strings + OpenAPI descriptions + client-facing errors |
| TC-EV048-002 | T0 | OpenAPI export / schema `description` + operation summaries pass guard (no internal-doc patterns) |
| TC-EV048-003 | T0/T2 | Operator-visible FE string catalogs (labels/helpers/tooltips/banners/empty states/console/catalog/example tiers/privacy-auth) pass guard |
| TC-EV048-004 | T0 | Client-facing API `detail` / error messages pass guard |
| TC-EV048-005 | T0/CI | Automated unit/CI test fails if a synthetic internal cite is injected into scanned OpenAPI or FE catalogs; comments/tests remain allowed |

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
| Unit coverage (Python + TS + scripts) | **100% line+branch** all packages/apps + **per-file ≥100%** (Python); scripts `*.py` cov + bats for every `*.sh` | ADR-007 / EV-080 / #1077 |
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
