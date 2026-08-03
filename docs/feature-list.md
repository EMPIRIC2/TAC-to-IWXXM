# Feature List

> **Project**: METAR to IWXXM Converter
> **Repository**: https://github.com/EMPIRIC2/TAC-to-IWXXM
> **Last updated**: 2026-08-01 (S036 / EV-029 — #823 eight-family AHL / lint / convert / validate)

## Summary

| # | Feature | Status | Category | Source |
|---|---------|--------|----------|--------|
| F1 | METAR → IWXXM conversion (GIFTs-era UX) | Superseded by F6 | Product | Historical; UI actions retained until F6 UI |
| F2 | IWXXM validation | Implemented | Product | backend → `packages/iwxxm-validate` |
| F3 | Airport data services | Implemented | Product | OpenAIP / reconciliation services |
| F4 | IWXXM version handling | Implemented | Product | docs/domain/iwxxm/IWXXM_VERSION_SWITCHING.md |
| F5 | User METAR work history | Planned | Product | S023 / EV-017 → **IndexedDB** (was Supabase JWT); #783 |
| F6 | General TAC→IWXXM (`tac2iwxxm`) | Implemented | Product | S008, ADR-013/014/019; bulletin split |
| F7 | Multi-product TAC operator UI / sessions | Planned | Product | S011 / EV-008; F7.g #780; **F7.h** IndexedDB (#783) |
| F8 | Near-realtime TAC ingest → IWXXM gate | Implemented | Product | S008 ADR-018/019; `apps/worker` |
| F9 | Value-aware live decode + plain-language summary | Done | Product | S013 / EV-009; shipped 2026-07-17 (#723) |
| F10 | Workbench preview clarity (IWXXM pane + lint UX) | Done | Product | S013 / EV-009; shipped 2026-07-17 (#723) |
| F11 | Validation stack perf review + msgspec HTTP + XSD codegen | Implemented | Product | S014 / EV-010; #703 |
| F12 | Publishable TAC product validation (`tac-validate`) | Implemented | Product | S014 / EV-010; #698 |
| F13 | Fast IWXXM validate (Rust core + Schematron + PyPI) | Implemented | Product | S014 / EV-010; #699 |
| F14 | Publish `tac2iwxxm` + validate extras + PyPI/release CI | Implemented | Product | S014 / EV-010; #693 |
| F15 | Maintainable TAC lint issue registry + METAR/SPECI quality bar | Done | Product | S015 / EV-011; #732; shipped 2026-07-20 (#742) |
| F16 | Dissemination drawer + multi-DB upload (BYOC URI) | Done | Product | S019 / EV-014; #729; **deepen** S024 / EV-018 multi-select (#785) |
| F17 | WIS2 dissemination pathway | Done | Product | S019 / EV-014; #2; mock-BYOC close (Q15 waive) |
| F18 | EDIS → RTH Washington dissemination | Done | Product | S019 / EV-014; #6; mock-BYOC close (Q15 waive) |
| F19 | AMHS / SWIM / AFS adapters | Done | Product | S019 / EV-014; staging stubs; live optional |
| F20 | TAF + SPECI quality bar (F15 sequel) | Done | Product | S020 / EV-015; #735/#734; #778 |
| F21 | Public unauthenticated operator app | Implemented | Product | S023 / EV-017; #783 |
| F22 | Privacy preference center (Solution A + GPC) | Implemented | Product | S023 / EV-017; #783 |
| F23 | SIGMET family quality bar (general + VA) | Done | Product | S025 / EV-019; #733/#739; PR #792 |
| F24 | AIRMET quality bar | Done | Product | S026 / EV-020; #731; PR #793 |
| F25 | WMO official example parity (METAR/SPECI/TAF) + UI gate | Done | Product | S026 / EV-020; PR #793 |
| F26 | VAA quality bar (VolcanicAshAdvisory) | Done | Product | S027 / EV-021; #736; PR #794 |
| F27 | TCA quality bar (TropicalCycloneAdvisory) | Done | Product | S027 / EV-021; #737; PR #794 |
| F28 | SWXA quality bar (SpaceWeatherAdvisory) | Done | Product | S036 / EV-029; #823/#740 closed; PR #828 |
| M1 | Monorepo layout (`apps/` + `packages/` + `vendor/`) | Planned | Platform | REQ-002–006 |
| M2 | Vendor snapshot sync (wmo-im iwxxm-*) | Planned | Platform | REQ-002, REQ-010 |
| M3 | GIFTs as in-repo package | Deprecated (ADR-014) | Platform | REQ-003; removed with F6 cutover |
| M4 | Auth merged into backend API | Deprecated (operator) | Platform | S023 / EV-017; #783 — operator Auth removed; F8 machine auth remains |
| M5 | Workspace tooling (uv + pnpm + Makefile) | Planned | Platform | REQ-005 |
| M6 | Vendor upstream sync (wmo-im iwxxm-*) | Planned | Platform | REQ-009 |

**Status key**: Implemented = production-ready, Planned = approved in requirements interview, Experimental = works but not validated, Superseded / Deprecated = replaced by a later decision

## Product Feature Details

### F1: METAR → IWXXM Conversion — Superseded by F6

- **Status**: **Superseded by F6** (S008). User-facing Convert / Convert&Send / Upload flows and
  #555 / #664 UX remain until F6 UI pickers land; conversion **engine** becomes `tac2iwxxm`.
- **Historical what it did**: Converted METAR/SPECI TAC via GIFTs.
- **UI actions** (still applicable until F6 UI replaces controls):
  - **Convert** — TAC → IWXXM only.
  - **Convert&Send** — TAC → IWXXM then upload to primary database (fixed defaults).
  - **Upload to Database** — upload previously converted files (dialog).
- **#555 UX (EV-004)**: On successful convert, replace result cards; collapsible error log from
  API `errors`/`issues`.
- **Custom output filename (EV-005 / #664)**: Optional manual-input output basename.
- **Limitations (historical)**: GIFTs; REMARKS stripped; no IWXXM-US.
- **Source**: S008 interview; ADR-014

### F2: IWXXM Validation

- **What it does**: Validates generated IWXXM against schemas and Schematron rules.
- **Inputs**: IWXXM XML, target IWXXM version.
- **Outputs**: Validation report (pass/fail + messages).
- **F6 delta**: Validation consumes WMO vendor pins and, when `profile=iwxxm_us`, combined
  IWXXM-US XSD (and US Schematron if published).
- **S008 package amend**: Core logic moves to **`packages/iwxxm-validate`** (XSD + Schematron
  against `vendor/schemas/*`). `apps/backend` validation routes become a **thin HTTP wrapper**.
  Schematron remains on **IWXXM only** — TAC quality is **F6/`packages/tac-validate`**, not F2.
- **S014 / EV-010 delta (F13)**: Engine gains a **Rust core** (well-formed + XSD + native
  Schematron/SVRL) with Python SDK; pinned schemas **bundled** in the wheel; published to
  PyPI as `iwxxm-validate` `0.1.0`. Backend `/validate` remains a thin wrapper. See F13.
- **Acceptance (this amend)**: Library API + CI tests; backend thin wrappers for validate
  endpoints call `iwxxm-validate` (no behavior regression vs current F2).
- **Limitations**: Schema bundles must match vendored snapshot version.
- **Source**: `apps/backend` validation routers; [Context: realtime-tac-ingest](context/realtime-tac-ingest.md);
  [Context: package-publish-validation](context/package-publish-validation.md)

### F3: Airport Data Services

- **What it does**: Enriches station metadata via OpenAIP and reconciliation across sources.
- **Inputs**: ICAO station identifiers, optional bbox queries.
- **Outputs**: Airport coordinates, elevation, reconciled metadata.
- **Limitations**: External API availability and cache TTL.
- **Source**: docs/guides/OPENAIP_INTEGRATION_PLAN.md, backend services

### F4: IWXXM Version Handling

- **What it does**: Supports multiple IWXXM release lines (e.g. 2023-1, 2025-2) with version-aware formatting.
- **Inputs**: Target version parameter, TAC product input.
- **Outputs**: Version-appropriate IWXXM XML.
- **Limitations**: Only versions present in `vendor/schemas/` snapshots (WMO + iwxxm-us when pinned).
- **Source**: docs/domain/iwxxm/IWXXM_VERSION_SWITCHING.md

### F5: User METAR Work History

- **Status**: **Planned** — **storage model superseded** by S023 / EV-017 / [#783](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/783).
- **What it does (EV-017)**: Persists METAR/SPECI converter work **in the browser (IndexedDB)** —
  status lifecycle **Draft → WIP → Finished** plus **Failed**; resumable on same device without
  login; browseable from converter sidebar and **My METARs**. Client-generated UUID per work item.
  **Export workspace** / **Import workspace** (JSON) for backup/move. No cross-device sync in v1.
- **Historical (pre-EV-017)**: Per-user Supabase Postgres via JWT + `tac_work_sessions` (unified
  under F7 / ADR-020). That server model is **retired for the public product path**.
- **Inputs**: Manual TAC textarea, queued files, conversion params — **no JWT**.
- **Outputs**: Local session records (TAC, IWXXM, errors/issues, timestamps, status). Dissemination
  send refs may be stored locally only; never upload history to public APIs.
- **UI**: Compact recent-history panel (5 recent); **New METAR**; My METARs with status + date
  filters; soft-delete trash (local). Admin cross-user browse remains removed (#697).
- **Legacy server rows**: No public API access. Archive/delete after ~**30-day** window post-cutover
  (optional one-time export if prod data exists). Do not mix IndexedDB IDs with old `user_id` rows.
- **Limitations**: Device-local only; clearing site data loses history unless exported; multi-tab
  last-write-wins locally; no RLS/server ownership.
- **Source**: #555 / S004; unified under F7 (S011); **IndexedDB amend** S023 / EV-017 / #783

### F6: General TAC→IWXXM Converter (`tac2iwxxm`)

- **Status**: **Implemented** (S008 / EV-006 — ADR-019). Local/CI + T0 Playwright approved;
  live H4–H7 / full UI 7-product matrix deferred (12/13 skipped this cycle).
- **What it does**: Converts TAC for **AIRMET, METAR, SIGMET, SPECI, TAF, VAA, and TCA** to IWXXM
  XML via `packages/tac2iwxxm`, with Annex-3 (or product-equivalent) body encoding and optional
  IWXXM-US national extensions; exposes the same products/profiles on HTTP convert and UI pickers;
  measures accuracy in library/CI metrics (not convert-response fields).
- **Package**: `packages/tac2iwxxm` (MIT). Architecture: Python API → (optional bulletin split) →
  IR → product plugins → profile plugins (`annex3` / `iwxxm_us`) → XML writer; metrics via
  `tac-validate` + `iwxxm-validate` in library/CI.
- **Companion packages (this amend)**:
  | Package | Role |
  |---------|------|
  | `packages/tac-validate` | TAC lint + shared business-rule pack (all seven product TAC forms) |
  | `packages/iwxxm-validate` | XSD + Schematron (F2 engine) |
- **Runtime**: Pure Python during M3–M4 development; **Rust/PyO3 required before cutover**
  (ADR-017 amends ADR-014). Not Cython.
- **Inputs**: TAC text/files **or WMO AHL bulletins**; `product`; `profile`; `iwxxm_version`.
- **Outputs**: IWXXM XML (per report after split); validation via F2/`iwxxm-validate`; TAC issues
  via `tac-validate`; metrics reports in tests/CI only.
- **Key parameters**:
| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| `product` | *(required on API)* | `airmet` \| `metar` \| `sigmet` \| `speci` \| `taf` \| `vaa` \| `tca` | UI may auto-detect then send; API rejects omit |
| `profile` | `annex3` | `annex3` \| `iwxxm_us` | International vs US extensions |
| `iwxxm_version` | app default (e.g. `2025-2`) | Vendored pins only | Schema line |
- **API**: Extend `POST /api/v1/convert` with `product` + `profile` (no per-product path prefix).
- **UI**: Product + profile (+ version) pickers in v1; H4–H5 connectivity required.
- **Input traceability (#655 / EV-007)**: Result cards always show Source TAC; TAC-derived
  headline; multi-line index chip; client fallback when API omits `tac_input`.
- **GIFTs**: On first PR that wires tac2iwxxm to `/api/v1/convert`, **remove `packages/gifts`**
  and stop all API use of gifts (hard cutover). REQ-014 / ADR-004 / M3 deprecated.
- **Vendor**: Pin `vendor/schemas/iwxxm-us` via `vendor/manifest.json` — HTTP snapshot of
  [nws.weather.gov/schemas/iwxxm-us/3.0](https://nws.weather.gov/schemas/iwxxm-us/3.0/) with
  `source_url` + content hash (D-S008-05-batch1 / C07).
- **Delivery phases** (v1 goal = all seven products; acceptance order):
  | Phase | Scope |
  |-------|--------|
  | **F6.bulletin** | WMO AHL bulletin split → one report each; golden fixtures (**with/before F6.a**) |
  | F6.a | Package scaffold + METAR/SPECI Annex-3 + metrics harness |
  | F6.b | IWXXM-US METAR/SPECI + vendor `iwxxm-us` (**with M4 cutover**, D-S008-05-batch2) |
  | F6.c | TAF Annex-3 + IWXXM-US forecast extensions |
  | F6.d | SIGMET + AIRMET (intl + US where published) |
  | F6.e | API `product`/`profile` + UI pickers + H4–H5 (M8) |
  | F6.f | VAA + TCA plugins |
- **Acceptance (F6 v1 done)**:
  1. All 7 products convert for pinned WMO versions
  2. `profile=iwxxm_us` encodes published US extensions where schemas exist
  3. M-parse, M-xsd, M-sch required; M-golden / M-field per fixture pack (library/CI)
  4. UI product + profile (+ version); H4–H5 live connectivity
  5. `POST /api/v1/convert` accepts `product` + `profile`; gifts not used
  6. `packages/gifts` removed in first wire-up PR
  7. MIT license; PyO3 + ADR-016 benches **hard-pass at cutover** (ADR-017)
  8. **Bulletin split** required for package acceptance (single-report input still supported)
  9. **`tac-validate` + `iwxxm-validate`** library APIs + CI; backend **thin wrappers** for
     validate (and convert) call these packages
- **S018 / EV-013 delta (#667 REMARKS)**: `annex3` emits `REMARKS_EXCLUDED` (info) when `RMK`
  present; `iwxxm_us` retains unparsed RMK remainder as `humanReadableText` (AO2/SLP/PK WND
  structured emit unchanged; T/P parsed to IR + free-text). Closes UJ-026.
- **Limitations**: US AIRMET/SIGMET docs thinner than METAR/TAF — may gate fixture depth inside
  F6.d; F5 not extended to other products in v1; exact AHL dialect coverage TBD in fixtures.
  Full FMH-1 remark catalog beyond AO/SLP/PK/T/P free-text is still scoped deepen work.
- **S011 / F7 engine deltas** (packages stay under F6; operator UX under F7):
  - `POST /api/v1/decode-tac` — ordered segments with `start`/`end` (+ short explanations).
  - Optional integer `start`/`end` on lint-tac / validate issue objects (span highlight).
  - Soft-fail **preview** convert path returning best-effort IWXXM + failed-span markers
    (exact shape in api-contract / 04-tech-plan).
- **Source**: S008 01-requirements; ADR-013; ADR-014; `docs/context/general-tac-iwxxm-converter.md`;
  `docs/context/realtime-tac-ingest.md`; S011 / EV-008

### F7: Multi-Product TAC Operator UI / Sessions

- **What it does**: Operator-facing UI for all **seven** F6 products — CodeMirror workbench,
  decode panel, failed-TAC / partial-preview UX, and **multi-product work sessions** (separate
  from F5). Shares the convert → lint → Schematron path with F6 packages over JWT HTTP APIs.
- **Status**: **Planned** (build-ready) — **built this cycle** (S011 / EV-008). Status flips to
  Implemented after 11-verify-impl / deploy gate.
- **Relationship to F5**: **Unified sessions** (S011 Spec Batch 2 / R2 amend). Canonical table
  `tac_work_sessions` covers all seven products. Existing F5 `metar_work_sessions` rows
  **migrate** into it (`product` = `metar`/`speci`); `metar_work_sessions` is deprecated and
  dropped after cutover. **My METARs** remains a METAR/SPECI filtered view; workbench history
  shows all products. Do **not** keep a parallel F7-only table.
- **Admin / BYO (R6 / #697)**: Remove `AdminDashboard` and `/admin/*`. Credentials are
  **operator-owned** (Supabase URL/keys **and** Postgres/`DATABASE_URL` via deploy env). No
  in-app paste-keys UI; no shared multi-tenant admin browse/approve/toggle-admin.
- **Delivery slices (R1 order)**:
  | Slice | Issues | Scope |
  |-------|--------|-------|
  | F7.a | #697 | BYO env-contract + admin retirement |
  | F7.b | #702 | `POST /api/v1/decode-tac` + lint/validate `start`/`end` + CodeMirror 6 + decode panel |
  | F7.c | #665/#666 | Failed-TAC visual cue + soft-fail partial/preview convert path |
  | F7.d | #694 | Live workbench (debounced lint/decode/validate/convert, spans, console) |
  | F7.e | F7 / R2′ | Unified `tac_work_sessions` + migrate F5; My METARs filter |
  | F7.f | — | Verify & deploy (08–13) |
  | F7.g | #780 | Pre-loaded golden examples (convert + validate) — S021 / EV-016 |
  | F7.h | #783 | IndexedDB local sessions (all products); drop JWT session APIs — S023 / EV-017 |
- **Inputs**: TAC text/files (`.txt` / `.metar` / `.tac`); `product` / `profile` /
  `iwxxm_version`; optional `bulletin_id` / `issuing_center` / `stop_on_error` /
  `validate_output` / `validation_level` (ADR-023); editor cursor and character spans
  for highlight/hover. **No operator JWT** after F21 (S023).
- **Outputs**: Ordered decode segments (`start`/`end` + explanation); span-aware lint/validate
  issues; best-effort IWXXM + failed-span markers on soft-preview; F7 session rows for seven
  products; optional in-band XSD/Schematron when Strict Validation is on (hard Convert).
- **Deferred (still Later)**: Full COLLECT member extract inside `ingest-collect` (UI + 501
  placeholder shipped ADR-024); deep honor of `include_nil_reasons` in tac2iwxxm emit.
- **Validation deepen (S016 / EV-012 / #730)**: Operator-visible Manual TAC Input modes
  (TAC / AHL / COLLECT) validated via UJ-025 / TC-F7-007 (Playwright **T1–T6** hard + Vitest + staging
  H4–H5 / AHL / COLLECT 501). Auto-switch required. Does **not** flip F7 → Implemented.
- **Golden examples (S021 / EV-016 / #780)**: Frontend-only static catalog in
  `apps/frontend` (copy from package goldens — no Python runtime import). Product-aware
  Examples control in `FileConverter` loads TAC / AHL / happy-path IWXXM into existing
  input modes and sets `product` / `inputMode`. Soft-fail IWXXM and file-upload queue
  **out of v1**. Hazard products may ship **1** known-good when a second in-repo fixture
  is absent (do not invent TAC). UJ-032 / TC-F7-008. Does **not** flip F7 → Implemented.
- **F6 engine companions (still F6 packages; UX under F7)**: decode segments; optional integer
  `start`/`end` on lint/validate issues; soft-preview / partial convert (flag or dedicated
  endpoint — finalize in 04-tech-plan).
- **Editor**: **CodeMirror 6** (new frontend dependency — inventory in 01; install in 04/07).
- **Parent tracker**: GitHub [#5](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/5)
  stays open; close/link child issues as slices land.
- **Acceptance (F7 v1 done)**:
  1. `/admin/*` and AdminDashboard gone; no approval/toggle-admin UI; BYO env documented
  2. Decode panel (Code | Explanation) for all 7 products; residuals explicit when undecoded
  3. Lint/validate issues include optional `start`/`end`; editor can highlight those spans
  4. Soft-preview path returns best-effort IWXXM + failed-span markers; Failed-TAC cue distinct
  5. Live workbench: debounced lint/decode; optional live IWXXM; cancellable in-flight requests
  6. Unified `tac_work_sessions` persist/resume for seven products; F5 rows migrated; My METARs
     = METAR/SPECI filter
  7. H4–H5 connectivity for new browser→API calls; admin E2E retired
  8. Child issues #697/#702/#665/#666/#694 closed or linked; #5 remains open with summary
- **Acceptance (F7.g / #780 — does not complete F7 v1)**:
  1. Each of seven products has ≥2 loadable TAC examples **or** documented 1-fixture gap
     (SIGMET/AIRMET/VAA/TCA when only one in-repo golden exists)
  2. ≥1 AHL bulletin and ≥1 happy-path IWXXM COLLECT/XML example loadable
  3. Loading sets editor body + `product` + `inputMode` when relevant; demo labeling clear
  4. Vitest: catalog completeness + click-to-load (TC-F7-008); H4–H5 smoke when FE deploys
     (**live H4–H5 waived 2026-07-27** → [#781](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/781);
     code on `main` @ `c49f22b` / PR #782)
  5. No backend routes, env vars, or DB seeds required
- **Resolved gaps (S011 Feature List Batch 2)**:
  | ID | Decision |
  |----|----------|
  | G1 | Keep `DISABLE_AUTH` / local–CI auth bypass patterns; BYO is deploy topology only |
  | G2 | Self-signup vs invite-only is **operator Supabase policy** — app adds no invite gate |
  | G3 | **No product migration** of shared-project users/data; clean BYO cut (point env at own project) |
  | G4 | VAA/TCA decode spans: **best-effort + explicit residuals** in v1 (full field offsets not required) |
  | R2′ | **Override R2**: unified `tac_work_sessions` + migrate F5 rows (Spec Batch 2 A / 2026-07-13) |
  | R2″ | **Override R2′ storage**: browser IndexedDB (S023 / EV-017 / #783); server session table retired from public product |
- **G1 amend (EV-017)**: Retire `DISABLE_AUTH` dual path when operator Auth is removed (F21) —
  public routes are the only operator path; F8 keeps separate machine credentials.
- **Source**: S011 Phase 0 R1–R6; Feature List Batches 1–2 (2026-07-13);
  [Context: f7-operator-ui](context/f7-operator-ui.md); issues #694/#702/#665/#666/#697;
  [Context: golden-examples-ui](context/golden-examples-ui.md); #780 (S021 / EV-016);
  [Context: public-app-privacy](context/public-app-privacy.md); #783 (S023 / EV-017)

### F8: Near-Realtime TAC Ingest → IWXXM Gate

- **Status**: **Implemented** (S008 / EV-006 — ADR-018/019). Worker unit/pipeline approved;
  live T7.4 staging smoke deferred (12/13 skipped this cycle).
- **What it does**: Continuous/near-realtime ingest of TAC (and bulletins) → `tac-validate` →
  `tac2iwxxm` → `iwxxm-validate` (Schematron/XSD) → **store**; **quarantine** on convert
  or Schematron failure (no publish). Latency target **&lt;5–15s** E2E; scale via **worker
  replicas** (drop nothing). Product scope = F6 seven.
- **Deployable**: Render Background Worker at `apps/worker/`; HTTPS/object poller; Supabase
  store + separate quarantine; service-role JWT for writers. Template → `static+api+worker`.
- **Non-goals (F8 worker path)**: public machine-ingest auth UX; **automatic** push of ingest
  results (operator dissemination sinks are **F16–F19**, not F8 auto-push).
- **Source**: [Context: realtime-tac-ingest](context/realtime-tac-ingest.md) R2–R15; ADR-018;
  [execution-plan](sessions/S008-general-tac-iwxxm-converter/reports/execution-plan.md)

### F9: Value-Aware Live Decode + Plain-Language Summary

- **Status**: **Done** — shipped S013 / EV-009 (2026-07-17, PR #723).
- **What it does**: Upgrades the F7 decode panel from generic group labels to **value-aware
  translations**, and adds a live **plain-language summary** of the whole report.
  - `packages/tac2iwxxm` `decode_tac` parses actual token values for all **seven** products:
    `24/18` → "Temperature 24 °C, dewpoint 18 °C"; `18004KT` → "Wind from 180° at 4 kt";
    `10SM` → "Visibility 10 statute miles"; `A3011` → "Altimeter 30.11 inHg"; etc.
    METAR/SPECI/TAF rich; SIGMET/AIRMET/VAA/TCA best-effort (residuals stay explicit — G4).
  - `decode_tac` builds a **deterministic** natural-language `summary` string (one flowing
    paragraph from decoded values; no LLM). Unrecognized content appends a
    "Not decoded: …" clause naming residual spans. Sparse products emit a short best-effort
    summary with "partial decode" wording.
  - `POST /api/v1/decode-tac` response gains `summary` (additive).
  - Frontend renders the summary live as a **"Plain language"** block at the top of the
    decode panel via the existing 300 ms debounce path (UJ-017 infrastructure).
- **Inputs**: TAC text; `product` (same enum as convert); JWT.
- **Outputs**: Value-aware `segments[].explanation`; `summary` string; residuals unchanged.
- **Out of scope**: LLM/AI-generated text; changing segment offsets contract; Layer 1–2 or
  Schematron semantics.
- **Acceptance (F9 v1 done)**:
  1. METAR/SPECI/TAF golden fixtures produce value-aware explanations for wind, visibility,
     temperature/dewpoint, altimeter/QNH, time, station, clouds, weather groups
  2. `summary` present for all seven products (best-effort where sparse) and updates live
     while typing
  3. Residuals named in summary via "Not decoded: …" when present
  4. Decode response stays backward-compatible (additive `summary` only)
- **Source**: S013 intake E9-2/E9-3/E9-4/E9-6; Batch 1 (all recommended, 2026-07-16);
  [evolve-decisions §EV-009](decisions/evolve-decisions.md)

### F10: Workbench Preview Clarity (IWXXM Pane + Lint UX)

- **Status**: **Done** — shipped S013 / EV-009 (2026-07-17, PR #723).
- **What it does**: Makes it obvious **where** Soft-preview / Live IWXXM output appears and
  removes confusing failure copy (user feedback on #665/#666/#694 surfaces).
  - **Side-by-side IWXXM preview pane** inside the workbench: pretty-printed IWXXM XML of
    the most recent preview + status badge (**Soft preview — not for publish** vs
    **Passed**) + failed-span count linked to editor highlights. Stacks below the editor
    under the `lg` breakpoint.
  - **`LAYER12_SOFT_FAIL` copy**: reword to plain language (status, cause, next step) in the
    pane badge and console line.
  - **`MISSING_TERMINATOR`**: downgrade to `info` severity in `packages/tac-validate`
    with actionable copy ("Reports in bulletins end with '=' — add it before publishing");
    `ok` remains keyed off `error` issues so single pasted reports lint clean. One-click
    **"Add `=`"** quick fix on the lint console line and as an editor affordance on the
    info-hint span hover.
- **Out of scope**: Changing preview/convert API semantics; new endpoints; altering
  Layer 1–2 checks themselves.
- **Acceptance (F10 v1 done)**:
  1. Preview pane visible side-by-side (≥ `lg`) and stacked (< `lg`); Soft-preview and
     Live IWXXM outputs land in the pane with status badge + span count
  2. Soft-fail copy explains "best-effort preview, not publishable" without error-code jargon
  3. `MISSING_TERMINATOR` is `info`; lint `ok: true` for otherwise-clean single reports
  4. "Add `=`" quick fix appends terminator from console line and editor affordance
- **Source**: S013 intake E9-5/E9-7; Batch 2 (all recommended, 2026-07-16);
  [evolve-decisions §EV-009](decisions/evolve-decisions.md)

### F11: Validation Stack Perf Review + msgspec HTTP + XSD Codegen

- **Status**: **Implemented** — S014 / EV-010 (#703 + ADR-026).
- **What it does**:
  1. **Layer cost matrix** — measure TAC lint, convert IR, XSD, Schematron, and HTTP DTO
     encode/decode (pydantic map vs msgspec) on single METAR, bulletin, and golden IWXXM;
     commit under session reports / `docs/context/`.
  2. **msgspec on high-churn HTTP** — `POST /api/v1/convert`, `/convert-zip`,
     `/convert-bulletin`, `/validate`, `/lint-tac`, `/decode-tac` use msgspec for **response**
     encode (+ optional Struct after multipart assemble); request intake stays multipart
     FastAPI Form/File. Auth/admin/work-sessions stay pydantic. **Pydantic retained for OpenAPI**
     schema integrations via thin aliases/export (ADR-026). Breaking **response** JSON shapes
     allowed; FE types updated same cycle; full Render 12–13.
  3. **Production XSD codegen** — generate Python models from published IWXXM **XSD**
     via **xsdata** (+ xsdata-pydantic) (ADR-027; modelling UML = provenance only);
     regenerate in CI on vendor pin bumps. Follow-on in-cycle tasks adapt generated models
     toward msgspec Structs and/or Rust types where convert builders benefit. Validate hot
     path remains Rust XSD+Schematron (F13) — not full Python bind-on-validate. TAC has
     **no** official model to import.
  4. Dedup orchestrator vs `iwxxm-validate` call paths so convert+validate does not double-run
     heavy layers.
- **Acceptance**:
  1. Layer cost matrix with p50/p95 (or blocked-with-reason) committed
  2. High-churn routes on msgspec; OpenAPI still published; FE types updated
  3. Soft benches during build; hard-fail at publish/cutover: library lint→convert→XSD+SCH
     vs lxml baseline; msgspec HTTP ≤ prior pydantic map path; wheel smokes
  4. Codegen from XSD in CI (xsdata → pydantic models per ADR-027; TAC out of scope)
- **Source**: Issues #703; E10-1..27; ADR-016 amended by ADR-026;
  [Context: package-publish-validation](context/package-publish-validation.md)

### F12: Publishable TAC Product Validation (`tac-validate`)

- **Status**: **Implemented** — S014 / EV-010 (#698); deepen METAR/SPECI via F15 / EV-011;
  EMPIRIC2 OIDC + consumer landing pages EV-028 / #781 (`0.1.1`).
- **What it does**: Design + publish **`tac-validate`** to PyPI — standalone TAC
  product validation for all seven F6 products with structured issues (code, severity, span).
  Aggressively encode mined rules from `docs/domain/` (cite-only for paywalled Annex text):
  **full depth** METAR/SPECI/TAF; SIGMET/AIRMET/VAA/TCA structured templates + coverage-matrix
  gates. CLI `tac-validate` for CI. No IWXXM/XSD in this package.
- **Acceptance**:
  1. `pip install tac-validate==<version>` in clean venv; library + CLI smoke (`0.1.0` first;
     `0.1.1`+ via EMPIRIC2 Trusted Publisher)
  2. METAR/SPECI/TAF full checklist rules; other products template+gate coverage documented
  3. Negative fixtures with useful diagnostics; CI wheel + fixture suite
  4. Tag `tac-validate-v*` → trusted-publishing workflow (`pypi-publish.yml` on
     `EMPIRIC2/TAC-to-IWXXM`)
  5. PyPI landing (`README.md` / `description`) usable without internal ADR/Feature IDs
- **Source**: #698; E10-4/9/19/21; docs/domain/rules/COVERAGE_MATRIX.md; #781

### F13: Fast IWXXM Validate (Rust Core + Schematron + PyPI)

- **Status**: **Implemented** — S014 / EV-010 (#699); EMPIRIC2 OIDC + consumer landing
  pages EV-028 / #781 (`0.1.1`).
- **What it does**: Publish **`iwxxm-validate`** with Rust core (PyO3/maturin):
  well-formed + XSD + **native Rust Schematron/SVRL**; Python SDK
  `validate_iwxxm(...)`; pinned `vendor/schemas/*` **bundled** in the wheel; version/profile
  selection aligned with manifest pins. Parity suite vs current lxml isoschematron.
  Backend F2 wrapper calls the SDK.
- **Acceptance**:
  1. `pip install iwxxm-validate==<version>`; `validate_iwxxm` returns structured issues for
     well-formed + XSD + Schematron
  2. Benchmarks show meaningful speedup vs current Python path; hard gate at publish
  3. Parity tests vs golden IWXXM corpus; IWXXM-US profile supported when pin present
  4. Tag `iwxxm-validate-v*` → trusted publishing; no TAC parsing in package
  5. PyPI landing usable without internal ADR/Feature IDs
- **Source**: #699; E10-6/7/19/22; ADR-017; #781

### F14: Publish `tac2iwxxm` + Validate Extras + PyPI/Release CI

- **Status**: **Implemented** — S014 / EV-010 (#693); EMPIRIC2 OIDC + consumer landing
  pages EV-028 / #781 (`0.1.1`).
- **What it does**: Publish **`tac2iwxxm`** to PyPI (conversion library + optional
  PyO3). Extra **`tac2iwxxm[validate]`** depends on `tac-validate` + `iwxxm-validate`.
  Shared GitHub Actions **OIDC trusted publishing** — one workflow matrix on version
  tags (`tac2iwxxm-v*`, `tac-validate-v*`, `iwxxm-validate-v*`) against
  `EMPIRIC2/TAC-to-IWXXM`. Documented public API + wheel smoke tests.
- **Acceptance**:
  1. `pip install tac2iwxxm==<version>` converts sample METAR → IWXXM
  2. `pip install tac2iwxxm[validate]` pulls both validators
  3. Tag-driven publish CI green; README install/usage (consumer-facing, no ADR/Fn required)
  4. UJ-DEV-005 / UJ-023 smokes pass
- **Source**: #693; E10-5/19/20/25; #781

### F15: Maintainable TAC Lint Issue Registry + METAR/SPECI Quality Bar

- **Status**: **Done** — shipped S015 / EV-011 (2026-07-20, PR [#742](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/742));
  issue [#732](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/732) closed on cycle close.
- **What it does**: Introduces a **maintainable issue registry** in `packages/tac-validate`
  (machine-readable `code` + default `severity` `info`|`warning`|`error` + message template).
  Rules import registry entries; a docs/generated catalog lists all codes for operators and
  maintainers. Raises **METAR and SPECI** TAC lint, convert, and IWXXM-validate quality to the
  F6.a/F6.b reference-product bar: expand accept/negative fixtures, golden TAC→IWXXM→XSD+Schematron,
  coverage-matrix METAR/SPECI row review, METAR↔SPECI adjacency, and opportunistic rule/convert
  improvements from external METAR/IWXXM research (MetarCentral, AviationRef, iwxxmConverter —
  cite-only for paywalled Annex text).
- **Registry home**: `packages/tac-validate` module + docs/generated catalog (**ADR-028**).
  Product-agnostic shape from day one; **this cycle encodes METAR/SPECI deeply** (R1–R8 +
  opportunistic); other products may gain thin registry rows when rules already emit codes.
- **Code stability**: Public issue codes are **stable** — renames require a deprecation note;
  default severities may tighten in minor releases (E11-10).
- **Deepens**:
  | Feature | Role this cycle |
  |---------|-----------------|
  | **F6** | METAR convert fidelity + `product_matrix` / golden IWXXM; Annex-3 + `iwxxm_us` where fixtures allow (COR/NIL/RMK as scoped) |
  | **F12** | METAR checklist rules wired through registry; accept + negative fixtures; no silent success |
- **Acceptance**:
  1. All METAR/**SPECI** lint emissions use registry codes; CI fails on unknown codes
  2. Adding a rule = registry row + fixture(s); no ad-hoc severity string literals in rule bodies
  3. Coverage-matrix METAR/**SPECI** rows updated; **R1–R8 themes closed this cycle** (HARD —
     E11-23/28); non–R-theme gaps only may defer with rationale + AskQuestion
  4. Accept METAR **and SPECI** → convert → `iwxxm-validate` XSD+Schematron pass (pinned
     versions) for expanded golden pack
  5. Negative METAR/**SPECI** fixtures produce useful diagnostics (no silent success)
  6. Workbench / `product=metar` **and** `product=speci` lint+convert smoke documented
     (F7 remains Planned; smoke only under F15); METAR↔SPECI adjacency covered (UJ-024 / TC-F15-005);
     catalog tooltips via `GET /api/v1/lint-issue-catalog` (E11-31)
- **Out of scope**: New products beyond the seven F6 set; COLLECT/dissemination; FlightPlanDatabase
  FMS as METAR authority; closing sibling product-quality tickets unless registry sharing requires it.
- **Source**: #732; E11-1..E11-10; [context/metar-lint-quality.md](context/metar-lint-quality.md);
  ADR-028; `docs/domain/rules/COVERAGE_MATRIX.md`

### F6 deepen (S015 / EV-011 — METAR)

- **Status note**: F6 remains **Implemented**; this cycle **deepens METAR/SPECI** convert/golden
  fidelity under F15 acceptance (not a new Fn). Track gaps vs #732 known list (COR/NIL/remarks;
  IWXXM-US AO2/SLP/PK WND; AHL+SPECI adjacency) — **R1–R8 themes must close** (HARD); other
  convert gaps outside those themes may defer only via AskQuestion + coverage note.

### F12 deepen (S015 / EV-011 — METAR)

- **Status note**: F12 remains **Implemented** (PyPI `0.1.0`); this cycle routes METAR/**SPECI**
  rules through the F15 registry and expands accept/negative packs to full-depth checklist targets.

### F16: Dissemination drawer + multi-DB upload (BYOC URI) — S019 / EV-014

- **Status**: **Done** (EV-014 closed 2026-07-21; #771/#772). **Deepen** S024 / EV-018 / [#785](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/785) — multi-file export selection (in progress).
- **What it does**: Unified **dissemination drawer** for Convert&Send / Upload: any **public**
  operator (F21 — no login) pastes a **one-shot** destination URI (memory-only on API; never
  persisted; no saved profiles). Backend-mediated preflight + send with structured schema diff;
  **block Send** until green. Supports **convert-then-send** and **drag-drop** of external
  IWXXM/TAC. **DDL / create-if-missing** against a versioned writer contract when the target
  table is missing or mismatched. Multi-DB sinks: **Postgres, MySQL/MariaDB, SQL Server,
  SQLite** (Q23=A–D; no other named vendor).
- **Auth vs destination**: Destination secrets are **not** Supabase and are never stored
  (IndexedDB may hold `kv_upload_key` / metadata only after F21).
- **Security (Q11=A+B)**: Backend-only egress; deny private/metadata ranges; DNS rebinding guard;
  TLS preferred; timeouts/size limits; secret redaction; rate limits; **required**
  `DISSEMINATION_EGRESS_ALLOWLIST` (empty ⇒ no user-URI egress).
- **UI**: Sink chooser in same drawer — Postgres/MySQL/… (F16), WIS2 (F17), EDIS (F18),
  AMHS/SWIM/AFS (F19).
- **EV-018 deepen (#785) — multi-file export selection**:
  1. **Export selection** panel lists eligible candidates (name, product type, size/status,
     source) from **current-session conversion outputs** and **dropped files** only (Finished
     IndexedDB history **out of scope** for v1 — E18-4).
  2. **Multi-select** — checkboxes + select-all / clear; Disseminate / Preflight-only operate on
     the **current selection only**.
  3. **Empty selection** disables Disseminate and Preflight-only with a clear message.
  4. Client runs **N sequential interleaved** `/preflight` then `/send` **per file**, then next
     (E18-10); continues after failures and **aggregates** per-file pass/fail/skip — **no**
     batched multi-payload API in v1 (E18-5/11). Primary **Disseminate**; optional
     **Preflight only** (E18-15).
  5. Selection **count cap ≤20**; reuse existing body/size limits; clear error when over (E18-6).
     Sole candidate: auto-selected; Export selection collapsed/optional (E18-9).
  6. Per-file **progress graphic**: mail travels along an arrow to the destination sink icon;
     green check on success, red mark on fail (E18-10/13). When `prefers-reduced-motion`,
     hide graphic and show text-only status (E18-14).
  7. F17–F19 **reuse the same selection contract** in the drawer (E18-2).
- **Acceptance** (base EV-014 + EV-018):
  1. Preflight returns actionable schema/permission/auth diffs; Send disabled until green
  2. One-shot URI never appears in logs, session JSON, or IndexedDB rows
  3. Allowlist enforced; private-IP / metadata targets rejected
  4. DDL path creates/migrates to versioned writer contract when opted
  5. Drag-drop and convert-then-send both reach the same preflight→send path
  6. All four DB engines covered by contract tests (SQLite may be file/local harness)
  7. When >1 candidate exists, drawer shows selectable list; select-all / clear work
  8. Disseminate / Preflight-only apply only to selection; empty selection disables both with message
  9. After run, per-file success/failure/skip is visible (progress graphic or text); one failure
     does not silently drop the rest without reporting
  10. BYOC credentials remain memory-only; no new destination-secret persistence
  11. Playwright visual snapshot of progress row (in-flight + failed) passes (E18-16)
- **Out of scope**: Saved/encrypted connection profiles; pasting Supabase **auth** keys in-app;
  F8 auto-push; Finished work-history as export sources (v1); batched multi-payload API (v1);
  browser zip archive download unrelated to sink send
- **Source**: #729; S019 / EV-014; ADR-021 amend; ADR-029 (SSRF); ADR-030 (package/API);
  **#785; S024 / EV-018** (multi-select deepen)

### F17: WIS2 dissemination pathway — S019 / EV-014

- **Status**: **Done** (EV-014 closed 2026-07-21; live destination BYOC waived via
  `D-S019-EV014-Q15-mock-waive`).
- **What it does**: Publish converted IWXXM via **WIS2** (MQTT notification + HTTP dataset) from
  the dissemination drawer. **Test harness**: project **Docker Compose / CI** wis2box
  (Q12=B / Q17 / E14-04=B — **not** a long-lived Render web service; may run on CI or a
  disposable Docker host). **Live**: user BYOC WIS2 node/endpoint credentials (memory-only);
  EV-014 close used mock/harness evidence instead of live destination demos (Q15/Q21 amended).
- **Acceptance**: Staging wis2box e2e in CI/staging; mock BYOC close-gate evidence for EV-014;
  drawer sink type WIS2 with preflight-equivalent connectivity checks; **EV-018** reuses F16
  export multi-select contract when multiple candidates exist.
- **Source**: #2; WIS2 overview / wis2box; S019 / EV-014; S024 / EV-018 (#785 selection reuse)

### F18: EDIS → RTH Washington dissemination — S019 / EV-014

- **Status**: **Done** (EV-014 closed 2026-07-21; live destination BYOC waived via
  `D-S019-EV014-Q15-mock-waive`).
- **What it does**: Produce **EDIS-compliant** ASCII messages with correct WMO abbreviated headers
  and submit to **NWS Telecommunications Gateway (RTH Washington)** using **one-shot BYOC**
  SMTP/gateway settings in the drawer (Q18≈A / Q16). EV-014 close used mocked SMTP/harness
  evidence (Q15/Q21 amended).
- **Acceptance**: Format validation + mocked submission path green; secrets never persisted;
  allowlist/SSRF policy applies to SMTP hosts.
- **Source**: #6; S019 / EV-014

### F19: AMHS / SWIM / AFS adapters — S019 / EV-014

- **Status**: **Done** (EV-014 closed 2026-07-21; staging stubs; live demos optional / not required).
- **What it does**: Dissemination adapters for **AMHS**, **SWIM**, and **AFS** selectable in the
  same drawer (Q20=D). BYOC connection parameters; backend-mediated; same secret/SSRF posture as
  F16–F18.
- **Acceptance**: Each adapter has a documented contract + staging/test path green (met).
  Postgres + WIS2 + EDIS close gate satisfied via mock BYOC waive for EV-014. F19 **live**
  demos remain optional follow-up.
- **Source**: S019 / EV-014 Phase 0 Q20=D / Q24=A; 02-verify-plan S-EV014-M2 (Q28=A)

### F20: TAF + SPECI Quality Bar (F15 Sequel) — S020 / EV-015

- **Status**: **Done** — S020 / EV-015; PR [#778](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/778)
  merged `eae8bdc`; T5.7 H1–H5 + catalog taf/speci live 2026-07-22
  (`reports/deploy-smoke.md`). Phase 0 approved 2026-07-22 (E15-1..E15-8;
  `D-S020-EV015-route-1` Lean+build).
- **What it does**: Raises **TAF** and **SPECI** TAC lint, convert, and IWXXM-validate quality
  to the same bar F15 set for METAR/SPECI. Reuses the **ADR-028** issue registry (new TAF codes
  + SPECI deepen as needed; no new registry architecture). Audits encode paths against WMO
  `TAC-to-XML-Guidance.txt` **plus** 2025-2 corrections (no removed `runwayState`). Expands
  accept/negative fixtures, golden TAC→IWXXM→XSD+Schematron, and coverage-matrix **TAF** +
  **SPECI** rows. SPECI is a **full** parallel quality bar (#734), not residual-only — including
  Auto-detect / lint never mis-classifying SPECI↔METAR.
- **Issues**: [#735](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/735) (TAF),
  [#734](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/734) (SPECI).
- **Deepens**:
  | Feature | Role this cycle |
  |---------|-----------------|
  | **F6** | F6.c TAF Annex-3 + IWXXM-US forecast extensions; F6.b SPECI convert/golden fidelity |
  | **F12** | TAF + SPECI checklist rules via registry; accept + negative fixtures; no silent success |
  | **F15** | Registry already product-agnostic; this cycle adds/extends codes only (F15 stays Done) |
- **Acceptance**:
  1. TAF and SPECI lint emissions use registry codes; CI fails on unknown codes
  2. #735 exceptional-rule table (NIL/CNL/AMD/COR, FM/BECMG/TEMPO/PROB, TX/TN, CAVOK/NSC/NSW, …)
     has accept + negative fixtures (or explicit deferrals with rationale)
  3. #734 exceptional-rule table (shared METAR/SPECI rules + mis-classification guards) has
     accept + negative fixtures (or explicit deferrals)
  4. Coverage-matrix TAF + SPECI rows updated; guidance gaps filed or closed
  5. Accept TAF **and** SPECI → convert → `iwxxm-validate` XSD+Schematron pass (pinned versions)
     for expanded golden pack; roots match `iwxxm:TAF` / `iwxxm:SPECI`
  6. Workbench / `product=taf` **and** `product=speci` lint+convert smoke documented
     (F7 remains Planned; smoke only under F20); H1–H3 if API ships; H4–H5 when FE touched
- **Out of scope**: Sibling product-quality tickets (#731, #733, #736–#741, …) unless shared
  common-rule touch; PyPI release bumps; F16–F19 changes; COLLECT; new products beyond F6 seven
- **Source**: #735/#734; E15-1..E15-8; [context/aerodrome-quality.md](context/aerodrome-quality.md);
  ADR-028; `docs/domain/rules/COVERAGE_MATRIX.md`; predecessor F15 / EV-011

### F6 deepen (S020 / EV-015 — TAF + SPECI)

- **Status note**: F6 remains **Implemented**; this cycle **deepens TAF (F6.c) and SPECI (F6.b)**
  convert/golden fidelity under F20 acceptance (not a new Fn). Track gaps vs #735/#734
  exceptional-rule tables and WMO guidance + 2025-2 corrections.

### F12 deepen (S020 / EV-015 — TAF + SPECI)

- **Status note**: F12 remains **Implemented**; this cycle expands TAF/**SPECI** rules through
  the ADR-028 registry and accept/negative packs to full-depth checklist targets for both products.

### F21: Public Unauthenticated Operator App — S023 / EV-017

- **Status**: **Implemented** (S023 / EV-017 / [#783](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/783); 11-verify-impl approved 2026-07-28)
- **What it does**: Makes the operator product **public** — no login/signup/logout/password-reset
  UX; no required Bearer JWT for convert, validate, lint, decode, preview, or dissemination-drawer
  flows. HTTP APIs are **stateless** with **baseline abuse controls** (per-IP + global rate limits,
  request/batch size limits, conversion timeouts/concurrency, content validation, generic errors).
  Dissemination keeps SSRF controls + destination allowlists; BYOC credentials memory-only
  (ADR-021/029). Retire operator `/auth/*` and `DISABLE_AUTH` dual path. **F8** worker
  service-role remains private (not part of the public router).
- **Sequence**: Ship IndexedDB F5/F7 (F7.h) **before** tearing down JWT session ownership.
- **Acceptance**:
  1. Unauthenticated user completes convert → validate → download/send without login
  2. No operator-facing `/auth/login` required in production
  3. Public `/api/v1/work-sessions*` removed or return gone; no access to legacy Supabase rows
  4. Abuse-control tests green; dissemination allowlist/SSRF unchanged in spirit
  5. Env/docs no longer require operator Supabase Auth for the public product path
  6. E2E: UJ-003 superseded; UJ-001/004/018 and H3–H6 updated for public path
- **Out of scope**: Legal DPIA; removing F8 credentials; admin UX; optional accounts; anonymous
  server sessions; CMP/analytics
- **Source**: #783; E17-4..E17-10; [Context: public-app-privacy](context/public-app-privacy.md)

### F22: Privacy Preference Center — S023 / EV-017

- **Status**: **Implemented** (S023 / EV-017 / #783; 11-verify-impl approved 2026-07-28)
- **What it does**: **Solution A** (no non-essential tracking). Inventory cookies/`localStorage`/
  `sessionStorage`/IndexedDB/CDN. Footer **Privacy settings** + short first-visit notice.
  One global preference schema (versioned); `necessary` always on; preferences/analytics/marketing
  default **false** and only shown if used. Honor **GPC**. Disclose IndexedDB work history.
  No CMP. Do not imply sale/share if the product does not sell personal information — still honor GPC.
- **Acceptance**:
  1. Privacy settings reachable from footer; preferences persist and are withdrawable
  2. Non-essential scripts (if any later) blocked until allowed — v1 has none
  3. GPC detection forces sale/sharing opt-out flags when applicable
  4. Privacy/Cookie policy links with jurisdiction-aware language (engineering copy; counsel review OOS)
  5. UJ-033 + TC-F22-* cover notice + settings + GPC
- **Source**: #783; E17-7/E17-9; ICO / CPPA baselines (engineering only)

### F23: SIGMET Family Quality Bar (General + VA) — S025 / EV-019

- **Status**: **Done** — S025 / EV-019 closed 2026-07-29 (PR [#792](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/792)
  merged `afffe86`; H1–H5 + live SIGMET catalog/lint/convert PASS).
- **What it does**: Raises **General SIGMET** and **Volcanic-ash SIGMET** TAC lint, convert,
  and IWXXM-validate quality to the same bar F15/F20 set for aerodrome products. Reuses the
  **ADR-028** issue registry (new SIGMET / VA SIGMET codes as needed; no new registry
  architecture). Audits encode paths against WMO `TAC-to-XML-Guidance.txt` **plus** 2025-2
  corrections. Expands accept/negative fixtures, golden TAC→IWXXM→XSD+Schematron, and
  coverage-matrix themes **G1–G3 / V1–V3 / C1**. Distinguishes VA SIGMET
  (`iwxxm:VolcanicAshSIGMET`) from VAA advisory (`iwxxm:VolcanicAshAdvisory`).
  API keeps `product=sigmet`; converter selects root from TAC (VA phenomenon / WV AHL) —
  **no new product enum** (E19-13=A).
- **Issues**: [#733](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/733) (general SIGMET),
  [#739](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/739) (VA SIGMET).
- **Deepens**:
  | Feature | Role this cycle |
  |---------|-----------------|
  | **F6** | F6.d SIGMET (+ VA SIGMET root) convert/golden fidelity per guidance |
  | **F12** | SIGMET + VA SIGMET checklist rules via registry; accept + negative fixtures |
  | **F15** | Registry already product-agnostic; this cycle adds/extends codes only (F15 stays Done) |
- **Acceptance**:
  1. SIGMET and VA SIGMET lint emissions use registry codes; CI fails on unknown codes
     (**TC-F23-001**)
  2. #733 exceptional-rule table (CNL, point→circle, single altitude, STNR, polygon/line CRS, …)
     has accept + negative fixtures (or explicit deferrals with rationale) (**G1**; TC-F23-002/004)
  3. #739 exceptional-rule table (volcano identity, ash geometry/forecast, `NO VA EXP`, CNL
     FIR-moved-ash) has accept + negative fixtures; not confused with VAA encode
     (**V1–V2**; TC-F23-003/004/006)
  4. Common rules covered: `reportStatus` / `permissibleUsage`, `translationFailedTAC`,
     geometry CRS, nilReasons, one-IWXXM-per-TAC-report (**C1**)
  5. Coverage-matrix SIGMET + VA SIGMET / F23 themes updated; guidance gaps filed or closed
  6. Accept fixtures → convert → `iwxxm-validate` XSD+Schematron pass (pinned versions);
     roots match `iwxxm:SIGMET` / `iwxxm:VolcanicAshSIGMET` for pinned `iwxxm_version`
     (esp. 2025-2) (**G3/V3**; TC-F23-002/003)
  7. Workbench / product path lint+convert smoke (**UJ-034** / **TC-F23-005**; F7 remains
     Planned; smoke only for product path); **additive FE catalog filters/copy for SIGMET
     (+ VA) tags** (E19-17=B amends E19-14); H1–H3 if API ships; **H4–H5 required** when FE
     touched (E19-7 / E19-17)
- **Journeys / tests**: **UJ-034**; **TC-F23-001..006**
- **Out of scope**: [#738](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/738) TC SIGMET;
  [#731](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/731) AIRMET; [#736](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/736)
  VAA; [#737](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/737) TCA; #740 SWX; #741 VONA;
  PyPI release bumps; F16–F19; COLLECT; new `product` enum values — unless shared
  common-rule touch (E19-6 / E19-13)
- **Source**: #733/#739; E19-1..E19-18; [context/sigmet-quality.md](context/sigmet-quality.md);
  ADR-028; `docs/domain/rules/COVERAGE_MATRIX.md`; predecessors F15 / EV-011, F20 / EV-015

### F6 deepen (S025 / EV-019 — SIGMET + VA SIGMET)

- **Status note**: F6 remains **Implemented**; this cycle **deepens F6.d** (general SIGMET +
  content-selected **`iwxxm:VolcanicAshSIGMET`** root) convert/golden fidelity under F23
  acceptance (not a new Fn). Track gaps vs #733/#739 exceptional-rule tables and WMO
  guidance + 2025-2 corrections. TC SIGMET remains sibling #738.

### F12 deepen (S025 / EV-019 — SIGMET + VA SIGMET)

- **Status note**: F12 remains **Implemented**; this cycle expands SIGMET / VA SIGMET rules
  through the ADR-028 registry and accept/negative packs to full-depth checklist targets.

### F24: AIRMET Quality Bar — S026 / EV-020

- **Status**: **Done** — S026 / EV-020 closed 2026-07-29 (PR [#793](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/793)
  merged `0f77194`; H1–H5 + live AIRMET smoke PASS).
- **What it does**: Raises **AIRMET** TAC lint, convert, and IWXXM-validate quality to the
  F15/F20/F23 bar. Target: WMO vendor `airmet-A6-1a-TS` TAC→IWXXM **`canonicalize_xml`-equal**
  under **default** convert settings (`profile=annex3`, default pinned `iwxxm_version`).
  Reuses **ADR-028** registry; **ADR-032** golden/glossary policy.
- **Issues**: [#731](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/731).
- **Deepens**: **F6** (AIRMET encode), **F12** (AIRMET checklist), **F7.g** (examples when passing).
- **Acceptance**:
  1. Registry-backed AIRMET lint codes; accept + negative fixtures (**TC-F24-001/004**)
  2. Convert of WMO `airmet-A6-1a-TS.tac` → `canonicalize_xml` equal to vendor XML under defaults;
     geometry present (**TC-F24-002**)
  3. XSD+Schematron pass on that golden (**TC-F24-003**)
  4. Workbench product-path smoke; H4–H5 when FE touched (**TC-F24-005** / **UJ-035**)
- **Journeys / tests**: **UJ-035**; **TC-F24-001..005**
- **Out of scope**: TC SIGMET #738; treating translation-failed WMO examples as happy-path goldens;
  non-default profile/version golden equality
- **Source**: E20-*; ADR-032; [evolve-decisions.md](decisions/evolve-decisions.md) §EV-020

### F25: WMO Official Example Parity (METAR/SPECI/TAF) + UI Gate — S026 / EV-020

- **Status**: **Done** — S026 / EV-020 closed 2026-07-29 (PR [#793](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/793)
  merged `0f77194`; H1–H5 + live WMO METAR/SPECI/TAF + catalog smoke PASS).
- **What it does**: Brings **METAR / SPECI / TAF** convert output to **`canonicalize_xml`-equal**
  match against WMO IWXXM `2025-2` vendor examples under **default** settings. Updates the F7.g
  **Examples** catalog so **only** demos that pass the strict WMO bar are offered (SIGMET keepers
  from F23; AIRMET when F24 passes).
- **Deepens**: **F6** encode fidelity; **F15** / **F20** quality bars; **F7.g** catalog policy.
- **Acceptance**:
  1. Listed WMO TAC→XML cases equal under defaults (**TC-F25-001**; **E20-E1**: `metar-A3-1`,
     `speci-A3-2`, `taf-A5-1`, `taf-A5-2` — A5-2 is WMO AMD/CNL cancel example)
  2. XSD+Schematron on those goldens (**TC-F25-002**)
  3. FE catalog: strict WMO-passers badged; provenance vendor/mirrored (**TC-F25-003**; deepen
     TC-F7-008) — **EV-024 / UJ-039** also allows official **WMO reference** samples (ADR-032 amend)
  4. Load example → convert smoke; H4–H5 when FE deploys (**TC-F25-004** / **UJ-036**)
- **Journeys / tests**: **UJ-036**; **TC-F25-001..004**; deepen **UJ-032** / **TC-F7-008**
- **Out of scope**: New SWX/VONA/VAA/TCA quality bars; forcing translation-failed examples to
  happy-path encode; non-default profile/version equality
- **Source**: E20-A=2; E20-3; E20-D3; ADR-032; [evolve-decisions.md](decisions/evolve-decisions.md) §EV-020

### F9 deepen (S026 / EV-020 — decode glossary)

- **Status note**: F9 remains **Done**; this cycle deepens plain-language decode across **all
  seven** products using **official / near-official** meanings (WMO codes, Annex cites, F3 /
  OpenAIP) with a packaged YAML file as **overrides** only (E20-E2). Tests: **TC-F9-003/004**;
  journey deepen **UJ-020**. Policy: **ADR-032**.

### F7.g deepen (S026 / EV-020 — WMO-passing examples only)

- **Status note**: F7.g remains under F7 Planned; S026 replaced catalog bodies/policy so the
  workbench Examples control offered **strict WMO-passing** demos for in-scope products
  (**UJ-036** / **TC-F25-003**). **Amended S031 / EV-024**: official WMO **reference** samples
  may also appear and load (**UJ-039**; ADR-032 amend) — strict passers remain distinctly badged.

### F26: VAA Quality Bar — S027 / EV-021

- **Status**: **Done** — shipped S027 / EV-021 (2026-07-30, PR [#794](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/794)); #736 closed.
- **What it does**: Raises **Volcanic Ash Advisory** TAC lint, convert, and IWXXM-validate
  quality to the F15/F20/F23/F24 bar. Target: WMO vendor `va-advisory-A7-2` TAC→IWXXM
  **`canonicalize_xml`-equal** under **default** convert settings (`profile=annex3`, default
  pinned `iwxxm_version`). Root `iwxxm:VolcanicAshAdvisory`. Reuses **ADR-028** registry
  (new VAA codes as needed); golden policy **ADR-032**. Distinguishes VAA from VA SIGMET
  (`iwxxm:VolcanicAshSIGMET` — F23 / #739).
- **Issues**: [#736](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/736).
- **Deepens**: **F6.f** (VAA encode), **F12** (VAA checklist), **F7.g** (Examples when passing).
- **Acceptance**:
  1. Registry-backed VAA lint codes; CI fails on unknown codes (**TC-F26-001**)
  2. #736 exceptional-rule table (UNKNOWN/UNNAMED, nilReasons, OBS/FCST status, `NO VA EXP`,
     remarks NIL, `NO FURTHER ADVISORIES`, …) has accept + negative fixtures (or explicit
     deferrals) (**F26 themes V1–V2**; TC-F26-002/004) — mine TAC themes from
     `iwxxm-translation` Amd79-80-2023; **no** byte-match of those XMLs under 2025-2 (E21-D4)
  3. Common rules: `reportStatus` / `permissibleUsage`, `translationFailedTAC`, geometry CRS,
     nilReasons, one-IWXXM-per-TAC-report (**F26 theme C1**)
  4. WMO `va-advisory-A7-2.tac` → convert (defaults) → `canonicalize_xml` == vendor XML;
     XSD+Schematron pass; root `iwxxm:VolcanicAshAdvisory` (**F26 theme V3**; TC-F26-002/003)
  5. Coverage-matrix VAA / F26 themes updated; guidance gaps filed or closed
  6. Workbench product-path lint+convert smoke; Examples list **only** VAA passers
     (**UJ-037** / **TC-F26-005**; deepen UJ-032 / TC-F7-008); unlock VAA Examples when
     F26 golden greens (**S02.M2** incremental); H4–H5 when FE touched
- **Journeys / tests**: **UJ-037**; **TC-F26-001..006**
- **Out of scope**: VA SIGMET #739 (Done); TCA handled by **F27**; SWX #740; VONA #741;
  treating `va-advisory-translation-failed` as happy-path golden; non-default profile/version
  equality; PyPI bumps
- **Source**: E21-*; [evolve-decisions.md](decisions/evolve-decisions.md) §EV-021;
  [wmo-vaa-tca-examples-inventory.md](sessions/S027-vaa-quality/reports/wmo-vaa-tca-examples-inventory.md);
  ADR-028; ADR-032; `docs/domain/rules/COVERAGE_MATRIX.md`

### F27: TCA Quality Bar — S027 / EV-021

- **Status**: **Done** — shipped S027 / EV-021 (2026-07-30, PR [#794](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/794)); #737 closed.
- **What it does**: Raises **Tropical Cyclone Advisory** TAC lint, convert, and IWXXM-validate
  quality to the same bar. Target: WMO vendor `tc-advisory-A2-2` TAC→IWXXM
  **`canonicalize_xml`-equal** under **default** convert settings. Root
  `iwxxm:TropicalCycloneAdvisory`. Reuses **ADR-028** / **ADR-032**. Distinguishes TCA from
  TC SIGMET (`iwxxm:TropicalCycloneSIGMET` — #738 OOS).
- **Issues**: [#737](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/737).
- **Deepens**: **F6.f** (TCA encode), **F12** (TCA checklist), **F7.g** (Examples when passing).
- **Acceptance**:
  1. Registry-backed TCA lint codes; CI fails on unknown codes (**TC-F27-001**)
  2. #737 exceptional-rule table (`UNNAMED`, CB NIL, remarks NIL, `NO MSG EXP`, forecast wind
     &lt;34 kt, no-longer-TC position, …) has accept + negative fixtures (or explicit deferrals)
     (**F27 themes T1–T2**; TC-F27-002/004) — mine TAC themes from translation package; no Amd79 XML
     byte-match under 2025-2 (E21-D4)
  3. Common rules covered (**F27 theme C1**)
  4. WMO `tc-advisory-A2-2.tac` → convert (defaults) → `canonicalize_xml` == vendor XML;
     XSD+Schematron pass; root `iwxxm:TropicalCycloneAdvisory` (**F27 theme T3**; TC-F27-002/003)
  5. Coverage-matrix TCA / F27 themes updated; guidance gaps filed or closed
  6. Workbench product-path smoke; Examples list **only** TCA passers (**UJ-038** /
     **TC-F27-005**; deepen UJ-032 / TC-F7-008); unlock TCA Examples when F27 golden greens
     (**S02.M2** incremental); H4–H5 when FE touched
- **Journeys / tests**: **UJ-038**; **TC-F27-001..006**
- **Out of scope**: TC SIGMET #738; VAA handled by **F26**; SWX #740; VONA #741;
  treating `tc-advisory-translation-failed` as happy-path golden; non-default profile/version
  equality; PyPI bumps
- **Source**: E21-*; [evolve-decisions.md](decisions/evolve-decisions.md) §EV-021;
  [wmo-vaa-tca-examples-inventory.md](sessions/S027-vaa-quality/reports/wmo-vaa-tca-examples-inventory.md);
  ADR-028; ADR-032; `docs/domain/rules/COVERAGE_MATRIX.md`

### F6.f deepen (S027 / EV-021 — VAA + TCA)

- **Status note**: F6 remains **Implemented**; this cycle **deepens F6.f** convert/golden
  fidelity for VAA + TCA under F26/F27 acceptance (not a new Fn).

### F12 deepen (S027 / EV-021 — VAA + TCA)

- **Status note**: F12 remains **Implemented**; this cycle expands VAA/TCA rules through the
  ADR-028 registry and accept/negative packs.

### F7.g deepen (S027 / EV-021 — VAA/TCA WMO-passers)

- **Status note**: Catalog only lists VAA/TCA demos that pass the F26/F27 golden bar (E21-3);
  hide `vaa_basic` / `tca_basic` until replaced by WMO passers (**UJ-037/038**; TC-F7-008 deepen).
  **Unlock cadence (`D-S027-EV021-s02m2-1`)**: incremental per product — unlock VAA Examples
  when F26 golden greens; TCA when F27 greens (may differ mid-cycle; peer E20-F4).

### F6 / F2 / F12 / F13 deepen (S030 / EV-023 — APAC FAQ + codes + WMO-306 encode deltas)

- **Status**: **Done** — S030 / EV-023 closed 2026-07-30 (PR [#801](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/801)
  `af98690`; closeout [#802](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/802) `5c7d3b5`; #800)
- **Issue**: [#800](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/800) (supersedes #797 impl backlog)
- **Runtime SoT**: `vendor/manifest.json` → IWXXM **v2025-2** (FAQ / 2019 Manual / translation suite are informative only)
- **What it does**: Close encode/lint/SCH gaps from APAC IWXXM FAQs 3rd, codes.wmo.int dual
  registers, iwxxm-translation parity notes, and optional WMO-306 2019/upd-2021 corroboration
- **Source**: E23-*; [evolve-decisions.md](decisions/evolve-decisions.md) §EV-023

### F6 / F2 / F4 / F12 / F13 / F25 deepen (S031 / EV-024 — IWXXM domain mine + WMO sample menu)

- **Status**: **Done** (S031 / EV-024) — discovery + sample-menu wiring; children #809–#812
- **Issues**: [#804](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/804),
  [#807](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/807),
  [#773](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/773) — **exclude** [#806](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/806)
- **Runtime SoT**: `vendor/manifest.json` → IWXXM **v2025-2** (+ `iwxxm-us` pin for #773)
- **What it does**:
  1. **#804** — Folder-by-folder relevancy of `IWXXM/` (+ sibling triage); official examples
     stem×surface matrix; wire in-scope stems into validate/CI; load WMO examples from the
     workbench **Examples / sample menu** (**UJ-039**)
  2. **#807** — Refresh wmo-im org / sibling ranking for encode/validate (not a substitute for #804)
  3. **#773** — Mine IWXXM-US METAR/SPECI PDF + MDL modelling → coverage checklist + catalog rows
  4. Promote durable findings; file **child issues** for encode/lint/SCH gaps (no big-bang engine rewrite)
- **Catalog policy (E24-C / ADR-032 amend)**: Sample menu lists official WMO example stems with
  TAC peers for in-scope products even when convert is not yet `canonicalize_xml`-equal.
  Retain a **strict passer** badge (`wmoPass`) for ADR-032 equality; non-equal official stems
  are **WMO reference** samples (loadable). Translation-failed / quarantine stems stay out of
  happy-path Examples. IWXXM-US examples never mix into the WMO catalog. Roadmap-only
  (WAFS/QVACI) deferred unless explicitly opted in during 04.
- **Acceptance**:
  1. Mining notes + folder×relevancy + examples matrix (#804); org refresh notes (#807); US
     type×TAC×encode×validate checklist (#773); indexed in `docs/domain/mining/README.md`
  2. Durable promotions to `RULE_SOURCE_URLS` / `COVERAGE_MATRIX` / canonicals where findings stick
  3. Validate/CI surfaces exercise in-scope WMO stems (or explicit defer + child issue)
  4. **UJ-039**: operator can load official WMO IWXXM example TAC from the sample menu for
     product-in-scope stems; `FIXTURE_GAPS.md` updated
  5. Child issues filed for ❌/⚠ encode/lint/SCH gaps; link #800 / product quality tickets
- **Journeys / tests**: **UJ-039** (new); deepen **UJ-036** / **UJ-032**; **TC-EV024-001..008**
- **Out of scope**: #806 WIS2; new product encode engines this cycle; hand-edit `vendor/schemas/*`;
  USWX; committing PDF/full clones; mixing US into WMO catalog
- **Packages / apps**: domain docs; `apps/frontend` examples catalog; validate/convert fixture
  surfaces; thin backend loaders as needed
- **Source**: E24-*; [evolve-decisions.md](decisions/evolve-decisions.md) §EV-024;
  [ADR-032](adr/ADR-032-wmo-default-golden-glossary.md) (amended)
- **Follow-on**: S032 / EV-025 implemented #810–#812 (+ dig ❌ US); #809 soft path only —
  equality residual → S033 / EV-026

### F6 / F6.b / F12 / F2 / F13 + F23 deepen (S032 / EV-025 — iwxxm-us REMARKS encode + VA multi-location)

- **Status**: **Done** (S032 / EV-025; PR [#816](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/816)
  `2412312`) — Lane A complete; Lane B soft-compare shipped; #809 left open for equality
- **Issues**: [#810](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/810),
  [#811](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/811),
  [#812](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/812) **closed**;
  [#809](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/809) **open** (soft done)
- **Runtime SoT**: `vendor/manifest.json` → IWXXM **v2025-2** + `iwxxm-us` **3.0**
- **What it did**:
  1. **Lane A** — Encode dig ❌ US METAR/SPECI REMARKS (#810/#811/#812 + adjacent)
  2. **Lane B** — #809 soft-compare golden + multi-location encode; catalog stayed
     `wmoReference` (`D-S032-EV025-s02m1-1`)
- **Journeys / tests**: **UJ-040**; **UJ-041** (soft path); **TC-EV025-001..010**
- **Follow-on**: S033 / EV-026 — ADR-032 equality → `wmoPass` (**UJ-041** promote)
- **Source**: E25-*; [evolve-report-EV-025.md](evolve-report-EV-025.md);
  [Context: va-multi-location-809](context/va-multi-location-809.md)

### F23 / F6 / F7.g deepen (S033 / EV-026 — #809 VA multi-location equality)

- **Status**: **Done** (S033 / EV-026) — PR #817 / #818; #809 closed
- **Issues**: [#809](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/809)
- **Runtime SoT**: `vendor/manifest.json` → IWXXM **v2025-2**
- **What it did**: Make `canonicalize_xml(convert(sigmet-multi-location-VA.tac))` equal
  vendor XML under annex3 + default pin (ADR-032); flip soft golden → strict; promote
  catalog `wmoReference` → `wmoPass`; close #809
- **Acceptance**:
  1. TC-EV025-008 green under **strict** equality (no soft_compare / inequality assert)
  2. TC-EV025-009 expects equality + catalog `wmoPass: true`
  3. FIXTURE_GAPS equality-pending note removed / closed
  4. GitHub #809 closed
- **Journeys / tests**: deepen **UJ-041** / **UJ-034** / **UJ-039**; reuse **TC-EV025-008..009**
  (EV-026 semantics — `E26-TC=1`)
- **Out of scope**: US REMARKS reopen; #738; sample-menu removal
- **Packages / apps**: `packages/tac2iwxxm` encode + annex3 golden; frontend catalog /
  FIXTURE_GAPS / Vitest (no new UI surface)
- **Source**: E26-*; [evolve-report-EV-026.md](evolve-report-EV-026.md);
  [Context: va-multi-location-809](context/va-multi-location-809.md)

### F6 deepen (S033 / EV-026)

- **Status note**: F6 remains **Implemented**; encoder deltas for multi-location VA shape /
  metadata so ADR-032 equality holds. **Done** with EV-026.

### F7.g deepen (S033 / EV-026)

- **Status note**: F7 remains **Planned**; catalog tier flip only (`wmoPass`) when equality
  holds — no new UI surface. **Done** with EV-026.

### F23 deepen (S033 / EV-026)

- **Status note**: F23 remains **Done**; EV-026 completed #809 multi-location VA convert
  equality / catalog promote (**UJ-041**).

### F25 / F9 / F7.g deepen (S034 / EV-027 — #815 official WMO decode residual matrix)

- **Status**: **Done** (S034 / EV-027) — PR [#821](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/821) merged `ad36aa0`; #815 closed; child [#820](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/820) open (VAA/TCA G4)
- **Issues**: [#815](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/815) (closed); [#820](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/820) (open)
- **Runtime SoT**: `vendor/manifest.json` → IWXXM **v2025-2**
- **What it does**:
  1. Inventory official WMO TAC peers under the vendor pin; match catalog ∪ `FIXTURE_GAPS`
  2. Every in-scope peer loads from the sample menu **or** has an explicit gap + child issue
  3. Decode residual matrix: happy-path official TAC → `residuals == []` for all seven
     products (**S02.M2=2**); allowlist only when standing docs mark residuals intentional
     (F9 **G4** / ADR-025) + linked child issue — fix when cheap otherwise (`E27-4`)
  4. Unexpected residuals fail parametrized CI (not only manual UI checks)
- **Acceptance**:
  1. Inventory SoT checked in (docs or generated list) matches catalog ∪ `FIXTURE_GAPS`
  2. Load path green for registered stems (ADR-032 `wmoPass` / `wmoReference`)
  3. Residual matrix CI green for happy-path peers; allowlist documented; child issues for
     stems deferred in-cycle
  4. GitHub #815 closable when AC met
- **Journeys / tests**: **UJ-042** (new); deepen **UJ-039** / **UJ-020**; **TC-EV027-001..005**
  (`E27-UJ=1`, `E27-TC=1`)
- **Out of scope**: inventing TAC; encode equality promotion; IWXXM-US in WMO menu; new
  products beyond F6 seven; deferred SWX/VONA/WAFS/QVACI / TC-SIGMET A6-2 unless catalogued
- **Packages / apps**: `packages/tac2iwxxm` decode + fixtures; FE catalog / FIXTURE_GAPS /
  Vitest; optional H4–H5 when FE ships
- **Source**: E27-*; [evolve-decisions.md](decisions/evolve-decisions.md) §EV-027;
  [Context: wmo-decode-residual-matrix](context/wmo-decode-residual-matrix.md)
- **Supersedes**: S029 / EV-022 (parked) narrow SIGMET A6-1a residual work

### F25 deepen (S034 / EV-027)

- **Status note**: F25 remains **Done**; this cycle deepens beyond catalog listing to
  **decode residual emptiness** on official TAC peers (**UJ-042** / TC-EV027).

### F9 deepen (S034 / EV-027)

- **Status note**: F9 remains **Done**; matrix asserts `decode_tac` residuals empty or
  allowlisted for official WMO peers (deepen **UJ-020**).

### F7.g deepen (S034 / EV-027)

- **Status note**: F7 remains **Planned**; inventory ↔ catalog ∪ `FIXTURE_GAPS` completeness
  for official WMO TAC peers (deepen **UJ-039**).

### F28: SWXA Quality Bar — S036 / EV-029

- **Status**: **Done** — S036 / EV-029; PR [#828](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/828);
  umbrella [#823](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/823) **closed**;
  [#740](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/740) **closed** (absorbed).
- **What it does**: Raises **Space Weather Advisory** (SWXA / SWX) TAC lint, convert, and
  IWXXM-validate quality to the F15–F27 product bar. Root `iwxxm:SpaceWeatherAdvisory`.
  TAC AHL `FN` → IWXXM AHL `LN`. Reuses **ADR-028** registry + **ADR-032** golden policy.
  Completes the eight-family TAC→IWXXM converter set (METAR/SPECI/TAF/SIGMET×3/AIRMET/VAA/TCA/SWXA).
- **Issues**: [#740](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/740) closed; parent [#823](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/823) closed.
- **Deepens**: **F6** (SWXA encode), **F12** (SWXA checklist), **F2/F13** (XSD+SCH), optional
  **F7.g** Examples when passers exist.
- **API**: Additive wire value **`product=swxa`** on convert / convert-bulletin / lint-tac /
  decode-tac ([api-contract.md](api-contract.md) §S036 / EV-029). Alias `swx` is **not**
  accepted. Keep-whole multiline `manual_text` (peer VAA/TCA).
- **Acceptance**:
  1. Registry-backed SWXA lint codes; CI fails on unknown codes (**TC-F28-001**)
  2. Authoritative exceptional rules (from mining / #823 / Annex 3 + PANS-MET + IWXXM 2025-2
     package) have accept + negative fixtures or explicit deferrals (**TC-F28-002/004**)
  3. Common COM rules apply: `reportStatus` / `permissibleUsage`, `translationFailedTAC`,
     nilReasons, one-IWXXM-per-TAC-report (**TC-F28-006** / COM theme)
  4. At least one WMO (or pinned official) SWXA TAC → convert (defaults) → XSD+Schematron pass;
     root `iwxxm:SpaceWeatherAdvisory`; golden equality when a vendor peer exists (**TC-F28-003**)
  5. Coverage-matrix SWXA / F28 themes updated; guidance gaps filed or closed
  6. Product-path lint+convert smoke; Examples list only SWXA passers when unlocked
     (**UJ-043** / **TC-F28-005**); H4–H5 only if FE touched
  7. API/runtime accept `product=swxa` (unknown → `unknown_product` 400)
- **Journeys / tests**: **UJ-043**; **TC-F28-001..006**; cycle **TC-EV029-***
- **Out of scope**: VONA #741; SIGWX / QVACI; dissemination sink UI; treating GIFTs as normative
- **Source**: E29-*; [evolve-decisions.md](decisions/evolve-decisions.md) §EV-029;
  [Context: eight-family-ahl-rules-823](context/eight-family-ahl-rules-823.md);
  ADR-028; ADR-032; `docs/domain/rules/COVERAGE_MATRIX.md`

### F6 / F6.bulletin / F12 / F2 / F13 / F15 / F20 / F23 / F24 / F26 / F27 deepen (S036 / EV-029 — #823)

- **Status**: **Done** (S036 / EV-029) — Phase A + Phase B complete; PR #828; residuals on children
- **Issues**: [#823](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/823) **closed**;
  [#738](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/738) closed (TC SIGMET);
  [#740](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/740) closed (via **F28**);
  residuals [#829](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/829) (TC deepen),
  [#820](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/820) (VAA/TCA decode)
- **Runtime SoT**: `vendor/manifest.json` → IWXXM **2025-2**
- **What it does**:
  1. **Phase A** — Mine/promote #823 COM/AHL/bulletin + per-product rules into
     `docs/domain/*` + `RULE_SOURCE_URLS` / `COVERAGE_MATRIX`; inventory TAC input shapes
     (standalone / AHL / multi-report) and official IWXXM examples per family
  2. **Phase B order** — Bulletin/AHL/COM → METAR → SPECI → TAF → SIGMET (gen/VA/**TC**/CNL)
     → AIRMET → VAA → TCA → SWXA (**F28**)
  3. **Shared AHL model** — TAC↔IWXXM `T1T2`, BBB→`reportStatus`, filename /
     `bulletinIdentifier` for `tac2iwxxm` + F16–F19 consumers (sink UI deferred)
  4. Close silent gaps across **lint · convert · IWXXM validate** for report states
     Normal / Amendment / Correction / Cancellation / NIL
  5. Child issues for residuals that cannot close in-cycle
- **Acceptance**:
  1. Coverage matrix cells for eight families × three roles filled or child-issued (**TC-EV029-001**)
  2. Example inventory covers TAC shapes + IWXXM peers; wired or gap-documented (**TC-EV029-002**)
  3. Shared AHL/`T1T2`/BBB rules enforced in convert + lint (**TC-EV029-003**)
  4. TC SIGMET path emits `iwxxm:TropicalCycloneSIGMET` (#738) (**TC-EV029-004**)
  5. VAA/TCA encode/decode residuals from #823 B4 / #820 closed or child-issued (**TC-EV029-005**)
  6. **F28** acceptance green or deferred with child issue
  7. #823 closable when umbrella AC met (or split children remain open with links)
- **Journeys / tests**: **UJ-043**; deepen UJ-024/031/034/035/037/038/039/042; **TC-EV029-001..008**;
  **TC-F28-001..006**
- **Out of scope**: SIGWX / VONA / QVACI as TAC converter inputs; #806 WIS2 topic mining;
  dissemination drawer UI; hand-edit `vendor/schemas/*`; GIFTs-as-normative
- **Packages / apps**: `packages/tac-validate`, `tac2iwxxm`, `iwxxm-validate`,
  `packages/dissemination` (AHL helpers only); domain docs; fixtures/CI; FE only if Examples unlock
- **Source**: E29-*; [evolve-decisions.md](decisions/evolve-decisions.md) §EV-029;
  [Context: eight-family-ahl-rules-823](context/eight-family-ahl-rules-823.md); #823 body + COM addendum

### F23 deepen (S036 / EV-029 — TC SIGMET #738)

- **Status note**: F23 remains **Done** for general + VA; this cycle **added TC SIGMET**
  (`iwxxm:TropicalCycloneSIGMET`, TAC `WC` / IWXXM `LY`) under the same quality bar.
  [#738](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/738) **closed** (M7 / #828);
  deepen residuals → [#829](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/829).

### F26 / F27 deepen (S036 / EV-029 — #820 + #823 B4)

- **Status note**: F26/F27 remain **Done**; this cycle closes encode/bulletin/decode residuals
  called out in #823 B4 and [#820](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/820).

### F6.bulletin deepen (S036 / EV-029 — AHL / COM)

- **Status note**: F6 remains **Implemented**; shared AHL parse, `=` splitter (incl. VAA/TCA
  multiline), BBB→`reportStatus`, COLLECT framing, and IWXXM filename/`T1T2` map deepen under
  #823 B1–B3.

## Platform Feature Details (Monorepo Migration)

### M1: Monorepo Layout

- **What it does**: Replaces six git submodules with a single-repo tree: `apps/`, `packages/`, `vendor/`.
- **F6 delta**: Approved tree gains `packages/tac2iwxxm`; loses `packages/gifts` at F6 cutover.
- **S008 package amend**: Also gains `packages/tac-validate` and `packages/iwxxm-validate`.
- **Key parameters**:
  | Parameter | Default | Description |
  |-----------|---------|-------------|
  | `apps/backend` | FastAPI API (public F21) | Single HTTP deployable |
  | `apps/frontend` | React/Vite UI | Static deployable |
  | `apps/worker` | F8 near-RT ingest poller | Render Background Worker (ADR-018) |
  | `apps/e2e` | Playwright cross-app tests | Dedicated workspace |
  | `packages/auth` | — | **Deleted** F21 / ADR-031 (E17-22) |
  | `packages/tac2iwxxm` | General TAC→IWXXM (F6) | uv workspace member; MIT |
  | `packages/tac-validate` | TAC lint / business rules | All seven product TAC forms |
  | `packages/iwxxm-validate` | XSD + Schematron (F2) | Consumes vendor schemas |
  | `packages/gifts` | — | **Removed** at F6 cutover (ADR-014) |
  | `packages/shared` | Types + cross-app utils | TS + Python shared constants |
  | `vendor/schemas/*` | Read-only schema snapshots | WMO + iwxxm-us; no local edits |
- **Source**: REQ-006, REQ-007; ADR-014; S008 realtime amend

### M2: Vendor Snapshot Sync

- **What it does**: Copies tagged releases from authoritative upstreams into `vendor/schemas/` per `vendor/manifest.json`.
- **F6 delta**: Also pins IWXXM-US (NOAA/MDL) alongside wmo-im iwxxm-*.
- **Limitations**: Read-only — no monorepo commits to vendor content except sync PRs.
- **Source**: REQ-002, REQ-012; ADR-013/014

### M3: GIFTs In-Repo Package — Deprecated

- **Status**: **Deprecated** by ADR-014. Package removed when F6 first wires `/api/v1/convert`.
- **Historical**: Moved GIFTs to `packages/gifts/`; REQ-014 manual upstream merges.
- **Source**: REQ-003; ADR-014

### M4: Auth Merged Into Backend — Deprecated (operator)

- **Status**: **Deprecated for operator Auth** (S023 / EV-017 / #783). Historical: collapsed auth
  microservice into backend via `packages/auth` (REQ-004); S003 key split (ADR-010); S011 removed
  `/admin/*` (#697).
- **EV-017**: Operator login/JWT surface removed (F21). F8 / internal service-role credentials
  remain. **`packages/auth` deleted entirely** this cycle (E17-22 / ADR-031); no residual
  helpers required for F8.
- **Source**: REQ-004, REQ-009; S011 / EV-008; **S023 / EV-017**

### M5: Workspace Tooling

- **What it does**: Root Makefile orchestrates uv (Python) and pnpm (JS) workspaces; pre-commit
  and GitHub Actions quality gates.
- **F6 delta**: Workspace member `tac2iwxxm`; drop gifts from test matrix at cutover; **PyO3 /
  maturin required** in CI before cutover (ADR-017).
- **S008 package amend**: Workspace members `tac-validate`, `iwxxm-validate` in test matrix.
- **Source**: REQ-005; EV-002; ADR-014; S008 realtime amend

### M6: Upstream Vendor Sync

- **What it does**: Scheduled GitHub Actions open PRs when upstream schema tags publish.
- **F6 delta**: Extend to iwxxm-us HTTP 3.0 snapshot pin; **GIFTs sync Action remains out of
  scope** (package deleted; REQ-014 deprecated).
- **Source**: REQ-008, REQ-009; ADR-014

## Feature Matrix

| Feature | Web UI | CLI/API | CI metrics | Render Deploy |
|---------|--------|---------|------------|---------------|
| F1 | Legacy until F6 UI | Superseded | — | — |
| F2 | Yes | Yes (wrapper) | Yes | Yes |
| F3 | Partial | Yes | Yes | Yes |
| F4 | Yes | Yes | Yes | Yes |
| F5 | Yes (METAR/SPECI) | Yes | Yes | Yes |
| F6 | Yes (product/profile) | Yes | Yes (lib/CI) | Yes (via API image) |
| F7 | Yes (workbench/decode/sessions) | Yes (decode/spans/preview) | Yes | Yes (static + API) |
| F8 | — | Worker poller | Store/quarantine | Background Worker |
| F9 | Yes (decode panel + plain language) | Yes (`decode-tac` `summary`) | Yes | Yes (static + API) |
| F10 | Yes (preview pane + quick fix) | Yes (lint `info` severity) | Yes | Yes (static) |
| F11 | Yes (msgspec FE types) | Yes (msgspec high-churn) | Yes (benches) | Yes (API + static) |
| F12 | — | PyPI `tac-validate` + CLI | Yes | — |
| F13 | — | PyPI `iwxxm-validate` + SDK | Yes | Via API image |
| F14 | — | PyPI `tac2iwxxm[+validate]` | Yes | Via API image |
| F15 | Yes (METAR/SPECI workbench smoke) | Yes (`lint-tac` registry codes) | Yes (registry + goldens) | Yes if API/FE contract changes |
| F16 | Yes (dissemination drawer) | Yes (preflight/upload APIs) | Yes | Yes (API + static + allowlist env) |
| F17 | Yes (WIS2 sink) | Yes (WIS2 publish) | Yes (wis2box harness) | Yes (staging wis2box + API) |
| F18 | Yes (EDIS sink) | Yes (EDIS submit) | Yes | Yes (API; BYOC SMTP) |
| F19 | Yes (AMHS/SWIM/AFS sinks) | Yes (adapter APIs) | Yes | Yes (API) |
| F20 | Yes (TAF/SPECI workbench smoke) | Yes (`lint-tac` / convert `taf`/`speci`) | Yes (goldens + matrix) | Yes if API/FE contract changes |
| F21 | Yes (no login) | Yes (public + rate limits) | Yes (abuse tests) | Yes (API + static; Auth secrets optional) |
| F22 | Yes (privacy settings) | — | Yes | Yes (static) |
| F23 | Yes (SIGMET/VA SIGMET workbench smoke) | Yes (`lint-tac` / convert sigmet + VA) | Yes (goldens + matrix) | Yes if API/FE contract changes |
| M1–M6 | — | — | Yes | Yes |

| F6 capability | Library | HTTP API | Web UI | CI metrics |
|---------------|---------|----------|--------|------------|
| product + profile convert | Yes | Yes | Yes | Yes |
| AHL bulletin split | Yes | Yes (`/convert-bulletin`) | Yes (ADR-024) | Gate |
| annex3 / iwxxm_us | Yes | Yes | Yes | Yes |
| TAC lint (`tac-validate`) | Yes | Thin wrapper | Live workbench | Gate |
| Schematron (`iwxxm-validate`) | Yes | Thin wrapper | Hard Convert + Strict Validation (ADR-023) | Gate |
| Convert bulletin_id / issuing_center / stop_on_error | Yes | Yes | Yes (ADR-023) | — |
| Console / Conversion log-level filter | — | `log_level` accepted | Yes (ADR-023/024) | — |
| IWXXM COLLECT ingest | — | Placeholder 501 `/ingest-collect` | Yes (placeholder UI) | — |
| Accuracy metrics report | Yes | No (v1) | No (v1) | Gate |
| Rust/PyO3 hotspots | **Required at cutover** | Via API image | — | Bench hard-pass |

## Non-Goals (Migration)

- No product feature rewrites during monorepo migration (REQ-016).
- No ongoing edits to authoritative iwxxm schema content in monorepo (vendor is read-only).
- No separate auth deployable after migration completes.

## Non-Goals (F6 / S008)

- Rewrite gifts in place (package is deleted instead).
- Cython native path (use Rust/PyO3 instead).
- Separate **converter** microservice (HTTP convert stays on existing API).
- Metrics fields on convert API responses in v1.
- Extend F5 work history to non-METAR products in F6 v1. *(Superseded for persistence by S011
  **R2′** / ADR-020 — unified `tac_work_sessions`; F6-era non-goal was pre-unify.)*
- Products beyond the seven listed (e.g. SWA) in F6 v1.

**Amended by 04-tech-plan**: PyO3 is a **cutover acceptance gate** (ADR-017). F8 worker is
**in scope** this cycle (ADR-018) — see Non-Goals amend below.

## Non-Goals (S008 realtime / package amend — updated 2026-07-12 04)

- ~~Building **F7** UI or multi-product sessions.~~ **Superseded** — F7 is **in scope** for
  S011 / EV-008 (see Non-Goals F7 below).
- ~~AMHS / SWIM / AFS ingest adapters.~~ **Superseded by S019 / EV-014 F19** — AMHS / SWIM /
  AFS **dissemination** adapters are **in scope** (Q20=D). F8 **ingest** remains store +
  quarantine only unless separately evolved.
- ~~**Push sinks** (webhook/S3/AMHS) — store + quarantine only for F8 v1.~~ **Superseded for
  operator dissemination (F16–F19)** — WIS2 / EDIS / AMHS / SWIM / AFS / multi-DB upload are
  **in scope** under EV-014. F8 worker v1 still does **not** auto-push ingest results unless
  wired later.
- Public machine-ingest auth UX (worker uses service-role JWT internally — ADR-018).
- Schematron applied to TAC (Schematron stays on IWXXM; TAC uses `tac-validate`).
- Dedicated converter API service (rejected; F8 worker is the new deployable).

## Non-Goals (F7 / S011 — EV-008)

- Teaching / CMS content beyond short decode explanations (#702 v1).
- Click-row-to-edit TAC mutation; full IWXXM field mapping inside the decode table.
- Extending **F5** as a permanent parallel METAR-only store after unified cutover (F5 UX remains
  as My METARs filter on `tac_work_sessions`).
- Separate F7-only sessions table alongside `metar_work_sessions` (rejected — R2′).
- ~~Per-user in-app “paste Supabase / DB keys” UI (BYO is deploy/env only — R6).~~ **Amended
  S019 / EV-014**: paste of **Supabase auth keys** remains a non-goal (ADR-021 / Q10A=D).
  Paste of **one-shot dissemination destination** credentials (DB URI / WIS2 / EDIS SMTP /
  AMHS params) is **in scope** (F16–F19); memory-only; never saved profiles.
- Shared hosted multi-tenant admin dashboard, approval queues, or toggle-admin (#697).
- ~~AMHS / SWIM / AFS; F8 push sinks.~~ **Superseded by F16–F19** (see S008 amend above).
- Rewriting conversion engines beyond span / decode / soft-preview hooks.

## Non-Goals (S019 / EV-014 — dissemination)

- Saved / encrypted connection profiles (Q14).
- Pasting Supabase **Auth** keys in the product UI (auth stays deploy-time BYO).
- Storing destination secrets on `tac_work_sessions` or in logs (Q19=A / Q11).
- Arbitrary SQL admin console / free-form DDL beyond the versioned writer-contract path.

## Non-Goals (S023 / EV-017 — public app + privacy)

- Formal legal advice / DPIA (engineering supports counsel review).
- Removing F8 worker **service-role** credentials or Render↔Supabase machine auth.
- Reintroducing admin role UX (#697).
- Optional user accounts or anonymous server sessions in v1.
- Cross-device work-history sync.
- Full CMP / analytics / marketing tags (Solution B/C) unless a later evolve cycle adds them.
- Per-US-state separate privacy UI variants (one global strict preference center).

## Planned Features (Post-Migration)

| # | Feature | Priority | Complexity | Notes |
|---|---------|----------|------------|-------|
| P1 | OpenAPI → TS codegen in packages/shared | Medium | Low | After layout stabilizes |
| P2 | Path-filtered CI per app/package | Medium | Medium | Reduce CI time |
