# User Journeys

> **Project**: METAR to IWXXM Converter
> **Source**: feature-list.md, requirements interview 2026-06-14; S008 F6 + realtime/package amend 2026-07-12
> **Last updated**: 2026-07-12

Product-facing journeys (UJ-*) describe end-user flows. Developer journeys (UJ-DEV-*)
describe monorepo workflows introduced by migration features M1–M6 and F6.

## Journey Index

| ID | Journey | Entry point | Feature | E2E tier |
|----|---------|-------------|---------|----------|
| UJ-001 | Convert METAR via UI (shorthand) | apps/frontend | F6 (was F1) | T2 / **T3** |
| UJ-002 | Validate IWXXM output (`iwxxm-validate`) | apps/frontend / API | F2+F6 | T2 / **T3** |
| UJ-003 | Register and login | apps/frontend | Auth | T2 / **T3** |
| UJ-004 | Resume & browse METAR work history | apps/frontend | F5 | T2 / **T3** |
| UJ-005 | Convert with product + profile via UI | apps/frontend | F6 | T2 / **T3** (all 7 products) |
| UJ-006 | Convert non-METAR product via API | HTTP API | F6 | T2 / **T3** |
| UJ-007 | Validate IWXXM-US profile document | apps/frontend / API | F2+F6 | T2 / **T3** |
| UJ-008 | Unsupported / unknown product TAC | UI / API | F6 | T2 / T3 |
| UJ-009 | US profile without iwxxm-us pin | UI / API | F6 | T2 |
| UJ-010 | Malformed US REMARKS | UI / API | F6 | T0 / T2 |
| UJ-011 | Bulletin split → convert → Schematron (API) | HTTP API | F6 | **T2** |
| UJ-012 | TAC lint failure (`tac-validate`) via API | HTTP API | F6 | **T2** |
| UJ-013 | Multi-product operator entry (F7) | apps/frontend | F7 | Planned — no T3 yet |
| UJ-014 | Near-RT ingest + quarantine (F8) | Worker / API | F8 | Planned — no T3 yet |
| UJ-DEV-001 | Clone and run monorepo | `git clone` + `make dev` | M1, M5 | T0 |
| UJ-DEV-002 | Sync vendor schemas | Scheduled Action / manual | M2, M6, F6 | CI |
| UJ-DEV-003 | ~~Merge GIFTs upstream~~ | — | M3 | **Deprecated** (ADR-014) |
| UJ-DEV-003b | Maintain tac2iwxxm + iwxxm-us pins | Maintainer workflow | F6, M2 | CI |
| UJ-DEV-004 | Package CI for tac-validate + iwxxm-validate | `make test` / CI | F2, F6, M5 | T0 / CI |
| UJ-OPS-001 | Deploy Render stack (API + static + worker) | render.yaml | M4, F8 | T3 (staging) |

**E2E tiers**:

- **T0** — Unit + package tests; no running services.
- **T2** — Local docker-compose or `make dev`; Playwright in `apps/e2e/`.
- **T3** — Deployed Render stack; Playwright + pytest against live URLs (manual `make test-live`).

Run local E2E: `make test-e2e-playwright`  
Run live E2E: `make test-live` (requires `.env` with `ADMIN_EMAIL` / `ADMIN_PASSWORD`)

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

**Actor**: User (authenticated for persistence; guests may convert without save — F5-R22)

**Goal**: Upload or paste METAR TAC and receive IWXXM XML (default product/profile).

**Feature**: F6 (supersedes F1 engine). Full product/profile matrix is **UJ-005**.

**Steps**:

1. Open frontend in browser.
2. Optionally log in (UJ-003) — required for work history persistence (UJ-004).
3. Drag-drop `.tac` file or paste manual text (METAR/SPECI).
4. Optionally leave product on **auto** / METAR and profile **annex3** (defaults).
5. **#664 (EV-005)**: Optionally type an **Output filename** for manually entered TAC.
6. Choose **Convert**, **Convert&Send**, or **Upload to Database**.
7. View output; #555 replace-on-success and error log panel behavior unchanged.
8. On convert failure after F6 cutover: structured error only — **no gifts rollback**.

