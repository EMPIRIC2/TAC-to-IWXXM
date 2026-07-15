# Feature List

> **Project**: METAR to IWXXM Converter
> **Repository**: https://github.com/joseph-c-mcguire/metar-to-IWXXM
> **Last updated**: 2026-07-15 (S011 / ADR-023 — wire dormant convert params)

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
- **Acceptance (this amend)**: Library API + CI tests; backend thin wrappers for validate
  endpoints call `iwxxm-validate` (no behavior regression vs current F2).
- **Limitations**: Schema bundles must match vendored snapshot version.
- **Source**: `apps/backend` validation routers; [Context: realtime-tac-ingest](context/realtime-tac-ingest.md)

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
- **Limitations**: US AIRMET/SIGMET docs thinner than METAR/TAF — may gate fixture depth inside
  F6.d; F5 not extended to other products in v1; exact AHL dialect coverage TBD in fixtures.
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
- **Non-goals (still)**: AMHS/SWIM/AFS adapters; public machine-ingest auth UX; **push sinks**.
- **Source**: [Context: realtime-tac-ingest](context/realtime-tac-ingest.md) R2–R15; ADR-018;
  [execution-plan](sessions/S008-general-tac-iwxxm-converter/reports/execution-plan.md)

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
- AMHS / SWIM / AFS ingest adapters.
- **Push sinks** (webhook/S3/AMHS) — store + quarantine only for F8 v1.
- Public machine-ingest auth UX (worker uses service-role JWT internally — ADR-018).
- Schematron applied to TAC (Schematron stays on IWXXM; TAC uses `tac-validate`).
- Dedicated converter API service (rejected; F8 worker is the new deployable).

## Non-Goals (F7 / S011 — EV-008)

- Teaching / CMS content beyond short decode explanations (#702 v1).
- Click-row-to-edit TAC mutation; full IWXXM field mapping inside the decode table.
- Extending **F5** as a permanent parallel METAR-only store after unified cutover (F5 UX remains
  as My METARs filter on `tac_work_sessions`).
- Separate F7-only sessions table alongside `metar_work_sessions` (rejected — R2′).
- Per-user in-app “paste Supabase / DB keys” UI (BYO is deploy/env only — R6).
- Shared hosted multi-tenant admin dashboard, approval queues, or toggle-admin (#697).
- AMHS / SWIM / AFS; F8 push sinks.
- Rewriting conversion engines beyond span / decode / soft-preview hooks.

## Planned Features (Post-Migration)

| # | Feature | Priority | Complexity | Notes |
|---|---------|----------|------------|-------|
| P1 | OpenAPI → TS codegen in packages/shared | Medium | Low | After layout stabilizes |
| P2 | Path-filtered CI per app/package | Medium | Medium | Reduce CI time |
