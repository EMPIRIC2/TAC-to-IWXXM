# Feature List

> **Project**: METAR to IWXXM Converter
> **Repository**: https://github.com/joseph-c-mcguire/metar-to-IWXXM
> **Last updated**: 2026-07-21 (S019 / EV-014 — dissemination epic F16–F19 Planned)

## Summary

| # | Feature | Status | Category | Source |
|---|---------|--------|----------|--------|
| F1 | METAR → IWXXM conversion (GIFTs-era UX) | Superseded by F6 | Product | Historical; UI actions retained until F6 UI |
| F2 | IWXXM validation | Implemented | Product | backend → `packages/iwxxm-validate` |
| F3 | Airport data services | Implemented | Product | OpenAIP / reconciliation services |
| F4 | IWXXM version handling | Implemented | Product | docs/domain/iwxxm/IWXXM_VERSION_SWITCHING.md |
| F5 | User METAR work history | Planned | Product | docs/context/metar-work-history.md, S004 |
| F6 | General TAC→IWXXM (`tac2iwxxm`) | Implemented | Product | S008, ADR-013/014/019; bulletin split |
| F7 | Multi-product TAC operator UI / sessions | Planned | Product | S011 / EV-008; build this cycle |
| F8 | Near-realtime TAC ingest → IWXXM gate | Implemented | Product | S008 ADR-018/019; `apps/worker` |
| F9 | Value-aware live decode + plain-language summary | Done | Product | S013 / EV-009; shipped 2026-07-17 (#723) |
| F10 | Workbench preview clarity (IWXXM pane + lint UX) | Done | Product | S013 / EV-009; shipped 2026-07-17 (#723) |
| F11 | Validation stack perf review + msgspec HTTP + XSD codegen | Implemented | Product | S014 / EV-010; #703 |
| F12 | Publishable TAC product validation (`tac-validate`) | Implemented | Product | S014 / EV-010; #698 |
| F13 | Fast IWXXM validate (Rust core + Schematron + PyPI) | Implemented | Product | S014 / EV-010; #699 |
| F14 | Publish `tac2iwxxm` + validate extras + PyPI/release CI | Implemented | Product | S014 / EV-010; #693 |
| F15 | Maintainable TAC lint issue registry + METAR/SPECI quality bar | Done | Product | S015 / EV-011; #732; shipped 2026-07-20 (#742) |
| F16 | Dissemination drawer + multi-DB upload (BYOC URI) | Planned | Product | S019 / EV-014; #729 |
| F17 | WIS2 dissemination pathway | Planned | Product | S019 / EV-014; #2 |
| F18 | EDIS → RTH Washington dissemination | Planned | Product | S019 / EV-014; #6 |
| F19 | AMHS / SWIM / AFS adapters | Planned | Product | S019 / EV-014; non-goals overturn |
| M1 | Monorepo layout (`apps/` + `packages/` + `vendor/`) | Planned | Platform | REQ-002–006 |
| M2 | Vendor snapshot sync (wmo-im iwxxm-*) | Planned | Platform | REQ-002, REQ-010 |
| M3 | GIFTs as in-repo package | Deprecated (ADR-014) | Platform | REQ-003; removed with F6 cutover |
| M4 | Auth merged into backend API | Planned | Platform | REQ-004 |
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

- **What it does**: Persists per-user METAR converter work in Supabase Postgres — status lifecycle
  **Draft → WIP → Finished** plus **Failed** for convert errors; resumable on login; browseable
  from converter sidebar and **My METARs** page.
- **Inputs**: Manual TAC textarea, queued `.tac`/`.txt` files, conversion params; JWT on all API calls.
- **Outputs**: Session rows with full TAC, IWXXM (when converted), errors/issues JSON, optional
  `kv_upload_key` when sent to operational database.
- **Status rules**:
  | Status | Meaning | Transition |
  |--------|---------|------------|
  | Draft | Saved input; not successfully converted | Auto-save (3s debounce); multiple Drafts allowed |
  | WIP | Convert succeeded; not sent to operational DB | At most **one** WIP per user |
  | Finished | Successfully sent via Convert&Send or Upload to Database | Stores KV upload reference |
  | Failed | Convert failed or partial failure | Treated like Draft for multi-session rules; stays Failed until user edits and re-converts |
- **UI**: Compact recent-history panel on converter (5 recent); **New METAR** button for fresh Draft;
  full **My METARs** page with status + date filters; Finished sessions open **read-only**; 30-day trash
  for soft-deleted sessions. **Admin page** for cross-user browse is **removed** by F7 / #697
  (S011 / EV-008) — operators use BYO credentials; no shared multi-tenant admin UI.
- **Retention**: Auto-purge **Draft** rows older than 30 days (Supabase pg_cron); WIP/Finished/Failed kept until user soft-deletes.
- **F6 non-goal (historical)**: F6 v1 did not extend F5 to non-METAR. **S011 / R2′** unifies
  persistence under F7 `tac_work_sessions` (see F7); F5 UI (My METARs) becomes a METAR/SPECI
  filter on the unified table after migration.
- **Limitations**: Persistence requires login (guests may convert without save; login auto-creates Draft
  from in-browser content); no append-only status audit trail in v1; WIP stays WIP when input edited
  before re-convert; Finished sessions disable convert/send (use **New METAR**); send failure keeps
  **WIP**; last-write-wins on multi-tab auto-save; no backfill from existing KV uploads; backend REST
  only (no direct browser Postgres writes).
- **Source**: GitHub #555 follow-on, requirements interview 2026-06-23 (F5 delta)

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
- **Inputs**: TAC text/files (`.txt` / `.metar` / `.tac`); `product` / `profile` /
  `iwxxm_version`; optional `bulletin_id` / `issuing_center` / `stop_on_error` /
  `validate_output` / `validation_level` (ADR-023); JWT; editor cursor and character spans
  for highlight/hover.
- **Outputs**: Ordered decode segments (`start`/`end` + explanation); span-aware lint/validate
  issues; best-effort IWXXM + failed-span markers on soft-preview; F7 session rows for seven
  products; optional in-band XSD/Schematron when Strict Validation is on (hard Convert).
- **Deferred (still Later)**: Full COLLECT member extract inside `ingest-collect` (UI + 501
  placeholder shipped ADR-024); deep honor of `include_nil_reasons` in tac2iwxxm emit.
- **Validation deepen (S016 / EV-012 / #730)**: Operator-visible Manual TAC Input modes
  (TAC / AHL / COLLECT) validated via UJ-025 / TC-F7-007 (Playwright **T1–T6** hard + Vitest + staging
  H4–H5 / AHL / COLLECT 501). Auto-switch required. Does **not** flip F7 → Implemented.
- **F6 engine companions (still F6 packages; UX under F7)**: decode segments; optional integer
  `start`/`end` on lint/validate issues; soft-preview / partial convert (flag or dedicated
  endpoint — finalize in 04-tech-plan).
- **Editor**: **CodeMirror 6** (new frontend dependency — inventory in 01; install in 04/07).
- **Parent tracker**: GitHub [#5](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/5)
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
- **Resolved gaps (S011 Feature List Batch 2)**:
  | ID | Decision |
  |----|----------|
  | G1 | Keep `DISABLE_AUTH` / local–CI auth bypass patterns; BYO is deploy topology only |
  | G2 | Self-signup vs invite-only is **operator Supabase policy** — app adds no invite gate |
  | G3 | **No product migration** of shared-project users/data; clean BYO cut (point env at own project) |
  | G4 | VAA/TCA decode spans: **best-effort + explicit residuals** in v1 (full field offsets not required) |
  | R2′ | **Override R2**: unified `tac_work_sessions` + migrate F5 rows (Spec Batch 2 A / 2026-07-13) |
- **Source**: S011 Phase 0 R1–R6; Feature List Batches 1–2 (2026-07-13);
  [Context: f7-operator-ui](context/f7-operator-ui.md); issues #694/#702/#665/#666/#697

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

- **Status**: **Implemented** — S014 / EV-010 (#698); deepen METAR/SPECI via F15 / EV-011.
- **What it does**: Design + publish **`tac-validate`** `0.1.0` to PyPI — standalone TAC
  product validation for all seven F6 products with structured issues (code, severity, span).
  Aggressively encode mined rules from `docs/domain/` (cite-only for paywalled Annex text):
  **full depth** METAR/SPECI/TAF; SIGMET/AIRMET/VAA/TCA structured templates + coverage-matrix
  gates. CLI `tac-validate` for CI. No IWXXM/XSD in this package.
- **Acceptance**:
  1. `pip install tac-validate==0.1.0` in clean venv; library + CLI smoke
  2. METAR/SPECI/TAF full checklist rules; other products template+gate coverage documented
  3. Negative fixtures with useful diagnostics; CI wheel + fixture suite
  4. Tag `tac-validate-v0.1.0` → trusted-publishing workflow
- **Source**: #698; E10-4/9/19/21; docs/domain/rules/COVERAGE_MATRIX.md

### F13: Fast IWXXM Validate (Rust Core + Schematron + PyPI)

- **Status**: **Implemented** — S014 / EV-010 (#699).
- **What it does**: Publish **`iwxxm-validate`** `0.1.0` with Rust core (PyO3/maturin):
  well-formed + XSD + **native Rust Schematron/SVRL**; Python SDK
  `validate_iwxxm(...)`; pinned `vendor/schemas/*` **bundled** in the wheel; version/profile
  selection aligned with manifest pins. Parity suite vs current lxml isoschematron.
  Backend F2 wrapper calls the SDK.
- **Acceptance**:
  1. `pip install iwxxm-validate==0.1.0`; `validate_iwxxm` returns structured issues for
     well-formed + XSD + Schematron
  2. Benchmarks show meaningful speedup vs current Python path; hard gate at publish
  3. Parity tests vs golden IWXXM corpus; IWXXM-US profile supported when pin present
  4. Tag `iwxxm-validate-v0.1.0` → trusted publishing; no TAC parsing in package
- **Source**: #699; E10-6/7/19/22; ADR-017

### F14: Publish `tac2iwxxm` + Validate Extras + PyPI/Release CI

- **Status**: **Implemented** — S014 / EV-010 (#693).
- **What it does**: Publish **`tac2iwxxm`** `0.1.0` to PyPI (conversion library + optional
  PyO3). Extra **`tac2iwxxm[validate]`** depends on `tac-validate` + `iwxxm-validate`.
  Shared GitHub Actions **OIDC trusted publishing** — one workflow per package on version
  tags (`tac2iwxxm-v*`, `tac-validate-v*`, `iwxxm-validate-v*`). Documented public API +
  wheel smoke tests.
- **Acceptance**:
  1. `pip install tac2iwxxm==0.1.0` converts sample METAR → IWXXM
  2. `pip install tac2iwxxm[validate]` pulls both validators
  3. Tag-driven publish CI green; README install/usage
  4. UJ-DEV-005 / UJ-023 smokes pass
- **Source**: #693; E10-5/19/20/25

### F15: Maintainable TAC Lint Issue Registry + METAR/SPECI Quality Bar

- **Status**: **Done** — shipped S015 / EV-011 (2026-07-20, PR [#742](https://github.com/joseph-c-mcguire/metar-to-IWXXM/pull/742));
  issue [#732](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/732) closed on cycle close.
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

- **Status**: **Planned** (Phase 0 approved 2026-07-21; Q24=A).
- **What it does**: Unified **dissemination drawer** for Convert&Send / Upload: any authenticated
  user pastes a **one-shot** destination URI (memory-only on API; never persisted; no saved
  profiles). Backend-mediated preflight + send with structured schema diff; **block Send** until
  green. Supports **convert-then-send** and **drag-drop** of external IWXXM/TAC. **DDL /
  create-if-missing** against a versioned writer contract when the target table is missing or
  mismatched. Multi-DB sinks: **Postgres, MySQL/MariaDB, SQL Server, SQLite** (Q23=A–D; no other
  named vendor).
- **Auth vs destination**: Supabase **Auth + F5 work history** remain deploy-time BYO (ADR-021 /
  Q10A=D / Q19=A). Destination secrets are **not** Supabase and are never stored on sessions
  (only `kv_upload_key` / metadata).
- **Security (Q11=A+B)**: Backend-only egress; deny private/metadata ranges; DNS rebinding guard;
  TLS preferred; timeouts/size limits; secret redaction; rate limits; **required**
  `DISSEMINATION_EGRESS_ALLOWLIST` (empty ⇒ no user-URI egress).
- **UI**: Sink chooser in same drawer — Postgres/MySQL/… (F16), WIS2 (F17), EDIS (F18),
  AMHS/SWIM/AFS (F19).
- **Acceptance**:
  1. Preflight returns actionable schema/permission/auth diffs; Send disabled until green
  2. One-shot URI never appears in logs, session JSON, or F5 rows
  3. Allowlist enforced; private-IP / metadata targets rejected
  4. DDL path creates/migrates to versioned writer contract when opted
  5. Drag-drop and convert-then-send both reach the same preflight→send path
  6. All four DB engines covered by contract tests (SQLite may be file/local harness)
- **Out of scope**: Saved/encrypted connection profiles; pasting Supabase **auth** keys in-app
- **Source**: #729; S019 / EV-014; ADR-021 amend; ADR-029 (SSRF); ADR-030 (package/API)

### F17: WIS2 dissemination pathway — S019 / EV-014

- **Status**: **Planned**.
- **What it does**: Publish converted IWXXM via **WIS2** (MQTT notification + HTTP dataset) from
  the dissemination drawer. **Test harness**: project-operated staging **wis2box** on Render/Docker
  (Q12=B / Q17). **Live**: user BYOC WIS2 node/endpoint credentials (memory-only); cycle close
  requires live BYOC green (Q15=A / Q21=A).
- **Acceptance**: Staging wis2box e2e in CI/staging; live BYOC demo before EV-014 close; drawer
  sink type WIS2 with preflight-equivalent connectivity checks.
- **Source**: #2; WIS2 overview / wis2box; S019 / EV-014

### F18: EDIS → RTH Washington dissemination — S019 / EV-014

- **Status**: **Planned**.
- **What it does**: Produce **EDIS-compliant** ASCII messages with correct WMO abbreviated headers
  and submit to **NWS Telecommunications Gateway (RTH Washington)** using **one-shot BYOC**
  SMTP/gateway settings in the drawer (Q18≈A / Q16). Cycle close requires live BYOC green (Q15=A).
- **Acceptance**: Format validation + live submission demo with user-supplied gateway creds;
  secrets never persisted; allowlist/SSRF policy applies to SMTP hosts.
- **Source**: #6; S019 / EV-014

### F19: AMHS / SWIM / AFS adapters — S019 / EV-014

- **Status**: **Planned** (overturns prior Non-Goals for AMHS/SWIM/AFS).
- **What it does**: Dissemination adapters for **AMHS**, **SWIM**, and **AFS** selectable in the
  same drawer (Q20=D). BYOC connection parameters; backend-mediated; same secret/SSRF posture as
  F16–F18.
- **Acceptance**: Each adapter has a documented contract + staging/test path green before
  EV-014 close. **Hard close gate** remains Postgres + WIS2 + EDIS live BYOC (Q15=A / Q21=A).
  F19 **live** demos are optional — record green evidence or an explicit AskQuestion waive
  (does not block close if staging/test path is green).
- **Source**: S019 / EV-014 Phase 0 Q20=D / Q24=A; 02-verify-plan S-EV014-M2 (Q28=A)

## Platform Feature Details (Monorepo Migration)

### M1: Monorepo Layout

- **What it does**: Replaces six git submodules with a single-repo tree: `apps/`, `packages/`, `vendor/`.
- **F6 delta**: Approved tree gains `packages/tac2iwxxm`; loses `packages/gifts` at F6 cutover.
- **S008 package amend**: Also gains `packages/tac-validate` and `packages/iwxxm-validate`.
- **Key parameters**:
  | Parameter | Default | Description |
  |-----------|---------|-------------|
  | `apps/backend` | FastAPI API + merged auth | Single HTTP deployable |
  | `apps/frontend` | React/Vite UI | Static deployable |
  | `apps/worker` | F8 near-RT ingest poller | Render Background Worker (ADR-018) |
  | `apps/e2e` | Playwright cross-app tests | Dedicated workspace |
  | `packages/auth` | Supabase middleware library | Imported by backend, not separate service |
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

### M4: Auth Merged Into Backend

- **What it does**: Collapses auth microservice into backend app using `packages/auth` library.
- **S003 security delta (2026-06-23)**: Publishable/Secret keys, runtime `config.json`, env sync
  (Render ↔ Supabase ↔ local). ADR-010.
- **S011 / F7.a (#697)**: Remove `/admin/*` routes and admin role UX; auth surface shrinks to
  operator/user JWT for convert, validation, lint, decode, preview, and F5/F7 sessions. BYO
  Supabase + Postgres credentials via deploy env (no shared multi-tenant admin assumption).
- **Source**: REQ-004, REQ-009; S011 / EV-008

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

## Planned Features (Post-Migration)

| # | Feature | Priority | Complexity | Notes |
|---|---------|----------|------------|-------|
| P1 | OpenAPI → TS codegen in packages/shared | Medium | Low | After layout stabilizes |
| P2 | Path-filtered CI per app/package | Medium | Medium | Reduce CI time |
