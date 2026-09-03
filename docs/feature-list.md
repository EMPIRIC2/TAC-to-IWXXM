# Feature List

> **Project**: METAR to IWXXM Converter
> **Repository**: https://github.com/EMPIRIC2/TAC-to-IWXXM
> **Last updated**: 2026-08-24 (EV-079 — US SIGMET/AIRMET national layer M8)

## Summary

| # | Feature | Status | Category | Source |
|---|---------|--------|----------|--------|
| F1 | METAR → IWXXM conversion (GIFTs-era UX) | Superseded by F6 | Product | Historical; UI actions retained until F6 UI |
| F2 | IWXXM validation | Implemented | Product | backend → `packages/iwxxm-validate`; **deepen** S064 / EV-055 #980/#979 (2025-2 Schematron/XSD); prior S046 / EV-038; **deepen** S071 / EV-061 readable item-by-item decode on validate (#1010) |
| F3 | Airport data services | Implemented | Product | OpenAIP / reconciliation services |
| F4 | IWXXM version handling | Implemented | Product | docs/domain/iwxxm/IWXXM_VERSION_SWITCHING.md; **deepen** S046 / EV-038 release-line SoT/UX (#851–#855) |
| F5 | User METAR work history | Implemented | Product | S038 / EV-031 / F31 hybrid: guest IndexedDB + logged-in DO Postgres |
| F6 | General TAC→IWXXM (`tac2iwxxm`) | Implemented | Product | S008, ADR-013/014/019; bulletin split; **deepen** S055 / EV-046 #889; **deepen** S059 / EV-050 #959 annex3 vs iwxxm_us membership compare; **deepen** S071 / EV-061 AHL decode+convert (#1012) + live multipart `files` chore (#1011) |
| F7 | Multi-product TAC operator UI / sessions | Planned | Product | S011; F7.g #780; F7.h IndexedDB; **F31** hybrid; **deepen** S063–S066 **F7.q**; **deepen** S068 / EV-058 **F7.q** side-by-side vs inline diff (#983); **deepen** S067 / EV-057 **F7.r** accumulate ZIP (#903) + **F7.s** validate-only IWXXM (#838); **deepen** S070 / EV-060 **F7.t** IWXXM product pass-through (#1003) + converter UX (#1001/#1002/#1004/#1005) + Auth UAT (#1006); **deepen** S071 / EV-061 **F7.u** Product/Profile bars (#1013) + **F7.v** lint/validation catalog tab (#1014); **deepen** EV-062 **F7.v** Validation Issues Catalog (#1017) |
| F8 | Near-realtime TAC ingest → IWXXM gate | Implemented | Product | S008 ADR-018; **F30** writers → DO Postgres (not Supabase DB) |
| F9 | Value-aware live decode + plain-language summary | Done | Product | S013 / EV-009; shipped 2026-07-17 (#723) |
| F10 | Workbench preview clarity (IWXXM pane + lint UX) | Done | Product | S013 / EV-009; shipped 2026-07-17 (#723); **deepen** S048 / EV-040 full lint console lines + preserve input on convert |
| F11 | Validation stack perf review + msgspec HTTP + XSD codegen | Implemented | Product | S014 / EV-010; #703 |
| F12 | Publishable TAC product validation (`tac-validate`) | Implemented | Product | S014 / EV-010; #698; **deepen** S043 / EV-035 lint↔source provenance; **deepen** S055 / EV-046 ISSUE_CATALOG; **deepen** S059 / EV-050 #959 offline membership Validated |
| F13 | Fast IWXXM validate (Rust core + Schematron + PyPI) | Implemented | Product | S014 / EV-010; #699; **deepen** S054 / EV-045 Rust CI (#725); **deepen** S064 / EV-055 #980 |
| F14 | Publish `tac2iwxxm` + validate extras + PyPI/release CI | Implemented | Product | S014 / EV-010; #693; **deepen** S054 / EV-045 Rust CI (#725) |
| F15 | Maintainable TAC lint issue registry + METAR/SPECI quality bar | Done | Product | S015 / EV-011; #732; **deepen** S055 / EV-046 #889 Lean; **deepen** S059 / EV-050 #959 Validated membership + RE*/cloud fixtures; **deepen** EV-062 #1017 catalog descriptions + provenance locators |
| F16 | Dissemination drawer + multi-DB upload (BYOC URI) | Done | Product | S019 / EV-014; #729; **deepen** S024 / EV-018 multi-select (#785); **deepen** S047 / EV-039 live local SQL; **deepen** S050 / EV-042 #897 UI-hide (API retained); **restore** EV-091 / #898 + #1089 exchange overlay |
| F17 | WIS2 dissemination pathway | Done | Product | S019 / EV-014; #2; S050 / EV-042 hide; **restore** EV-091 / #898 |
| F18 | EDIS → RTH Washington dissemination | Done | Product | S019 / EV-014; #6; S050 / EV-042 hide; **restore** EV-091 / #898 |
| F19 | AMHS / SWIM / AFS adapters | Done | Product | S019 / EV-014; S050 / EV-042 hide; **restore** EV-091 / #898 |
| F20 | TAF + SPECI quality bar (F15 sequel) | Done | Product | S020 / EV-015; #735/#734; #778; **deepen** S055 / EV-046 #889; **deepen** S059 / EV-050 #959 |
| F21 | Public convert + optional Auth for long-term storage | Amended | Product | S023 #783; **S038 / EV-031 / F31** amend; **deepen** S057 / EV-048 #951 OpenAPI/error copy hygiene |
| F22 | Privacy preference center (Solution A + GPC) | Implemented | Product | S023 / EV-017; #783; **deepen** F31 storage gates |
| F23 | SIGMET family quality bar (general + VA) | Done | Product | S025 / EV-019; #733/#739; PR #792; **deepen** S055 / EV-046 #889; **deepen** S059 / EV-050 #959 phenomena membership; **deepen** EV-074 / #1043 CA ops validate-first (no TAC convert) |
| F24 | AIRMET quality bar | Done | Product | S026 / EV-020; #731; PR #793; **deepen** S055 / EV-046 #889; **deepen** S059 / EV-050 #959 underscore phenomena fixtures |
| F25 | WMO official example parity (METAR/SPECI/TAF) + UI gate | Done | Product | S026 / EV-020; PR #793 |
| F26 | VAA quality bar (VolcanicAshAdvisory) | Done | Product | S027 / EV-021; #736; PR #794; **deepen** S055 / EV-046 #889; **deepen** EV-074 / #1043 CA ops validate-first (no TAC convert) |
| F27 | TCA quality bar (TropicalCycloneAdvisory) | Done | Product | S027 / EV-021; #737; PR #794; **deepen** S055 / EV-046 #889 |
| F28 | SWXA quality bar (SpaceWeatherAdvisory) | Done | Product | S036 / EV-029; #823/#740 closed; PR #828; **deepen** S055 / EV-046 #889; **deepen** S059 / EV-050 #959 SpaceWxPhenomena fixtures |
| F29 | Parameterized lint/convert/validate rule matrices | Done | Product | S037 / EV-030; #831; shipped 2026-08-03 (#832) |
| F30 | Platform independence (Auth / DO DB / DOKS) | Done | Platform | S038 / EV-031; S042 / EV-034 CD; S052 / EV-043 staging CD (#886); S053 / EV-044 dual DOKS; **deepen** S060 / EV-051 tag-driven prod Deploy; **deepen** S067 / EV-057 apex → app redirect (#948) |
| F31 | Hybrid operator sessions (guest local + Auth long-term) | Done | Product | S038 / EV-031; amends F5/F7/F21/F22 |
| F32 | VONA quality bar (VolcanoObservatoryNoticeForAviation) | Done | Product | S040 / EV-032; #741 closed; **deepen** S055 / EV-046 #889; prior S046 / EV-038; epic #846 |
| F33 | Secure mass file/folder ingest | Implemented | Product | S050 / EV-042; #897; auth + caps + sniff/zip-bomb; multi-file + folder/zip; 11 approved |
| F34 | Contract + mutation quality gates | Done | Platform | S069 / EV-059; epic #841 CLOSED; #727 Schemathesis; #874 Stryker + pytest-gremlins; **deepen** S071 / EV-061 stricter stage→main required checks (#1015); promote held |
| F35 | Semantic vs exchange profiles + canonical ID migration | Implemented | Product | EV-063 / PR #1026; #912 / #914; ADR-036 Accepted; alias cutover #1025 (2026-10-31); amends F6 wire |
| F36 | National semantic + regional exchange profile content | In progress | Product | EV-063 / #912; **#919 US closed (EV-085)**; **#916 CA_ECCC P1 closed (EV-078)**; **EV-098 CA_ECCC mining #1028–#1031**; **#1032 closed (EV-075)**; **#1061 SIGMET emit (EV-076)**; VAA TAC validate-first (EV-077); VAA exchange emit waived |
| M1 | Monorepo layout (`apps/` + `packages/` + `vendor/`) | Planned | Platform | REQ-002–006 |
| M2 | Vendor snapshot sync (wmo-im iwxxm-*) | Planned | Platform | REQ-002, REQ-010 |
| M3 | GIFTs as in-repo package | Deprecated (ADR-014) | Platform | REQ-003; removed with F6 cutover |
| M4 | Auth library in backend API | Implemented | Platform | S038 / EV-031 — Supabase Auth-only restore; was Deprecated operator #783 |
| M5 | Workspace tooling (uv + pnpm + Makefile) | Planned | Platform | REQ-005; **deepen** S056 / EV-047 slim husky (#833; supersedes EV-036 day-to-day hook weight) |
| M6 | Vendor upstream sync (wmo-im iwxxm-*) | Planned | Platform | REQ-009 |

**Status key**: Implemented = production-ready, In progress = partial delivery on approved scope, Planned = approved in requirements interview, Experimental = works but not validated, Superseded / Deprecated = replaced by a later decision

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
  IWXXM-US XSD. **Official US Schematron is not published** (S045 / EV-037 / #870) — do not
  treat the whole US validate column as N/A; pipeline = WMO XSD + US XSD + WMO `iwxxm.sch` +
  project semantic rules + fixtures.
- **S008 package amend**: Core logic moves to **`packages/iwxxm-validate`** (XSD + Schematron
  against `vendor/schemas/*`). `apps/backend` validation routes become a **thin HTTP wrapper**.
  Schematron remains on **IWXXM only** — TAC quality is **F6/`packages/tac-validate`**, not F2.
- **S014 / EV-010 delta (F13)**: Engine gains a **Rust core** (well-formed + XSD + native
  Schematron/SVRL) with Python SDK; pinned schemas **bundled** in the wheel; published to
  PyPI as `iwxxm-validate` `0.1.0`. Backend `/validate` remains a thin wrapper. See F13.
- **S043 / EV-035 deepen (rule-source provenance)**: Revisited IWXXM-validation rules
  (XSD / Schematron / guidance) must map to standing domain provenance rows under
  `docs/domain/rules/` (path-cite; no new Fn) with **dense CI asserts**; unfindable
  sources raised to the operator. Complements F29 matrix harness.
- **S045 / EV-037 deepen (matrix dispositions)**: Document official IWXXM-US Schematron as
  **N/A / not published**; split validate classes in `COVERAGE_MATRIX` / `PROVENANCE_MAP`
  (`US_SCH_ABSENT`); optional 2025-2 + iwxxm-us 3.0 combined-catalog note. See deepen below.
- **Acceptance (this amend)**: Library API + CI tests; backend thin wrappers for validate
  endpoints call `iwxxm-validate` (no behavior regression vs current F2).
- **Limitations**: Schema bundles must match vendored snapshot version; no official US `.sch`.
  **2025-2** may emit `SCHEMATRON_SKIPPED` (xslt2) and/or `SCHEMA_IMPORT_WARNING` until EV-055
  disposition lands (#980 / #979).
- **S064 / EV-055 deepen (#980 / #979)**: **Hard** this cycle (`D-S064-sch-hard=1` /
  `D-S064-xsd-hard=1`): enable Schematron evaluation for 2025-2 xslt2 (prefer native) and
  fix `SCHEMA_IMPORT_WARNING` import resolution. Quality metrics consume outcomes. See F7.q
  EV-055 AC4–AC6 and F13.
- **Source**: `apps/backend` validation routers; [Context: realtime-tac-ingest](context/realtime-tac-ingest.md);
  [Context: package-publish-validation](context/package-publish-validation.md);
  **S043 / EV-035** · [Context: rule-source-traceability](context/rule-source-traceability.md);
  **S045 / EV-037** · [Context: matrix-disposition-residuals](context/matrix-disposition-residuals.md);
  **S064 / EV-055** · #980 / #979

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

- **Status**: **Planned** — **hybrid storage** under S038 / EV-031 / **F31** (amends S023 / EV-017 IndexedDB-only).
- **What it does (EV-031)**:
  - **Guest (not logged in)**: Device-local **IndexedDB** (Draft → WIP → Finished / Failed); export/import JSON; no cross-device sync.
  - **Logged-in**: Long-term work sessions on **DigitalOcean Postgres**, keyed by Supabase Auth user id (F30 data plane). Convert/lint/validate APIs stay public (no JWT required).
  - On login: **auto-upload** all eligible local drafts into DO Postgres (`D-S038-guest-merge`=2); no merge prompt.
- **What it did (EV-017)**: IndexedDB-only public path; server `tac_work_sessions` retired from public product.
- **Historical (pre-EV-017)**: Per-user Supabase Postgres via JWT + `tac_work_sessions`.
- **UI**: Guest path keeps recent-history / My METARs locally; logged-in path shows server sessions; persistent notice when guest that progress may be lost without login (F31).
- **Legacy Supabase rows**: No product reads from Supabase DB; archive/export/delete policy under F30/#830.
- **Source**: #555 / S004; F7; #783; **S038 / EV-031 / F31**; [Context: platform-independence-842](context/platform-independence-842.md)

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
| `product` | *(required on API)* | `airmet` \| `metar` \| `sigmet` \| `speci` \| `taf` \| `vaa` \| `tca` \| `swxa` \| `vona` | UI may auto-detect then send; API rejects omit |
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
- **EV-981 / #981 delta (propagate decode residuals → remarks / HRT)**: Opt-in convert flag
  `propagate_residuals_to_remarks` (default **off**; omitted → profile default). When **on**
  and the profile already emits remarks / `humanReadableText`, decode residual token text
  (excluding spans already covered by remarks retain) is appended into that emit path with
  info `ConvertIssue` `RESIDUALS_PROPAGATED_TO_REMARKS`. On **annex3**, do **not** invent
  free-text remarks XML; flag-on + residuals still emit that issue documenting **no XML
  target** (QM `residuals_propagated_to_remarks` stays false). When **off**, residuals remain
  decode-panel / quality-metrics diagnostics only (UJ-026 unchanged). Profile-default hook is
  wired; **annex3 / ICAO_2025 default stays off**; no other profile defaults enabled this
  cycle. `/convert-zip` inherits the Form field. Does **not** flip F6 status; does **not**
  implement UJ-040 structured remark codecs. See [Context: propagate-residuals-to-remarks](context/propagate-residuals-to-remarks.md);
  UJ-070; [evolve-decisions.md](decisions/evolve-decisions.md) §EV-981.
- **Limitations**: US AIRMET/SIGMET docs thinner than METAR/TAF — may gate fixture depth inside
  F6.d; F5 not extended to other products in v1; exact AHL dialect coverage TBD in fixtures.
  Full FMH-1 remark catalog beyond AO/SLP/PK/T/P free-text is still scoped deepen work.
- **S011 / F7 engine deltas** (packages stay under F6; operator UX under F7):
  - `POST /api/v1/decode-tac` — ordered segments with `start`/`end` (+ short explanations).
  - Optional integer `start`/`end` on lint-tac / validate issue objects (span highlight).
  - Soft-fail **preview** convert path returning best-effort IWXXM + failed-span markers
    (exact shape in api-contract / 04-tech-plan).
- **Source**: S008 01-requirements; ADR-013; ADR-014; `docs/context/general-tac-iwxxm-converter.md`;
  `docs/context/realtime-tac-ingest.md`; S011 / EV-008; **S043 / EV-035** encode/AHL
  provenance deepen (see deepen section below)

### F6 deepen (S043 / EV-035 — rule-source provenance)

- **Status note**: F6 remains **Implemented**; this cycle **re-links** encode + bulletin/AHL
  rules already extracted to authoritative sources (canonicals + `RULE_SOURCE_URLS` + mining
  digs) via a standing provenance map under `docs/domain/rules/` (**no new Fn** — G1=2).
- **Acceptance (EV-035)**:
  1. Every encode / AHL / bulletin rule cited or revisited has ≥1 provenance row
     (`ok` | `gap` | `paywall` | `N/A`) with source URL or explicit raise
  2. Dense CI asserts (many per rule / matrix cell) — reuse F29 harness patterns where useful
  3. Unfindable sources raised to operator; no silent invent
- **Out of scope**: New product encode; UI provenance UX; vendor hand-edits
- **Source**: [Context: rule-source-traceability](context/rule-source-traceability.md);
  [evolve-decisions.md](decisions/evolve-decisions.md) §EV-035

### F6 deepen (S056 / EV-047 — converter perf regression harness / #834)

- **Status note**: F6 remains **Implemented**; add a **hard PR/CI gate** when
  `tac2iwxxm.convert` regresses vs committed baselines (`D-S056-perf=1`). Soft benches and
  publish-only hard gates (E10-24 / T66) remain; this cycle adds a **default-branch merge
  block** for converter latency.
- **Defaults**: convert-only wall **p95**; committed YAML baselines; hard-fail if **>20%
  slower than baseline or above absolute ceiling**; product smoke = METAR/SPECI/TAF + thin
  SIGMET-family; **CI required check only** (not husky); pure-Python path first;
  median-of-N + documented flake retry; intentional baseline bumps via documented refresh
  (no silent auto-raise).
- **Acceptance (EV-047 / #834)** — **approved** (`D-S056-01-ac=1`):
  1. Artificial slowdown in `tac2iwxxm.convert` turns the gate **red** in CI.
  2. Reverting the slowdown turns the gate **green**.
  3. Gate is a **required** status check (or equivalent) on the protected branch path.
  4. Baselines + refresh procedure documented; flake policy documented.
  5. TC-EV047-005..008 green.
- **Out of scope**: Converter micro-optimizations; hard-failing every soft validate bench;
  husky-local enforcement of the perf gate.
- **Source**: [#834](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/834);
  [evolve-decisions.md](decisions/evolve-decisions.md) §EV-047; [Corpus: tests]

### F6 deepen (S045 / EV-037 — Bulletin AHL source vs impl matrix)

- **Status note**: F6 remains **Implemented**; this cycle **reclassifies** eight-family
  **Bulletin AHL** coverage so **source availability** is not conflated with parser /
  splitter / fixture / CI gaps ([#872](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/872)).
- **What changes**:
  1. Mark `AHL T1T2 source available = ✅` for all WMO-mapped families (METAR…VONA) from
     current WMO aviation AHL publication + vendor `AHL.asciidoc`
  2. Redesign the single **Bulletin AHL** cell into columns:
     `AHL source | T1T2 map | parser | BBB | body splitter | filename | COLLECT | fixtures | CI`
  3. Close #872 when sources are ✅ and residual **implementation** gaps have child issues
     (or are already tracked); do **not** leave stale `gap` that only meant “source missing”
- **Acceptance (EV-037 / #872)**: See shared EV-037 ACs under F32 deepen / test-plan
  **TC-EV037-***.
- **Out of scope**: Full per-family body-split / fixture pack implementation beyond matrix
  redesign and residual child tickets
- **Source**: [Context: matrix-disposition-residuals](context/matrix-disposition-residuals.md);
  [evolve-decisions.md](decisions/evolve-decisions.md) §EV-037; [COVERAGE_MATRIX](domain/rules/COVERAGE_MATRIX.md)

### F2 deepen (S045 / EV-037 — IWXXM-US Schematron N/A)

- **Status note**: F2 remains **Implemented**; document official US Schematron artifact as
  **N/A / not published** ([#870](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/870)).
- **Validation class split** (matrix / provenance):

  | Class | Status |
  |-------|--------|
  | WMO core XSD | ✅ |
  | IWXXM-US 3.0 XSD | ✅ |
  | WMO core Schematron | ✅ |
  | Official IWXXM-US Schematron | **N/A — not published** |
  | U.S. profile semantic checks | ✅/⚠ per project rule coverage |
  | U.S. examples/goldens | ✅/⚠ per fixture coverage |

- **Acceptance (EV-037 / #870)**: `US_SCH_ABSENT` disposition = `N/A` (not `gap` invent);
  METAR_US validate cell no longer implies “all US validation ⚠”; TC-EV037-002 green.
- **Out of scope**: Authoring a project Schematron to replace NOAA; claiming 2025-2
  certification of IWXXM-US 3.0 without a combined-catalog check note
- **Source**: [Context: matrix-disposition-residuals](context/matrix-disposition-residuals.md);
  NOAA iwxxm-us 3.0 publication; [PROVENANCE_MAP](domain/rules/PROVENANCE_MAP.md)

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
  | F7.i | #842 / F31 | Hybrid: guest IndexedDB + logged-in DO Postgres; auto-upload on login — S038 / EV-031 |
  | F7.q | #836 / #982 / #988 / #983 / #981 | Quality metrics tab — official WMO corpus; W3C C14N match/diff (S063 / EV-054; S064 / EV-055); dedicated detail route + collapsible diffs (S066 / EV-056); selectable side-by-side vs inline XML diff (S068 / EV-058); **EV-981** residual fold indicator (`residuals_propagated_to_remarks`) |
  | F7.r | #903 | Accumulate back-to-back conversions → one ZIP (S067 / EV-057) |
  | F7.s | #838 | Validate existing IWXXM (paste / single `.xml` upload; no TAC) (S067 / EV-057) |
  | F7.t | #1003 | IWXXM as **product** pass-through (lint + F2 validate; no TAC convert) (S070 / EV-060); siblings #1001 AHL noise, #1002 profile picker, #1004 log_level, #1005 bulletin fields, #1006 Auth UAT |
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
- **S056 / EV-047 deepen (#956/#957 — operator docs + Help)**: User-facing **one-pager** and
  **minimal operational handbook** under `docs/guides/`; discoverable from README Quick start
  **and** in-app Help (`D-S056-docs=1`). No internal `[Corpus:]` / ADR / session IDs in
  published operator text. Does **not** flip F7 → Implemented.
- **Acceptance (EV-047 / #956/#957)** — **approved** (`D-S056-01-ac=1`):
  1. `docs/guides/operator-one-pager.md` fits one printed page; covers paste/convert →
     validate → download; IWXXM version pick; soft preview in plain language.
  2. `docs/guides/operator-handbook.md` covers login/access, convert & validate, work
     history, dissemination destinations (high level), troubleshooting; points to automated
     ingest when available.
  3. README Quick start links both; in-app Help entry reaches the one-pager (handbook linked
     from one-pager for depth).
  4. No internal engineering citations in user-facing handbook/one-pager text.
  5. UJ-054 / TC-EV047-009..011 green (Vitest/Playwright for Help entry as applicable).
- **S057 / EV-048 deepen (#951 — strip internal doc refs from operator UI)**: Operator-visible
  UI copy (labels, helpers, tooltips, banners, empty states, console/catalog copy, example
  tier labels, privacy/auth copy) must not cite internal engineering vocabulary
  (`[Corpus:…]`, ADR/session/EV IDs, product `FNN` ids, `docs/` paths, UJ/TC/issue numbers).
  Source comments, tests, and repo docs remain allowed. Does **not** flip F7 → Implemented.
- **Acceptance (EV-048 / #951 — F7 UI slice)** — **approved** (`D-S057-01-ac=1`):
  1. Audit findings for UI string catalogs listed in the PR.
  2. No operator-visible UI string matches guard patterns (see test-plan TC-EV048).
  3. Automated guard covers FE string catalogs; comments/tests excluded.
  4. UJ-055 / TC-EV048-003 green.
- **S063 / EV-054 deepen (F7.q / #836 — Quality metrics tab)**: Primary **app shell tab**
  (peer to Convert / History — not a panel inside the convert workbench) that browses the
  official WMO IWXXM example corpus by product/file type and surfaces **precomputed** match,
  residuals, lint, and validate diagnostics via public **`GET /api/v1/quality-metrics*`**
  (`D-S063-compute=1` + `D-S063-gateA=2`). Per-file detail includes **unified XML diff** of
  official vs our conversion (`D-S063-diff=2`). Does **not** flip F7 → Implemented;
  complements CI matrices (#815 / #831 / F29) without replacing them.
- **Acceptance (EV-054 / #836 — F7.q)** — **approved** (`D-S063-01-ac=1`; Gate A amend
  `D-S063-gateA=2`):
  1. Quality metrics is a **separate primary tab** (shell navigation); lists official corpus
     files by product / file type (ADR-032 tiers visible).
  2. Selecting a file shows official peer + our conversion (TAC/XML inspectable) with
     **match status** and a **unified XML diff**.
  3. Residuals, lint, and validation issue panels visible (empty states when clean).
  4. Product-level summary counts match the precomputed fixture run (or documented refresh),
     loaded via **`GET /api/v1/quality-metrics`**.
  5. Deferred / FIXTURE_GAPS stems labeled; no silent missing in-scope official files.
  6. H4–H5 or Playwright smoke: open tab → filter one product → open one passer → clean or
     expected diagnostics (**UJ-056** / TC-EV054).
  7. No Supabase and no live upstream WMO fetch; metrics come from our public API backed by
     precomputed fixtures (same API host as convert — not FE-only bundle).
- **S064 / EV-055 deepen (F7.q / #982 + validate follow-ups #980/#979)**: Compare official and
  converted XML with **W3C C14N** (`D-S064-c14n=1`) so `match_status` and unified diffs reflect
  semantic differences (`D-S064-normalize=1`). Shared normalize semantics in generator + FE
  (`D-S064-gateA-M1=1`). Detail panes show **normalized** XML by default with operator override
  to un-normalized (`D-S064-gateA-M2=override`). Regenerate precomputed `corpus_metrics`
  (`D-S064-regen=1`). **Hard** this cycle: enable Schematron for IWXXM **2025-2** xslt2 via
  native when required (`D-S064-sch-hard=1`) and **fix** `SCHEMA_IMPORT_WARNING` for 2025-2
  (`D-S064-xsd-hard=1`) — overrides earlier soft “prefer/optional” intake. Engine changes in
  `packages/iwxxm-validate` (F2/F13); operator surface remains Quality metrics. Does **not**
  flip F7 → Implemented.
- **Acceptance (EV-055 / #982/#980/#979 — F7.q + F2/F13)** — **approved** (`D-S064-01-ac=1`;
  Gate A `D-S064-gateA=1`):
  1. Whitespace/formatting-only official↔converted pairs no longer dominate unified diff;
     semantic diffs remain (C14N peers).
  2. `match_status` uses equality of **C14N** XML on both sides **after** volatile-attr
     strip (`D-S064-c14n-volatile=1` / ADR-035); API/product copy free of internal planning ids.
  3. Normalize helper (C14N) unit tests + ≥1 golden stem; vendor schemas remain read-only;
     shared by generator and FE.
  4. #980: Schematron for 2025-2 **enabled** (native path); engine matrix documented; not
     closed as UX-only skip.
  5. #979: root cause (file + import URI) documented **and fixed** this cycle (regression test).
  6. Quality metrics: validate chips reflect fixed/enabled disposition; detail XML panes
     default to normalized with override to un-normalized; no internal planning ids.
  7. `corpus_metrics` regenerated for new match semantics; UJ-056 deepen / TC-EV055 smoke.
- **S066 / EV-056 deepen (F7.q / #988 — detail page + collapsible diffs)**: After S065
  pretty-print hotfix (#987), replace inline Quality metrics detail+diff with a **dedicated
  shareable route** `/quality/:stem` (`D-S066-route-shape=1`) and **GitHub-style** unified
  diff hunk folding (default **3** context lines; expand hunk / expand all —
  `D-S066-context-n=1`). List navigates to detail; back returns to list (`D-S066-list=1`).
  Keep **C14N equality** / `match_status` unchanged; no API contract change unless shell
  routing needs it; reuse `unifiedLineDiff` + pretty C14N helpers (no new npm diff lib
  unless AskQuestion). Does **not** flip F7 → Implemented.
- **Acceptance (EV-056 / #988 — F7.q)** — **approved** (`D-S066-01-ac=1`):
  1. List row opens dedicated detail route `/quality/:stem` (shareable URL) with back-to-list.
  2. Official/Converted/TAC panes remain; normalized panes = pretty C14N (S065 helpers).
  3. Diff shows collapsible equal-context hunks (default 3 lines; expand N / expand all).
  4. Unequal SIGMET stems remain navigable and readable on staging.
  5. UJ-056 / TC-EV056 updated; FE unit + Playwright smoke (H4–H5 via 13).
- **S068 / EV-058 deepen (F7.q / #983 — side-by-side vs inline XML diff)**: On
  `/quality/:stem`, add a **segmented control** — **Inline (unified)** | **Side-by-side** —
  so operators can switch layouts without reload (`D-S068-01-control=3a`). Default remains
  **unified** (UJ-056 backward compatible). Side-by-side uses existing `unifiedLineDiff` /
  line-diff helpers (no new npm `diff` unless Gate B re-approved). Preference persists in
  **localStorage**. Synced scroll between side-by-side panes is **best-effort** (not a
  blocking AC — `D-S068-01-ac=2b`). Keep raw TAC / diagnostics / collapse-equal-context.
  C14N / `match_status` unchanged; FE-only. Does **not** flip F7 → Implemented.
- **Acceptance (EV-058 / #983 — F7.q)** — **approved** (`D-S068-01-ac=2b`):
  1. Operator switches Inline (unified) ↔ Side-by-side without reload.
  2. Default layout is unified (compatible with prior UJ-056 assertions unless updated).
  3. Side-by-side highlights changed lines via existing line-diff util; no new npm `diff`.
  4. Layout preference persists in localStorage across visits.
  5. Raw TAC / diagnostics / collapsible unified equal-context remain; Vitest + Playwright
     cover both modes; H4–H5 via 13. Synced scroll is best-effort polish, not required to pass.
- **EV-981 / #981 deepen (F7.q — residual fold hook)**: Quality metrics detail exposes
  additive boolean `residuals_propagated_to_remarks` (fixture-backed; existing stems
  **false** until regenerated). Residuals panel shows plain-language whether leftover TAC
  was folded into remarks / human-readable text for that fixture. Does **not** rebuild the
  corpus browser; does **not** live-fetch WMO; does **not** flip F7 → Implemented.
- **Acceptance (EV-981 / #981 — F7.q hook)** — **approved** (`D-EV981-qm`):
  1. Detail JSON includes `residuals_propagated_to_remarks`.
  2. UI residuals panel reflects the field with operator-safe copy (no planning ids).
  3. Default corpus fixtures remain `false` compatible with prior UJ-056 assertions.
  4. TC-EV981-* + UJ-070 / UJ-056 deepen; H4–H5 after Build.
- **S067 / EV-057 deepen (F7.r / #903 — accumulate conversions → one ZIP)**: Successful
  converts **append** to the current result set instead of wiping prior successes so operators
  can convert A→B→C and **Download all** as one ZIP. Default archive basename when custom
  output name is empty: sanitize **first ~8 characters** of the **first** successful conversion’s
  TAC + timestamp (`{stem}_{yyyyMMddHHmmss}.zip`). Custom basename keeps `{base}.zip` (#664 /
  EV-005). Explicit clear/reset restores empty batch. Failed convert leaves prior successes.
  Soft accumulate cap **≤200** results (`D-S067-903-cap=1c` — align with F33 file-count
  ceiling for sequential UI; clear error when over). Does **not** flip F7 → Implemented.
  Notes F1/F6 download path only — no batch disseminate.
- **Acceptance (EV-057 / #903 — F7.r)** — **approved** (`D-S067-01-ac=1`):
  1. N≥2 sequential successful converts remain visible without re-pasting earlier TAC.
  2. Download all packages every accumulated IWXXM into one ZIP (per-file naming unchanged).
  3. Empty custom name → `{stem}_{yyyyMMddHHmmss}.zip` (≈8 sanitized TAC chars of first success).
  4. Custom basename → `{base}.zip` per #664.
  5. Explicit clear/reset of the accumulated set.
  6. Failed convert leaves prior successes untouched.
  7. Soft accumulate cap **≤200**; clear error when over (`D-S067-903-cap=1c`).
  8. UJ-057 / TC-EV057-* unit + Playwright; H4–H5 via 13.
- **S067 / EV-057 deepen (F7.s / #838 — validate existing IWXXM)**: Dedicated **Validate**
  mode: paste IWXXM XML and/or upload **one** `.xml` file through F2 `iwxxm-validate` **without**
  TAC→IWXXM convert. Reuse existing `POST /api/v1/validate` unless 04 finds a wire gap.
  Same F4 version/profile controls as convert/validate elsewhere. Multi-file/zip deferred.
  Guest-usable (no Supabase). Does **not** flip F7 → Implemented; does not replace F7.q.
- **Acceptance (EV-057 / #838 — F7.s)** — **approved** (`D-S067-01-ac=1`):
  1. Paste IWXXM and run validate without converting TAC.
  2. Upload one IWXXM `.xml` and see F2 XSD+Schematron results.
  3. Invalid / non-IWXXM XML fails clearly (structured error; no opaque 5xx for bad input).
  4. Version/profile selection consistent with convert/validate UI (F4).
  5. Happy path works without Supabase.
  6. UJ-058 / TC-EV057-* : good fixture pass; broken XML structured fail; H4–H5 via 13.
- **S070 / EV-060 deepen (F7.t / #1003 — IWXXM product pass-through)**: Add **IWXXM** to the
  product select. Selecting it skips TAC→IWXXM convert; paste/upload XML is linted
  (well-formed / COLLECT vs report) and validated (F2) only. Convert is disabled or no-ops
  with a clear operator message. **F7.s Validate-only stays**. FileConverter / accumulate /
  Quality metrics honor `product=iwxxm`. API enum adds `iwxxm`. Does **not** flip F7 →
  Implemented. Parent epic [#1000](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1000).
- **Acceptance (EV-060 / #1003 — F7.t)** — **approved** (`D-S070-e3a` / `D-S070-e9`):
  1. Given product=IWXXM and valid IWXXM XML, when lint+validate, then no TAC convert runs and F2 result is shown.
  2. Given product=IWXXM and TAC text, when run, then operator/API get a not-XML error.
  3. FileConverter / accumulate / Quality metrics honor product=IWXXM.
  4. API `product=iwxxm` on convert/lint/validate; OpenAPI updated.
- **S070 / EV-060 deepen (#1001 AHL bulletin lint noise)**: AHL wrapper lints as bulletin COM;
  contained TAC reports lint/validate with the selected product. Heading tokens are not
  product-syntax errors. Same on workbench, FileConverter, and `/convert-bulletin` / lint.
- **S071 / EV-061 deepen (#1012 AHL decode + convert)**: Well-formed multi-report METAR AHL
  (canonical heading `T1T2A1A2ii CCCC YYGGgg [BBB]` + `=`-terminated reports; golden
  `SAUS31 KZNY` fixture) **decodes** with item-by-item readable rows per report **and**
  **convert-bulletin** succeeds. Malformed AHL → clear `INVALID_AHL` / `empty_bulletin`.
  Context for operators/API: product, profile, optional Bulletin ID / Issuing Center.
  Distinct from #1011 (stale live harness field name).
- **S071 / EV-061 chore (#1011)**: `tests/live/test_tc_live_f6_030_bulletin.py` posts multipart
  field `files` (API contract), not `file`.
- **Acceptance (EV-060 / #1001)**: Given a well-formed AHL METAR bulletin, when lint/validate,
  then heading is not a flood of product-syntax errors and contained METARs are checked.
- **S070 / EV-060 deepen (#1002 profile picker)**: Clearly labeled Profile (Annex 3 / IWXXM-US)
  at converter **top** (not buried in params); applied to convert/lint/validate; keyboard
  accessible name+label. Not the #933 editor.
- **S070 / EV-060 deepen (#1005 Bulletin ID / Issuing Center)**: Labeled, editable fields;
  sent on convert; empty → discover-from-AHL or defaults; invalid CCCC/ID → one field error.
- **S070 / EV-060 deepen (#1004 log_level)**: Existing UI/API log-level enum sets **logger
  verbosity** in backend + packages (not client-echo filter only). DEBUG must not dump JWTs,
  passwords, or Authorization headers.
- **S070 / EV-060 deepen (#1006 Auth UAT)**: Facilitated UAT + Playwright register, login,
  logout, session persist; guest convert still works (F21). Deepens F31 / UJ-003 / UJ-046.
- **S071 / EV-061 deepen (F7.u / #1013)**: Product Type + Profile at converter top do **not
  wrap** at ≥1024px; mode selects share one aligned bar/row; conversion parameters share one
  aligned bar/row; visually polished; stacked OK below 1024px. Keyboard labels preserved.
- **S071 / EV-061 deepen (F7.v / #1014)**: Top-level **Lint & validation catalog** nav tab +
  page listing code, description, level, and **working** source links for TAC lint **and**
  IWXXM validation checks. Source policy (`D-S071-links-resolve`): three tiers; `codes.wmo.int`
  concept paths may be **semantic-only**; operator hrefs use verified landings (registry guide,
  wmo-im/iwxxm, AHL knowledge-hub, NWS iwxxm-us, APAC FAQ). See
  [mining/ev061-catalog-source-replacements-2026-08-18.md](domain/mining/ev061-catalog-source-replacements-2026-08-18.md).
  Related but distinct from #996 click-for-detail.
- **EV-062 deepen (F7.v / #1017)**: Rename operator surface to **Validation Issues Catalog**.
  Expose **issue_type** (`presence` \| `structure` \| `content` \| `consistency` \|
  `iwxxm_schema` \| `other`) with sort + multi-filter (type, level, family, product,
  source access/tier). Descriptions are natural-language **what / why / severity** with
  section-level citations or explicit **Source section unavailable**. Prefer public primary
  `source_url`; label paywall; expose `source_locator` + `source_access`. Distinct from #996.
- **Resolved gaps (S011 Feature List Batch 2)**:
  | ID | Decision |
  |----|----------|
  | G1 | Keep `DISABLE_AUTH` / local–CI auth bypass patterns; BYO is deploy topology only |
  | G2 | Self-signup vs invite-only is **operator Supabase policy** — app adds no invite gate |
  | G3 | **No product migration** of shared-project users/data; clean BYO cut (point env at own project) |
  | G4 | VAA/TCA decode spans: **best-effort + explicit residuals** in v1 (full field offsets not required) |
  | R2′ | **Override R2**: unified `tac_work_sessions` + migrate F5 rows (Spec Batch 2 A / 2026-07-13) |
  | R2″ | **Override R2′ storage**: browser IndexedDB (S023 / EV-017 / #783); server session table retired from public product |
  | R2‴ | **Override R2″**: hybrid — guest IndexedDB; logged-in DO Postgres via Supabase Auth (S038 / EV-031 / F31) |
- **G1 amend (EV-017)**: Retire `DISABLE_AUTH` dual path when operator Auth is removed (F21) —
  public routes are the only operator path; F8 keeps separate machine credentials.
- **Source**: S011 Phase 0 R1–R6; Feature List Batches 1–2 (2026-07-13);
  [Context: f7-operator-ui](context/f7-operator-ui.md); issues #694/#702/#665/#666/#697;
  [Context: golden-examples-ui](context/golden-examples-ui.md); #780 (S021 / EV-016);
  [Context: public-app-privacy](context/public-app-privacy.md); #783 (S023 / EV-017)

### F8: Near-Realtime TAC Ingest → IWXXM Gate

- **Status**: **Implemented** (S008 / EV-006 — ADR-018/019). Worker unit/pipeline approved;
  live T7.4 staging smoke deferred (12/13 skipped this cycle). **Deepened EV-033 / S041** —
  DOKS poller URL fail-closed (code + preflight + docs fixture pin + CrashLoop check).
- **What it does**: Continuous/near-realtime ingest of TAC (and bulletins) → `tac-validate` →
  `tac2iwxxm` → `iwxxm-validate` (Schematron/XSD) → **store**; **quarantine** on convert
  or Schematron failure (no publish). Latency target **&lt;5–15s** E2E; scale via **worker
  replicas** (drop nothing). Product scope = F6 seven.
- **Deployable**: Background Worker at `apps/worker/` (DOKS `metar-worker` / Render suspended);
  HTTPS/object poller; store + quarantine on **DigitalOcean Postgres** via `DATABASE_URL` (not
  Supabase DB / service-role PostgREST). `INGEST_POLLER_URL` must be real `https://` before
  replicas &gt; 0 (`scripts/deploy/doks_worker_poller_preflight.sh`).
- **Non-goals (F8 worker path)**: public machine-ingest auth UX; **automatic** push of ingest
  results (operator dissemination sinks are **F16–F19**, not F8 auto-push).
- **Source**: [Context: realtime-tac-ingest](context/realtime-tac-ingest.md) R2–R15; ADR-018;
  **S038 / EV-031 / F30** DO Postgres amend; [Context: platform-independence-842](context/platform-independence-842.md);
  [deploy/doks/README-worker-hardening.md](../deploy/doks/README-worker-hardening.md)

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
- **EV-981 / #981 note**: Decode residuals remain on the decode contract. Folding residual
  text into IWXXM remarks / HRT is a **convert** opt-in (`propagate_residuals_to_remarks`)
  under F6 — not a change to `/decode-tac` response shape.
- **Out of scope**: LLM/AI-generated text; changing segment offsets contract; Layer 1–2 or
  Schematron semantics.
- **Acceptance (F9 v1 done)**:
  1. METAR/SPECI/TAF golden fixtures produce value-aware explanations for wind, visibility,
     temperature/dewpoint, altimeter/QNH, time, station, clouds, weather groups
  2. `summary` present for all seven products (best-effort where sparse) and updates live
     while typing
  3. Residuals named in summary via "Not decoded: …" when present
  4. Decode response stays backward-compatible (additive `summary` only)
- **S071 / EV-061 deepen (#1010)**: When Validate IWXXM (or product=IWXXM validate path)
  still produces decode, the UI shows the **same item-by-item readable description panel**
  used for other TAC product types (parity with F9 decode rows / plain-language patterns) —
  not a raw dump. F7.s validate-only and F7.t pass-through remain. UJ-064.
- **Source**: S013 intake E9-2/E9-3/E9-4/E9-6; Batch 1 (all recommended, 2026-07-16);
  [evolve-decisions §EV-009](decisions/evolve-decisions.md); S071 / EV-061 #1010

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
- **Source**: #698; E10-4/9/19/21; docs/domain/rules/COVERAGE_MATRIX.md; #781;
  **S043 / EV-035** lint↔source provenance deepen

### F12 deepen (S043 / EV-035 — rule-source provenance)

- **Status note**: F12 remains **Implemented**; this cycle links every revisited
  `tac-validate` / `ISSUE_CATALOG` code to normative (or paywall/gap) cites in the domain
  provenance map with dense CI asserts (completeness, URL shape, behavioral fixture where
  executable). Complements F15 catalog drift + F29 matrices.
- **Acceptance**: See EV-035 ACs under F15 deepen / test-plan **TC-EV035-***.
- **Source**: [Context: rule-source-traceability](context/rule-source-traceability.md)

### F13: Fast IWXXM Validate (Rust Core + Schematron + PyPI)

- **Status**: **Implemented** — S014 / EV-010 (#699); EMPIRIC2 OIDC + consumer landing
  pages EV-028 / #781 (`0.1.1`); **deepen** S054 / EV-045 ([#725](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/725)).
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
- **S054 / EV-045 deepen (Rust CI — #725)**: PR/default CI must gate
  `packages/iwxxm-validate/rust` with `cargo fmt --check`, `cargo clippy -- -D warnings`,
  `cargo test`, plus maturin/PyO3 smoke (parity with `tac2iwxxm` native job). Local
  `make rust-check` mirrors CI. See TC-EV045-*.
- **Acceptance (EV-045 deepen)**:
  1. CI fails on unformatted Rust under `packages/iwxxm-validate/rust`
  2. CI fails on clippy warnings (`-D warnings`) unless documented allowlist
  3. `cargo test` green for the crate on PR/push default CI
  4. Maturin/PyO3 integration smoke required for `iwxxm-validate` (not only `tac2iwxxm`)
  5. Required check name(s) documented so red Rust CI blocks merge (**ops** ruleset
     apply may be deferred — D-S054-ac6-waive=2)
- **S064 / EV-055 deepen (#980 — Schematron 2025-2 xslt2)**: Native path must **enable**
  evaluation for vendor 2025-2 Schematron with `queryBinding="xslt2"` (`D-S064-sch-hard=1`);
  document lxml vs native matrix. Soft UX-only skip is **not** an acceptable cycle close.
- **Source**: #699; E10-6/7/19/22; ADR-017; #781; #725; #980

### F14: Publish `tac2iwxxm` + Validate Extras + PyPI/Release CI

- **Status**: **Implemented** — S014 / EV-010 (#693); EMPIRIC2 OIDC + consumer landing
  pages EV-028 / #781 (`0.1.1`); **deepen** S054 / EV-045 ([#725](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/725)).
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
- **S054 / EV-045 deepen (Rust CI — #725)**: Same Rust lint/typecheck/unit/integration
  gates for `packages/tac2iwxxm/rust` as F13; extend beyond maturin-only
  `tac2iwxxm-native` smoke. Deploy `needs` must include the new Rust check job(s).
- **Acceptance (EV-045 deepen)**:
  1. CI fails on unformatted Rust under `packages/tac2iwxxm/rust`
  2. CI fails on clippy warnings (`-D warnings`) unless documented allowlist
  3. `cargo test` green for the crate on PR/push default CI
  4. Existing maturin smoke retained; crate-local `cargo test` is also required
  5. `make rust-check` documents local parity for both crates
- **Source**: #693; E10-5/19/20/25; #781; #725

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
  ADR-028; `docs/domain/rules/COVERAGE_MATRIX.md`; **S043 / EV-035** ISSUE_CATALOG↔source

### F15 deepen (S043 / EV-035 — rule-source provenance)

- **Status note**: F15 remains **Done**; this cycle does **not** add a new Fn. Standing
  provenance map under `docs/domain/rules/` links registry codes ↔ sources; CI fails on
  cite drift for in-scope codes; gaps raised to operator.
- **Acceptance (EV-035 shared with F6/F12/F2 deepen)**:
  1. Provenance artifact lists digs reviewed + rules extracted + source links
  2. Every in-scope `ISSUE_CATALOG` code has provenance status (`ok`/`gap`/`paywall`/`N/A`)
  3. Coverage-matrix cells for revisited products/roles cite URL or explicit gap
  4. Dense asserts: many per cited/revisited rule (not single smoke) — TC-EV035-*
  5. Encode/SCH/bulletin cites included when those rules are revisited (full stack)
- **Source**: [Context: rule-source-traceability](context/rule-source-traceability.md);
  [evolve-decisions.md](decisions/evolve-decisions.md) §EV-035

### F7 / F10 / F15 deepen (S048 / EV-040 — workbench lint UX + catalog attribution)

- **Status note**: F7 remains **Planned**; F10/F15 remain **Done**; **no new Fn**. Operator UX
  and catalog presentation deepen only.
- **Acceptance (EV-040)**:
  1. Lint console: one line per issue (no `+N more` truncation) — F10
  2. Convert / Convert&Send does not clear manual TAC input — F7/F10
  3. **New TAC** label; action strip below header, above selects, above bench — F7
  4. UserPreferences slimmed to output name + extension (F22 Privacy unchanged) — F7
  5. Examples include official-provenanced AHL bulletin + IWXXM Collect — F7.g
  6. Lint catalog (MD/JSON/API/FE) shows WMO/ICAO/IWXXM source attribution — F15
  7. WMO A3-1 + AHL demo lint without false-positive errors; FPs logged — F15
- **Source**: [Context: workbench-lint-ux](context/workbench-lint-ux.md);
  [evolve-decisions.md](decisions/evolve-decisions.md) §EV-040

### F15 / F7.v deepen (EV-062 — Validation Issues Catalog / #1017)

- **Status note**: F15 remains **Done**; F7 remains **Planned**; **no new Fn**. Catalog UX +
  provenance presentation deepen only (encode engines unchanged for link polish).
- **Acceptance (EV-062)**:
  1. Operator surface titled **Validation Issues Catalog**
  2. Each row has filterable `issue_type` (closed vocab)
  3. Descriptions explain what/why/severity with section cite or explicit unavailable
  4. `source_locator` + `source_access` on API; public-prefer primary hrefs; paywall labeled
  5. Sort + multi-filter; H4–H5 + TC-EV062-*; #996 remains OOS
- **Source**: [#1017](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1017);
  [evolve-decisions.md](decisions/evolve-decisions.md) §EV-062;
  [mining/ev061-catalog-source-replacements-2026-08-18.md](domain/mining/ev061-catalog-source-replacements-2026-08-18.md)

### F6 deepen (S015 / EV-011 — METAR)

- **Status note**: F6 remains **Implemented**; this cycle **deepens METAR/SPECI** convert/golden
  fidelity under F15 acceptance (not a new Fn). Track gaps vs #732 known list (COR/NIL/remarks;
  IWXXM-US AO2/SLP/PK WND; AHL+SPECI adjacency) — **R1–R8 themes must close** (HARD); other
  convert gaps outside those themes may defer only via AskQuestion + coverage note.

### F12 deepen (S015 / EV-011 — METAR)

- **Status note**: F12 remains **Implemented** (PyPI `0.1.0`); this cycle routes METAR/**SPECI**
  rules through the F15 registry and expands accept/negative packs to full-depth checklist targets.

### F16: Dissemination drawer + multi-DB upload (BYOC URI) — S019 / EV-014

- **Status**: **Done** (EV-014 closed 2026-07-21; #771/#772). **Deepen** S024 / EV-018 /
  [#785](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/785) — multi-file export selection.
  **Deepen** S047 / EV-039 — live local multi-DB SQL ingest Playwright + teardown hygiene
  (in progress).
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
- **EV-039 deepen (S047) — live local SQL ingest + teardown**:
  1. Reuse **`docker-compose.mock-byoc.yml`** profile `mock-byoc` for disposable Postgres,
     MySQL, and SQL Server; SQLite uses a disposable file path (not a long-lived service).
  2. Playwright **live** (no HTTP route mocks) exercises drawer preflight→send against those
     local URIs for **all four** dialects and asserts a successful write (row / writer-contract
     equivalent).
  3. Mocked H6′ UJ-027 suite remains **separate** and must stay green.
  4. **Teardown** is mandatory across integration (Testcontainers), e2e/Playwright, and local
     Compose make targets — no orphan containers, volumes (where safe), temp SQLite files, or
     lingering processes after pass/fail/skip.
  5. Document `make` / CI entrypoints; live suite may be opt-in in CI if SQL Server is heavy,
     but must be runnable locally for EV-039 close.
- **Acceptance** (base EV-014 + EV-018 + EV-039):
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
  12. **(EV-039 AC1)** Compose mock-byoc profile brings healthy Postgres, MySQL, SQL Server;
      SQLite disposable file path documented
  13. **(EV-039 AC2)** Live Playwright preflight→send succeeds for each of four dialects against
      local URIs with write assertion
  14. **(EV-039 AC3)** Existing mocked H6′ UJ-027 suite stays green and separate from live suite
  15. **(EV-039 AC4)** After live e2e / mock-byoc targets: Compose down; no orphan
      containers/processes; SQLite temp files removed
  16. **(EV-039 AC5)** Integration/Testcontainers writer-contract fixtures always tear down on
      pass/fail/skip
  17. **(EV-039 AC6)** Teardown audit gaps fixed or explicitly waived in session report
  18. **(EV-039 AC7)** Test-plan maps UJ-027 live path ↔ TC-F16-LIVE-*; `make`/CI documents how
      to run the live suite
- **Out of scope**: Saved/encrypted connection profiles; pasting Supabase **auth** keys in-app;
  F8 auto-push; Finished work-history as export sources (v1); batched multi-payload API (v1);
  browser zip archive download unrelated to sink send; new DB vendors; live WIS2/EDIS/F19 BYOC;
  production SQL containers
- **Source**: #729; S019 / EV-014; ADR-021 amend; ADR-029 (SSRF); ADR-030 (package/API);
  **#785; S024 / EV-018** (multi-select deepen); **S047 / EV-039** (live local SQL + teardown)

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

### F21: Public Convert + Optional Auth for Long-Term Storage — Amended S038 / EV-031

- **Status**: **Amended** (S038 / EV-031 / **F31**; was **Implemented** public-only S023 / EV-017 / [#783](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/783)).
- **What it does (EV-031)**: Convert, validate, lint, decode, preview, and dissemination-drawer
  flows remain **usable without login** (public APIs + abuse controls). **Optional Supabase Auth**
  login exists solely so operators can **keep long-term work history** on DO Postgres (F30/F31).
  Guests are warned in-UI that progress may be lost without login.
- **What it did (EV-017 — historical)**: Fully public — no login/signup UX; no Bearer JWT for
  operator flows; `/auth/*` retired; IndexedDB-only work history. **Superseded for Auth/sessions
  by EV-031 / F31** (optional Auth restored; convert remains public).
- **Acceptance (amended)**:
  1. Unauthenticated user completes convert → validate → download/send without login
  2. Optional `/auth/*` (or equivalent) for login/logout; JWT required only for **server session** APIs
  3. Logged-in work sessions live on DO Postgres — not Supabase DB
  4. Abuse-control + dissemination SSRF/allowlist unchanged in spirit
  5. Env/docs: Supabase **Auth** credentials for login path; product **DB** = DO `DATABASE_URL`
  6. E2E: public convert UJs plus login / guest-notice / privacy UJs (F31)
- **Out of scope**: Forced login for convert; CMP; selling personal data
- **S057 / EV-048 deepen (#951 — public OpenAPI / client error copy)**: Public OpenAPI
  path/operation summaries, parameter/schema `description` fields, runtime `/docs` / Redoc
  text, and client-facing `detail`/error messages must use operator-friendly language —
  no `[Corpus:…]`, ADR/session/EV IDs, product `FNN` ids, `docs/` paths, TC/E## planning
  IDs, or GitHub issue `#NNN` citations. Developer comments and test docstrings remain allowed.
- **Acceptance (EV-048 / #951 — F21 API slice)** — **approved** (`D-S057-01-ac=1`):
  1. Audit findings for OpenAPI + client-facing errors listed in the PR.
  2. OpenAPI export and error surfaces pass automated guard (TC-EV048-002/004/005).
  3. Soft-preview and related field descriptions preserve intent without ADR citations.
  4. Backend unit/OpenAPI snapshot tests updated.
- **Source**: #783; E17-*; **S038 / EV-031**; [Context: platform-independence-842](context/platform-independence-842.md);
  [#951](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/951) (S057 / EV-048)

### F22: Privacy Preference Center — S023 / EV-017

- **Status**: **Implemented** (S023 / EV-017 / #783; 11-verify-impl approved 2026-07-28); **deepen** S038 / EV-031 / F31.
- **What it does**: **Solution A** (no non-essential tracking). Inventory cookies/`localStorage`/
  `sessionStorage`/IndexedDB/CDN. Footer **Privacy settings** + short first-visit notice.
  One global preference schema (versioned); `necessary` always on; preferences/analytics/marketing
  default **false** and only shown if used. Honor **GPC**. Disclose IndexedDB work history.
  No CMP. Do not imply sale/share if the product does not sell personal information — still honor GPC.
- **F31 deepen**: Preference schema must gate **guest local work-history** persistence and disclose
  **Auth session cookies** when login is used; loss-of-progress notice must not bypass declined
  non-necessary storage (if guest history is classified non-necessary).
- **Acceptance**:
  1. Privacy settings reachable from footer; preferences persist and are withdrawable
  2. Non-essential scripts (if any later) blocked until allowed — v1 has none
  3. GPC detection forces sale/sharing opt-out flags when applicable
  4. Privacy/Cookie policy links with jurisdiction-aware language (engineering copy; counsel review OOS)
  5. UJ-033 + TC-F22-* cover notice + settings + GPC
  6. **F31**: TC/UJ cover privacy ↔ guest IndexedDB ↔ Auth cookie disclosure
- **Source**: #783; E17-7/E17-9; **S038 / EV-031 / F31**

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

### F29: Parameterized Rule Quality Matrices — S037 / EV-030

- **Status**: **Done** — shipped S037 / EV-030 (2026-08-03, PR #832).
- **What it does**: Adds a maintainable, **parameterized** regression harness so lint
  (`tac-validate`), convert (`tac2iwxxm`), and IWXXM-validate (`iwxxm-validate`) rules each
  have a fixed case budget: **5 happy · 5 sad · 5 edge-pass · 5 edge-fail** (or explicit
  `needs-fixture` inventory slots). Stable IDs (`RULE_ID/happy/03`). Design-before-bulk:
  evaluation answers (#831) land in a session design note before flooding fixtures.
- **Issues**: [#831](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/831) (priority-high)
- **Deepens**: **F12** / **F2** / **F13** / **F15** (and product bars) via shared runners —
  does not replace family quality packs; complements them.
- **API**: No new public routes required for v1 (offline pytest/CI). Optional later CLI.
- **Acceptance**:
  1. Written harness recommendation answering #831 evaluation questions (**TC-F29-001**)
  2. Runner(s) for lint + convert + validate with skip/`needs-fixture` policy (**TC-F29-002**)
  3. Pilot product set (recommend METAR/SPECI) has filled slots or explicit gaps (**TC-F29-003**)
  4. Inventory gate: in-scope rules have 20 slots or tracked TODO (**TC-F29-004**)
  5. Failures identify `rule_id` + bucket + case id in pytest node ids (**TC-F29-005**)
  6. CI: PR-smoke subset + optional full matrix; no network/Supabase (**TC-F29-006**)
  7. Authoring docs: how to add a case when adding/changing a rule (**TC-F29-007**)
- **Journeys / tests**: **UJ-044** (operator-invisible CI quality); **TC-F29-001..007**;
  cycle **TC-EV030-***
- **Out of scope**: Claiming 100% Annex-3 coverage in first PR; duplicating entire WMO trees
  ×20; coupling matrix to live network
- **S070 / EV-060 deepen (#1004)**: Conversion parameter `log_level` must set backend/package
  logger verbosity (not only client-echoed process-issue filter). DEBUG must not dump JWTs,
  passwords, or Authorization headers. UJ-063 / TC-EV060-1004-*.
- **Source**: E30-*; [evolve-decisions.md](decisions/evolve-decisions.md) §EV-030;
  [Context: quality-residuals-831](context/quality-residuals-831.md); #831

### F30: Platform Independence (Auth / DO DB / DOKS) — S038 / EV-031

- **Status**: **Done** (S038 / EV-031; `D-S038-13` = 1) — deepen S042 / EV-034 **completed**;
  S052 / EV-043 staging + dual CD ([#886](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/886));
  **deepen** S053 / EV-044 separate staging DOKS + DO Project (in progress).
- **What it does**: Splits platform lock-in under epic [#842](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/842):
  1. **Supabase Auth only** — JWT issue/verify for optional operator login (no product PostgREST / hosted Postgres app tables).
  2. **DigitalOcean Postgres** — all product DB including F8 store/quarantine and logged-in work sessions (`DATABASE_URL`).
  3. **DOKS production cutover** — API + worker + static from Render → DigitalOcean Kubernetes; decommission Render after soak ([#712](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/712)).
  4. Amend [#830](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/830): strip Supabase **data** plane; keep Auth.
  5. **CD auto-rollout (EV-034)**: On `main` Deploy after GHCR push, pin `metar-api` /
     `metar-frontend` / `metar-worker` to the immutable `TIMESTAMP-SHA` tag via kubectl
     (`KUBE_CONFIG` Actions secret). Render hooks optional/non-blocking.
  6. **Dual-env CD (EV-043 / #886)**: `stage` → staging auto-Deploy; promote `stage`→`main`
     only after Staging smoke green (`staging-gate`). Solo-dev: PR is the promote-to-`main`
     step (no Environment reviewers).
  7. **Dual DOKS + DO Projects (EV-044)**: Staging cluster + managed PG under DO Project
     **Staging TAC-to-IWXXM**; prod cluster + PG under **TAC-to-IWXXM**. Amends ADR-034
     (supersedes same-cluster two-namespace staging).
  8. **Tag-driven prod (EV-051 / S060)**: Push to `main` runs full CI **without** prod Deploy.
     Prod Deploy runs after full CI on `vYYYY.MM.DD-deploy` tag push (pattern `v*-*-deploy`)
     or optional `workflow_dispatch`. Deploy `needs` include `e2e-smoke`. Solo-dev “approval”
     = cutting the deploy tag (or dispatch).
- **Convert APIs**: Remain public (no JWT) for convert/lint/validate/disseminate (`D-S038-F30`).
- **Acceptance**:
  1. Product path boots/smokes without Supabase **database** credentials (**TC-F30-001**)
  2. Auth verify uses Supabase Auth only; no Supabase DB writes on default path (**TC-F30-002**)
  3. F8 persists via `DATABASE_URL` → DO Postgres (**TC-F30-003**)
  4. DOKS hosts API + worker + static; cutover runbook + H0–H5 against new endpoints (**TC-F30-004**)
  5. Render decommissioned after soak or residual ticket with checklist (**TC-F30-005**)
  6. Docs/CORPUS/env-contract no longer require Supabase as data plane (**TC-F30-006**)
  7. Prod CD rolls DOKS images to the immutable tag without manual kubectl when a deploy
     tag (or dispatch) runs (**TC-F30-007**)
  8. Staging DOKS + isolated DB/secrets on DO Project **Staging TAC-to-IWXXM**; prod on
     **TAC-to-IWXXM** (**TC-F30-008** / **TC-F30-008′**)
  9. Staging DNS + TLS for `api|app.staging.tac-to-iwxxm.com` → staging LB (**TC-F30-009**)
  10. `stage` auto-deploys staging after full CI; `main` push does **not** auto-deploy prod
      (**TC-F30-010** amended EV-051)
  11. Branch protection / rulesets: PR required on `stage` and `main` (**TC-F30-011**)
  12. PRs to `main` require head=`stage` + Staging smoke green (**TC-F30-012**)
  13. Shared-cluster staging namespace removed after dual-cluster cutover (**TC-F30-013**)
  14. Prod Deploy via `vYYYY.MM.DD-deploy` tag (or `workflow_dispatch`) after full CI incl.
      `e2e-smoke` (**TC-F30-014** / TC-EV051-*)
- **S067 / EV-057 deepen (#948 — apex → app redirect)**: Configure prod apex
  `https://tac-to-iwxxm.com` (and `www` when DNS/cert covers it) to permanently redirect to
  canonical `https://app.tac-to-iwxxm.com` via sibling Ingress **`metar-frontend-apex`**
  plus tiny nginx **`metar-apex-redirect`** (`D-S067-948-ingress=2a`,
  `D-S067-948-redirect=1a`). Preserve path + query. HTTP must end on HTTPS app URL.
  Document mechanism in [deploy.md](deploy.md). Staging short host
  `staging.tac-to-iwxxm.com` → `app.staging.tac-to-iwxxm.com` mirrors the same
  sibling-Ingress + redirect-pod pattern. No new Fn.
- **Acceptance (EV-057 / #948 — F30 deepen)** — **approved** (`D-S067-01-ac=1`):
  1. `https://tac-to-iwxxm.com` → `https://app.tac-to-iwxxm.com` (301 or equivalent).
  2. Path + query preserved.
  3. `www` included if DNS/cert covers it; HTTP→HTTPS app URL.
  4. TLS covers apex (and `www` if enabled).
  5. Deploy docs state prod FE Ingress extension; TC-EV057-948 / ops smoke.
- **Out of scope**: Convert/validate engine rewrites; App Platform; multi-reviewer Environment
  approvals (solo uses tag/dispatch); changing canonical app host away from `app.`
- **Source**: E31-*; E34-*; E43-*; E44-*; E51-*; E57-*; [Context: platform-independence-842](context/platform-independence-842.md); #842/#830/#712/#886/#948; S042 / EV-034; S052 / EV-043; S053 / EV-044; S060 / EV-051; S067 / EV-057

### F31: Hybrid Operator Sessions — S038 / EV-031

- **Status**: **Done** (S038 / EV-031; `D-S038-13` = 1) — T7.1 Playwright + 11/13 approved.
- **What it does**: Optional Supabase Auth for **long-term** work storage; guests stay on local/IndexedDB with a persistent **loss-of-progress** notice; privacy preference center (F22) gates local storage and discloses Auth cookies.
  - Logged-in: session CRUD on **DO Postgres** keyed by Supabase user id.
  - Guest→login: **auto-upload** all eligible local drafts (no prompt) (`D-S038-guest-merge`=2).
  - Amends **F21** (public convert + optional accounts), **F5** / **F7** storage, **F22** deepen.
- **Acceptance**:
  1. Guest converts without login; history local-only (**TC-F31-001**)
  2. UI notice when not logged in that progress may be lost (**TC-F31-002**)
  3. Login enables DO Postgres session APIs; JWT not required for convert (**TC-F31-003**)
  4. On login, local drafts auto-upload to server (**TC-F31-004**)
  5. F22 prefs gate guest IndexedDB / disclose Auth cookies (**TC-F31-005**)
  6. H4–H5 + UJs for notice, login, privacy interplay (**TC-F31-006**)
- **Out of scope**: Forced login for convert; CMP; selling personal data
- **Journeys / tests**: **UJ-045+** (assign in user-journeys delta); **TC-F30-*** / **TC-F31-***; **TC-EV031-***
- **S070 / EV-060 deepen (#1006)**: Auth/Register UAT — Playwright register, login, logout,
  session persist; guest convert still works. Facilitated `uat` Spec then Build. UJ-003 /
  UJ-046 / TC-EV060-1006-*.
- **Source**: E31-*; [Context: platform-independence-842](context/platform-independence-842.md)

### F23 / F12 / F2 / F13 deepen (S037 / EV-030 — #829 TC SIGMET)

- **Status**: **Planned** deepen (F23 remains **Done** for gen/VA/TC quality path from EV-029)
- **Issues**: [#829](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/829)
- **What it does**:
  1. Dedicated `tac-validate` TC SIGMET accept/negative pack (peer VA pack)
  2. STNR / exceptional geometry negatives beyond A6-2-TC happy path — or explicit OOS with cite
  3. Sample-menu / catalog tier decision for `sigmet-A6-2-TC` (UJ-039 / ADR-032)
- **Acceptance**: #829 checkboxes; **TC-EV030-829-***; H4–H5 only if FE menu unlock ships

### F9 / F26 / F27 deepen (S037 / EV-030 — #820 VAA/TCA decode)

- **Status**: **Planned** deepen (F9/F26/F27 remain **Done** for prior bars)
- **Issues**: [#820](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/820)
- **What it does**: Structured decode for major VAA/TCA field labels and forecast hours;
  shrink residual allowlist / update matrix tests toward `residuals == []` on official peers
  where feasible (F9 G4 best-effort intent preserved until closed).
- **Acceptance**: #820 checkboxes; **TC-EV030-820-***; deepen UJ-042

### F9 / F28 / F32 deepen (EV-099 — #1119 SWXA/VONA structured decode)

- **Status**: **Planned** deepen (F9/F28/F32 remain **Done** for prior bars)
- **Issues**: [#1119](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1119); related #740 / #741
- **Session**: `EV-099-f9-swxa-vona-structured-decode`
- **What it does**: Add **SWXA** and **VONA** to `decode_tac` `_SUPPORTED` with structured
  `LABEL:` field spans (mirror VAA/TCA EV-030). Ends whole-TAC residual on quality peers
  (`vona_a7_1`, `swxa_a7_3` / `_4` / `_5`) while convert annex3 peer XML stays **bit-identical**.
- **Residual policy (D-EV099-residuals)**: Prefer empty residuals on official peers; **explicit
  meaningful** leftover tokens may remain via exact allowlist rows (SIGMET-style). **Forbidden:**
  `allow_any` / single residual spanning the entire TAC body.
- **Acceptance**:
  1. Structured field segments for major SWXA/VONA labels on unlocked peers
  2. No whole-TAC residual; drop `allow_any` for `vona_a7_1` / `swxa_a7_3`
  3. Convert/XSD/SCH unchanged green for those stems
  4. Quality metrics UI/API reflects field-level residuals only
  5. **TC-EV099-*** + SWXA/VONA quality packs green
- **Out of scope**: Encode deepen (G-VONA-5 etc.); dissemination; FE redesign; CORS changes
- **Source**: [evolve-decisions.md](decisions/evolve-decisions.md) §EV-099; ADR-025 G4

### F32: VONA Quality Bar — S040 / EV-032

- **Status**: **Done** (M2 closed 2026-08-04; [#741](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/741) closed).
- **What it does**: Raises **VONA** (Volcano Observatory Notice for Aviation) TAC lint,
  convert, and IWXXM-validate quality to the F15–F28 product bar. Root
  `iwxxm:VolcanoObservatoryNoticeForAviation`. **WMO `TAC-to-XML-Guidance.txt` has no VONA
  section** — this is a **non-blocking upstream documentation gap** (S045 / EV-037 / #869),
  not an undefined conversion. Encode SoT hierarchy:
  1. ICAO PANS-MET / applicable ICAO provisions
  2. WMO FM 205 + IWXXM 2025-2 model (package `1.0.0`, `vona.xsd`)
  3. WMO `vona.xsd`, `iwxxm.sch`, code lists
  4. WMO aviation AHL (`WM`→`LM`)
  5. Official `vona-A7-1.xml` example (fixture, not sole SoT)
  6. Project cookbook — **derived** implementation guide only
  Model volcano/ash as `MeteorologicalFeature` objects; colour codes via
  `AviationColourCode` vocabulary; bounding period/volume/phenomena per XSD.
  Reuses **ADR-028** registry + **ADR-032** golden policy. Catalog `vona_a7_1` → **`wmoPass`**.
- **Issues**: [#741](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/741) closed; parent epic [#846](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/846);
  Guidance silence tracker [#869](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/869) (S045 disposition).
- Deepen children: G-VONA-1 (vertical extent) [#849](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/849),
  G-VONA-5 (resuspended ash) [#850](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/850) — under #846.
- **Deepens**: **F6** (VONA encode plugin), **F12** (VONA checklist), **F2/F13** (XSD+SCH),
  **F7** full product surface (picker + Examples unlocked), **F9** best-effort decode.
- **API**: Additive wire value **`product=vona`** on convert / convert-bulletin / lint-tac /
  decode-tac ([api-contract.md](api-contract.md) §S040 / EV-032). Keep-whole multiline
  `manual_text` (peer VAA/TCA/SWXA).
- **Acceptance**:
  1. ✅ Registry-backed VONA lint codes; CI fails on unknown codes (**TC-F32-001**)
  2. ✅ Encode path from XSD+SCH+`vona-A7-1` (+ PANS-MET); guidance-silent gaps documented
     (**TC-F32-002**)
  3. ✅ `MeteorologicalFeature` volcano/ash + bounding period/volume/phenomena; colour codes via
     correct `AviationColourCode` list (**TC-F32-003**)
  4. ✅ Accept + negative fixtures; convert → XSD+Schematron; golden equality when vendor peer
     exists under defaults (**TC-F32-004** / ADR-032)
  5. ✅ Coverage-matrix VONA / F32 themes updated; guidance gaps filed or closed (**T2.9**)
  6. ✅ **Full F7 surface**: product picker + workbench path; Examples list VONA passers
     unlocked (**UJ-049** / **TC-F32-005**); H4–H5 at deploy
  7. ✅ API/runtime accept `product=vona` (unknown → `unknown_product` 400) (**TC-F32-006**)
- **Journeys / tests**: **UJ-049**; **TC-F32-001..006**; cycle **TC-EV032-***;
  closeout [t2.9-741-closeout.md](sessions/S040-iwxxm-corpus-quality/reports/t2.9-741-closeout.md)
- **Out of scope**: Metrics UI #836; SIGWX / QVACI; hand-edit `vendor/schemas/*`; treating
  guidance-file runway-state rules as normative for other products
- **Source**: E32-*; [evolve-decisions.md](decisions/evolve-decisions.md) §EV-032;
  [Context: iwxxm-corpus-quality-846](context/iwxxm-corpus-quality-846.md); #741; ADR-028;
  ADR-032; `docs/domain/rules/COVERAGE_MATRIX.md`

### F32 deepen (S045 / EV-037 — VONA SoT / Guidance silence)

- **Status note**: F32 remains **Done**; dispose [#869](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/869)
  as non-blocking upstream Guidance silence with explicit SoT hierarchy (cookbook = derived).
- **Acceptance (EV-037 shared — #869 / #870 / #872)**:
  1. VONA conversion cell + provenance: Guidance silence ⚠ non-blocking; SoT hierarchy
     documented; cookbook labeled derived; `VONA_GUIDANCE_SILENT` disposition updated
     (**TC-EV037-001**)
  2. IWXXM-US validate classes split; official US Schematron = **N/A**; `US_SCH_ABSENT`
     (**TC-EV037-002**)
  3. Eight-family Bulletin AHL: every mapped family `AHL source = ✅`; impl columns separate;
     #872 closeable when children exist only for true parser/splitter/fixture/CI gaps
     (**TC-EV037-003**)
  4. GitHub #869/#870/#872 closed or reworded per dispositions; epic #846 linked
     (**TC-EV037-004**)
- **Journeys / tests**: No new UJ (no UI); **TC-EV037-001..004**; prior **TC-F32-*** /
  **TC-EV035-*** remain
- **Out of scope**: Editing upstream `TAC-to-XML-Guidance.txt`; inventing US Schematron;
  full AHL impl packs beyond matrix redesign
- **Source**: E37-*; [evolve-decisions.md](decisions/evolve-decisions.md) §EV-037;
  [Context: matrix-disposition-residuals](context/matrix-disposition-residuals.md); #869/#870/#872

### F33: Secure mass file/folder ingest — S050 / EV-042

- **Status**: **Implemented** (S050 / EV-042; 11-verify-impl approved 2026-08-07).
- **What it does**: Authenticated operators ingest **many** TAC (and related text) files via
  multi-select and **folder/zip** upload, with progress and per-file errors, then feed the
  existing convert → lint → validate path (**no** operator dissemination destinations this
  cycle — F16–F19 UI hidden). Server enforces size/count/MIME caps, rejects
  binaries/executables, and applies **content sniff + zip-bomb guards**.
- **Caps (R1)**: ≤**200** files / request; ≤**5 MiB** / file; ≤**50 MiB** total unzipped.
- **Auth (R3)**: JWT required for folder/zip mass path; guests may keep existing small
  multi-file upload behavior.
- **Issues**: Parent epic [#897](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/897);
  restore destinations [#898](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/898).
- **Deepens / companions**: **F7** (queue + batch convert/validate), **F16–F19** (UI-hide
  all sinks; API retained for harness).
- **Acceptance**:
  1. Auth-gated folder/zip mass ingest with progress + per-file errors (**TC-F33-001**, **UJ-051**)
  2. Caps enforced: 200 files / 5 MiB each / 50 MiB total unzipped (**TC-F33-002**)
  3. Binary/executable + content-sniff rejects; zip-bomb / nested-zip abuse rejected (**TC-F33-003**)
  4. Unauthenticated mass path → clear 401/403; guest small multi-file unchanged if previously allowed (**TC-F33-004**)
  5. Ingested items enter workbench queue for convert/validate churn (**TC-F33-005**, **UJ-052**)
  6. H4–H5 connectivity for new browser→API mass ingest calls (**TC-F33-006**)
- **Out of scope**: Restoring F16–F19 destinations (#898); connector spike (#896);
  `DatabaseUploadDialog`; F8 auto-push; operator dissemination send; weakening SSRF allowlist.
- **Source**: E42-*; [evolve-decisions.md](decisions/evolve-decisions.md) §EV-042;
  [Context: remove-db-tools-operator-throughput](context/remove-db-tools-operator-throughput.md);
  #897; ADR-029 / ADR-030

### F34: Contract + mutation quality gates — S069 / EV-059

- **Status**: **Planned** (S069 / EV-059; Spec-development).
- **What it does**: Adds developer/CI quality gates that complement line coverage:
  1. **Schemathesis** property-based suite against `apps/backend` OpenAPI (ASGI) — no unexpected
     5xx; response schema conformance; auth strategy so protected routes are exercised.
  2. **Mutation testing** — **pytest-gremlins** (Python) + **Stryker** (TypeScript) across
     packages/services, run as **nightly / `workflow_dispatch`** (not every PR).
- **Issues**: Epic [#841](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/841);
  [#727](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/727) (Schemathesis);
  [#874](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/874) (mutation).
- **CI posture** (`D-S069-ci`): Schemathesis = **path-filtered required** on
  `apps/backend/**` / OpenAPI-related paths with **Hypothesis max-examples ≤ 25** and job
  timeout ≤ **10 min**. Mutation = **nightly/manual only**, chunked matrix + hard timeouts.
- **PRs**: Two separate PRs (do not bundle #727 + #874). Target `stage`; promote held.
- **Acceptance** (`D-S069-01-ac=2b`):
  1. Schemathesis loads OpenAPI from backend ASGI; auth strategy exercises protected routes
     (**TC-F34-001**)
  2. `make test-schemathesis` + path-filtered required CI within budget ceilings (**TC-F34-002**,
     **TC-F34-007**)
  3. pytest-gremlins + Stryker configs + `make` targets; nightly/manual matrix covers Python
     packages/services + TS surfaces (**TC-F34-003**, **TC-F34-004**, **TC-F34-005**)
  4. Deps listed in [dependency-inventory.md](dependency-inventory.md); notes in
     [test-plan.md](test-plan.md) (**TC-F34-006**)
  5. Findings: product/schema bugs fixed (bug-investigation) or survivors/waivers documented
     (**TC-F34-006**)
  6. Two PRs land; epic #841 closable when #727 and #874 Done (**TC-F34-006**)
  7. Documented Hypothesis `max-examples` ≤ 25 and Schemathesis job timeout ≤ 10 min in
     test-plan (**TC-F34-007**)
- **Mutation matrix (Python)**: `apps/backend`, `apps/worker`,
  `packages/{auth,shared,tac-validate,tac2iwxxm,iwxxm-validate,dissemination}`
- **Mutation matrix (TS)**: `apps/frontend` (+ `packages/shared` JS if present)
- **Excluded**: `apps/e2e` Playwright; Rust crate mutation (first pass)
- **Journeys / tests**: No new UJ (dev/CI only); **TC-F34-001..007**; cycle **TC-EV059-***
- **Out of scope**: Mutation required on every PR; Rust mutation; live staging/prod Schemathesis
  as merge gate; product UI; weaken coverage ≥95%; promote `stage`→`main`; replace hand-written
  UJ/pytest with Schemathesis alone
- **OpenAPI**: Breaking cleanup **allowed** when Schemathesis proves export wrong (`D-S069-e5`)
- **S071 / EV-061 deepen (#1015)**: PRs **`stage` → `main`** require a stricter merge gate than
  Staging gate alone: **full CI** (unit suites), **lint**, **typecheck**, and **full E2E**
  (not smoke-only) as required status checks before merge. Documented in deploy.md; GitHub
  branch protection / required checks as needed. No new app secrets. UJ-DEV-009 (doc/CI).
- **Source**: E0–E8 / 01 intake; [evolve-decisions.md](decisions/evolve-decisions.md) §EV-059;
  #841 / #727 / #874; [Corpus: tests] [Corpus: tech-spec] [Corpus: api]; S071 / EV-061 #1015

### F35: Semantic vs exchange profiles + canonical ID migration — EV-063 / #912

- **Status**: **Implemented** (EV-063 / PR [#1026](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/1026); ADR-036 Accepted).
- **What it does**: Splits F6 **semantic** profile selection (TAC→IWXXM) from **exchange**
  profile selection (post-convert packaging). Introduces canonical ids `ICAO_2025` and
  `US_FAA_NWS` with legacy aliases `annex3` / `iwxxm_us` during a deprecation window ending
  **2026-10-31** ([#1025](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1025)). Nested wire
  shape: `conversion.semanticProfile`, `conversion.iwxxmVersion`, `conversion.extensions`,
  `exchange.profile` (default `GLOBAL_AFS` when packaging invoked).
- **Issues**: Epic [#912](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/912);
  architecture [#914](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/914); cutover
  [#1025](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1025).
- **Amends**: F6 convert/validate wire; [Corpus: api]; ADR-013 profile plugin naming (follow-up
  when Build lands).
- **Must-not-break**: annex3 / iwxxm_us golden parity during alias window; F16–F19 credential /
  allowlist unchanged; convert-only path must not pay exchange packaging latency.
- **Acceptance (Spec close)**:
  1. ADR-036 accepted; api-contract + env-contract deltas merged
  2. #913 mine catalog published under [Corpus: domain-profiles]
  3. Unknown semantic/exchange id → 400 documented (`invalid_profile` or successor)
  4. Deprecation signal documented for alias ids
- **Acceptance (Build — after gate)**:
  1. Runtime accepts canonical + alias ids; metrics for profile id + alias counters
  2. E2E convert → package with `exchange.profile=GLOBAL_AFS` (no live sinks in CI)
  3. Config flag `PROFILE_WIRE_V2` gates nested wire default
- **Out of scope**: Full #933 editor; #908 cross-version; baking destinations into profiles
- **Source**: EV-063 intake; [ADR-036](adr/ADR-036-semantic-vs-exchange-profiles.md);
  [domain/profiles/README.md](domain/profiles/README.md)

### F36: National semantic + regional exchange profile content — EV-063 / #912

- **Status**: **In progress** (EV-064 CA_ECCC P1 merged; **EV-098** CA_ECCC deep mining [#1028](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1028)–[#1031](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1031); EV-065/086/090 #921 exchange stubs + mining; **EV-087** `AU_BOM` + `NZ_CAA_MET`; **EV-089** thin/compat #920; **EV-090** exchange light picker; **EV-093** #1024 semantic picker deepen; **EV-094** thin/compat deepen [#1098](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1098)).
- **What it does**: Implements profile **content** on top of F35 architecture: deepen
  `US_FAA_NWS` ([#919](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/919)), **`CA_ECCC`**
  ([#916](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/916) / EV-064), **`AU_BOM`**
  ([#917](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/917) / EV-087), **`NZ_CAA_MET`**
  ([#918](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/918) / EV-087), thin/compat nationals
  ([#920](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/920) / EV-089), regional exchange
  overlays ([#921](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/921)) as capacity allows.
  Data-driven rules mined from authoritative sources (#913 / parallel MANOBS/MANAIR notes).
- **Priority spine**: #913 → #914 → #919 → #916 → #921 → **#917 / #918** (EV-087) → **#920** (EV-089 thin path; UK first).
- **Fixture layout**: `profiles/<id>/<product>/{valid,invalid,expected-*}` with first heavy
  national profile.
- **Acceptance (Spec close)**:
  1. ≥1 P1 national issue (#916) **In Progress** with fixtures started
  2. #913 catalog row per targeted profile id in [Corpus: domain-profiles]
- **Acceptance (Build)**:
  1. `US_FAA_NWS` deepened per #919 scope — **closed EV-085** (RMK M7, SIGMET/AIRMET M8–M19, TAF lint M13, SWXA/TCA thin M22; M14 alias waived)
  2. `CA_ECCC` — EV-064 / #916: vendor `iwxxm-ca` + IWXXM 3.0.0 pin; METAR/SPECI/TAF/AIRMET
     convert + validate paths; API + FE picker; fixtures under `profiles/CA_ECCC/`
  3. One exchange overlay path (`GLOBAL_AFS` minimum) exercised in packaging tests — **EV-065**: `APAC_ROBEX` P0 stub added
  4. **EV-074 / #1043:** CA_ECCC SIGMET **validate-first** ops corpus (≥2 SIGMET IWXXM) against WMO 3.0.0; `ca_xsd` skipped N/A; no TAC convert
  5. **EV-075 / #1032:** Umbrella closeout verified — aerodrome exchange output + COLLECT + ops met
  6. **EV-076 / #1061:** SIGMET exchange output emit closed on `stage`
  7. **EV-077:** VAA validate-first via Montreal VAAC TAC (`D-EV074-vaa-waiver-tac`); +2 AIRMET ops fixtures
  8. **EV-078 / #916:** P1 closeout verified — VAA exchange *emit* waived (`D-EV074-vaa-follow`); re-harvest when VAAC publishes ≥2
  9. **EV-079 / #919 M8:** US SIGMET/AIRMET phenomenon tokens + fixtures
  10. **EV-080 / #919 M9:** VOR reference geometry parser + fixtures
  11. **EV-081 / #919 M10–M13:** weather-hazard emit, convective SIGMET (WST), structured VIS verify, US TAF lint
  12. **EV-082 / #919 M15–M16:** AIRMET outlook (`OTLK VALID`) + multi-area sub-periods
  13. **EV-083 / #919 M17–M18:** CONUS `UPDT` header + FRZLVL `FreezingLevelForecast`
  14. **EV-084 / #919 M19:** WAUS multi-section AIRMET bulletin (ICE + OTLK + FRZLVL + VOR FROM)
  15. **EV-085 / #919 closeout:** acceptance audit (M20), SWXA/TCA thin US lint (M22); #919 closed with M14 + §12.7.2 additive RMK waivers
  16. **EV-086 / #921:** `EUR_RODEX`, `AFI`, `CAR_SAM` exchange stubs — registry + GLOBAL_AFS COLLECT baseline + catalog stubs + TC-EV086 (APAC_ROBEX P0 pattern); #921 stays open for #898 drawer + #913 mining deepen
  17. **EV-087 / #917+#918:** `AU_BOM` + `NZ_CAA_MET` P1 kickoff — catalog P1, semantic stubs, mining notes; INTER emit = `TEMPORARY_FLUCTUATIONS` + provenance (D-EV087-inter-emit); TAF3 as RMK flag; NZ domestic extras → IR + remarks; core IWXXM only (no national XSD); TC-EV087-*
  18. **EV-088 / #1044:** National profile **onboarding playbook** + `_template/` stubs + scaffold
     script (engineering enablement) — thin vs full paths; A–P ↔ CA reference map; no #920/#921
     feature content that cycle
  19. **EV-089 / #920:** Thin/compat packs `UK_METOFFICE`, `BR_DECEA`, `KR_KMA`, `JP_JMA`,
     `IN_IMD`, `HK_HKO` — catalog + semantic stubs + mining notes + fixtures + registry
     (EV-088 thin path); ship UK first; GAMET **parse-only** (no IWXXM emit); no national XSD invent;
     SAM packaging deepen stays #921
  20. **EV-090 / #921+#913+#1024:** Exchange mining promote (catalog/stubs/PROVENANCE from existing
     notes; ROBEX handbook durable URL still gap if unpinned) + workbench **Exchange profile**
     light picker (default `GLOBAL_AFS`; wire `exchange_profile` on package/bulletin paths;
     ignored on convert-only). Close #921 on land; spawn child for #898 drawer overlay selector.
     No new COLLECT/FTBP packaging rules this cycle.
  21. **EV-093 / #1024:** Semantic Profile light picker deepen — canonical uppercase
     `semantic_profile` wire (`ICAO_2025`, `US_FAA_NWS`, `CA_ECCC`, `AU_BOM`, `NZ_CAA_MET`,
     thin packs); legacy `annex3`/`iwxxm_us` alias options through #1025 window; Profile trust
     copy via compact bar layout (icons/tooltips + under-bar summary + collapsed details);
     local UI preview; close #1024 on land (exchange picker already EV-090/091).
  22. **EV-094 / #1098:** Deepen thin/compat packs (post-#920) — attributed real TAC corpora;
     durable catalog/mining URLs; **SPECI** on `KR_KMA` + `JP_JMA`; **`in_imd` lint overlay**
     for TAF TX/TN omission awareness (convert stays core IWXXM); GAMET parse-only reaffirm;
     UK-first PRs; catalog `status: implemented` for six packs; **close #1098** on land
     (**do not reopen #920**).
  23. **EV-098 / #1028–#1031:** CA_ECCC deep mining — datamart triage (#1028); MSC `doc/` PDFs
     (#1031); MANOBS P0 TAC rules + fixtures (#1029); MANAIR TAF/AIRMET/GFA (#1030). Research via
     deep-research-domain-handoff (EV-097); promote via mine-domain-sources after gate C.
     No UI; no SIGMET national / VAA convert this cycle. **TC-EV098-***.
- **Out of scope**: Full ROBEX/RODEX packaging rule matrices beyond documented gaps; national VAA/VONA **convert** forks (EV-074 is **validate-first** CA SIGMET/VAA ops, not a national VAA schema fork); **M14** alias cutover [#1025](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1025); inventing national IWXXM enums/XSDs; China unless public sources appear; GAMET→IWXXM conversion; #933 ConversionProfile editor
- **Related UI**: Light picker [#1024](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1024) —
  semantic (**EV-093** canonical + nationals) + **exchange** control (EV-090 / drawer EV-091)
- **Enablement**: [NATIONAL_PROFILE_PLAYBOOK.md](domain/profiles/NATIONAL_PROFILE_PLAYBOOK.md)
- **Source**: Epic [#912](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/912); EV-063; EV-064;
  [Corpus: domain-profiles]

### F7 / F16–F19 deepen (S050 / EV-042 — #897 destinations UI hide + churn)

- **Status note**: F16–F19 remain **Done** (engines/APIs). EV-042 temporarily hid operator
  destinations; **EV-091 / #898** restores Convert&Send, Disseminate drawer, and Upload to
  Database (URI-BYOC). **#1089** adds drawer exchange overlay (parity with EV-090 workbench picker).
- **Acceptance (EV-042 historical)**: destinations hidden (**UJ-053**, **TC-EV042-001**); harness API retained (**TC-EV042-002**); queue/batch churn (**UJ-052**, **TC-EV042-003..004**)
- **Acceptance (EV-091 restore)**: destinations visible (**TC-EV091-001**); drawer exchange overlay on convert-before-send (**TC-EV091-002**); UJ-027–030 operator UI; connection-first preflight retained
- **Journeys / tests**: **UJ-027–030**, **UJ-051..053** (UJ-053 inverted by EV-091); **TC-F33-***; **TC-EV042-***; **TC-EV091-***
- **Out of scope**: #896 connector; soft-deleting `packages/dissemination` adapters
- **Source**: #897; #898; #1089; evolve-decisions §EV-042 / §EV-091

### F23 deepen (S040 / EV-032 — #835 A6-2-TC → wmoPass)

- **Status**: **Done** (M1 closed 2026-08-04; F23 remains **Done** for gen/VA/TC quality path)
- **Issues**: [#835](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/835) closed; parent [#846](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/846)
- **What it does**: Closed ADR-032 `canonicalize_xml` equality vs vendor `sigmet-A6-2-TC.xml`
  under default pin; promoted catalog `sigmet_a6_2_tc` → **`wmoPass`**; FIXTURE_GAPS /
  inventory notes updated. Encode deltas: coordinate formatting, airspace type `FIR`,
  omit `intensityChange` on `NO_CHANGE`, forecast-centre trailing zeros.
- **Acceptance**: #835 checkboxes; **TC-EV032-002** / **TC-EV032-003**; deepen UJ-039;
  path-filtered canary + `make test-tc-sigmet-quality` (E32-T7 / T1.5)
- **Closeout**: [t1.6-835-closeout.md](sessions/S040-iwxxm-corpus-quality/reports/t1.6-835-closeout.md)

### F4 / F6 / F2 / F13 deepen (S040 / EV-032 — #808 release-line adoptability)

- **Status**: **Done** (M3 closed 2026-08-04; [#808](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/808) closed).
- **Issues**: [#808](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/808) closed; companion [#847](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/847) closed; parent [#846](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/846).
  Automation/UX children: #851–#855.
- **What it does**: Written maintainability assessment + adopt/deprecate checklists aligned with
  `docs/domain/iwxxm/VERSION_SUPPORT_POLICY.md`; blast-radius map across convert / validate /
  vendor / UI / PyPI; **keep latest+1** recommendation; staff guide for non-engineers.
- **Acceptance**: #808 AC1–5; **TC-EV032-004**; no engine rewrite / no re-pin
- **Durable docs**: [RELEASE_LINE_ADOPTABILITY.md](domain/iwxxm/RELEASE_LINE_ADOPTABILITY.md) ·
  [RELEASE_LINE_STAFF_GUIDE.md](domain/iwxxm/RELEASE_LINE_STAFF_GUIDE.md)
- **Closeout**: [t3.3-808-847-closeout.md](sessions/S040-iwxxm-corpus-quality/reports/t3.3-808-847-closeout.md)

### Corpus / WMO-source parity (S040 / EV-032 — #846)

- **Status**: **In progress** — core children closed (S040); matrix residuals closed (S045);
  remaining **#849–#861** under S046 / EV-038
- **What it does**: Continuous good results vs official IWXXM corpus and related WMO sources
  (wmo-im/iwxxm, iwxxm-translation, iwxxm-codelists, codes.wmo.int, iwxxm-modelling). File
  child issues for concrete gaps; index durable stance in domain/session docs.
- **Acceptance**: **TC-EV032-005**; children linked from #846; deepen UJ-039 / UJ-042 /
  UJ-045 as applicable; **TC-EV038-001..014** for residual closeout
- **Children (T4.1)**: #849–#861 (see [t4.1-846-children.md](sessions/S040-iwxxm-corpus-quality/reports/t4.1-846-children.md))
- **XML-only OOS (corpus G5 / #858)**: **WAFS / QVACI / SIGWX** — durable row in
  [COVERAGE_MATRIX.md](domain/rules/COVERAGE_MATRIX.md) §XML-only products; not F6 convert
- **Out of scope**: Metrics UI #836; re-doing closed mining #804/#807 as primary deliverable;
  WAFS/QVACI/SIGWX TAC→IWXXM encode (see G5 table)

### F2 / F4 / F6 / F7 / F32 deepen (S046 / EV-038 — #846 residuals #849–#861)

- **Status**: **In progress** (S046 / EV-038) — deepen only; **no new Fn**
- **Epic**: [#846](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/846)
- **Milestones** (`D-S046-mplan`):
  | M | Issues | Theme |
  |---|--------|-------|
  | M1 | #858, #861, #855 | Docs / process (G5 OOS, G8 watch, deprecation template) |
  | M2 | #851–#854 | Release-line SoT, tip-diff, iwxxm-us gate, picker Latest/Previous |
  | M3 | #859, #860, #857 | Codes drift, translation-failed, SWXA A7-4/A7-5 |
  | M4 | #849, #850, #856 | VONA deepen + VA-EGGX `wmoPass` |
- **Acceptance**: AC1–AC14 in
  [01-requirements-summary.md](sessions/S046-iwxxm-corpus-residuals/reports/01-requirements-summary.md);
  **TC-EV038-001..014**
- **UI**: #854 — local non-deployed preview at M2 (`D-S046-mplan` Q2=1); H4–H5 at deploy
- **SoT (#851)**: Python `iwxxm_versions.py` → generated committed JSON (roles
  `latest`/`previous`) → FE + OpenAPI/CI (`D-S046-sot`=1)
- **US gate (#853)**: `make iwxxm-us-compat-smoke` + lag policy **D-S046-853** (ship
  WMO-only first); see RELEASE_LINE_ADOPTABILITY §iwxxm-us lag policy
- **Journeys / tests**: **UJ-050** (version picker Latest/Previous); **TC-EV038-001..014**;
  prior **TC-EV032-*** / **TC-F32-***
- **Execution plan**: [execution-plan.md](sessions/S046-iwxxm-corpus-residuals/reports/execution-plan.md)
- **Out of scope**: Metrics UI #836; workbench epic #840 unless tiny catalog-tier;
  hand-edit `vendor/schemas/*`; re-pin as primary goal
- **Corpus**: `[Corpus: product]` · `[Corpus: tech-spec]` · `[Corpus: api]` ·
  `[Corpus: tests]` · `[Corpus: decisions]` ·
  `[docs/domain/iwxxm/RELEASE_LINE_ADOPTABILITY.md]` ·
  `[docs/domain/rules/COVERAGE_MATRIX.md]`

### F6 / F12 / F15 / F20 / F23 / F24 / F26 / F27 / F28 / F32 deepen (S055 / EV-046 — #889)

- **Status note**: Quality bars remain **Done** / F6–F12 **Implemented**; this **Lean** cycle
  does **not** add a new Fn. Standing deliverable: present → cite → cover (+ gap report) for
  aviation `codes.wmo.int` registers across **all supported F6 products**; **Validated** triad
  element **waived** for Lean close with a Standard follow-on child (`D-S055-validated=1`).
- **Issue**: [#889](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/889) · epic
  [#846](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/846) · compose
  [#859](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/859) / [#882](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/882)
- **What changes**:
  1. Priority-register inventory vs vendor SoT + dual/404/obsolete dispositions
  2. Stable concept URI citations in RULE_SOURCE_URLS / mining / COVERAGE_MATRIX and
     ISSUE_CATALOG / PROVENANCE_MAP where notations already claim codes.wmo.int
  3. Per-product-family coverage % of register members exercised by TAC fixtures +
     exclusions with cite + reason
  4. Gap backlog children or explicit deferrals; document Validated waiver + follow-on
- **Acceptance**: AC1–AC6 in [evolve-decisions.md](decisions/evolve-decisions.md) §EV-046;
  **TC-EV046-001..006**
- **Out of scope**: Live HTML in PR CI; vendor hand-edits; #882 notify; standing harvest +
  `tac-validate` membership asserts (Standard follow-on)
- **Journeys / UI**: N/A (docs/coverage)
- **Corpus**: `[Corpus: product]` · `[Corpus: tests]` · `[Corpus: decisions]` ·
  `[docs/domain/rules/RULE_SOURCE_URLS.md]` · `[docs/domain/rules/COVERAGE_MATRIX.md]` ·
  `[docs/domain/mining/codes-wmo-int-aviation-mining-notes.md]`
- **Follow-on**: [#959](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/959) / S059 / EV-050
  (Validated — below)

### F6 / F12 / F15 / F20 / F23 / F24 / F28 deepen (S059 / EV-050 — #959 Validated)

- **Status note**: No new Fn. Standard follow-on to EV-046 Lean: standing **offline harvest** +
  `tac-validate` membership CI for the Validated triad element; aggressive fixture expansion
  for EV-046 gap rows (`D-S059-fixtures=2c`); **profile compare** `annex3` vs `iwxxm_us`
  with true-error fixes (AC7–AC8).
- **Issue**: [#959](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/959) · parent
  [#889](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/889) · epic
  [#846](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/846) · compose
  [#859](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/859) / [#882](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/882)
- **What changes**:
  1. Offline harvest from `vendor/schemas/iwxxm-codelists` (+ pin RDF) → membership sets
  2. Wire `tac-validate` / matrix: happy + unknown/sad for weather, recent, cloud,
     SIGMET/AIRMET phenomena, nilReason where lint already touches URIs
  3. Document harvest cadence vs `vendor/manifest.json` `iwxxm-codelists` pin
  4. Aggressive fixtures: `RE*`, AIRMET `_` phenomena, SpaceWxPhenomena, TCU
  5. Design-only #882 compose note (no scheduled live job this cycle)
  6. **Compare** membership/lint under `profile=annex3` vs `profile=iwxxm_us` for **all F6
     products** (`iwxxm_us` **N/A** where unsupported); classify shared / intentional L5 /
     true error; **fix true errors** this cycle with regressions
- **Acceptance**: AC1–AC8 in [evolve-decisions.md](decisions/evolve-decisions.md) §EV-050;
  **TC-EV050-001..008**
- **Out of scope**: Live HTML in PR CI; vendor hand-edits; full #882 notify; `iwxxm-validate`
  replacement; `stage`→`main` promote; exhaustive 402 weather combos; country scorecards
  beyond the two profiles; inventing US tokens outside FMH-1 / NWS / iwxxm-us
- **Journeys / UI**: N/A
- **Corpus**: `[Corpus: product]` · `[Corpus: tests]` · `[Corpus: tech-spec]` ·
  `[Corpus: decisions]` · `[docs/domain/TAC_VALIDATION.md]` ·
  `[docs/domain/rules/COVERAGE_MATRIX.md]`

### F29 / F6 / F21 / F30 / M5 deepen (S061 / EV-052 — #950 + #900 + quality PR stats)

- **Status note**: No new Fn. CI polish: restore **≥95% coverage gates** (#950); second
  sticky **PR comment** with golden/quality-matrix outcomes by product × profile; free-tier
  **Sentry** + **Upstash Redis** for shared slowapi limits + OpenAPI→typed FE client (#900).
- **Issues**: [#950](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/950) ·
  [#900](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/900) · epic
  [#841](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/841)
- **What changes**:
  1. Inventory + enforce ADR-007 **≥95%** on every package/app coverage surface; fill tests
  2. CI job: quality-matrix + annex3/`iwxxm_us` golden outcome summary → sticky PR comment
     (marker ≠ EV-036 coverage comment)
  3. Sentry SDK (API + FE + worker) behind DSN env; Developer free tier
  4. Upstash Redis (`REDIS_URL` or approved Upstash env) as slowapi shared store — **no**
     new DOKS Redis Deployment (`D-S061-redis=1`)
  5. `openapi-typescript` FE types from committed OpenAPI snapshot (`make openapi-refresh`;
     `pnpm openapi:check` drift gate) — locked `D-S061-orval=1` (not full Orval)
- **Acceptance**: AC1–AC12 in [evolve-decisions.md](decisions/evolve-decisions.md) §EV-052;
  **TC-EV052-001..012**
- **Out of scope**: Paid Sentry/Valkey; in-cluster Redis service; #874/#727/#836; AMS #958;
  stage→main promote this cycle
- **Journeys / UI**: N/A (codegen only; no new operator UJ)
- **Corpus**: `[Corpus: product]` · `[Corpus: tests]` · `[Corpus: tech-spec]` ·
  `[Corpus: deploy]` · `[Corpus: adr/ADR-007]` · `[Corpus: adr/ADR-006]` ·
  `[Corpus: adr/ADR-031]` · `[Corpus: decisions]`
- **Infra**: `docs/sessions/S061-ci-polish-quality-pr-stats/reports/infra-free-tier.md`

### F29 / M5 deepen (S062 / EV-053 — Vitest branches ≥95 / #968)

- **Status note**: No new Fn. Close EV-052 Vitest **branches** waiver
  (`D-S061-cov-branches=3`): raise frontend `branches` to **≥95**, re-include
  `FileConverter.tsx` in Vitest coverage, and require FileConverter itself ≥95% branches.
- **Issues**: [#968](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/968) (child of
  [#950](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/950) / EV-052)
- **What changes**:
  1. Remove `FileConverter.tsx` from Vitest coverage `exclude`; set `branches: 95`
  2. Fill FileConverter-heavy branch (and line) tests until aggregate + FileConverter ≥95
  3. Resolve coverage inventory `branch_waiver`; cite closeout in decisions / test-plan
- **Acceptance**: AC1–AC5 in [evolve-decisions.md](decisions/evolve-decisions.md) §EV-053;
  **TC-EV053-001..005** (`D-S062-01-ac=1`)
- **Out of scope**: Lowering other thresholds; #874/#727/#836; stage→main; UI redesign
- **Journeys / UI**: N/A (CI / Vitest only; `D-S062-ui-preview=2`)
- **Corpus**: `[Corpus: product]` · `[Corpus: tests]` · `[Corpus: adr/ADR-007]` ·
  `[Corpus: decisions §EV-052]` · `[Corpus: decisions §EV-053]`

### M5 deepen (EV-080 / #1077 — Universal 100% unit coverage gate)

- **Status note**: No new Fn. Raise ADR-007 from ≥95% to **100%** line+branch for all
  Python apps/packages, Vitest unit surfaces, and repo scripts (Python coverage +
  **bats-core** for every `scripts/**/*.sh`).
- **Issues**: [#1077](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1077)
- **What changes**:
  1. Inventory all coverage surfaces @ `target_floor: 100`; approved omits only
     (vendor / generated / fixtures)
  2. Python `fail_under` + per-file `--min-pct 100`; remove `__init__.py` omit; fill tests
  3. Vitest FE + shared thresholds **100**; remove executable coverage excludes; fill tests
  4. Scripts: dedicated Python cov job + bats-core suite covering every `.sh`
  5. Amend ADR-007 / typing-policy / test-plan; sticky PR coverage floors 100
- **Acceptance**: AC1–AC6 in [evolve-decisions.md](decisions/evolve-decisions.md) §EV-080;
  **TC-EV080-001..010**
- **Out of scope**: Product features; promote; weaken F34/lint/typecheck; covering vendor/
  generated; using Playwright to satisfy unit thresholds
- **Journeys / UI**: N/A (CI / unit only; thin UJ-DEV-COV-001)
- **Corpus**: `[Corpus: product]` · `[Corpus: tests]` · `[Corpus: tech-spec]` ·
  `[Corpus: adr/ADR-007]` · `[Corpus: decisions §EV-080]`

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
  | `packages/auth` | Auth library in backend | **Restored** F31 / ADR-033 (was Deleted F21) |
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

### M4: Auth Library in Backend API — Restore (S038 / EV-031)

- **Status**: **Planned (restore)** under F30/F31. Was **Deprecated for operator Auth** (S023 / EV-017 / #783; `packages/auth` deleted ADR-031).
- **EV-031**: Reintroduce Auth verify against **Supabase Auth only** (JWT for long-term session APIs). Product data remains on DO Postgres — not Supabase DB. F8 uses machine/`DATABASE_URL` credentials, not operator JWT.
- **Historical**: Collapsed auth microservice into backend via `packages/auth` (REQ-004); S003 key split (ADR-010); S011 removed `/admin/*` (#697); EV-017 deleted operator Auth.
- **Source**: REQ-004; S023 / EV-017; **S038 / EV-031 / F30/F31**

### M5: Workspace Tooling

- **What it does**: Root Makefile orchestrates uv (Python) and pnpm (JS) workspaces; pre-commit
  and GitHub Actions quality gates.
- **F6 delta**: Workspace member `tac2iwxxm`; drop gifts from test matrix at cutover; **PyO3 /
  maturin required** in CI before cutover (ADR-017).
- **S008 package amend**: Workspace members `tac-validate`, `iwxxm-validate` in test matrix.
- **S044 / EV-036 deepen (local-first gates)**: Tiered local hooks save CI runner time:
  - **Commit (pre-commit)**: existing fast gates + **medium** `validate-ci` extras (de-duped).
  - **Push (husky pre-push)**: `make ci` = `ci-prepush` + Compose **integration** (ports
    18000/18001; includes wis2box harness if wired into local integration target) — no second
    `validate-ci`.
  - **Remote (ci-cd.yml)**: drop **validate** + Compose **integration**; **keep** package
    **unit matrix + coverage** and post a sticky **PR coverage comment**; keep
    `tac2iwxxm-native`, `e2e-smoke`, `test-alembic`, deploy (needs graph updated). Strict
    lint/format stays on local hooks. Family quality packs stay path-filtered / opt-in.
- **Acceptance (EV-036)** — **approved** (`AC=1`, `R1=local`, Gate A amend `D-S044-02-gate-a`):
  1. `make install-hooks` → commit runs fast + medium validate; push runs `make ci` (units + Compose).
  2. `docs/ops/DEVELOPMENT.md` + `docs/test-plan.md` CI tables match the tier model.
  3. PR CI has no validate job and no Compose integration job; **unit matrix + coverage + PR
     coverage comment** remain.
  4. Deploy on `main` gated by remaining remote jobs (test + alembic + native [+ e2e per graph]).
  5. TC-EV036-001..003 green (hook wiring + workflow contract tests; dense asserts).
- **Source**: REQ-005; EV-002; ADR-014; S008 realtime amend; **S044 / EV-036**
- **S056 / EV-047 deepen (#833 — slim husky)**: **Supersedes EV-036 day-to-day local hook
  weight** for developer commit/push. Target shape **A** (`D-S056-husky-shape=1`):
  - **Commit (husky → pre-commit)**: **lint/format only** (ruff / prettier / eslint — align
    `Makefile` `PY_LINT` / JS lint). No typecheck, catalog-check, issue-registry-guard,
    actionlint/yamllint, or medium `validate-ci` on the default commit path.
  - **Push (husky pre-push)**: **fast unit-test subset only** (explicit target; not full
    coverage-fail-under matrix / not `make validate-ci` / not Compose integration).
  - **Remote CI**: unchanged merge strength — typecheck, catalog/registry, secrets/yaml,
    unit coverage, integration/e2e, Rust checks remain enforced in `.github/workflows`.
  - Heavy local parity stays opt-in via `make validate-fast` / `validate-ci` / `ci-prepush`.
- **Acceptance (EV-047 / #833)** — **approved** (`D-S056-01-ac=1`):
  1. After `make install-hooks`, normal commit does **not** run typecheck / catalog /
     registry-guard / actionlint / yamllint / medium validate unless opted in.
  2. Normal push runs the agreed **fast unit** subset only (not full `validate-ci`).
  3. `docs/ops/DEVELOPMENT.md` + test-plan hook tables match shape A.
  4. PR/`main`/`stage` CI still fails if any offloaded gate fails.
  5. TC-EV047-001..004 green.

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
| F21 | Yes (public convert + optional login) | Yes (public + session APIs) | Yes | Yes → **DOKS** (F30) |
| F22 | Yes (privacy settings) | — | Yes | Yes (static) |
| F23 | Yes (SIGMET/VA SIGMET workbench smoke) | Yes (`lint-tac` / convert sigmet + VA) | Yes (goldens + matrix) | Yes if API/FE contract changes |
| F29 | — (CI harness; FE only if #829 menu) | — | Yes (rule matrices) | Yes if FE unlock |
| F30 | — | Yes (Auth verify + DO DB + DOKS) | Yes | **DOKS** cutover |
| F31 | Yes (notice, login, hybrid sessions) | Yes (session CRUD) | Yes | Yes (static + API) |
| F32 | Yes (picker + Examples when unlocked) | Yes (`product=vona`) | Yes (lint/convert/validate) | Yes (API + static) |
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
- Public machine-ingest auth UX (worker uses private `DATABASE_URL` / machine credentials —
  ADR-018 amended by ADR-033 / F30; not operator JWT).
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
- ~~Removing F8 worker **service-role** credentials or Render↔Supabase machine auth.~~
  **Amended S038 / EV-031**: F8 writers move to DO `DATABASE_URL` (not Supabase PostgREST);
  machine credentials remain private — not operator JWT.
- Reintroducing admin role UX (#697).
- ~~Optional user accounts or anonymous server sessions in v1.~~
  **Amended S038 / EV-031 / F31**: Optional Supabase Auth accounts for **long-term** server
  sessions only; convert remains public; guests keep IndexedDB.
- Cross-device sync **without** login (logged-in DO sessions are in scope via F31).
- Full CMP / analytics / marketing tags (Solution B/C) unless a later evolve cycle adds them.
- Per-US-state separate privacy UI variants (one global strict preference center).

## Planned Features (Post-Migration)

| # | Feature | Priority | Complexity | Notes |
|---|---------|----------|------------|-------|
| P1 | OpenAPI → TS codegen in packages/shared | Medium | Low | After layout stabilizes |
| P2 | Path-filtered CI per app/package | Medium | Medium | Reduce CI time |