**Acceptance**: METAR converts without error via tac2iwxxm; schema/Schematron pass for selected
version; UX behaviors from #555/#664 preserved.

**Automated tests**: `apps/e2e/tac-file-conversion.e2e.spec.ts` (T2); `make test-live-e2e` (T3)

**Browser wiring**: Frontend → API base URL; CORS must allow frontend origin (H4).

---

### UJ-002: Validate IWXXM Output

**Actor**: Authenticated user or API client

**Goal**: Confirm generated XML passes schema/Schematron validation via
`packages/iwxxm-validate` (backend thin wrapper).

**Steps**:

1. Obtain IWXXM XML from conversion (UJ-001 / UJ-005 / UJ-006 / UJ-011).
2. Trigger validation endpoint or UI action with the same **profile** used for convert.
3. Backend invokes **`iwxxm-validate`** (not inline schema loading long-term).
4. Review pass/fail and error messages.
5. If `profile=iwxxm_us`, validation uses **combined** WMO + iwxxm-us catalogs; `annex3` uses WMO only.

**Acceptance**: Valid sample produces validation pass for selected IWXXM version and profile.

**Automated tests**: `packages/iwxxm-validate` unit + backend wrapper tests + E2E where exposed (T2); H3 + H6 (T3)

---

### UJ-003: Register and Login

Unchanged from prior interview (Supabase JWT via merged `/auth/*`).

**Acceptance**: Protected `/api/v1/*` returns 401 without token, 200 with valid token.

**Automated tests**: `apps/e2e/auth.e2e.spec.ts` (T2); `make test-live-e2e` (T3)

---

### UJ-004: Resume & Browse METAR Work History

Unchanged scope: **METAR/SPECI sessions only** in F6 v1. Product/profile may be stored in
`conversion_params` when present; no multi-product history UI.

**Steps**: See prior F5 journey (auto-save, Draft/WIP/Finished/Failed, sidebar, My METARs, admin).

**Acceptance**: Same F5 acceptance as S004.

**Automated tests**: `apps/e2e/metar-work-history.e2e.spec.ts` (T2); live H6 delta (T3)

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

**Acceptance**: Error/issues list non-empty; annex3 mode still ignores US-only remarks without
failing international validation (profile isolation).

**Tier**: T0 / T2 primarily.

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

### UJ-013: Multi-Product Operator Entry (F7) — Planned

**Status**: **Planned — not this build.** Stub for multi-product sessions / operator UI beyond F5.

**Acceptance**: ⚠️ Deferred. No T3 until F7 session.

---

### UJ-014: Near-Realtime Ingest + Quarantine (F8)

**Status**: **Build this cycle (S008 / ADR-018).** Worker ingest → pipeline → Supabase store or
separate quarantine on Schematron/convert fail. No push sinks in v1.

**Acceptance**: Worker processes HTTPS/object-prefix fixture feed; pass rows in
`iwxxm_ingest_results`; fail rows in `iwxxm_ingest_quarantine`; service-role JWT for writers.
Live: T7.4 / Phase 6 gate.

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

## Operations Journeys

### UJ-OPS-001: Deploy Render stack (API + static + F8 worker)

Topology: API + static frontend + **Background Worker** (ADR-018). After F6: API image includes
tac2iwxxm + validate packages (not gifts); frontend build includes product/profile controls
(M8). Redeploy API before frontend when CORS/API contract changes. Deploy worker after F8
migrations. Signoff includes UJ-005/006/007 live coverage plus F8 live smoke (T7.4).

---

### Session changelog

- S008 (2026-07-12): F6 UJ-001/002/005–010; UJ-DEV-003 deprecated → 003b; T3 seven products
- S008 amend (2026-07-12): UJ-002/005–007 package wiring; UJ-011/012 T2; UJ-013/014 Planned stubs;
  UJ-DEV-004
- S008 05 (2026-07-12): UJ-014 + UJ-OPS-001 aligned to ADR-018 F8 worker (D-S008-05-batch1)
