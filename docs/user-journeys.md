# User Journeys

> **Project**: METAR to IWXXM Converter
> **Source**: feature-list.md; S008 F6 + realtime amend; S011 / EV-008 F7 operator UI;
> S013 / EV-009 F9/F10 decode + preview UX; S014 / EV-010 package publish + msgspec HTTP;
> S015 / EV-011 F15 METAR lint registry + #732 quality; S016 / EV-012 Manual TAC Input modes (#730);
> S019 / EV-014 dissemination epic F16–F19; S020 / EV-015 F20 TAF+SPECI quality (#735/#734);
> S023 / EV-017 public app + privacy (#783); S038 / EV-031 platform independence F30/F31;
> S040 / EV-032 F32 VONA + #846 corpus
> **Last updated**: 2026-08-22 (EV-063 semantic + exchange profiles — UJ-069)

Product-facing journeys (UJ-*) describe end-user flows. Developer journeys (UJ-DEV-*)
describe monorepo workflows introduced by migration features M1–M6 and F6.

## Journey Index

| ID | Journey | Entry point | Feature | E2E tier |
|----|---------|-------------|---------|----------|
| UJ-001 | Convert METAR via UI (shorthand) | apps/frontend | F6+F21 Amended | T2 / **T3** |
| UJ-002 | Validate IWXXM output (`iwxxm-validate`) | apps/frontend / API | F2+F6+F21 | T2 / **T3** |
| UJ-003 | Register and login | apps/frontend | Auth | **Restored (F31)** — see UJ-046; was Superseded F21 |
| UJ-004 | Resume & browse METAR work history (hybrid) | apps/frontend | F5+F7+F31 | T2 / **T3** |
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
| UJ-018 | Unified sessions persist/resume (hybrid local + server) | apps/frontend | F5+F7+F31 | T2 / **T3** |
| UJ-019 | Admin routes removed / BYO operator surface | apps/frontend | F7 / M4 | T2 / **T3** |
| UJ-020 | Value-aware decode + plain-language summary | apps/frontend | F9 | T0 / T2 / **T3** |
| UJ-021 | IWXXM preview pane + terminator quick fix | apps/frontend | F10 | T2 / **T3** |
| UJ-022 | Operator convert/validate after msgspec HTTP | apps/frontend | F11 | T2 / **T3** / H6′ |
| UJ-023 | PyPI release tag → install smoke | CI / maintainer | F12–F14 | CI |
| UJ-024 | METAR/SPECI lint registry + convert→validate golden | UI / API / CI | F15 (+F6/F12) | T0 / T2 / **T3** |
| UJ-025 | Manual TAC Input modes (TAC / AHL / COLLECT) | apps/frontend | F7 (ADR-024) | T2 / **T3** / H6′ |
| UJ-026 | METAR REMARKS retain / exclusion (#667) | UI / API / package | F6 | T0 / T2 |
| UJ-027 | Dissemination drawer — multi-DB upload (BYOC URI) + multi-select | apps/frontend | F16 | T2 / **T3** / H6′ (+ **live local** Compose); **operator UI deferred EV-042** — harness only until #898 |
| UJ-028 | Dissemination drawer — WIS2 publish | apps/frontend | F17 | T2 / **T3** / H6′; **operator UI deferred EV-042** until #898 |
| UJ-029 | Dissemination drawer — EDIS → RTH Washington | apps/frontend | F18 | T2 / **T3**; **operator UI deferred EV-042** until #898 |
| UJ-030 | Dissemination drawer — AMHS / SWIM / AFS | apps/frontend | F19 | T2 / **T3**; **operator UI deferred EV-042** until #898 |
| UJ-031 | TAF + SPECI lint / convert→validate golden | UI / API / CI | F20 (+F6/F12) | T0 / T2 / **T3** |
| UJ-032 | Load golden example → convert / validate | apps/frontend | F7 (#780) | T0 / T2 / H4–H5 |
| UJ-033 | Privacy notice + settings + GPC | apps/frontend | F22 | T0 / T2 / H4–H5 |
| UJ-034 | SIGMET + VA SIGMET lint / convert→validate golden | UI / API / CI | F23 (+F6/F12) | T0 / T2 / **T3** |
| UJ-035 | AIRMET lint / convert→validate WMO golden | UI / API / CI | F24 (+F6/F12) | T0 / T2 / **T3** |
| UJ-036 | WMO-passing Examples catalog + METAR/SPECI/TAF goldens | apps/frontend / CI | F25 (+F7.g) | T0 / T2 / **T3** / H4–H5 |
| UJ-037 | VAA lint / convert→validate WMO golden | UI / API / CI | F26 (+F6.f/F12) | T0 / T2 / **T3** |
| UJ-038 | TCA lint / convert→validate WMO golden | UI / API / CI | F27 (+F6.f/F12) | T0 / T2 / **T3** |
| UJ-039 | Load official WMO IWXXM examples from sample menu | apps/frontend / CI | F25/F7.g deepen (EV-024) | T0 / T2 / **T3** / H4–H5 |
| UJ-040 | Convert METAR/SPECI with structured iwxxm-us REMARKS | library / API / CI | F6.b deepen (EV-025) | T0 / T2 (+ T3 smoke if API ships) |
| UJ-041 | Promote sigmet-multi-location-VA to WMO passer | library / CI / catalog | F23 deepen (EV-025 soft; EV-026 equality) | T0 / T2 |
| UJ-042 | Official WMO TAC peers decode with empty/allowlisted residuals | library / CI / workbench | F25/F9/F7.g deepen (EV-027) | T0 / T2 / **T3** / H4–H5 |
| UJ-043 | Eight-family rules gap sweep + SWXA quality | UI / API / CI | F28 + deepen (EV-029) | T0 / T2 / **T3** / H4–H5 if FE |
| UJ-044 | Rule matrix harness + TC / VAA–TCA residuals | CI / workbench | F29 + deepen (EV-030) | T0 / T2 / H4–H5 if FE |
| — | **EV-023 #800** — no new UJ; deepen UJ-001/005/006/016 + TC-EV023-001..009 | library / API / CI | F6/F2/F12/F13 | T0 / T2 (+ T3 smoke if API ships) |
| UJ-045 | Guest convert + loss-of-progress notice + local history | apps/frontend | F31+F21 | T2 / **T3** / H4–H5 |
| UJ-046 | Login → auto-upload drafts → server sessions | apps/frontend | F31+F30 | T2 / **T3** / H4–H5 |
| UJ-047 | Privacy prefs ↔ IndexedDB / Auth cookies (deepen UJ-033) | apps/frontend | F22+F31 | T0 / T2 / H4–H5 |
| UJ-048 | Ops: DOKS cutover smoke (API + FE + worker) | DOKS / ops | F30 | T3 / H0–H5 |
| UJ-049 | VONA lint / convert→validate + F7 product surface | apps/frontend / API / CI | F32 (+F6/F7/F12) | T0 / T2 / **T3** / H4–H5 |
| UJ-050 | IWXXM version picker Latest / Previous labels | apps/frontend | F4+F7 deepen (EV-038 / #854) | T2 / **T3** / H4–H5 |
| UJ-051 | Secure mass file/folder ingest (auth + caps) | apps/frontend | F33 | T2 / **T3** / H4–H5 |
| UJ-052 | Operator queue + keyboard/batch convert·validate churn | apps/frontend | F7 deepen (EV-042) | T2 / **T3** / H4–H5 |
| UJ-053 | Operator UI has no dissemination destinations | apps/frontend | F16–F19 deepen (EV-042) | T2 / **T3** / H4–H5 |
| UJ-054 | Operator Help → one-pager / handbook | apps/frontend | F7 deepen (EV-047 / #956/#957) | T0 / T2 / **T3** |
| UJ-055 | Operator UI + API docs free of internal planning vocabulary | apps/frontend / OpenAPI | F7+F21 deepen (EV-048 / #951) | T0 / T2 / **T3** |
| UJ-056 | Browse official corpus Quality metrics tab | apps/frontend | F7.q deepen (EV-054 / #836; EV-055 / #982+#980+#979; EV-056 / #988; EV-058 / #983) | T0 / T2 / **T3** / H4–H5 |
| UJ-057 | Accumulate conversions → Download all ZIP | apps/frontend | F7.r deepen (EV-057 / #903) | T0 / T2 / **T3** / H4–H5 |
| UJ-058 | Validate existing IWXXM (paste / upload; no TAC) | apps/frontend | F7.s deepen (EV-057 / #838) | T0 / T2 / **T3** / H4–H5 |
| UJ-059 | AHL bulletin lint/validate without heading flood | apps/frontend / API | F7/F6 deepen (EV-060 / #1001) | T0 / T2 / **T3** / H4–H5 |
| UJ-060 | IWXXM product pass-through (lint + F2; no TAC convert) | apps/frontend / API | F7.t (EV-060 / #1003) | T0 / T2 / **T3** / H4–H5 |
| UJ-061 | Profile labeled at converter top (Annex 3 / IWXXM-US) | apps/frontend | F7/F6 deepen (EV-060 / #1002) | T0 / T2 / **T3** / H4–H5 |
| UJ-062 | Bulletin ID + Issuing Center labeled and applied | apps/frontend / API | F7/F6 deepen (EV-060 / #1005) | T0 / T2 / **T3** / H4–H5 |
| UJ-063 | Conversion log_level changes logger verbosity | UI / API | F29 deepen (EV-060 / #1004) | T0 / T2 |
| UJ-064 | Validate IWXXM shows item-by-item readable decode | apps/frontend | F2/F9/F10 deepen (EV-061 / #1010) | T0 / T2 / **T3** / H4–H5 |
| UJ-065 | AHL bulletin decode + convert end-to-end | apps/frontend / API | F6/F7 deepen (EV-061 / #1012) | T0 / T2 / **T3** / H4–H5 |
| UJ-066 | Product Type + Profile bars no-wrap / aligned | apps/frontend | F7.u (EV-061 / #1013) | T0 / T2 / **T3** / H4–H5 |
| UJ-067 | Conversion parameter bar aligned with mode selects | apps/frontend | F7.u (EV-061 / #1013) | T0 / T2 / **T3** / H4–H5 |
| UJ-068 | Lint & validation catalog top-level tab/page | apps/frontend | F7.v/F15 (EV-061 / #1014; **EV-062 / #1017** deepen) | T0 / T2 / **T3** / H4–H5 |
| UJ-069 | Convert with semantic profile → package with exchange profile | API / library / optional UI (#1024) | F35+F36 (EV-063 / #912) | T2 / **T3** (API); H4–H5 if #1024 |
| UJ-DEV-009 | stage→main promote requires full CI+E2E+lint+typecheck | GitHub Actions / branch protection | F34 deepen (EV-061 / #1015) | CI |
| UJ-OPS-002 | Prod apex redirects to app host | DNS / ingress / ops | F30 deepen (EV-057 / #948) | T3 / ops smoke |
| UJ-DEV-001 | Clone and run monorepo | `git clone` + `make dev` | M1, M5 | T0 |
| UJ-DEV-002 | Sync vendor schemas | Scheduled Action / manual | M2, M6, F6 | CI |
| UJ-DEV-003 | ~~Merge GIFTs upstream~~ | — | M3 | **Deprecated** (ADR-014) |
| UJ-DEV-003b | Maintain tac2iwxxm + iwxxm-us pins | Maintainer workflow | F6, M2 | CI |
| UJ-DEV-004 | Package CI for tac-validate + iwxxm-validate | `make test` / CI | F2, F6, M5 | T0 / CI |
| UJ-DEV-005 | pip install published packages + convert/validate | clean venv | F12–F14 | T0 / CI |
| UJ-DEV-006 | Rust crate CI (fmt/clippy/test + maturin) | `make rust-check` / CI | F13, F14 | T0 / CI |
| UJ-DEV-007 | Slim husky — lint commit + fast-unit push | husky / make install-hooks | M5 deepen (EV-047 / #833) | T0 |
| UJ-DEV-008 | Converter perf regression blocks PR | CI perf gate | F6 deepen (EV-047 / #834) | T0 / CI |
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
| API (DOKS prod) | `LIVE_API_URL` | `https://api.tac-to-iwxxm.com` |
| Frontend (DOKS prod) | `LIVE_FRONTEND_URL` / `PLAYWRIGHT_BASE_URL` | `https://app.tac-to-iwxxm.com` |

Until Render decommission (TC-F30-005), historical onrender.com URLs remain in
[ops/render-decommission-archive.md](ops/render-decommission-archive.md). After cutover (UJ-048),
`LIVE_*` must point at DOKS public DNS.

**F6 T3 requirement**: All **seven** products (AIRMET, METAR, SIGMET, SPECI, TAF, VAA, TCA)
must pass annex3 convert via UI (UJ-005 parametrize) and API smoke (UJ-006). US profile
(`iwxxm_us`) T3 cases for METAR/SPECI/TAF where schemas apply (UJ-007).

---

## Product Journeys

### UJ-001: Convert METAR via UI (shorthand)

**Actor**: Anyone (public convert — F21 Amended; login optional for long-term storage only)

**Goal**: Upload or paste METAR TAC and receive IWXXM XML (default product/profile).

**Feature**: F6 (+ F21 Amended). Full product/profile matrix is **UJ-005**. History via **UJ-004** /
**UJ-045** (guest) or **UJ-046** (logged-in).

**Steps**:

1. Open frontend in browser (no login required for convert).
2. Drag-drop `.tac` file or paste manual text (METAR/SPECI).
3. Optionally leave product on **auto** / METAR and profile **annex3** (defaults).
4. **#664 (EV-005)**: Optionally type an **Output filename** for manually entered TAC.
5. Choose **Convert**, **Convert&Send**, or **Upload to Database**.
6. View output; each result card shows **TAC-derived title**, optional **Line N of M** for
   multi-line manual input, prominent **Source TAC** panel, and download filename when it
   differs (#655 / EV-007). #555 replace-on-success and error log panel behavior unchanged.
7. On convert failure after F6 cutover: structured error only — **no gifts rollback**.
8. If guest: work may auto-save to IndexedDB (UJ-004/045) with loss-of-progress notice.
   If logged in: may sync to DO Postgres sessions (UJ-046).

**Acceptance**: METAR converts without error via tac2iwxxm; **no JWT required for convert**;
schema/Schematron pass for selected version; UX behaviors from #555/#664 preserved.

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

### UJ-003: Register and Login — Restored (F31)

**Status**: **Restored** under S038 / EV-031 / F31 for **long-term storage** only. Was
**Superseded** by F21 (S023 / EV-017 / #783) public-only path.

**Goal**: Optional Supabase Auth login/logout so work sessions can persist on DO Postgres.

**Canonical flow**: **UJ-046** (login + auto-upload). Convert remains public (**UJ-001**).

**Automated tests**: Restore/adapt `apps/e2e/auth.e2e.spec.ts` for login happy path; convert
still works without JWT.

**EV-060 / #1006 UAT**: Facilitated UAT plus Playwright covering **register, login, logout,
and logged-in session persist**. Guest/public convert (F21 / UJ-001) still works without an
account. Test accounts only — no production PII in fixtures. [Corpus: product §F31]
[Corpus: tests]

---

### UJ-004: Resume & Browse METAR Work History

**Actor**: Guest (same browser) or logged-in operator

**Goal**: Resume Draft/WIP and browse Finished/Failed METAR/SPECI work from **hybrid** storage
(F5 / F7.i / F31 — S038): IndexedDB when guest; DO Postgres when logged in.

**Deepen**: Guest path + notice = **UJ-045**; login + auto-upload = **UJ-046**.

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

**Deepen (S032 / EV-025)**: New structured REMARKS codecs (#810–#812 + adjacent) must not
weaken malformed-path diagnostics — unknown / broken US remark tokens still surface issues;
partial success may encode recognized elements and retain remainder (UJ-026).

---

### UJ-026: METAR REMARKS retain / exclusion (#667)

**Goal**: Remark portion of METAR/SPECI is not silently ignored ([#667](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/667)).

**Acceptance**:
1. `profile=annex3` with `RMK` → convert succeeds with `ConvertIssue` code `REMARKS_EXCLUDED` (info).
2. `profile=iwxxm_us` → structured AO2/SLP/PK WND still emitted; unparsed remainder retained in
   `iwxxm-us:humanReadableText` (never drop).
3. Additive `T########` / `P####` parsed into IR and retained in free-text until structured codecs land.

**Tier**: T0 / T2 primarily.

**Deepen (S032 / EV-025)**: As dig ❌ types gain structured codecs (UJ-040), acceptance (2)
expands to those types; any still-unparsed tokens remain in `humanReadableText` (never drop).

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

**Status**: **Implemented** (S008 / ADR-018/019); **amended S038 / EV-031 / F30** — store/
quarantine on **DigitalOcean Postgres** via `DATABASE_URL` (not Supabase PostgREST).
Worker ingest → pipeline → DO store or separate quarantine on Schematron/convert fail.
No push sinks in v1. Deployable moves Render → **DOKS** with F30.

**Acceptance**: Worker processes HTTPS/object-prefix fixture feed; pass rows in
`iwxxm_ingest_results`; fail rows in `iwxxm_ingest_quarantine`; writers use private
`DATABASE_URL` / machine credentials (not operator JWT; not Supabase service-role DB).
Live: T7.4 / Phase 6 gate (may remain deferred); TC-F30-003 covers DO write path.

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

**S034 / EV-027 deepen**: Official WMO textbook TAC peers must leave **no unexpected
residuals** after decode — see **UJ-042** / TC-EV027 residual matrix (allowlist + child issue
when not fixable in-cycle).

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

1. Tag `{package}-v{version}` matching `pyproject.toml` (e.g. `tac-validate-v0.1.1`,
   `iwxxm-validate-v0.1.1`, `tac2iwxxm-v0.1.1`). First public release was `0.1.0`.
2. GitHub Actions OIDC trusted-publishing workflow (`.github/workflows/pypi-publish.yml` on
   `EMPIRIC2/TAC-to-IWXXM`, Environment `pypi`) builds sdist+wheel and publishes to PyPI.
3. CI (or follow-up) `pip install <pkg>=={version}` in a clean venv and runs a one-liner smoke
   (lint / validate_iwxxm / convert).

**Acceptance**: Tag → publish → install smoke green for all three packages. **Tier: CI**.
   EV-028 / #781 proves the path with `0.1.1` under EMPIRIC2 Trusted Publishers.

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

### UJ-DEV-006: Rust Crate CI — fmt / clippy / test / maturin (F13/F14 / #725)

**Actor**: Developer / CI

**Goal**: Catch Rust style, borrow-checker, unit, and PyO3 bridge regressions before merge
for both native crates.

**Steps**:

1. Locally: `make rust-check` (or CI equivalent) on
   `packages/tac2iwxxm/rust` and `packages/iwxxm-validate/rust`.
2. CI on PR/push: `cargo fmt --check`, `cargo clippy -- -D warnings`, `cargo test`.
3. Maturin/PyO3 smoke for **both** packages (required-Rust env flags).
4. Confirm required GH check(s) block merge when red.

**Acceptance**: Unformatted Rust, clippy warnings, failing `cargo test`, or missing
iwxxm-validate maturin smoke fail CI. **Tier: T0 / CI**. TC-EV045-001..007.
[Corpus: product §F13] [Corpus: product §F14] [Corpus: tests]

---

### UJ-DEV-007: Slim Husky — Lint on Commit + Fast Units on Push (M5 / #833)

**Actor**: Developer

**Goal**: Keep the day-to-day git hook path fast (lint + unit subset) while remote CI holds
merge-strength gates.

**Steps**:

1. `make install-hooks`.
2. Make a trivial lint-clean change; `git commit` — only lint/format hooks run.
3. `git push` — only the agreed fast unit subset runs (not typecheck / validate-ci / Compose).
4. Confirm heavier targets still available via `make` and enforced in PR CI.

**Acceptance**: TC-EV047-001..004. **Tier: T0**.
[Corpus: product §M5] [Corpus: tests]

---

### UJ-DEV-008: Converter Perf Regression Blocks PR (F6 / #834)

**Actor**: Developer / CI

**Goal**: A slower `tac2iwxxm.convert` cannot merge green.

**Steps**:

1. CI runs converter hard-gate job on PR (convert-only p95 vs committed baselines).
2. Artificial slowdown → job red; revert → green.
3. Intentional baseline bump uses documented refresh procedure (not silent on failure).

**Acceptance**: TC-EV047-005..008. **Tier: T0 / CI**.
[Corpus: product §F6] [Corpus: tests]

---

### UJ-054: Operator Help → One-Pager / Handbook (F7 / #956/#957)

**Actor**: Meteorological operator / workshop attendee

**Goal**: Find a one-page quick start and a short handbook without reading engineering docs.

**Steps**:

1. From the operator app, open **Help** (entry reaches the one-pager).
2. Follow paste/convert → validate → download; note IWXXM version pick and soft-preview wording.
3. From the one-pager (or README Quick start), open the minimal handbook for login, history,
   dissemination overview, troubleshooting, and automated-ingest pointer.

**Acceptance**: User-facing text has **no** internal corpus/ADR/session citations.
TC-EV047-009..011. **Tier: T0 / T2 / T3**.
[Corpus: product §F7] [Corpus: journeys]

---

### UJ-055: Operator Surfaces Without Internal Doc References (F7+F21 / #951)

**Actor**: Meteorological operator / API consumer

**Goal**: Use convert soft-preview, public OpenAPI `/docs` field descriptions, and
representative privacy/auth empty-state copy without seeing internal planning vocabulary.

**Steps**:

1. Open the operator app (non-deployed or deployed). Confirm soft-preview helper text
   describes best-effort IWXXM / failed spans in plain language (no ADR/Corpus/session IDs).
2. Open public API `/docs` (or Redoc). Spot-check convert `preview` / nilReason / plain-language
   field descriptions — operator meaning only.
3. Spot-check privacy/auth empty-state or helper copy for the same constraint.

**Acceptance**: No `[Corpus:…]`, `ADR-NNN`, `EV-NNN`, `S0NN`, `FNN` product ids, or
`docs/…` path citations in those surfaces. TC-EV048-001..005. **Tier: T0 / T2**;
**T3** if UI audit finds visible hits.
[Corpus: product §F7] [Corpus: product §F21] [Corpus: api] [Corpus: journeys]

---

### UJ-056: Browse Official Corpus Quality Metrics Tab (F7.q / #836)

**Actor**: Meteorological operator / maintainer / demo presenter

**Goal**: Open a **dedicated Quality metrics tab** (primary shell navigation — not inside
the convert workbench) and explore official WMO IWXXM example quality by product: match,
residuals, lint, validate, with a unified XML diff vs our conversion.

**Steps**:

1. From the operator app, open the **Quality metrics** primary tab (peer to Convert /
   History — not a sub-panel of the convert workbench).
2. See product-level summary counts (match / residual / lint / validate) loaded from
   public **`GET /api/v1/quality-metrics`** (precomputed fixture-backed — not live WMO fetch).
3. Filter to one product (e.g. METAR); open a known passer stem
   (`GET /api/v1/quality-metrics/{stem}`).
4. **EV-056**: selecting a row **navigates** to shareable **`/quality/:stem`** with
   back-to-list (`D-S066-route-shape=1` / `D-S066-list=1`). Detail remains Official /
   Converted / TAC panes (normalized = pretty C14N by default with override) plus
   **GitHub-style** unified diff with collapsible equal-context hunks (default **3**
   context lines; expand hunk / expand all — `D-S066-context-n=1`). C14N /
   `match_status` semantics unchanged from EV-055.
5. **EV-058 / #983**: on the detail page, use a **segmented control** —
   **Inline (unified)** | **Side-by-side** — to switch XML diff layout without reload
   (`D-S068-01-control=3a`). Default is **Inline**. Side-by-side reuses existing
   line-diff helpers (no new npm `diff`). Preference persists in **localStorage**.
   Synced scroll between panes is **best-effort** (`D-S068-01-ac=2b`). Raw TAC /
   diagnostics / collapse-equal-context remain available.
6. In the detail view: confirm **match status** and the active XML diff layout;
   residuals / lint / validate panels show empty or expected diagnostics. **EV-055**:
   panes default to C14N-normalized with override to un-normalized; validate chips
   reflect enabled / fixed 2025-2 disposition without internal planning ids.
7. Confirm a deferred / gap stem is labeled (not silently missing).
8. Optional later: deep-link the same stem into the convert workbench.

**Acceptance**: AC1–AC7 in evolve-decisions §EV-054 (tab shell) **and** AC1–AC7 in
evolve-decisions §EV-055 (normalize + validate disposition) **and** AC1–AC5 in
evolve-decisions §EV-056 (detail route + collapsible diffs) **and** AC1–AC5 in
evolve-decisions §EV-058 (side-by-side vs inline); TC-EV054-001..008 +
TC-EV055-001..007 + TC-EV056-001..005 + TC-EV058-001..005. Default view needs no
Supabase and no live upstream WMO fetch — metrics come from public
`GET /api/v1/quality-metrics*` backed by precomputed fixtures (`D-S063-gateA=2`;
regen under `D-S064-regen=1`).
**Tier: T0 / T2 / T3 / H4–H5**.
Related: UJ-032 / UJ-039 / UJ-042.
[Corpus: product §F7] [Corpus: product §F2] [Corpus: product §F13] [Corpus: product §F25]
[Corpus: journeys] [Corpus: tests] [Corpus: api] [Corpus: adr/ADR-032]

---

### UJ-057: Accumulate Conversions → Download All ZIP (F7.r / #903)

**Actor**: Meteorological operator (guest or logged-in)

**Goal**: Convert several TAC reports back-to-back, keep all successful IWXXM results in the
workbench, and download them together as **one ZIP** with a content-derived default name.

**Steps**:

1. Open the convert workbench; leave custom output basename empty (or clear it).
2. Convert report A successfully — result card visible.
3. Convert report B (and optionally C) without clearing the batch — prior successes remain.
4. Optionally trigger a failed convert — prior successes stay; failure is shown for the attempt.
5. Choose **Download all** / ZIP — receive one archive containing each accumulated IWXXM.
6. Confirm default ZIP name is `{stem}_{yyyyMMddHHmmss}.zip` where `stem` is ≈ first 8
   sanitized characters of the **first** successful conversion’s TAC.
7. Set a custom output basename and Download all — archive is `{base}.zip` (#664).
8. Clear / reset the accumulated set; confirm the batch is empty.

**Acceptance**: AC1–AC8 in evolve-decisions / feature-list §F7.r EV-057; TC-EV057-903-*.
Soft accumulate cap **≤200** (`D-S067-903-cap=1c`).
**Tier: T0 / T2 / T3 / H4–H5**. Related: UJ-001 / UJ-005 / UJ-052; F33 mass ingest orthogonal.
[Corpus: product §F7] [Corpus: product §F1] [Corpus: product §F6] [Corpus: journeys]
[Corpus: tests]

---

### UJ-058: Validate Existing IWXXM Without TAC Convert (F7.s / #838)

**Actor**: Meteorological operator (guest OK — no Supabase required)

**Goal**: Paste or upload an existing IWXXM document and run F2 XSD + Schematron validation
without performing TAC→IWXXM conversion.

**Steps**:

1. Open the operator UI **Validate** mode (dedicated validate-only intake — not Quality metrics).
2. Paste a known-good IWXXM fixture; select version/profile with the same F4 controls used on
   convert/validate elsewhere; run validate — pass (or expected clean diagnostics).
3. Upload one `.xml` IWXXM file; run validate — F2 issue list / pass-fail shown.
4. Paste broken / non-IWXXM XML — structured fail (no opaque 5xx).
5. Confirm no TAC convert was required and no Supabase login was needed for the happy path.

**Acceptance**: AC1–AC6 in feature-list §F7.s EV-057; TC-EV057-838-*. Multi-file/zip deferred.
Does not replace UJ-056 Quality metrics corpus browse.
**Tier: T0 / T2 / T3 / H4–H5**. Related: UJ-002 / UJ-007 / UJ-032.
[Corpus: product §F7] [Corpus: product §F2] [Corpus: product §F4] [Corpus: api]
[Corpus: journeys] [Corpus: tests]

---

### UJ-059: AHL Bulletin Lint/Validate Without Heading Flood (EV-060 / #1001)

**Actor**: Meteorological operator (guest OK) or API/CLI client

**Goal**: Lint/validate a WMO AHL bulletin without scoring heading tokens as product TAC errors.

**Steps**:

1. Set input mode to AHL bulletin (or `POST /api/v1/convert-bulletin` / lint equivalent).
2. Paste a well-formed AHL METAR bulletin.
3. Run lint/validate — heading is bulletin COM; contained METARs are checked as METAR.
4. Optionally paste malformed AHL — one bulletin-level error; still try to split reports.

**Acceptance**: feature-list EV-060 / #1001; TC-EV060-1001-*. FileConverter same behavior.
**Tier: T0 / T2 / T3 / H4–H5**. Related: UJ-011 / UJ-025.
[Corpus: product §F6] [Corpus: product §F7] [Corpus: api] [Corpus: tests]

---

### UJ-060: IWXXM Product Pass-Through (F7.t / #1003)

**Actor**: Meteorological operator (guest OK) or API/CLI client

**Goal**: Select product **IWXXM** and lint + F2-validate XML without TAC convert.

**Steps**:

1. Choose product IWXXM (workbench, FileConverter, accumulate, Quality metrics honor).
2. Paste valid IWXXM XML; run lint+validate — F2 result; no TAC convert.
3. Paste TAC text — structured not-XML error (not METAR lint).
4. Confirm Convert is disabled or no-ops with a clear operator message.
5. F7.s Validate-only mode still exists.

**Acceptance**: feature-list §F7.t AC1–4; TC-EV060-1003-*.
**Tier: T0 / T2 / T3 / H4–H5**. Related: UJ-058 / UJ-002.
[Corpus: product §F7] [Corpus: product §F2] [Corpus: api] [Corpus: tests]

---

### UJ-061: Profile Labeled at Converter Top (EV-060 / #1002)

**Actor**: Meteorological operator

**Goal**: Annex 3 vs IWXXM-US profile is obvious at the top of the converter and is what convert/lint/validate use.

**Steps**:

1. Open converter — Profile control is labeled at the top (not only inside conversion parameters).
2. Change profile; run convert/lint/validate — requests use the selected `profile`.
3. Keyboard: visible label + accessible name.
4. FileConverter / accumulate / Quality metrics honor the same profile.

**Acceptance**: feature-list EV-060 / #1002; TC-EV060-1002-*. Not #933 editor.
**Tier: T0 / T2 / T3 / H4–H5**. Related: UJ-005 / UJ-007.
[Corpus: product §F6] [Corpus: product §F7] [Corpus: journeys] [Corpus: tests]

---

### UJ-062: Bulletin ID and Issuing Center Applied (EV-060 / #1005)

**Actor**: Meteorological operator or API client

**Goal**: Labeled, editable Bulletin ID and Issuing Center are sent on convert and appear in output.

**Steps**:

1. Fill Bulletin ID and Issuing Center; convert — output/API payload uses those values.
2. Leave empty — discover-from-AHL or existing defaults.
3. Invalid CCCC/ID — one operator-visible field error, not a silent drop.

**Acceptance**: feature-list EV-060 / #1005; TC-EV060-1005-*.
**Tier: T0 / T2 / T3 / H4–H5**. Related: UJ-011.
[Corpus: product §F6] [Corpus: product §F7] [Corpus: api] [Corpus: tests]

---

### UJ-063: Conversion Log Level Changes Logger Verbosity (EV-060 / #1004)

**Actor**: Operator / API client / maintainer reading logs

**Goal**: The conversion-parameters log-level control actually changes backend/package logger verbosity.

**Steps**:

1. Run the same convert at DEBUG vs ERROR.
2. Observe emitted logs differ in verbosity.
3. Confirm DEBUG does not dump JWTs, passwords, or Authorization headers.

**Acceptance**: feature-list EV-060 / #1004; TC-EV060-1004-*. No live in-app log panel required.
**Tier: T0 / T2**. [Corpus: product §F29] [Corpus: api] [Corpus: tests]

---

### UJ-064: Validate IWXXM Shows Item-by-Item Readable Decode (EV-061 / #1010)

**Actor**: Public/guest operator

**Goal**: When Validate IWXXM still produces decode, the UI shows the same item-by-item readable
description pattern used for other product types.

**Steps**:

1. Open Validate IWXXM (or product=IWXXM validate path) with a sample IWXXM document.
2. Observe decode/summary presentation as structured readable item rows (parity with TAC decode).
3. Confirm F7.s validate-only and F7.t pass-through still work.

**Acceptance**: feature-list F9/F2 deepen EV-061 / #1010; TC-EV061-1010-*.
**Tier: T0 / T2 / T3 / H4–H5**. [Corpus: product §F2] [Corpus: product §F9] [Corpus: product §F10]

---

### UJ-065: AHL Bulletin Decode + Convert End-to-End (EV-061 / #1012)

**Actor**: Public/guest operator

**Goal**: Well-formed AHL METAR bulletin decodes per report and converts via convert-bulletin.

**Context required**: Heading `T1T2A1A2ii CCCC YYGGgg [BBB]` + TAC body (`=` terminators);
product/profile; optional Bulletin ID / Issuing Center. Golden: `SAUS31 KZNY` multi-METAR.

**Steps**:

1. Paste golden multi-report AHL METAR bulletin in AHL / auto-detect mode.
2. Observe decode: bulletin framing + item-by-item readable rows per report.
3. Convert — per-report IWXXM results (convert-bulletin).
4. Paste malformed AHL — clear `INVALID_AHL` / empty_bulletin (no silent success).

**Acceptance**: feature-list F6 deepen EV-061 / #1012; TC-EV061-1012-*. Distinct from #1011 harness.
**Tier: T0 / T2 / T3 / H4–H5**. [Corpus: product §F6] [Corpus: product §F7] [Corpus: domain/IWXXM_CONVERSION §AHL]

---

### UJ-066: Product Type + Profile Bars No-Wrap / Aligned (EV-061 / #1013)

**Actor**: Public/guest operator

**Goal**: Product Type and Profile controls do not wrap awkwardly at desktop widths and look polished.

**Steps**:

1. Open converter at viewport ≥1024px.
2. Confirm Product Type + Profile stay on one visual bar without wrap.
3. Confirm mode selects share one aligned row.
4. Resize below 1024px — stacking OK.

**Acceptance**: feature-list F7.u / #1013; TC-EV061-1013-*.
**Tier: T0 / T2 / T3 / H4–H5**. [Corpus: product §F7] [Corpus: journeys]

---

### UJ-067: Conversion Parameter Bar Aligned (EV-061 / #1013)

**Actor**: Public/guest operator

**Goal**: Conversion parameters sit on one aligned bar/row consistent with Product/Profile chrome.

**Steps**:

1. Open converter at ≥1024px with conversion parameters visible.
2. Confirm parameters share one centered/aligned bar with mode chrome.

**Acceptance**: feature-list F7.u / #1013; TC-EV061-1013-*.
**Tier: T0 / T2 / T3 / H4–H5**. [Corpus: product §F7]

---

### UJ-068: Validation Issues Catalog Top-Level Tab (EV-061 / #1014; EV-062 / #1017)

**Actor**: Public/guest operator

**Goal**: Browse a top-level **Validation Issues Catalog** of lint **and** validation checks with
code, descriptive what/why text, level, **issue type**, working source links, and section
locators (or explicit unavailable).

**Source policy**: Operator click-targets are verified landings (`D-S071-links-resolve`);
prefer public primary hrefs (`D-EV062-sources`); `codes.wmo.int/49-2*` / `common/nil` may
appear as semantic/legacy aliases without being the href. Paywall access is labeled.

**Steps**:

1. Open top-level **Validation Issues Catalog** nav tab.
2. See rows with code, description (what/why + section cite or unavailable), level, issue type,
   clickable source URL(s), and access/locator when present.
3. Filter by family, issue type, level, and/or source access; sort by code/level/type/access.
4. Spot-check that **operator** source links resolve (HTTP 2xx/3xx) for public rows.

**Acceptance**: feature-list F7.v / F15 / #1014 + #1017; TC-EV061-1014-* + TC-EV062-*. Distinct from #996.
**Tier: T0 / T2 / T3 / H4–H5**. [Corpus: product §F7] [Corpus: product §F15] [Corpus: api]

---

### UJ-069: Semantic Convert → Exchange Package (EV-063 / #912)

**Actor**: Library integrator or operator (API; optional UI via #1024)

**Goal**: Convert TAC with a **semantic** profile (`ICAO_2025` or `US_FAA_NWS`, or legacy alias
during deprecation window), then prepare output for dissemination using an **exchange** profile
(default `GLOBAL_AFS`) without conflating profile choice with sink credentials.

**Steps**:

1. Submit convert with `semantic_profile=ICAO_2025` (or alias `annex3`) and a supported product.
2. Receive IWXXM matching pre-migration annex3 goldens; observe deprecation signal if alias used.
3. Invoke packaging/disseminate-prep with `exchange_profile=GLOBAL_AFS` (or rely on default).
4. Confirm packaging hooks run deterministically in CI (no live sink push).
5. Confirm F16–F19 BYOC credentials are not stored or implied by exchange profile selection.

**Acceptance**: feature-list F35/F36; ADR-036; api-contract EV-063 section; TC-EV063-*.
**Tier: T2 / T3 (API)**; H4–H5 if #1024 FE ships. [Corpus: product §F35] [Corpus: api] [Corpus: adr/ADR-036]

---

### UJ-DEV-009: stage→main Promote Requires Full Quality Gate (EV-061 / #1015)

**Actor**: Maintainer

**Goal**: Promote PRs `stage`→`main` cannot merge without full CI unit + lint + typecheck + full E2E.

**Steps**:

1. Open a `stage`→`main` PR.
2. Confirm required checks include full CI unit jobs, lint, typecheck, and full E2E (not smoke-only).
3. Confirm merge is blocked while any required check is red/missing.

**Acceptance**: feature-list F34 deepen / #1015; deploy.md §Promote; TC-EV061-1015-*.
**Tier: CI**. [Corpus: product §F34] [Corpus: tech-spec] [Corpus: deploy] [Corpus: tests]

---

### UJ-OPS-002: Prod Apex Redirects to App Host (F30 / #948)

**Actor**: Ops / maintainer / anonymous visitor

**Goal**: Hitting the apex domain lands on the canonical operator app host.

**Steps**:

1. Request `https://tac-to-iwxxm.com/` (and a path+query such as `/foo?bar=1`).
2. Observe permanent redirect to `https://app.tac-to-iwxxm.com/` (path+query preserved).
3. If `www` is in DNS/cert coverage, repeat for `https://www.tac-to-iwxxm.com`.
4. Confirm HTTP apex (if served) ends on HTTPS app URL.
5. Confirm deploy docs describe the DOKS/ingress (or equivalent) mechanism.

**Acceptance**: AC1–AC5 in feature-list §F30 EV-057 / #948; TC-EV057-948-*. Staging apex out of
scope unless free with the same change.
**Tier: T3 / ops smoke**. [Corpus: product §F30] [Corpus: deploy] [Corpus: tech-spec]

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

**Deepen (S032 / EV-025)**: #809 multi-location VA stem — soft-compare golden shipped
(**UJ-041** / TC-EV025-008 soft). Does not change product enum (still `product=sigmet`
content-selected root).

**Deepen (S033 / EV-026)**: ADR-032 equality under defaults → strict TC-EV025-008 + catalog
`wmoPass` (TC-EV025-009); close #809.

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

**Deepen (S032 / EV-025)**: New US REMARKS goldens / fixtures (**UJ-040**) remain **out** of
the WMO sample menu — regression assert in TC-EV025-005.

**Deepen (S034 / EV-027)**: Inventory completeness for official WMO TAC peers is gated with
decode residual emptiness (**UJ-042** / TC-EV027-001..003) — listing alone is not enough.

**Automated tests**: TC-EV024-*; TC-F25-003 deepen; examplesCatalog Vitest; TC-EV025-005;
TC-EV027-001..003.

---

### UJ-040: Convert METAR/SPECI with Structured iwxxm-us REMARKS (S032 / EV-025)

**Actor**: Package / API consumer / CI maintainer

**Goal**: Under `profile=iwxxm_us`, METAR/SPECI REMARKS that map to dig ❌ US extension types
encode to the corresponding `iwxxm-us` elements (pin XSD 3.0), with goldens and combined-catalog
validate smoke. Named tickets #810 / #811 / #812 plus all remaining dig ❌ types.

**Feature**: Deepen F6.b / F12 / F2·F13 — S032 / EV-025

**Steps (CI — T0)**:

1. For each dig ❌ type (or fixture pack): TAC with REMARKS → `tac2iwxxm` convert `iwxxm_us`.
2. Assert extension element(s) present per PDF/XSD (e.g. Variable RVR, ObservedLightning,
   SnowIncrease, FailedSensors, …).
3. Run `iwxxm-validate` combined catalog smoke on emitted XML.
4. Negatives / malformed tokens still diagnostics (**UJ-010**); unparsed remainder in
   `humanReadableText` (**UJ-026**).
5. Confirm annex3 profile still excludes US extension XML (`REMARKS_EXCLUDED` path).

**Steps (API — T2 / optional T3)**:

1. `POST /api/v1/convert` with `profile=iwxxm_us` and a US REMARKS accept fixture.
2. Response XML contains expected extension blocks; optional validate round-trip.

**Acceptance**: TC-EV025-001..007 green. Dig ❌ encode residuals **block Gate C**
(E25-T5=3 — supersedes soft child-issue deferral from S02.M2).

**Automated tests**: TC-EV025-001..007; package annex3/`iwxxm_us` goldens.

**Source**: #810 / #811 / #812 · dig checklist · E25-*

---

### UJ-041: Promote sigmet-multi-location-VA to WMO Passer (S032 soft / S033 equality)

**Actor**: CI maintainer / package harness

**Goal**: Vendor stem `sigmet-multi-location-VA` has package annex3 convert equal to vendor
XML under ADR-032 defaults (`canonicalize_xml`), root `iwxxm:VolcanicAshSIGMET`, multi-location
OBS/FCST collections per Guidance. Catalog tier is `wmoPass` (strict passer). Soft-compare
path already shipped in EV-025 / #816; **EV-026** completes equality + promote.

**Feature**: Deepen F23 / F6 / F7.g — S033 / EV-026 · Issue [#809](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/809)

**Steps (CI — T0)**:

1. Convert vendor TAC peer under annex3 + default pin → `canonicalize_xml` **equals** vendor XML.
2. Flip catalog tier `wmoReference` → `wmoPass`; Vitest/catalog assert; clear FIXTURE_GAPS note.
3. Sample-menu listing remains (now as passer) — UJ-039 deepen.

**Acceptance**: TC-EV025-008..009 green under **strict** semantics (EV-026); deepen UJ-034 /
TC-F23-003 adjacency; #809 closable.

**Automated tests**: TC-EV025-008..009 (reused ids — `E26-TC=1`); FIXTURE_GAPS / catalog row.

**Source**: #809 · [Context: va-multi-location-809](context/va-multi-location-809.md) · ADR-032

---

### UJ-042: Official WMO TAC Peers Decode Cleanly (S034 / EV-027)

**Actor**: Operator / CI maintainer

**Goal**: Every in-scope official WMO IWXXM TAC peer (vendor pin) is either loadable from the
workbench sample menu or explicitly deferred in `FIXTURE_GAPS`, and after `decode_tac` the
report has **empty residuals** unless listed on a documented expected-residual allowlist.
Unexpected leftovers are defects (fix decode or file a child issue — no silent leftovers).

**Feature**: Deepen F25 / F9 / F7.g — S034 / EV-027 · Issue [#815](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/815)

**Steps (CI — T0)**:

1. Inventory official WMO stems with TAC peers under the current vendor pin; assert the set
   equals catalog registrations ∪ `FIXTURE_GAPS` rows (no silent omissions).
2. For each registered happy-path stem: load fixture TAC → `decode_tac` → `residuals == []`
   **or** match expected-residual allowlist entry (product G4 best-effort / deferred token /
   linked child issue).
3. Parametrized tests fail CI on unexpected residuals.
4. Catalog Vitest: every in-scope vendor TAC peer is registered or gap-documented.

**Steps (operator — T2 / T3 / H4–H5 when FE ships)**:

1. Open **Examples / sample menu** — select a registered official WMO stem (UJ-039 path).
2. Confirm TAC loads with correct product + provenance banner (`wmoPass` vs `wmoReference`).
3. Open decode panel (UJ-020) — no unexpected residual chrome / “Not decoded: …” for
   happy-path textbook peers (allowlisted stems may show named residuals).

**Acceptance**: TC-EV027-001..005 green; #815 closable; child issues for in-cycle deferrals.

**Automated tests**: TC-EV027-001..005; deepen TC-EV024-004..006; examplesCatalog Vitest;
`decode_tac` residual matrix pytest.

**Browser wiring**: Same public decode-tac + static catalog as UJ-039 / UJ-020 — no new
origins (H4–H5 when FE ships).

**Source**: #815 · ADR-025 · ADR-032 · [Context: wmo-decode-residual-matrix](context/wmo-decode-residual-matrix.md)

---

### UJ-043: Eight-Family Rules Gap Sweep + SWXA Quality (S036 / EV-029)

**Actor**: Operator / CI maintainer / package consumer

**Goal**: For every TAC→IWXXM product family in scope (METAR, SPECI, TAF, SIGMET general/VA/TC
+ CNL, AIRMET, VAA, TCA, SWXA), rules for **lint**, **conversion**, and **IWXXM validation**
are documented and exercised — including bulletin/AHL framing and report states — with no
silent coverage gaps. SWXA reaches the same quality bar as peer products (**F28**).

**Feature**: **F28** + deepen F6/F6.bulletin/F12/F2/F13/F15/F20/F23/F24/F26/F27 — S036 / EV-029 ·
Issues [#823](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/823),
[#738](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/738),
[#820](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/820),
[#740](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/740)

**Steps (CI — T0 / T2)**:

1. Phase A: coverage matrix + canonical domain docs have a cell (pass / defer+child) for each
   family × role × report-state × TAC input shape (standalone / AHL / multi-report).
2. Shared AHL/`T1T2`/BBB fixtures: parse → `reportStatus` + IWXXM designator map.
3. Product-by-product (locked order): accept TAC → lint registry → convert → XSD+Schematron;
   TC SIGMET root `iwxxm:TropicalCycloneSIGMET`; SWXA root `iwxxm:SpaceWeatherAdvisory`.
4. Example inventory: official IWXXM peers + TAC shapes wired or gap-documented.
5. Negatives / residual allowlists linked to child issues (no silent leftovers).

**Steps (operator — T2; H4–H5 only if FE Examples unlock)**:

1. Load a fixture per family (API or workbench when catalog ships SWXA / TC SIGMET passers).
2. Confirm lint codes, convert root, and validate pass (or documented soft-fail).

**Acceptance**: TC-EV029-001..008 + TC-F28-001..006 green (or waived with child issues);
#823 umbrella AC met or children linked.

**Automated tests**: TC-EV029-*; TC-F28-*; deepen TC-F15/F20/F23/F24/F26/F27 suites.

**Browser wiring**: No new origins. H4–H5 only if FE catalog/Examples change ships.

**Source**: #823 · ADR-014 · ADR-028 · ADR-032 ·
[Context: eight-family-ahl-rules-823](context/eight-family-ahl-rules-823.md)

---

### UJ-044: Rule Matrix Harness + TC / VAA–TCA Residuals (S037 / EV-030)

**Actor**: CI maintainer / package consumer (operator-invisible for F29; operator for #829 menu)

**Goal**: Every in-scope lint/convert/validate rule has a discoverable 5×4 case budget (or
explicit `needs-fixture` slot); TC SIGMET lint pack + STNR/geometry (or OOS) and A6-2-TC
catalog tier are decided; VAA/TCA decode residuals shrink beyond F9 G4 best-effort.

**Feature**: **F29** + deepen F23/F12/F2/F13/F9/F26/F27 — S037 / EV-030 ·
Issues [#831](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/831),
[#829](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/829),
[#820](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/820)

**Steps (CI — T0 / T2)**:

1. Design note answers #831 evaluation questions; runners load `RuleCase`-style fixtures.
2. Pilot METAR/SPECI (lint+encode+validate) matrices green or inventory-gated TODOs.
3. TC SIGMET `tac-validate` accept/negative pack + STNR/geometry cases (or OOS cite).
4. Official VAA/TCA peers: decode residual spans shrink; allowlist/matrix updated.
5. Pytest node ids include `rule_id` / bucket / case; PR-smoke subset in CI.

**Steps (operator — T2; H4–H5 only if FE menu unlock)**:

1. If catalog unlocks `sigmet-A6-2-TC`: load from Examples → lint/convert/validate pass per ADR-032.
2. Otherwise: catalog decision recorded; no FE change this cycle.

**Acceptance**: TC-EV030-* + TC-F29-001..007 green (or child-issued); #831/#829/#820 closable
or split with links.

**Automated tests**: TC-EV030-*; TC-F29-*; deepen TC-F23 / TC-F9 / TC-F26 / TC-F27.

**Browser wiring**: No new origins. H4–H5 only if FE catalog/Examples change ships.

**Source**: #831 · #829 · #820 · ADR-028 · ADR-032 ·
[Context: quality-residuals-831](context/quality-residuals-831.md)

---

### UJ-045: Guest Convert + Loss-of-Progress Notice (S038 / EV-031 / F31)

**Actor**: Transient / guest operator (not logged in)

**Goal**: Convert and keep **local** work history while clearly warned that progress may be lost
without login.

**Feature**: F31 + F21 Amended (+ F5/F7 guest path)

**Steps**:

1. Open workbench without logging in (privacy prefs allow local storage if required — UJ-047).
2. See a **persistent banner/callout** while guest and local/unsaved work exists: progress may be
   lost unless logged in (`D-S038-uj` Q2=1).
3. Paste/convert TAC (UJ-001); history saves to IndexedDB only.
4. Refresh / resume from local sidebar / My METARs (UJ-004 guest path).
5. Clearing site data or declining storage prefs loses local history (documented).

**Acceptance**: Convert works without JWT; notice visible for guest+local work; no server
session writes; TC-F31-001/002.

**Automated tests**: Playwright T2/T3; TC-F31-001/002; H4–H5.

**Browser wiring**: Same API origin rules as UJ-001; no Auth required.

**Source**: E31-*; [Context: platform-independence-842](context/platform-independence-842.md)

---

### UJ-046: Login → Auto-Upload Drafts → Server Sessions (S038 / EV-031 / F31)

**Actor**: Operator who wants long-term storage

**Goal**: Log in via Supabase Auth; local drafts **auto-upload** to DO Postgres; resume from server.

**Feature**: F31 + F30 (+ restore UJ-003)

**Steps**:

1. As guest, create one or more local drafts (UJ-045).
2. Open login (`/auth` UI or equivalent); authenticate with Supabase Auth.
3. Client receives JWT; **auto-uploads** all eligible local drafts to
   `POST /api/v1/work-sessions*` (no merge prompt — `D-S038-guest-merge`=2).
4. Sidebar / My METARs shows server sessions; further edits sync to DO Postgres.
5. Logout returns to guest mode; notice returns; new work is local-only unless login again.

**Acceptance**: JWT required only for session APIs; convert still public; auto-upload completes
or surfaces structured errors; TC-F31-003/004.

**Automated tests**: Playwright auth + session; API integration with DO Postgres; H4–H5.

**Browser wiring**: Auth against Supabase; session APIs against API on DOKS; CORS for FE origin.

**Source**: E31-*; F30/F31

---

### UJ-047: Privacy Prefs ↔ Storage / Auth Cookies (S038 / EV-031)

**Actor**: Anyone

**Goal**: Privacy settings (UJ-033) correctly gate guest IndexedDB work history and disclose
Auth session cookies when login is used.

**Feature**: F22 deepen + F31

**Steps**:

1. Open Privacy settings; review categories for local work history and Auth cookies.
2. If guest history is non-necessary and declined: do not persist IndexedDB work history;
   notice still explains login for long-term storage.
3. After login: Auth cookies/disclosures visible; GPC still honored.
4. Withdraw preferences; confirm storage/cookie behavior updates.

**Acceptance**: TC-F31-005; deepen TC-F22-*; no silent storage against declined prefs.

**Automated tests**: T0 unit + T2/H4–H5 privacy flows.

**Source**: F22; F31; UJ-033 deepen

---

### UJ-048: DOKS Cutover Smoke (S038 / EV-031 / F30)

**Actor**: Operator / deployer

**Goal**: After Render→DOKS cutover, API + static + worker are healthy; public convert and
(optional) Auth/session paths work against new endpoints.

**Feature**: F30 (#712)

**Steps**:

1. Deploy API, frontend, worker to DOKS; apply Alembic migrations to DO Postgres.
2. Point DNS / `LIVE_*` URLs to `https://api.tac-to-iwxxm.com` / `https://app.tac-to-iwxxm.com`.
3. Run H0–H5: health, convert, CORS, FE→API; F8 store write smoke; Auth login + session CRUD.
4. Confirm product path works **without** Supabase DB credentials; Auth keys present for login.
5. Decommission Render after soak checklist.

**Acceptance**: TC-F30-004/005; H0–H5 green on DOKS; UJ-001 + UJ-045/046 smoke.

**Automated tests**: `make test-live*` against DOKS URLs; deploy-smoke report.

**Source**: #712; F30; UJ-OPS-001 supersession notes

---

### UJ-049: VONA Lint / Convert→Validate + F7 Product Surface (S040 / EV-032)

**Actor**: Operator / CI maintainer / package consumer

**Goal**: Lint VONA TAC with registry codes; convert accept fixtures (esp. official
`vona-A7-1` peer when available) to `iwxxm:VolcanoObservatoryNoticeForAviation` that
passes XSD+Schematron under default convert settings; ADR-032 golden equality when a
vendor peer exists; full F7 workbench surface — product picker includes **VONA**, Examples
lists VONA passers when unlocked. Encode authority is XSD+SCH+example+PANS-MET (guidance
file silent).

**Feature**: **F32** (+ deepen F6 / F7 / F12 / F2 / F13 / F9) — S040 / EV-032 ·
Issues [#741](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/741),
[#846](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/846)

**Related cycle work (same session, not this UJ alone)**:

- [#835](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/835) — A6-2-TC ADR-032 → `wmoPass` (deepen UJ-034/039)
- [#808](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/808) — release-line adoptability docs (no operator UJ)
- Corpus children under #846 — deepen UJ-039/042 as filed

**Steps (operator — T2/T3; H4–H5 when FE ships)**:

1. Open workbench; Product = **VONA** (picker present — full F7 surface).
2. Load / paste VONA accept TAC; lint — registry codes only.
3. Convert → Strict Validation — pass; root `iwxxm:VolcanoObservatoryNoticeForAviation`.
4. Paste a known-bad VONA negative — lint returns registry codes (no silent success).
5. Examples control lists VONA **strict passers** when they pass the golden bar; official
   WMO VONA stems may also load as **reference** per UJ-039 / ADR-032.

**Steps (CI — T0 / T2)**:

1. Registry completeness + accept/negative packs (**TC-F32-001..004**).
2. API accepts `product=vona`; unknown aliases → `unknown_product` 400 (**TC-F32-006**).
3. Product-path smoke + catalog unlock when green (**TC-F32-005**).

**Acceptance**: TC-F32-001..006 + TC-EV032-* green (or child-issued); #741 closable or split
with links; H4–H5 when FE picker/Examples ship.

**Automated tests**: TC-F32-*; TC-EV032-*; deepen TC-F7-008 / UJ-032 / UJ-039.

**Browser wiring**: No new origins. Same API host; `product=vona` multipart field. H4–H5
required when FE ships (`D-S040-E32-M` Q2=3).

**Source**: #741 · #846 · ADR-028 · ADR-032 ·
[Context: iwxxm-corpus-quality-846](context/iwxxm-corpus-quality-846.md)

---

### UJ-050: IWXXM Version Picker Latest / Previous Labels (S046 / EV-038)

**Actor**: Operator (guest or logged-in)

**Goal**: See which IWXXM release-line option is **Latest** (default) vs **Previous**
without reading domain policy docs; labels stay aligned with the shared version SoT
(#851) when lines rotate. Convert semantics unchanged.

**Feature**: **F4** + **F7** deepen — S046 / EV-038 ·
Issue [#854](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/854) · parent
[#846](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/846)

**Steps (operator — T2/T3; H4–H5 when FE ships)**:

1. Open workbench; open the IWXXM **version** control.
2. Confirm options indicate **Latest** / **Previous** (label, badge, or adjacent help)
   matching `VERSION_SUPPORT_POLICY` / SoT roles.
3. Select Previous vs Latest — convert still uses the chosen year line (no remap surprise).
4. After a line rotation (staging/local SoT change), labels still match roles.

**Acceptance**: **TC-EV038-007** green; SoT drift CI (#851 / TC-EV038-004) keeps options
aligned; local non-deployed UI preview at M2 (`D-S046-mplan` Q2=1).

**Automated tests**: TC-EV038-007; FE Vitest/Playwright as applicable; H4–H5 at deploy.

**Browser wiring**: No new origins. Same API host; version field unchanged.

**Source**: #854 · #851 ·
[RELEASE_LINE_STAFF_GUIDE.md](domain/iwxxm/RELEASE_LINE_STAFF_GUIDE.md) ·
[Context: iwxxm-corpus-residuals-846](context/iwxxm-corpus-residuals-846.md)

---

### UJ-051: Secure Mass File/Folder Ingest (S050 / EV-042 / F33)

**Actor**: Authenticated operator

**Goal**: Upload many TAC text files via multi-select and folder/zip, with progress and
per-file errors, under auth + size/count caps + sniff/zip-bomb guards.

**Feature**: **F33** — [#897](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/897)

**Steps**:

1. Sign in; open workbench mass-ingest control (folder and/or zip).
2. Select ≤200 files totaling ≤50 MiB unzipped (each ≤5 MiB); see progress toast.
3. Per-file failures (binary, oversize, sniff reject) do not abort the rest.
4. Successful items appear in the result/work queue for convert/validate (UJ-052).
5. Without JWT, mass path is denied with a clear error; guest small multi-file (if any) unchanged.

**Acceptance**: TC-F33-001..006; caps R1; auth R3.

**Browser wiring**: Same API origin; new mass-ingest route(s) require Authorization.

---

### UJ-052: Operator Queue + Keyboard/Batch Convert·Validate (S050 / EV-042)

**Actor**: Operator (guest or logged-in)

**Goal**: Churn through reports quickly via queue navigation and batch convert/validate
(no dissemination destinations this cycle).

**Feature**: **F7** deepen — EV-042 / #897

**Steps**:

1. After convert or mass ingest, see a sticky result/queue list.
2. Use next/prev keyboard shortcuts; Enter triggers convert or validate for the focused item.
3. Multi-select items → batch convert and/or batch validate; progress visible.
4. Confirm Convert&Send / Disseminate destination UI is absent (UJ-053).

**Acceptance**: TC-EV042-003..004.

---

### UJ-053: No Operator Dissemination Destinations (S050 / EV-042)

**Actor**: Operator

**Goal**: Dissemination drawer sink chooser, Convert&Send destination path, and
**Upload to Database** / `DatabaseUploadDialog` are not available (DB + WIS2/EDIS/AMHS/SWIM/AFS).
Backend APIs remain for harness until #898.

**Feature**: **F16–F19** deepen — EV-042 / #897; restore [#898](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/898)

**Steps**:

1. Open workbench; confirm no sink chooser / Convert&Send / Upload to Database.
2. Convert and validate still work (UJ-001/002/052).
3. Harness/tests may still call `/api/v1/dissemination/*` outside the operator UI.

**Acceptance**: TC-EV042-001..002.

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
**Tier**: T2 / T3 / H6′. **Tests**: TC-F16-001..005 (mocked H6′); **TC-F16-LIVE-001..004**
(live local Compose — S047 / EV-039).

**Live local path (S047 / EV-039 — deepen F16)**:
1. Start disposable engines: `make compose-mock-byoc-up` (Postgres, MySQL, SQL Server via
   `docker-compose.mock-byoc.yml` profile `mock-byoc`). SQLite uses a disposable file URI.
2. Configure API allowlist for local compose hosts (`DISSEMINATION_EGRESS_ALLOWLIST` includes
   `127.0.0.1` / `localhost` and documented compose hostnames — [Corpus: adr/ADR-029]).
3. Run Playwright **without** mocking `/api/v1/dissemination/preflight` or `/send`: for each
   sink type (postgres, mysql, sqlserver, sqlite), paste the local URI, preflight (DDL if
   needed), Disseminate, assert UI success **and** a DB write (or writer-contract equivalent).
4. Tear down: `make compose-mock-byoc-down` (or suite global teardown) removes containers;
   SQLite temp files deleted; no orphan processes. Integration Testcontainers fixtures must
   likewise always tear down on pass/fail/skip.

Mocked H6′ specs (`uj027-030-dissemination-drawer.e2e.spec.ts`) remain the default CI smoke;
live suite is a **separate** target (may be opt-in in CI if SQL Server is heavy).

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

### UJ-OPS-001: Deploy stack (API + static + F8 worker)

**Historical**: Render Blueprint (`render.yaml`) — API + static + Background Worker (ADR-018).

**S038 / EV-031**: Primary topology becomes **DOKS** (F30 / UJ-048). Render remains until soak
completes, then decommissioned. Redeploy API before frontend when CORS/API contract changes.
Apply DO Postgres migrations before worker/API traffic. Signoff includes UJ-001/045/046 + H0–H5.

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
- S038 / EV-031 (2026-08-03): UJ-045..048 hybrid Auth sessions + DOKS; UJ-003 restored via
  UJ-046; deepen UJ-001/004/033; UJ-OPS-001 → DOKS primary (F30/F31; #842/#830/#712)
- S047 / EV-039 (2026-08-06): UJ-027 live local Compose multi-DB path + TC-F16-LIVE-*;
  teardown hygiene across integration / e2e / local (F16 deepen)
- S054 / EV-045 (2026-08-08): UJ-DEV-006 Rust crate CI (F13/F14 deepen; #725)
- S070 / EV-060 (2026-08-17): UJ-059 AHL bulletin quality (#1001); UJ-060 IWXXM product
  pass-through (#1003); UJ-061 profile picker (#1002); UJ-062 bulletin fields (#1005);
  UJ-063 log_level (#1004); deepen UJ-003/046 Auth UAT (#1006)
- S071 / EV-061 (2026-08-18): UJ-064 validate readable decode (#1010); UJ-065 AHL decode+convert
  (#1012); UJ-066/067 Product/Profile + param bars (#1013); UJ-068 catalog tab (#1014, links
  resolved / unblocked); UJ-DEV-009 stage→main full gate (#1015)
