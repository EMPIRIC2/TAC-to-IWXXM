# User Journeys

> **Project**: METAR to IWXXM Converter
> **Source**: feature-list.md; S008 F6 + realtime amend; S011 / EV-008 F7 operator UI;
> S013 / EV-009 F9/F10 decode + preview UX; S014 / EV-010 package publish + msgspec HTTP;
> S015 / EV-011 F15 METAR lint registry + #732 quality; S016 / EV-012 Manual TAC Input modes (#730);
> S019 / EV-014 dissemination epic F16–F19; S020 / EV-015 F20 TAF+SPECI quality (#735/#734);
> S023 / EV-017 public app + privacy (#783)
> **Last updated**: 2026-07-30 (S030 / EV-023 — #800 deepen UJ-001/005/006/016; no new UJ)

Product-facing journeys (UJ-*) describe end-user flows. Developer journeys (UJ-DEV-*)
describe monorepo workflows introduced by migration features M1–M6 and F6.

## Journey Index

| ID | Journey | Entry point | Feature | E2E tier |
|----|---------|-------------|---------|----------|
| UJ-001 | Convert METAR via UI (shorthand) | apps/frontend | F6+F21 (was F1) | T2 / **T3** |
| UJ-002 | Validate IWXXM output (`iwxxm-validate`) | apps/frontend / API | F2+F6+F21 | T2 / **T3** |
| UJ-003 | Register and login | apps/frontend | Auth | **Superseded** (F21 / S023) |
| UJ-004 | Resume & browse METAR work history (local IndexedDB) | apps/frontend | F5+F7+F21 | T2 / **T3** |
| UJ-005 | Convert with product + profile via UI | apps/frontend | F6 | T2 / **T3** (all 7 products) |
| UJ-006 | Convert non-METAR product via API | HTTP API | F6 | T2 / **T3** |
| UJ-007 | Validate IWXXM-US profile document | apps/frontend / API | F2+F6 | T2 / **T3** |
| UJ-008 | Unsupported / unknown product TAC | UI / API | F6 | T2 / T3 |
| UJ-009 | US profile without iwxxm-us pin | UI / API | F6 | T2 |
| UJ-010 | Malformed US REMARKS | UI / API | F6 | T0 / T2 |
| UJ-011 | Bulletin split → convert → Schematron (API) | HTTP API | F6 | **T2** |
| UJ-012 | TAC lint failure (`tac-validate`) via API | HTTP API | F6 | **T2** |
| UJ-013 | Multi-product operator entry / workbench shell (F7) | apps/frontend | F7 | T2 / **T3** |
| UJ-014 | Near-RT ingest + quarantine (F8) | Worker / API | F8 | T2 / T3 (staging) |
| UJ-015 | TAC decode panel (Code \| Explanation) | apps/frontend | F7 | T2 / **T3** |
| UJ-016 | Failed-TAC cue + soft-preview / partial | apps/frontend | F7 | T2 / **T3** |
| UJ-017 | Live workbench (debounce, spans, console, live IWXXM) | apps/frontend | F7 | T2 / **T3** |
| UJ-018 | Unified local sessions persist/resume (IndexedDB) | apps/frontend | F5+F7+F21 | T2 / **T3** |
| UJ-019 | Admin routes removed / BYO operator surface | apps/frontend | F7 / M4 | T2 / **T3** |
| UJ-020 | Value-aware decode + plain-language summary | apps/frontend | F9 | T0 / T2 / **T3** |
| UJ-021 | IWXXM preview pane + terminator quick fix | apps/frontend | F10 | T2 / **T3** |
| UJ-022 | Operator convert/validate after msgspec HTTP | apps/frontend | F11 | T2 / **T3** / H6′ |
| UJ-023 | PyPI release tag → install smoke | CI / maintainer | F12–F14 | CI |
| UJ-024 | METAR/SPECI lint registry + convert→validate golden | UI / API / CI | F15 (+F6/F12) | T0 / T2 / **T3** |
| UJ-025 | Manual TAC Input modes (TAC / AHL / COLLECT) | apps/frontend | F7 (ADR-024) | T2 / **T3** / H6′ |
| UJ-026 | METAR REMARKS retain / exclusion (#667) | UI / API / package | F6 | T0 / T2 |
| UJ-027 | Dissemination drawer — multi-DB upload (BYOC URI) + multi-select | apps/frontend | F16 | T2 / **T3** / H6′ |
| UJ-028 | Dissemination drawer — WIS2 publish | apps/frontend | F17 | T2 / **T3** / H6′ |
| UJ-029 | Dissemination drawer — EDIS → RTH Washington | apps/frontend | F18 | T2 / **T3** (live BYOC) |
| UJ-030 | Dissemination drawer — AMHS / SWIM / AFS | apps/frontend | F19 | T2 / **T3** |
| UJ-031 | TAF + SPECI lint / convert→validate golden | UI / API / CI | F20 (+F6/F12) | T0 / T2 / **T3** |
| UJ-032 | Load golden example → convert / validate | apps/frontend | F7 (#780) | T0 / T2 / H4–H5 |
| UJ-033 | Privacy notice + settings + GPC | apps/frontend | F22 | T0 / T2 / H4–H5 |
| UJ-034 | SIGMET + VA SIGMET lint / convert→validate golden | UI / API / CI | F23 (+F6/F12) | T0 / T2 / **T3** |
| UJ-035 | AIRMET lint / convert→validate WMO golden | UI / API / CI | F24 (+F6/F12) | T0 / T2 / **T3** |
| UJ-036 | WMO-passing Examples catalog + METAR/SPECI/TAF goldens | apps/frontend / CI | F25 (+F7.g) | T0 / T2 / **T3** / H4–H5 |
| UJ-037 | VAA lint / convert→validate WMO golden | UI / API / CI | F26 (+F6.f/F12) | T0 / T2 / **T3** |
| UJ-038 | TCA lint / convert→validate WMO golden | UI / API / CI | F27 (+F6.f/F12) | T0 / T2 / **T3** |
| UJ-039 | Load official WMO IWXXM examples from sample menu | apps/frontend / CI | F25/F7.g deepen (EV-024) | T0 / T2 / **T3** / H4–H5 |
| — | **EV-023 #800** — no new UJ; deepen UJ-001/005/006/016 + TC-EV023-001..009 | library / API / CI | F6/F2/F12/F13 | T0 / T2 (+ T3 smoke if API ships) |
| UJ-DEV-001 | Clone and run monorepo | `git clone` + `make dev` | M1, M5 | T0 |
| UJ-DEV-002 | Sync vendor schemas | Scheduled Action / manual | M2, M6, F6 | CI |
| UJ-DEV-003 | ~~Merge GIFTs upstream~~ | — | M3 | **Deprecated** (ADR-014) |
| UJ-DEV-003b | Maintain tac2iwxxm + iwxxm-us pins | Maintainer workflow | F6, M2 | CI |
| UJ-DEV-004 | Package CI for tac-validate + iwxxm-validate | `make test` / CI | F2, F6, M5 | T0 / CI |
| UJ-DEV-005 | pip install published packages + convert/validate | clean venv | F12–F14 | T0 / CI |
| UJ-OPS-001 | Deploy Render stack (API + static + worker) | render.yaml | M4, F8 | T3 (staging) |

**E2E tiers**:

- **T0** — Unit + package tests; no running services.
- **T2** — Local docker-compose or `make dev`; Playwright in `apps/e2e/`.
- **T3** — Deployed Render stack; Playwright + pytest against live URLs (manual `make test-live`).

Run local E2E: `make test-e2e-playwright`
Run live E2E: `make test-live` (after F21: public convert path needs **no** `E2E_USER_*`)

**T3 URLs** (canonical):

| Role | Env var | URL |
|------|---------|-----|
| API | `LIVE_API_URL` | `https://metar-to-iwxxm-api.onrender.com` |
| Frontend | `LIVE_FRONTEND_URL` / `PLAYWRIGHT_BASE_URL` | `https://metar-to-iwxxm-frontend-v4-web.onrender.com` |

**F6 T3 requirement**: All **seven** products (AIRMET, METAR, SIGMET, SPECI, TAF, VAA, TCA)
must pass annex3 convert via UI (UJ-005 parametrize) and API smoke (UJ-006). US profile
(`iwxxm_us`) T3 cases for METAR/SPECI/TAF where schemas apply (UJ-007).

---

## Product Journeys

### UJ-001: Convert METAR via UI (shorthand)

**Actor**: Anyone (public app — F21; no login)

**Goal**: Upload or paste METAR TAC and receive IWXXM XML (default product/profile).

**Feature**: F6 (+ F21). Full product/profile matrix is **UJ-005**. History optional via **UJ-004**.

**Steps**:

1. Open frontend in browser (no login).
2. Drag-drop `.tac` file or paste manual text (METAR/SPECI).
3. Optionally leave product on **auto** / METAR and profile **annex3** (defaults).
4. **#664 (EV-005)**: Optionally type an **Output filename** for manually entered TAC.
5. Choose **Convert**, **Convert&Send**, or **Upload to Database**.
6. View output; each result card shows **TAC-derived title**, optional **Line N of M** for
   multi-line manual input, prominent **Source TAC** panel, and download filename when it
   differs (#655 / EV-007). #555 replace-on-success and error log panel behavior unchanged.
7. On convert failure after F6 cutover: structured error only — **no gifts rollback**.
8. Work may auto-save to IndexedDB (UJ-004) — not to server session APIs.

**Acceptance**: METAR converts without error via tac2iwxxm; **no JWT required**; schema/Schematron
pass for selected version; UX behaviors from #555/#664 preserved.

**Automated tests**: `apps/e2e/tac-file-conversion.e2e.spec.ts` (T2); `make test-live-e2e` (T3)

**Browser wiring**: Frontend → API base URL; CORS must allow frontend origin (H4).

---

### UJ-002: Validate IWXXM Output

**Actor**: Anyone (public) or API client

**Goal**: Confirm generated XML passes schema/Schematron validation via
`packages/iwxxm-validate` (backend thin wrapper).

**Steps**:

1. Obtain IWXXM XML from conversion (UJ-001 / UJ-005 / UJ-006 / UJ-011).
2. Trigger validation via **Convert with Strict Validation** (UI maps to
   `validate_output=true` + `validation_level=comprehensive` on `/api/v1/convert`) **or** a
   dedicated validate endpoint/UI action with the same **profile** used for convert.
3. Backend invokes **`iwxxm-validate`** (not inline schema loading long-term).
4. Review pass/fail and error messages (conversion log / issues arrays).
5. If `profile=iwxxm_us`, validation uses **combined** WMO + iwxxm-us catalogs; `annex3` uses WMO only.

**Acceptance**: Valid sample produces validation pass for selected IWXXM version and profile.
Soft-preview Convert does **not** satisfy UJ-002 (ADR-022 / ADR-023). **No JWT required** (F21).

**Automated tests**: `packages/iwxxm-validate` unit + backend wrapper tests + FE convert-params
mapping (ADR-023) + E2E where exposed (T2); H3 + H6 (T3)

---

### UJ-003: Register and Login — Superseded

**Status**: **Superseded** by F21 (S023 / EV-017 / #783). Operator Auth UX and JWT gates removed.

**Historical**: Supabase JWT via merged `/auth/*`; protected `/api/v1/*` returned 401 without token.

**Replacement**: Public convert/validate (UJ-001/002); local history (UJ-004); privacy (UJ-033).

**Automated tests**: Retire or rewrite `apps/e2e/auth.e2e.spec.ts` to assert Auth routes absent /
gone (negative). Live H6 must not require `E2E_USER_*` for primary journeys.

---

### UJ-004: Resume & Browse METAR Work History

**Actor**: Anyone (same browser / origin)

**Goal**: Resume Draft/WIP and browse Finished/Failed METAR/SPECI work from **IndexedDB**
(F5 deepen / F7.h — S023).

**Steps**:

1. Open converter (no login).
2. Open converter sidebar (**5 recent**) and/or **My METARs** (`/history`).
3. My METARs lists local rows with `product IN (metar, speci)`.
4. Open a Draft — editor restores TAC + `conversion_params`; auto-save (~3s) continues locally.
5. Use **Export workspace** / **Import workspace** (JSON) for backup or device move.
6. Finished sessions open read-only; soft-deleted sessions appear in local trash.
7. **No** admin cross-user browse (UJ-019); **no** `/api/v1/work-sessions` calls.

**Acceptance**: F5 UX preserved for METAR/SPECI on IndexedDB; clearing site data loses history
unless exported.

**Automated tests**: FE unit + Playwright history (T2); live H6 delta (T3)

**Browser wiring**: Local IndexedDB for persistence; convert APIs CORS H4.

---

### UJ-005: Convert with Product + Profile via UI

**Actor**: User (guest or authenticated)

**Goal**: Select product and profile, convert TAC, view IWXXM for any of the seven F6 products.

**Steps**:

1. Open frontend converter.
2. Set **product** (airmet | metar | sigmet | speci | taf | vaa | tca | auto).
3. Set **profile** (`annex3` | `iwxxm_us`); default annex3.
4. Set IWXXM **version** (vendored pin).
5. Paste or upload TAC appropriate to the product.
6. If explicit product ≠ auto-detect, UI **warns** but proceeds with explicit selection.
7. **Convert** — pipeline may run **`tac-validate`** then **`tac2iwxxm`**; view XML / download;
   TAC lint and convert errors via #555 panel.
8. Optionally validate via UJ-002 (`iwxxm-validate`).

**Acceptance (F6 v1 / T3)**: Parametrized Playwright (or 7 cases) — each product with
`profile=annex3` and golden TAC fixture converts successfully and shows XML. Additional
`iwxxm_us` cases for METAR/SPECI/TAF where US schemas apply.

**Automated tests**: `apps/e2e/` F6 product-matrix spec (planned); `make test-live-e2e` (T3)

**Browser wiring**: Same API origin; `product` + `profile` in form/`conversion_params` (H4–H5).

---

### UJ-006: Convert Non-METAR Product via API

**Actor**: API client / live harness

**Goal**: HTTP convert for AIRMET, SIGMET, TAF, VAA, TCA (and METAR/SPECI) without UI.

**Steps**:

1. `POST /api/v1/convert` with TAC + `product` + `profile` (+ version).
2. Server path: optional **`tac-validate`** → **`tac2iwxxm`** (single report or after split).
3. Receive IWXXM (or structured TAC lint / convert errors).
4. Optionally chain validate (UJ-002 / UJ-007 via `iwxxm-validate`).

**Acceptance**: T2 and T3 API smoke for all seven products (annex3). Required alongside UJ-005
for F6 v1.

**Automated tests**: pytest live/API convert matrix (H3 extended); T2 integration.

---

### UJ-007: Validate IWXXM-US Profile Document

**Actor**: User or API client

**Goal**: Validate XML produced with `profile=iwxxm_us` through **`iwxxm-validate`**.

**Steps**:

1. Convert METAR/SPECI/TAF (as applicable) with `profile=iwxxm_us`.
2. Validate with combined catalogs via package / API wrapper.
3. Confirm pass (or expected Schematron messages documented in fixtures).

**Acceptance**: At least one US-profile METAR (and SPECI/TAF when fixtures exist) validates on T2/T3.

---

### UJ-008: Unsupported / Unknown Product TAC

**Goal**: Fail clearly when product cannot be determined or is unsupported.

**Steps**: Submit ambiguous/unsupported TAC; observe API/UI error; confirm **no** silent success
and **no** gifts fallback.

**Acceptance**: Structured error; H6/T2 assert error panel or API `errors`.

---

### UJ-009: US Profile Without iwxxm-us Pin

**Goal**: Fail closed if `profile=iwxxm_us` but vendor pin/catalog missing.

**Acceptance**: Actionable error (not empty XML / not annex3 silent downgrade).

**Tier**: T2 (and T0 unit); T3 once pin is deployed.

---

### UJ-010: Malformed US REMARKS

**Goal**: Under `iwxxm_us`, malformed REMARKS yield structured diagnostics (not silent drop).

**Acceptance**: Error/issues list non-empty (`MALFORMED_REMARKS`); annex3 still does not emit
US extension XML (profile isolation). See also UJ-026 for annex3 exclusion messaging.

**Tier**: T0 / T2 primarily.

---

### UJ-026: METAR REMARKS retain / exclusion (#667)

**Goal**: Remark portion of METAR/SPECI is not silently ignored ([#667](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/667)).

**Acceptance**:
1. `profile=annex3` with `RMK` → convert succeeds with `ConvertIssue` code `REMARKS_EXCLUDED` (info).
2. `profile=iwxxm_us` → structured AO2/SLP/PK WND still emitted; unparsed remainder retained in
   `iwxxm-us:humanReadableText` (never drop).
3. Additive `T########` / `P####` parsed into IR and retained in free-text until structured codecs land.

**Tier**: T0 / T2 primarily.

**Automated tests**:
- Package: `packages/tac2iwxxm/tests/test_issue_667_metar_remarks.py`
- API unit: `apps/backend/tests/unit/test_uj026_remarks_convert_issues.py`
- Live API: `tests/live/test_uj026_metar_remarks_live.py`
- Playwright: `apps/e2e/uj026-metar-remarks.e2e.spec.ts`

**Source**: S018 / EV-013

---

### UJ-011: Bulletin Split → Convert → Schematron (API)

**Actor**: API client / package harness

**Goal**: Submit a WMO AHL bulletin containing multiple reports; split; convert each; Schematron
via `iwxxm-validate`.

**Feature**: F6 (F6.bulletin)

**Steps**:

1. `POST /api/v1/convert-bulletin` with a multi-report bulletin + product/profile/version.
2. Server/`tac2iwxxm` **splits** into individual TAC reports.
3. Each report: optional `tac-validate` / prior `/lint-tac` → convert → collect IWXXM.
4. Validate one or more results with `iwxxm-validate` (UJ-002).

**Acceptance**: Fixture bulletin yields N IWXXM documents (or structured per-report errors);
Schematron pass on golden reports. **Tier: T2** locally; live gate **H7** (TC-LIVE-F6-030).

**Automated tests**: `packages/tac2iwxxm` bulletin fixtures + `/convert-bulletin` API (T2);
`make test-live-bulletin` (H7, planned).

---

### UJ-012: TAC Lint Failure via API

**Actor**: API client

**Goal**: Malformed / rule-violating TAC fails at **`tac-validate`** with structured issues
(before or instead of successful IWXXM).

**Steps**:

1. Submit TAC that fails the shared rule pack (product-appropriate fixture).
2. Observe structured lint issues in API response / errors list.
3. Confirm no silent success / empty IWXXM presented as valid.

**Acceptance**: Non-empty structured issues; convert may be skipped or marked failed per API
contract (04). **Tier: T2**.

**Automated tests**: `packages/tac-validate` + backend wrapper (T2).

---

### UJ-013: Multi-Product Operator Entry / Workbench Shell (F7)

**Actor**: Anyone (public app — F21; no login)

**Goal**: Use the F7 workbench shell for any of the seven F6 products (editor + product/profile/
version + convert path), as the umbrella entry for F7 UI.

**Feature**: F7 (S011 / EV-008; public + IndexedDB — S023 / F21 / F7.h)

**Steps**:

1. Open frontend converter / workbench (CodeMirror 6 editor replaces plain textarea) — **no login**.
2. Select or auto-detect **product**; set **profile** and **version**.
3. Paste or upload TAC; observe product-aware chrome (not METAR-only copy).
4. Run **Convert** (hard path) and view IWXXM / Source TAC / downloads (UJ-001/005 behaviors).
5. Optionally open decode (UJ-015), exercise Failed-TAC/preview (UJ-016), live assist (UJ-017),
   or save/resume **local** session (UJ-018 / IndexedDB).

**Acceptance**: All seven products reachable from the same operator entry; H4–H5 connectivity;
no `/admin` or `/auth` dependency; sessions persist locally without JWT.

**Automated tests**: Playwright workbench shell + product matrix extension (T2); live T3 smoke.

**Browser wiring**: API base from `/config.json`; CORS allows frontend origin (H4–H5); public
`/api/v1/*` (F21).

---

### UJ-014: Near-Realtime Ingest + Quarantine (F8)

**Status**: **Implemented** (S008 / ADR-018/019). Worker ingest → pipeline → Supabase store or
separate quarantine on Schematron/convert fail. No push sinks in v1.

**Acceptance**: Worker processes HTTPS/object-prefix fixture feed; pass rows in
`iwxxm_ingest_results`; fail rows in `iwxxm_ingest_quarantine`; service-role JWT for writers.
Live: T7.4 / Phase 6 gate (may remain deferred).

---

### UJ-015: TAC Decode Panel (Code | Explanation)

**Actor**: Anyone (public — F21)

**Goal**: See ordered decode segments for the current TAC with short explanations and explicit
residuals (#702).

**Steps**:

1. Enter TAC for any of the seven products in the workbench (no login).
2. Open **Decode** panel (collapsible Code | Explanation).
3. UI calls `POST /api/v1/decode-tac` (**no JWT** — F21 public).
4. Segments show `start`/`end`; clicking/hovering highlights spans in the editor when offsets exist.
5. Undecoded material appears as explicit **residuals** (esp. VAA/TCA — G4).

**Acceptance**: At least METAR/SPECI/TAF show non-empty segment lists for golden fixtures; all
seven products return a well-formed decode response (may be residual-heavy).

**Automated tests**: API contract + Vitest panel; Playwright smoke (T2); live T3 sample.

---

### UJ-016: Failed-TAC Cue + Soft-Preview / Partial

**Actor**: Operator

**Goal**: Distinguish Failed-TAC and obtain best-effort IWXXM + failed-span markers (#665/#666).

**Steps**:

1. Enter malformed or partially valid TAC.
2. Observe distinct **Failed-TAC** visual cue in editor/results (not only generic error toast).
3. Trigger **soft-preview** path (exact control: flag vs button — 04-tech-plan).
4. Response includes best-effort XML (when any) and failed-span markers aligned to editor spans.
5. Hard convert may still 4xx/structured-fail per api-contract; preview must not be confused with
   a successful Schematron-passed publish.

**Acceptance**: Failed cue visible; preview returns markers for injected bad span; cancel/Abort
safe if in-flight.

**Automated tests**: Backend preview + Playwright highlight (T2); live T3 optional.

---

### UJ-017: Live Workbench (Debounce, Spans, Console, Live IWXXM)

**Actor**: Operator

**Goal**: Edit TAC with live assist — debounced lint/decode, span highlight, hover, optional live
IWXXM, pull-up console (#694).

**Steps**:

1. Type in CodeMirror workbench; requests debounce; prior in-flight calls abort.
2. Lint/decode issues highlight `start`/`end` spans; hover shows issue/segment detail.
3. Toggle **live IWXXM** (validate/convert/preview per 04) without leaving the editor.
4. Open pull-up **console** for structured messages.
5. Full Schematron/convert may remain behind toggle if latency requires (lint/decode first).

**Acceptance**: Debounce + AbortController evidenced in network; spans align to known issue
fixture; console captures errors without crashing the editor.

**Automated tests**: Vitest debounce helpers; Playwright live-edit smoke (T2); live T3 light.

**Browser wiring**: Multiple public API calls to lint/decode/validate/preview — H4–H5 required
(no JWT — F21).

---

### UJ-018: Unified Local Sessions Persist/Resume (IndexedDB)

**Actor**: Anyone (same browser — F21)

**Goal**: Persist/resume work for any of seven products in **IndexedDB** (F7.h / S023); My METARs
filters METAR/SPECI locally.

**Steps**:

1. Create Draft for a non-METAR product (e.g. TAF); wait for local autosave.
2. Reload — session restores TAC + product/profile from IndexedDB.
3. Convert to WIP/Finished per status rules (one WIP per browser workspace).
4. Open My METARs — non-METAR draft **not** listed; workbench history **does** list it.
5. Export workspace JSON; import on another profile/browser to restore (no server sync).

**Acceptance**: Local CRUD for seven products; product filter correct; **no** `/api/v1/work-sessions`;
legacy Supabase rows not exposed.

**Automated tests**: FE IndexedDB unit + Playwright (T2); staging smoke (T3).

---

### UJ-019: Admin Routes Removed / BYO Operator Surface

**Actor**: Operator / former admin user

**Goal**: Confirm admin product surface is gone and BYO topology is the credential model (#697).

**Steps**:

1. Navigate to `/admin` and legacy admin deep links — expect **404** / not found (no dashboard).
2. Confirm no UI for approval queue, toggle-admin, or cross-user session browse.
3. Public user can convert and use local sessions (UJ-013/018) **without** login (F21).
4. Operator deploy docs/env describe remaining infra secrets (F8 / dissemination allowlist) —
   no paste of Supabase **Auth** keys; no operator Auth required after F21.

**Acceptance**: Admin UI/routes absent; public convert works; E2E admin suite remains negative.

**Automated tests**: Playwright negative `/admin` (T2/T3); retire prior admin panel locators.

---

### UJ-020: Value-Aware Decode + Plain-Language Summary (F9)

**Actor**: Operator (including non-specialist readers of a report)

**Goal**: Read what the TAC actually says — decoded values per token and a natural-language
description of the whole report — updating live while typing.

**Steps**:

1. Type or paste TAC in the workbench (any of the seven products).
2. Decode panel updates live (existing 300 ms debounce; UJ-017 path).
3. Each recognized token shows a **value-aware** explanation: `24/18` →
   "Temperature 24 °C, dewpoint 18 °C"; `18004KT` → "Wind from 180° at 4 kt"; `10SM` →
   "Visibility 10 statute miles"; `A3011` → "Altimeter 30.11 inHg".
4. A **"Plain language"** block at the top of the decode panel shows one flowing paragraph
   summarizing the report, e.g. "Routine METAR for KJFK observed on day 12 at 12:51 UTC.
   Wind from 180° at 4 kt. …".
5. Unrecognized content appends "Not decoded: …" naming the residual spans; sparse products
   (SIGMET/AIRMET/VAA/TCA) show a short best-effort summary with "partial decode" wording.

**Acceptance**: METAR/SPECI/TAF golden fixtures show value-aware explanations for wind,
visibility, temperature/dewpoint, pressure, time, station, clouds, weather; `summary`
renders live for all seven products; residuals named when present.

**Automated tests**: `decode_tac` unit tests (T0); decode-tac API contract + Vitest panel
(T0/T2); Playwright live-typing smoke (T2); live T3 sample.

**Browser wiring**: Same public decode-tac call as UJ-015 — no new origins (H4–H5 unchanged).

**S026 / EV-020 deepen**: Explanations use **glossary registry** English meanings for all seven
products (e.g. `OBSC` → “Obscured”, `TS` → “Thunderstorm”); optional OpenAIP/F3 **names** when
available. Tests: TC-F9-003/004; ADR-032.

---

### UJ-021: IWXXM Preview Pane + Terminator Quick Fix (F10)

**Actor**: Operator

**Goal**: Always know where Soft-preview / Live IWXXM output appears and what its status
means; fix a missing `=` terminator in one click.

**Steps**:

1. Enable **Soft-preview** and/or **Live IWXXM** in the workbench.
2. A **side-by-side IWXXM preview pane** (stacked below the editor under `lg`) shows the
   most recent pretty-printed IWXXM, a status badge — **Soft preview — not for publish**
   (plain-language soft-fail copy replacing raw `LAYER12_SOFT_FAIL`) or **Passed** — and a
   failed-span count linked to editor highlights.
3. Paste a single report without `=`: lint shows an **info-level** hint ("Reports in
   bulletins end with '=' — add it before publishing"); lint `ok` stays true when no error
   issues remain.
4. Click **"Add `=`"** on the console line (or the editor affordance on the hint span) —
   terminator appended; hint clears on next live pass.

**Acceptance**: Preview output never appears "somewhere unclear" — pane is the single
anchored destination with status; terminator hint is info-level with working one-click fix.

**Automated tests**: Vitest pane/status/quick-fix units (T0); Playwright preview + quick-fix
flow (T2); live T3 smoke.

**Browser wiring**: Reuses existing convert-preview and lint-tac calls (H4–H5 unchanged).

---

### UJ-022: Operator Convert/Validate After msgspec HTTP (F11)

**Actor**: Operator

**Goal**: Convert and validate continue to work from the workbench after high-churn routes
move to msgspec (ADR-026); any breaking JSON shapes are reflected in the FE.

**Steps**:

1. Open the workbench (no login — F21).
2. Convert a golden METAR (product/profile as today) — result card / preview pane populate.
3. Run validate on produced IWXXM — pass/fail + issues render.
4. Lint and decode update live (debounce) without Auth regressions.

**Acceptance**: Functional parity with pre-msgspec operator paths; TypeScript types match
OpenAPI/alias schemas; H4–H5 still green after Render redeploy; **no JWT required**.

**Automated tests**: Contract + Vitest (T2); Playwright H6′ (T3); live connectivity H4–H5.

---

### UJ-023: PyPI Release Tag → Install Smoke (F12–F14)

**Actor**: Maintainer / CI

**Goal**: Pushing a version tag publishes the package and a clean venv can install it.

**Steps**:

1. Tag `tac-validate-v0.1.0` (or `iwxxm-validate-v*` / `tac2iwxxm-v*`).
2. GitHub Actions OIDC trusted-publishing workflow builds sdist+wheel and publishes to PyPI.
3. CI (or follow-up job) `pip install <pkg>==0.1.0` in a clean venv and runs a one-liner smoke
   (lint / validate_iwxxm / convert).

**Acceptance**: Tag → publish → install smoke green for all three packages. **Tier: CI**.

---

## Developer Journeys

### UJ-DEV-001: Clone and Run Monorepo

Unchanged: single clone, `make install`, `make dev`, no submodules.

---

### UJ-DEV-002: Sync Vendor Schemas

Extended: sync may include **iwxxm-us** pin updates via manifest (in addition to wmo-im).

---

### UJ-DEV-003: Merge GIFTs Upstream — Deprecated

**Status**: Deprecated (ADR-014). `packages/gifts` removed at F6 cutover; REQ-014 deprecated.

---

### UJ-DEV-003b: Maintain tac2iwxxm + iwxxm-us Pins

**Actor**: Maintainer

**Goal**: Develop/test `packages/tac2iwxxm`; update IWXXM-US (and WMO) vendor pins safely.

**Steps**:

1. Implement/fix product or profile plugins under `packages/tac2iwxxm`.
2. Run package metrics/golden suite (M-parse / M-xsd / M-sch / M-golden / M-field).
3. When upstream US/WMO tags publish, run vendor sync → PR → review → merge.
4. Ensure backend adapter and frontend enums stay in sync with product/profile sets.

**Acceptance**: CI green for tac2iwxxm + conversion regression; manifest integrity passes.

---

### UJ-DEV-004: Package CI for tac-validate + iwxxm-validate

**Actor**: Developer / CI

**Goal**: Run unit and package tests for both validate packages in the uv workspace.

**Steps**:

1. `make test` (or package-scoped pytest) includes `packages/tac-validate` and
   `packages/iwxxm-validate`.
2. Schematron fixtures use vendored schemas; TAC rule fixtures cover at least METAR + one
   non-METAR product.
3. Backend thin-wrapper smoke tests call the packages (T2 optional).

**Acceptance**: CI gate fails if either package suite fails. **Tier: T0 / CI**.

---

### UJ-DEV-005: pip install Published Packages + Convert/Validate (F12–F14)

**Actor**: Developer / third party

**Goal**: Install from PyPI (or built wheel) and convert/validate without the monorepo.

**Steps**:

1. `python -m venv .venv && source .venv/bin/activate`
2. `pip install tac2iwxxm==0.1.0` — convert a sample METAR string to IWXXM.
3. `pip install tac-validate==0.1.0` — lint the same TAC; structured issues.
4. `pip install iwxxm-validate==0.1.0` — validate produced XML (schemas bundled).
5. Optionally `pip install 'tac2iwxxm[validate]'` — extras pull both validators.

**Acceptance**: All install+smoke steps succeed offline for schema-bundled validate.
**Tier: T0 / CI**.

---

### UJ-024: METAR/SPECI Lint Registry + Convert→Validate Golden (F15 / #732)

**Actor**: Operator / CI maintainer

**Goal**: Lint **METAR and SPECI** TAC with stable registry issue codes; convert accept
fixtures to IWXXM; validate with XSD+Schematron; see useful diagnostics on negative fixtures.
SPECI shares the METAR/SPECI rule pack and `metarSpeci` IWXXM schemas — adjacency is explicit
(product hint `speci`, Auto-detect, and AHL bulletin METAR/SPECI neighbors).

**Steps (operator — T2/T3)**:

1. Open workbench; set Product = **METAR** (or Auto-detect when unambiguous).
2. Paste a valid METAR accept fixture; run lint — `ok: true` or only `info` (e.g. terminator);
   all issue `code` values exist in the `tac-validate` registry catalog
   (`GET /api/v1/lint-issue-catalog` powers tooltips / catalog panel — E11-31).
3. Convert → Strict Validation — XSD+Schematron pass for pinned `iwxxm_version`.
4. Paste a known-bad METAR negative fixture — lint returns registry codes with useful messages
   (no silent success); hover/code tooltip resolves via catalog endpoint.
5. Repeat steps 1–4 with Product = **SPECI** (and at least one SPECI accept + one SPECI
   negative fixture); confirm Auto-detect chooses SPECI when the TAC starts with `SPECI`.

**Steps (CI — T0)**:

1. Registry CI: every emitted METAR/SPECI code is registered; catalog export in sync.
2. Golden pack: METAR **and** SPECI TAC → `tac2iwxxm` → `iwxxm-validate` (M-xsd / M-sch) green.
3. Negative pack: expected registry codes asserted for both products.
4. Adjacency: bulletin or paired fixtures where METAR and SPECI coexist do not mis-route
   product selection or silent-pass lint.

**Acceptance**: F15 criteria 1–6 (METAR + SPECI); coverage-matrix METAR/SPECI **R1–R8** closed
this cycle (HARD — E11-23/28); non–R-theme gaps only may defer with rationale + AskQuestion.
**Tier: T0 / T2 / T3** (T3 = workbench smoke when API/FE redeployed).

---

### UJ-031: TAF + SPECI Lint / Convert→Validate Golden (F20 / #735 / #734)

**Actor**: Operator / CI maintainer

**Goal**: Lint **TAF** and **SPECI** TAC with stable registry issue codes; convert accept
fixtures to IWXXM (`iwxxm:TAF` / `iwxxm:SPECI`); validate with XSD+Schematron; useful
diagnostics on negative fixtures. SPECI full quality bar (#734) is parallel to TAF (#735),
including Auto-detect / product-hint never mis-classifying SPECI↔METAR.

**Steps (operator — T2/T3)**:

1. Open workbench; set Product = **TAF** (or Auto-detect when unambiguous).
2. Paste a valid TAF accept fixture; run lint — registry codes only
   (`GET /api/v1/lint-issue-catalog` for tooltips).
3. Convert → Strict Validation — XSD+Schematron pass for pinned `iwxxm_version`; root `iwxxm:TAF`.
4. Paste a known-bad TAF negative fixture — lint returns registry codes (no silent success).
5. Repeat with Product = **SPECI** (accept + negative); confirm Auto-detect chooses SPECI for
   TAC starting with `SPECI`; root `iwxxm:SPECI`.

**Steps (CI — T0)**:

1. Registry CI: every emitted TAF/SPECI code is registered; catalog export in sync.
2. Golden pack: TAF **and** SPECI TAC → `tac2iwxxm` → `iwxxm-validate` (M-xsd / M-sch) green.
3. Negative pack: expected registry codes for both products (#735/#734 exceptional-rule tables).
4. Guidance audit: exceptional rules covered or explicitly deferred with rationale in coverage matrix.

**Acceptance**: F20 criteria 1–6; coverage-matrix TAF + SPECI rows updated; gaps filed or closed.
**Tier: T0 / T2 / T3** (T3 = workbench smoke when API/FE redeployed; H4–H5 when FE touched).

---

### UJ-025: Manual TAC Input Modes (TAC / AHL Bulletin / IWXXM COLLECT)

**Actor**: Operator

**Goal**: Use FileConverter **Manual TAC Input** modes correctly — TAC report convert,
AHL bulletin → `/convert-bulletin`, IWXXM COLLECT → `/ingest-collect` **501** placeholder —
with honest UX and required paste/upload auto-switch (ADR-024 / [#730](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/730)).

**Feature**: F7 (validation deepen; status remains Planned) — S016 / EV-012

**Relationship**: UI surface that routes operators onto UJ-011 (bulletin API) and the COLLECT
placeholder; does **not** replace H7 API gate design.

**Steps**:

1. Open operator workbench → Manual TAC Input (`data-testid="input-mode-group"`).
2. **T1 — TAC report**: Mode = TAC; Product = Auto-detect; paste single METAR; convert succeeds.
3. **T2 — AHL bulletin**: Mode = AHL; paste multi-report WMO AHL; convert hits
   `POST /api/v1/convert-bulletin`; UI shows bulletin summary and/or per-report results/errors
   (no silent fall-through to single `/convert`).
4. **T3 — Auto-switch**: With Mode = TAC, paste AHL-looking bulletin (or COLLECT XML) → mode
   switches to AHL (or COLLECT) with toast (“Detected AHL bulletin…” / “Detected IWXXM
   COLLECT…”). **Required** — fail if missing (E12-3).
5. **T4 — IWXXM COLLECT**: Mode = COLLECT; paste/upload COLLECT (`.xml` / `.gz` if supported)
   → `POST /api/v1/ingest-collect` → **501** surfaces as placeholder notice / warning toast
   (not success, not silent fail).
6. **T5 — gzip** (when UI accepts): `.gz` COLLECT or bulletin inflates then matches T2/T4.
7. **T6 — Read-only**: Finished/read-only session → mode buttons disabled.

**Acceptance**:

1. Mode toggle + helper copy visible; disabled when session read-only
2. TAC Auto-detect convert happy path
3. AHL path uses `/convert-bulletin` with summary/results
4. COLLECT path uses `/ingest-collect` and treats **501** as placeholder UX
5. Auto-switch on paste/upload works (T3)
6. Playwright **T1–T6** green (T2/T3); Vitest anchors remain green; staging H4–H5 + AHL + COLLECT
   501 (13-deploy-smoke)
7. Gaps vs H7 (API-only UJ-011) documented; defects filed as separate bugs linked from #730

**Automated tests**: Vitest (`inputKind`, `api` 501, `FileConverter` mode group); Playwright
`apps/e2e/` (TC-F7-007 T1–T6 hard); live H6′ / staging smoke. **Tier: T2 / T3 / H6′**.

---

### UJ-032: Load Golden Example → Convert / Validate (F7.g / #780)

**Actor**: Operator

**Goal**: One-click load a curated **demo / non-operational** TAC, AHL bulletin, or
happy-path IWXXM sample into the workbench — no paste — then convert or validate using
existing APIs.

**Feature**: F7 deepen (F7.g) — S021 / EV-016; status remains **Planned**

**Relationship**: Complements UJ-025 input modes and UJ-005/UJ-002 convert/validate paths;
does **not** add backend fixture APIs.

**Steps**:

1. Open operator workbench → Manual TAC Input / FileConverter.
2. Open **Examples** control (product-aware dropdown or chip row).
3. Select a named example for a product (e.g. METAR basic) → editor fills; `product` set;
   toast (“Loaded METAR basic example”); label shows demo / non-operational.
4. Convert (TAC mode) succeeds for happy-path goldens.
5. Select AHL bulletin example → `inputMode` = `ahl_bulletin`; body is multi-report bulletin.
6. Select IWXXM COLLECT/XML example → `inputMode` = `collect_iwxxm` (or validate path);
   body is happy-path IWXXM (soft-fail examples **out of v1**).
7. Repeat for remaining products; where only one in-repo fixture exists
   (SIGMET/AIRMET/VAA/TCA), catalog documents the gap — do not invent TAC.

**Acceptance**:

1. Catalog exposes ≥2 TAC examples per product **or** an explicit 1-fixture gap note
2. ≥1 AHL + ≥1 happy-path IWXXM loadable
3. Load sets body + product + inputMode when relevant
4. Vitest TC-F7-008 green (catalog completeness + click-to-load)
5. No backend / env / DB changes; examples are static FE assets
6. H4–H5 smoke when frontend deploys (optional Playwright smoke — Vitest is hard gate)

**Automated tests**: Vitest catalog + FileConverter Examples UX (TC-F7-008); staging H4–H5

---

### UJ-033: Privacy Notice + Settings + GPC (F22 / #783)

**Actor**: Anyone (public)

**Goal**: See a short first-visit privacy notice; open **Privacy settings** from the footer;
manage versioned preferences; confirm GPC is honored when present.

**Feature**: F22 — Solution A (no non-essential tracking)

**Steps**:

1. First visit (or after preference schema bump) — short notice with link to Privacy settings;
   equally clear dismiss / open settings (no dark patterns).
2. Open footer **Privacy settings** — see categories actually in use (at minimum: necessary +
   disclosure of IndexedDB work history / preference storage).
3. Non-essential categories (if present) default off; reject as easy as accept.
4. With `navigator.globalPrivacyControl === true`, sale/sharing / targeted-advertising opt-outs
   are forced on and confirmation is visible.
5. Withdraw / change preferences anytime; applicable non-essential storage cleared on withdraw.

**Acceptance**: Settings always reachable; preferences persist with `schemaVersion`; no CMP;
no marketing/analytics scripts in v1; IndexedDB history disclosed.

**Automated tests**: Vitest preference store + GPC (TC-F22-001..003); Playwright smoke (T2);
H4–H5 when FE deploys.

---

### UJ-034: SIGMET + VA SIGMET Lint / Convert→Validate Golden (F23 / #733 / #739)

**Actor**: Operator / CI maintainer

**Goal**: Lint **General SIGMET** and **VA SIGMET** TAC with stable registry issue codes;
convert accept fixtures to IWXXM (`iwxxm:SIGMET` / `iwxxm:VolcanicAshSIGMET`); validate with
XSD+Schematron; useful diagnostics on negative fixtures. VA path stays on API
`product=sigmet` with content-selected root (not a separate enum; not VAA).

**Feature**: F23 (+ deepen F6.d / F12) — S025 / EV-019

**Steps (operator — T2/T3)**:

1. Open workbench; set Product = **SIGMET** (or Auto-detect when unambiguous).
2. Paste a valid general SIGMET accept fixture; run lint — registry codes only
   (`GET /api/v1/lint-issue-catalog` for tooltips).
3. Convert → Strict Validation — XSD+Schematron pass for pinned `iwxxm_version`; root
   `iwxxm:SIGMET`.
4. Paste a known-bad SIGMET negative fixture — lint returns registry codes (no silent success).
5. Paste a valid **VA SIGMET** accept fixture (still Product = SIGMET) — convert root
   `iwxxm:VolcanicAshSIGMET`; never emit VAA advisory root.
6. Confirm adjacency: VA phenomenon / WV-shaped TAC does not silent-succeed as general
   `iwxxm:SIGMET`; VAA advisory TAC is not treated as VA SIGMET.

**Steps (CI — T0)**:

1. Registry CI: every emitted SIGMET / VA SIGMET code is registered; catalog export in sync.
2. Golden pack: general + VA SIGMET TAC → `tac2iwxxm` → `iwxxm-validate` (M-xsd / M-sch) green.
3. Negative pack: expected registry codes for both (#733/#739 exceptional-rule tables).
4. Guidance audit: exceptional rules covered or explicitly deferred with rationale in coverage
   matrix (themes G1–G3 / V1–V3 / C1).

**Acceptance**:

1. TC-F23-001..006 green (or deferred with rationale in matrix)
2. Roots match `iwxxm:SIGMET` / `iwxxm:VolcanicAshSIGMET` for pinned versions (esp. 2025-2)
3. No new HTTP product enum / routes (E19-13=A)
4. F7 remains Planned — smoke only for product path under F23; **additive FE catalog
   filters/copy for SIGMET (+ VA) tags** (E19-17=B amends E19-14)
5. H1–H3 if API ships; **H4–H5 required** when FE touched (E19-7 / E19-17)

**Automated tests**: Package/CI TC-F23-001..004/006; API/workbench smoke TC-F23-005;
staging H4–H5 when FE redeployed.

---

### UJ-035: AIRMET Lint / Convert→Validate WMO Golden (F24 / #731)

**Actor**: Operator / CI maintainer

**Goal**: Lint AIRMET TAC with registry codes; convert accept fixtures (esp. WMO
`airmet-A6-1a-TS`) to `iwxxm:AIRMET` that is **`canonicalize_xml`-equal** to the vendor
IWXXM example **under default convert settings** (`profile=annex3`, default pinned
`iwxxm_version`); XSD+Schematron pass; useful diagnostics on negatives.

**Feature**: F24 (+ deepen F6 / F12) — S026 / EV-020

**Steps (operator — T2/T3)**:

1. Open workbench; Product = **AIRMET** (or Auto-detect).
2. Load / paste WMO AIRMET accept TAC; lint — registry codes only.
3. Convert → Strict Validation — pass; root `iwxxm:AIRMET`; geometry present (not nil-only).
4. Paste a known-bad AIRMET negative — lint returns registry codes (no silent success).
5. Optionally open decode (UJ-020) — token meanings from glossary (not category-only labels).

**Steps (CI — T0)**:

1. Registry completeness for AIRMET codes.
2. Golden: vendor `airmet-A6-1a-TS.tac` → convert (defaults) → `canonicalize_xml` == vendor XML.
3. Negatives + coverage-matrix AIRMET themes closed or deferred with rationale.

**Acceptance**: TC-F24-001..005 green; H4–H5 when FE touched.

**Automated tests**: TC-F24-*; deepen TC-F9 for AIRMET glossary tokens.

---

### UJ-036: WMO-Passing Examples Catalog + METAR/SPECI/TAF Goldens (F25)

**Actor**: Operator / CI maintainer

**Goal**: METAR/SPECI/TAF convert matches WMO vendor XML under **default** settings; workbench
**Examples** marks **strict passers** (`wmoPass`) for demos that pass that bar (plus SIGMET
keepers from F23; AIRMET when F24 passes). **EV-024 deepen**: official WMO stems that are not
yet equal may still appear as **WMO reference** samples — see **UJ-039** / ADR-032 amend.
Translation-failed fixtures remain excluded from happy-path Examples.

**Feature**: F25 (+ deepen F6 / F7.g / F15 / F20) — S026 / EV-020; catalog tiers S031 / EV-024

**Steps (operator)**:

1. Open **Examples** — strict passers and (when EV-024 ships) WMO reference samples for
   in-scope products; UI distinguishes the two.
2. Load METAR / SPECI / TAF / SIGMET / AIRMET (when ready) WMO example — editor + product set;
   demo banner shows non-operational provenance pointing at vendor (or mirrored fixture).
3. For strict passers: Convert → Strict Validation succeeds; decode shows glossary English
   (UJ-020 deepen). Reference samples may not convert-equal yet.

**Steps (CI)**:

1. Golden pack: listed WMO TAC→XML cases equal under defaults + `canonicalize_xml` (strict).
2. Catalog unit tests: provenance policy; tier badges; no translation-failed in happy-path.
3. Deepen TC-F7-008; **UJ-039** / TC-EV024 for expanded sample menu.

**Acceptance**: TC-F25-001..004 green; H4–H5 when FE redeployed; EV-024 sample menu via UJ-039.

**Automated tests**: TC-F25-*; TC-F7-008 deepen; TC-F9 deepen; TC-EV024-*.

---

### UJ-039: Load Official WMO IWXXM Examples from Sample Menu (S031 / EV-024)

**Actor**: Operator / CI maintainer

**Goal**: Official WMO IWXXM package examples (vendor pin `IWXXM/examples/`, product-in-scope
stems with TAC peers) are available from the workbench **Examples / sample menu** and load
into the editor. Operators can try the real WMO corpus without waiting for encode parity.
Strict passers remain badged; non-equal official stems load as **WMO reference** samples.
Encode/lint/SCH gaps are tracked as child issues — not blocked by menu listing.

**Feature**: Deepen F25 / F7.g (+ F6/F2 wiring) — S031 / EV-024 · Issues #804 / #807 / #773
(exclude #806)

**Steps (operator)**:

1. Open **Examples / sample menu** — see official WMO stems for in-scope products (beyond the
   prior subset), each with provenance to vendor / mirrored fixture paths.
2. Distinguish **strict passer** vs **WMO reference** (badge or equivalent copy).
3. Select a stem → TAC loads into the editor; product/profile set appropriately; banner shows
   non-operational / WMO-example provenance.
4. Optionally convert / validate — reference samples need not be `canonicalize_xml`-equal yet.
5. Confirm translation-failed / quarantine examples are **not** offered as happy-path samples.
6. Confirm IWXXM-US examples are **not** mixed into the WMO sample list.

**Steps (CI)**:

1. Catalog Vitest: in-scope WMO stems with TAC peers are registered (or explicitly deferred in
   `FIXTURE_GAPS.md` with rationale + child issue link).
2. Load-path unit/smoke: selecting a registered stem populates editor body from fixture.
3. Validate/CI matrix covers wired stems (TC-EV024 validate surface).
4. H4–H5 when FE catalog ships to deployed static site.

**Acceptance**: TC-EV024-004..006 green; deepen TC-F25-003 / TC-F7-008; `FIXTURE_GAPS.md`
accurate; ADR-032 amend honored.

**Automated tests**: TC-EV024-*; TC-F25-003 deepen; examplesCatalog Vitest.

---

### UJ-037: VAA Lint / Convert→Validate WMO Golden (F26 / #736)

**Actor**: Operator / CI maintainer

**Goal**: Lint VAA TAC with registry codes; convert accept fixtures (esp. WMO
`va-advisory-A7-2`) to `iwxxm:VolcanicAshAdvisory` that is **`canonicalize_xml`-equal** to the
vendor IWXXM example **under default convert settings**; XSD+Schematron pass; useful
diagnostics on negatives. Never confuse with VA SIGMET (`iwxxm:VolcanicAshSIGMET`).

**Feature**: F26 (+ deepen F6.f / F12 / F7.g) — S027 / EV-021

**Steps (operator — T2/T3)**:

1. Open workbench; Product = **VAA** (or Auto-detect).
2. Load / paste WMO VAA accept TAC; lint — registry codes only.
3. Convert → Strict Validation — pass; root `iwxxm:VolcanicAshAdvisory`.
4. Paste a known-bad VAA negative — lint returns registry codes (no silent success).
5. Examples control lists VAA **strict passers** when they pass the golden bar (E21-3);
   additional official WMO VAA stems may load as **reference** samples per **UJ-039** / ADR-032 amend.

**Steps (CI — T0)**:

1. Registry completeness for VAA codes.
2. Golden: vendor `va-advisory-A7-2.tac` → convert (defaults) → `canonicalize_xml` == vendor XML.
3. Exceptional + translation-package TAC themes as fixtures; negatives + matrix V1–V3/C1.

**Acceptance**: TC-F26-001..006 green; H4–H5 when FE touched.

**Automated tests**: TC-F26-*; deepen TC-F7-008 / UJ-032.

---

### UJ-038: TCA Lint / Convert→Validate WMO Golden (F27 / #737)

**Actor**: Operator / CI maintainer

**Goal**: Lint TCA TAC with registry codes; convert accept fixtures (esp. WMO
`tc-advisory-A2-2`) to `iwxxm:TropicalCycloneAdvisory` that is **`canonicalize_xml`-equal**
under defaults; XSD+Schematron pass; negatives diagnostic. Never confuse with TC SIGMET
(`iwxxm:TropicalCycloneSIGMET`).

**Feature**: F27 (+ deepen F6.f / F12 / F7.g) — S027 / EV-021

**Steps (operator — T2/T3)**:

1. Open workbench; Product = **TCA** (or Auto-detect).
2. Load / paste WMO TCA accept TAC; lint — registry codes only.
3. Convert → Strict Validation — pass; root `iwxxm:TropicalCycloneAdvisory`.
4. Paste a known-bad TCA negative — lint returns registry codes.
5. Examples control lists TCA **strict passers** when they pass the golden bar (E21-3);
   additional official WMO TCA stems may load as **reference** samples per **UJ-039** / ADR-032 amend.

**Steps (CI — T0)**:

1. Registry completeness for TCA codes.
2. Golden: vendor `tc-advisory-A2-2.tac` → convert (defaults) → `canonicalize_xml` == vendor XML.
3. Exceptional + translation-package TAC themes; negatives + matrix T1–T3/C1.

**Acceptance**: TC-F27-001..006 green; H4–H5 when FE touched.

**Automated tests**: TC-F27-*; deepen TC-F7-008 / UJ-032.

---

### UJ-027: Dissemination drawer — multi-DB upload (F16 / #729; multi-select #785)

**Actor**: Anyone (public — F21; no login)
**Goal**: Convert (or drag-drop IWXXM/TAC) and send **selected** file(s) to a user-supplied
database via one-shot URI.

**Steps**:
1. Convert TAC → IWXXM **or** drag-drop existing IWXXM/TAC into the workbench/drawer (no login).
   Multiple conversion/drop results may appear as **export candidates** (current-session +
   drops only — not Finished IndexedDB history).
2. Open **Dissemination** drawer; choose DB sink (Postgres / MySQL|MariaDB / SQL Server / SQLite).
3. In **Export selection**, review candidates (name, product, size/status, source); select
   subset (checkboxes / select-all / clear). Empty selection keeps Disseminate / Preflight-only
   disabled. Sole candidate is auto-selected (panel may be collapsed).
4. Paste destination **URI only**. Optionally run **Preflight only** on the selection, or
   proceed with primary **Disseminate** (interleaved per file: `/preflight` → `/send` → next;
   N ≤ 20).
5. Watch per-file progress (mail travels along an arrow to the sink; green check / red fail).
   Under `prefers-reduced-motion`, text-only status replaces the graphic. One failure must not
   stop remaining files; results stay visible.
6. If a file needs DDL / create-if-missing after preflight diffs, use that path (optional
   confirm) then continue Disseminate for remaining green files.
7. On success, local session may mark Finished with send ref (no secrets stored; IndexedDB only).

**Errors**: Auth/SSL/allowlist/private-IP/schema mismatch — actionable drawer messages; Send
blocked for non-green files; over-cap (>20) shows clear error.
**Tier**: T2 / T3 / H6′. **Tests**: TC-F16-001..005.

### UJ-028: Dissemination drawer — WIS2 publish (F17 / #2)

**Actor**: Anyone (public — F21; no login)
**Goal**: Publish **selected** IWXXM file(s) to WIS2 (MQTT notify + HTTP dataset).

**Steps**:
1. From drawer, select **WIS2**. Use the same **Export selection** multi-select as UJ-027
   when multiple candidates exist (current-session + drops; ≤20).
2. For staging: use project wis2box harness (Render/Docker). For live: paste BYOC endpoint creds
   (memory-only).
3. Preflight connectivity/topic checks → Send (N sequential calls when multi-selected).
4. Confirm notification + retrievable dataset (staging automated; live BYOC before cycle close).

**Tier**: T2 / T3 / H6′. **Tests**: TC-F17-001..002.

### UJ-029: Dissemination drawer — EDIS → RTH Washington (F18 / #6)

**Actor**: Anyone (public — F21; no login) with BYOC gateway credentials
**Goal**: Submit **selected** EDIS-compliant ASCII + WMO headers to RTH Washington.

**Steps**:
1. Select **EDIS** in drawer; use the same **Export selection** multi-select as UJ-027 when
   multiple candidates exist (current-session + drops; ≤20).
2. Paste SMTP/gateway settings (one-shot).
3. Preview formatted message (ASCII-only, headers).
4. Preflight → Send (N sequential when multi-selected); redact secrets in errors/logs.

**Tier**: T2 / T3 (live BYOC). **Tests**: TC-F18-001..002.

### UJ-030: Dissemination drawer — AMHS / SWIM / AFS (F19)

**Actor**: Anyone (public — F21; no login)
**Goal**: Send **selected** file(s) via AMHS, SWIM, or AFS adapter using BYOC params in the
same drawer (same export selection contract as UJ-027).

**Steps**: Select adapter → select files if multi-candidate → paste BYOC connection params →
preflight → send (SSRF/allowlist; N sequential when multi-selected).
**Tier**: T2 / T3. **Tests**: TC-F19-001..003.

---

## Operations Journeys

### UJ-OPS-001: Deploy Render stack (API + static + F8 worker)

Topology: API + static frontend + **Background Worker** (ADR-018). After F6: API image includes
tac2iwxxm + validate packages (not gifts); frontend build includes product/profile controls
(M8). After F7: frontend includes CodeMirror workbench; API includes decode/spans/preview;
**no** admin static routes; BYO env. Redeploy API before frontend when CORS/API contract changes.
Deploy worker after F8 migrations. Signoff includes UJ-005/013/015–019 live coverage plus F8
live smoke (T7.4) when scheduled.

---

### Session changelog

- S008 (2026-07-12): F6 UJ-001/002/005–010; UJ-DEV-003 deprecated → 003b; T3 seven products
- S008 amend (2026-07-12): UJ-002/005–007 package wiring; UJ-011/012 T2; UJ-013/014 Planned stubs;
  UJ-DEV-004
- S008 05 (2026-07-12): UJ-014 + UJ-OPS-001 aligned to ADR-018 F8 worker (D-S008-05-batch1)
- S011 / EV-008 (2026-07-13): UJ-004 unified filter; UJ-013 expanded; UJ-015–019 added; UJ-014
  Implemented note; admin journeys retired via UJ-019
- S014 / EV-010 (2026-07-18): UJ-022/023 + UJ-DEV-005 (F11–F14 msgspec HTTP + PyPI)
- S015 / EV-011 (2026-07-19): UJ-024 METAR/**SPECI** lint registry + convert→validate golden
- S016 / EV-012 (2026-07-20): UJ-025 Manual TAC Input modes (ADR-024 / #730)
  (F15 / #732; SPECI adjacency explicit; catalog via `GET /lint-issue-catalog` E11-31)
- S019 / EV-014 (2026-07-21): UJ-027–030 dissemination drawer (F16–F19; #729/#2/#6)
- S020 / EV-015 (2026-07-22): UJ-031 TAF + SPECI lint / convert→validate golden (F20; #735/#734)
- S023 / EV-017 (2026-07-27): UJ-003 superseded; UJ-001/004/018 public + IndexedDB; UJ-033 privacy
  (F21/F22; #783)
- S024 / EV-018 (2026-07-28): UJ-027 multi-file export selection (F16 deepen; #785); UJ-028–030
  reuse same selection contract
- S025 / EV-019 (2026-07-29): UJ-034 SIGMET + VA SIGMET lint / convert→validate golden
  (F23; #733/#739)
- S026 / EV-020 (2026-07-29): UJ-035 AIRMET WMO golden (F24/#731); UJ-036 WMO-passing
  Examples + METAR/SPECI/TAF parity (F25); deepen UJ-020/032
- S027 / EV-021 (2026-07-29): UJ-037 VAA WMO golden (F26/#736); UJ-038 TCA WMO golden
  (F27/#737); deepen UJ-032 / TC-F7-008
