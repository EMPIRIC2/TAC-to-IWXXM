# Technical Specification

> **Project**: METAR to IWXXM Converter
> **Repository**: https://github.com/EMPIRIC2/TAC-to-IWXXM
> **Version**: monorepo + F6 tac2iwxxm + F7 operator UI (S011 / EV-008)
> **Last updated**: 2026-07-30 (S030 / EV-023 — #800 encode deepen; F26/F27 Done)

## Overview

METAR to IWXXM converts aviation TAC messages (AIRMET, METAR, SIGMET, SPECI, TAF, VAA, TCA)
to WMO IWXXM XML via `packages/tac2iwxxm`, lints TAC via `packages/tac-validate`, and
validates IWXXM via `packages/iwxxm-validate` (XSD + Schematron) against authoritative WMO
and optional NOAA IWXXM-US schema bundles under `vendor/schemas/`. The system is a
**single-git monorepo** with `apps/` (deployables), `packages/` (libraries), and `vendor/`
(read-only upstream snapshots). **F7** (multi-product operator UI / sessions) is **Planned**
(S011). **F8** (near-realtime ingest worker) is **Implemented** (ADR-018/019).
**App auth** credentials are **BYO** (operator-owned Supabase via deploy env — ADR-021).
**Dissemination destinations** (F16–F19) use **one-shot user-pasted BYOC** credentials
(memory-only; never saved profiles) under SSRF + required egress allowlist (ADR-029).

## System Architecture

### Runtime (post–F6 cutover; F7 operator UI this cycle)

```
Browser (CodeMirror 6 workbench + IndexedDB history + privacy prefs)
   │  debounce + AbortController (public /api/v1 — no JWT)
   ▼
apps/frontend (static — Render static site or Vite dev)
   │  convert UI + decode panel + local F7.h sessions — no /admin, no /auth
   │  runtime /config.json → API base URL
   ▼
apps/backend (FastAPI — Render web service)
   ├── public /api/v1/* (convert/validate/lint/decode/preview/dissemination)
   │     + abuse controls (rate limits, body/batch size — F21)
   ├── packages/tac-validate (TAC lint; optional start/end spans)
   ├── packages/tac2iwxxm (convert; decode segments; soft-preview)
   ├── packages/iwxxm-validate (XSD + Schematron; F2 engine)
   └── vendor/schemas/{iwxxm*, iwxxm-us} (read-only)

apps/worker (Render Background Worker — F8)
   └── same packages (poller → lint → convert → Schematron → store/quarantine;
       service-role JWT — machine path only, not operator Auth)
```

`packages/gifts` is **absent** after the first PR that wires tac2iwxxm to `/api/v1/convert`
(ADR-014). F8 worker still uses server-side Supabase service-role credentials (ADR-018).
Operator Auth / `packages/auth` on the public router is **removed** (F21 / S023 / EV-017).

### Repository (target tree)

```
metar-to-IWXXM/
├── apps/
│   ├── backend/          # FastAPI — conversion, validation, auth routes
│   ├── frontend/         # React/Vite UI
│   ├── worker/           # F8 near-RT ingest poller (Render Background Worker)
│   └── e2e/              # Playwright + cross-service integration
├── packages/
│   ├── auth/             # Supabase auth library (not a deployable)
│   ├── tac2iwxxm/        # General TAC→IWXXM (F6); MIT; PyO3 required at cutover
│   ├── tac-validate/     # TAC lint + business rules (all 7 product TAC forms)
│   ├── iwxxm-validate/   # XSD + Schematron (F2); vendor consumers
│   └── shared/           # API types, env helpers, constants
├── vendor/
│   ├── manifest.json     # Pins upstream repo/tag/SHA or HTTP URL+hash per bundle
│   └── schemas/
│       ├── iwxxm/
│       ├── iwxxm-codelists/
│       ├── iwxxm-modelling/
│       ├── iwxxm-translation/
│       └── iwxxm-us/     # NOAA/MDL national extensions (F6; HTTP 3.0 snapshot)
├── pyproject.toml        # uv workspace root
├── pnpm-workspace.yaml
├── Makefile
└── docker-compose.yml    # backend + frontend (+ worker optional locally)
```

### Component Overview

| Component | Purpose | Location | Dependencies |
|-----------|---------|----------|--------------|
| Backend API | Conversion, validation, auth; **Done** F16–F19 dissemination preflight/send (BYOC, memory-only) | `apps/backend/` | tac2iwxxm, tac-validate, iwxxm-validate, dissemination, auth, shared, vendor |
| Frontend | Operator UI (workbench, decode, F7 sessions; **Done** F16–F19 drawer; **EV-018** multi-select deepen) | `apps/frontend/` | shared (types); CodeMirror 6 |
| E2E workspace | Cross-app tests | `apps/e2e/` | backend, frontend |
| Auth library | Supabase middleware | `packages/auth/` | supabase-py |
| tac2iwxxm | TAC → IWXXM (7 products, bulletin split, profiles) | `packages/tac2iwxxm/` | tac-validate (optional), vendor; PyO3 required at cutover (ADR-017) |
| tac-validate | TAC lint / shared rule pack | `packages/tac-validate/` | — (no FastAPI/Supabase) |
| iwxxm-validate | XSD + Schematron (F2 engine) | `packages/iwxxm-validate/` | vendor schemas (read-only) |
| Dissemination | Sink adapters, writer-contract DDL, SSRF helpers (F16–F19) | `packages/dissemination/` | SQLAlchemy async + dialect drivers; aiosmtplib (ADR-030) |
| Shared | Cross-cutting utils/types | `packages/shared/` | — |
| Vendor schemas | Authoritative IWXXM SoT | `vendor/schemas/*` | wmo-im + iwxxm-us snapshots |
| Work history (F5) | Local METAR/SPECI session persistence | Browser IndexedDB (`apps/frontend`) | F7.h / F21 |
| Worker (F8) | Near-RT ingest poller → store/quarantine | `apps/worker/` | same packages as backend; Supabase service role |

## Component Details

### apps/backend

- **Purpose**: Single **public** HTTP API for health, conversion, validation, lint, decode,
  soft-preview, and dissemination — **no** operator Auth / JWT gates (F21 / S023 / EV-017).
  **Done (F16–F19)**: backend-mediated dissemination preflight/send for one-shot BYOC
  destinations (memory-only; ADR-029 allowlist). **No** `/admin/*` (F7.a / #697); **no**
  `/auth/*` or server work-session CRUD (F21 / F7.h — history is IndexedDB on the client).
- **Inputs**: HTTP multipart/JSON (TAC + `product` + `profile` + version; decode/lint bodies);
  env config (`DISSEMINATION_EGRESS_ALLOWLIST`; abuse-control knobs finalized in 04). F8
  worker credentials are **not** on the public operator path.
- **Outputs**: JSON responses, IWXXM XML, span-aware issue lists, decode segments,
  soft-preview payloads; structured preflight/send results (no destination secrets persisted).
- **Algorithm**:
  1. Public routes apply **abuse controls** (per-IP + global rate limits, body/batch size,
     timeouts/concurrency — numeric defaults in 04). `DISABLE_AUTH` dual path **retired**.
  2. Conversion router may run **`tac-validate`**, then **`tac2iwxxm`** (bulletin split when
     needed); soft-preview path returns best-effort IWXXM + failed-span markers (exact route
     shape in api-contract / 04).
  3. Validation / lint routers are **thin wrappers** over **`iwxxm-validate`** /
     **`tac-validate`**; issue objects may include optional integer `start`/`end`.
  4. Decode router (`POST /api/v1/decode-tac`) wraps tac2iwxxm decode/annotate segments.
  5. **Done (F16–F19)**: Dissemination routers are thin wrappers over
     **`packages/dissemination`** (`/api/v1/dissemination/preflight` + `/send`; ADR-030).
- **S014 / EV-010 delta (F11, ADR-026)**: High-churn route **responses**
  (`/convert`, `/convert-zip`, `/convert-bulletin`, `/validate`, `/lint-tac`, `/decode-tac`)
  encode with **msgspec**; multipart **request** intake stays FastAPI `Form`/`File`. OpenAPI
  kept via thin pydantic aliases/export (no dual runtime validation). FE types updated same
  cycle. (Pre-F21 auth/work-sessions pydantic paths removed with those routes.)
- **Error handling**: HTTP 4xx for validation / abuse limits; 5xx for conversion failures with
  structured errors; soft-preview is not a hard 5xx for parse failures when preview mode is
  selected.
- **Source**: F6 / ADR-014; S011 / EV-008; S014 / ADR-026; **S023 / EV-017 / F21**.

### packages/tac2iwxxm

- **Purpose**: General TAC→IWXXM library (F6). Python public API → **bulletin split** (WMO AHL)
  → versioned IR → product plugins → profile plugins (`annex3` / `iwxxm_us`) → XML writer;
  library/CI metrics via companion validate packages.
- **Products (v1)**: AIRMET, METAR, SIGMET, SPECI, TAF, VAA, TCA.
- **Inputs**: TAC string/files **or bulletins**; `product`; `profile`; `iwxxm_version`; schema paths under vendor.
- **Outputs**: IWXXM XML bytes/strings (per report); metrics reports in tests/CI only (not convert API fields).
- **S011 deltas**: Decode/annotate ordered segments (`start`/`end` + short explanation);
  soft-preview / partial convert hooks returning best-effort XML + failed spans. VAA/TCA spans
  may be best-effort with explicit residuals (G4).
- **S013 delta (F9)**: `decode_tac` explanations become **value-aware** (parsed values —
  temps, wind direction/speed/gusts, visibility, pressure, times, change groups) for all
  seven products (sparse ones best-effort), and the result gains a deterministic
  plain-language `summary` paragraph ("Not decoded: …" clause when residuals exist;
  "partial decode" wording for sparse products). Offsets and existing fields unchanged
  (additive). ADR-025.
- **S014 / EV-010 delta (F14)**: Published to PyPI as `tac2iwxxm` `0.1.0`; optional extra
  `[validate]` depends on `tac-validate` + `iwxxm-validate`. Public convert API documented for
  third-party install.
- **S020 / EV-015 delta (F20)**: Deepen **TAF (F6.c)** and **SPECI (F6.b)** convert/golden
  fidelity — exceptional-rule tables from #735/#734; guidance + 2025-2 corrections; expanded
  annex3 / `iwxxm_us` goldens; convert → `iwxxm-validate` round-trip. Roots `iwxxm:TAF` /
  `iwxxm:SPECI`.
- **S025 / EV-019 delta (F23)**: Deepen **SIGMET (F6.d)** — general `iwxxm:SIGMET` plus
  content-selected **`iwxxm:VolcanicAshSIGMET`** (VA phenomenon / WV AHL; still
  `product=sigmet` on HTTP). Exceptional-rule tables from #733/#739; guidance + 2025-2
  corrections; expanded goldens; convert → `iwxxm-validate` round-trip. TC SIGMET OOS (#738).
- **S027 / EV-021 delta (F26/F27)**: Deepen **VAA (F6.f)** + **TCA (F6.f)** WMO golden bar —
  `canonicalize_xml` under defaults; see feature-list F26/F27 (**Done**).
- **S030 / EV-023 delta (#800)**: Cross-product encode correctness deepen — NSC vs layered
  cloud; Guidance nils (`common/nil` vs `iwxxm/nil`); `translationFailedTAC` quarantine;
  dual-register colour href policy (offline vendor RDF/CSV); iwxxm-translation Amd79-80-2023
  TAC → 2025-2 as **informative** (no 2023-1 XML byte-match); default omit `translationCentre*`
  (optional config/request gate for Translation Centre); FIR/“S OF” polygon helpers (#738
  coord); COLLECT/multi-version hooks under F16–F19 (not single-report SoT). Runtime pin
  **v2025-2**.
- **SoC**: **No** FastAPI or Supabase imports.
- **Runtime**: Pure Python v0; optional **Rust/PyO3** hotspots after benchmarks (not Cython).
- **License**: MIT.
- **IR**: **msgspec.Struct** (ADR-016); HTTP high-churn paths also msgspec (ADR-026).
- **Source**: [feature-list.md](feature-list.md) F6/F14/F20/F23/F26/F27; ADR-013; ADR-014; ADR-026;
  evolve-decisions EV-023; [context/general-tac-iwxxm-converter.md](context/general-tac-iwxxm-converter.md);
  [context/package-publish-validation.md](context/package-publish-validation.md);
  [context/aerodrome-quality.md](context/aerodrome-quality.md);
  [context/sigmet-quality.md](context/sigmet-quality.md).

### packages/tac-validate

- **Purpose**: TAC linting and shared **business-rule pack** for all seven product TAC forms
  (parse gate + rules). **Not** Schematron.
- **Inputs**: TAC text or bulletin fragments; product hint when known.
- **Outputs**: Structured issue list (severity, code, message, location; optional integer
  `start`/`end` character offsets for editor highlight — S011).
- **S013 delta (F10)**: Severity enum `error | warning | info`; `ok` computed from `error` only.
  `MISSING_TERMINATOR` → `info` with actionable copy + paired `add_terminator` fix entry
  (`replacement` = text with `=` appended) powering the UI quick fix. ADR-025.
- **S014 / EV-010 delta (F12)**: Published to PyPI `tac-validate` `0.1.0`; encode mined
  `docs/domain/` rules — full depth METAR/SPECI/TAF; SIGMET/AIRMET/VAA/TCA templates + gates;
  cite-only for paywalled Annex text. CLI for CI.
- **S015 / EV-011 delta (F15)**: **Issue registry** module is the single source of lint
  `code` + default `severity` + message template (ADR-028). Rules import registry entries;
  docs/generated catalog lists codes. METAR rule pack expanded (R1–R6 + opportunistic);
  CI rejects unknown codes. Public codes stable; severities may tighten in minor releases.
  Workbench METAR lint+convert smoke under F15 (F7 status unchanged).
- **S020 / EV-015 delta (F20)**: Same registry — add/extend **TAF** codes and deepen **SPECI**
  rules/fixtures to the #734 full quality bar (not residual-only). Coverage-matrix TAF + SPECI
  rows; exceptional-rule accept/negative packs. Workbench `product=taf` / `product=speci` smoke
  under F20 (F7 status unchanged). No new registry architecture (ADR-028 reuse).
- **S025 / EV-019 delta (F23)**: Same registry — add/extend **SIGMET** (+ VA SIGMET) codes and
  fixtures to the #733/#739 full quality bar. Coverage-matrix themes G1–G3 / V1–V3 / C1;
  exceptional-rule accept/negative packs. Workbench `product=sigmet` (+ VA fixture) smoke
  under F23 (F7 status unchanged). No new registry architecture (ADR-028 reuse).
- **S030 / EV-023 delta (#800)**: Tighten NSC / related lint beyond research `NSC_PRESENT` if
  needed for P0 exclusivity with layered cloud; ADR-028 registry codes only (no new architecture).
- **SoC**: **No** FastAPI or Supabase imports.
- **Source**: feature-list F6/F12/F15/F20/F23; S011 / EV-008; S013 / EV-009; S014 / EV-010;
  S015 / EV-011; S020 / EV-015; S025 / EV-019; S030 / EV-023.

### packages/iwxxm-validate

- **Purpose**: F2 engine — XSD + Schematron validation of IWXXM XML against vendored schemas.
- **Inputs**: IWXXM XML; `iwxxm_version`; optional `profile` (US catalogs when `iwxxm_us`).
- **Outputs**: Validation report (pass/fail + messages).
- **S014 / EV-010 delta (F13)**: **Rust core** (well-formed + XSD + native Schematron/SVRL)
  via PyO3; Python SDK; pinned schemas **bundled** in the wheel; PyPI `iwxxm-validate` `0.1.0`.
  Parity suite vs historical lxml isoschematron. Optional **XSD-derived** typed models
  (codegen; F11) — UML modelling is provenance only; TAC has no official model.
- **S030 / EV-023 delta (#800)**: SCH/XSD **negative** fixtures for NSC+layers; dual-register
  colour / dual nil RDF policy tests under offline vendor SoT (v2025-2 pin).
- **SoC**: **No** FastAPI or Supabase imports; **read-only** consumption of `vendor/schemas/*`
  (and bundled copies in published wheels).
- **Source**: feature-list F2/F13; [context/realtime-tac-ingest.md](context/realtime-tac-ingest.md);
  [context/package-publish-validation.md](context/package-publish-validation.md);
  evolve-decisions EV-023.

### packages/gifts — removed

- **Status**: Deleted in the first PR that wires tac2iwxxm to `/api/v1/convert` (ADR-014).
- **Historical**: Fork of mgoberfield/GIFTs; REQ-014 / ADR-004 / M3 deprecated.

### vendor/schemas

- **Purpose**: Read-only copies of upstream schema repositories at pinned tags.
- **Inputs**: `vendor/manifest.json` pins; sync script/Action fetches release artifacts
  (wmo-im iwxxm-* and IWXXM-US — URL/tag TBD in 04).
- **Outputs**: XSD, Schematron, codelist files consumed by `iwxxm-validate` and tac2iwxxm.
- **Constraints**: **No direct edits** in monorepo except manifest version bumps via sync PRs.
- **Source**: REQ-002, REQ-012; ADR-013/014.

### packages/shared

- **Purpose**: Shared API types (OpenAPI-derived TS), env URL helpers, constants (CORS origins,
  version enums, F6 product/profile enums).
- **Config loader (S003)**: Loads `config/{local,prod}.json` by `METAR_CONFIG_ENV`; exposes merged
  config to Python and TypeScript; secrets resolved from env only.
- **Source**: REQ-010, ADR-010.

### apps/frontend

- **Purpose**: Public converter UI (product/profile/version), CodeMirror 6 workbench, decode
  panel, Failed-TAC / soft-preview UX, **IndexedDB** F5 My METARs + F7 multi-product sessions
  (F7.h), and F22 privacy notice/settings. **Done (F16–F19)**: Dissemination drawer (sink
  chooser, one-shot URI/params, preflight, Send blocked until green; convert-then-send and
  drag-drop). **EV-018 / #785**: **Export selection** multi-select (current-session + drops;
  ≤20; N sequential preflight/send with per-file results). **No** AdminDashboard, `/admin/*`,
  or operator login (F21).
- **F6 delta**: Product select (7 values + auto-detect), profile select (`annex3` | `iwxxm_us`),
  version control; values passed via `conversion_params` / multipart to `/api/v1/convert`.
- **F7 delta (S011; F21 amend)**: Debounced **public** calls to lint/decode/validate/preview with
  AbortController; span highlight + hover; collapsible Code|Explanation decode panel; toggleable
  live IWXXM; pull-up console; **local** F7.h session persist/resume (IndexedDB — not server).
- **F7 convert-params (ADR-023)**: Hard Convert maps Bulletin ID, Issuing Center, On Error →
  `stop_on_error`, and Strict Validation → `validate_output`/`validation_level`. Soft-preview
  skips post-convert validation. Console Log Level filters workbench lines client-side.
  Upload accept: `.txt`, `.metar`, `.tac`.
- **F7 input modes (ADR-024)**: TAC | AHL bulletin (`/convert-bulletin`) | IWXXM COLLECT
  (`/ingest-collect` 501 placeholder). Accept `.xml`/`.gz` (inflate). `log_level` +
  `include_nil_reasons` on Convert. Log Level filters Conversion log + console for lint/validate
  process messages. **Validation**: UJ-025 / TC-F7-007 (S016 / EV-012 / #730) — auto-switch
  required; COLLECT 501 honest UX; F7 status unchanged.
- **F7.g golden examples (S021 / EV-016 / #780)**: Static frontend catalog (copied package
  goldens) + Examples control in FileConverter; loads TAC / AHL / happy-path IWXXM into
  existing modes; sets product/inputMode; demo labeling. No new API routes. Soft-fail XML
  and file-upload queue deferred. UJ-032 / TC-F7-008. F7 status unchanged.
- **F7.h / F5 (S023)**: Work history for all seven products in IndexedDB; My METARs =
  `product IN (metar, speci)` local filter; **no** `/api/v1/work-sessions`.
- **F9/F10 delta (S013)**: Decode panel gains a top **"Plain language"** block rendering the
  backend `summary` live (existing debounce path). New **side-by-side IWXXM preview pane**
  (stacked < `lg`) anchors Soft-preview / Live IWXXM output — pretty-printed XML + status
  badge ("Soft preview — not for publish" plain-language copy vs "Passed") + failed-span
  count linked to editor highlights. Lint console renders `info` severity distinctly with a
  one-click **"Add `=`"** quick fix (also as editor affordance on the hint span). ADR-025.
- **Source**: F6-R5; feature-list F6/F7/F9/F10/F21/F22; [context/f7-operator-ui.md](context/f7-operator-ui.md).

### Runtime configuration (`config/`)

- **Purpose**: Non-secret per-environment settings (URLs, CORS, validation flags).
- **Files**: `config/local.json`, `config/prod.json` (committed).
- **Frontend**: Static host serves `/config.json` (prod copy + publishable key injected at deploy).
- **BYO (R6 / ADR-021)**: Operator deploy env supplies Supabase URL/keys (and optional app
  `DATABASE_URL` for legacy primary upload). **No** in-app paste of **Supabase auth** keys.
- **Dissemination BYOC (S019 / EV-014)**: Users may paste **one-shot destination** credentials
  (DB URI / WIS2 / EDIS SMTP / AMHS params) in the dissemination drawer; API memory-only;
  required `DISSEMINATION_EGRESS_ALLOWLIST` (ADR-029).
- **Source**: [config-spec.md](config-spec.md), S003 session; S011 / EV-008.

### F5 — User METAR work history (S004 / EV-004; unified under F7; **IndexedDB — S023**)

- **Purpose**: Durable converter **work history** (current session state) for METAR/SPECI —
  **browser IndexedDB** after S023 / EV-017 / #783 (no login, no server ownership).
- **Historical (pre-EV-017)**: Supabase `tac_work_sessions` + JWT RLS (ADR-020 / R2′). That HTTP
  + table model is **retired** from the public product path; legacy rows archived/deleted after
  ~30 days with no public API access.
- **Client store**: UUID per work item; fields mirror prior session shape (product, status,
  title, TAC, results, errors, params, timestamps, soft-delete). Export/import JSON workspace.
- **Frontend**: Debounced draft sync (~3s) to IndexedDB; sidebar (**5 recent**); **My METARs**
  = filter `product IN (metar, speci)`; **no** `/api/v1/work-sessions`.
- **Source**: F5 requirements 2026-06-23; S011 R2′; **S023 / EV-017** (R2″ IndexedDB).

### F7 — Multi-product operator UI / sessions (S011 / EV-008; **F7.h IndexedDB — S023**)

- **Purpose**: Operator UI for all seven F6 products — workbench, decode, soft-preview,
  Failed-TAC cue — plus **local unified work sessions** in IndexedDB (F7.h).
- **Status**: **Planned (build-ready)** — flips Implemented after verify/deploy gate.
- **Slices**: F7.a–F7.g as before; **F7.h #783** IndexedDB local sessions + drop JWT session APIs.
- **Sessions (R2″)**: Client IndexedDB for all seven products; My METARs remains METAR/SPECI filter.
- **API companions**: decode/lint/validate/convert remain public (F21); session CRUD **removed**.
- **Editor**: CodeMirror 6.
- **Golden examples (F7.g)**: Unchanged static FE catalog.
- **BYO / admin**: AdminDashboard deleted (#697); operator Auth removed (F21).
- **Source**: S011; S021 F7.g; **S023 / EV-017** F7.h + F21.

### F21 — Public unauthenticated operator app (S023 / EV-017)

- **Purpose**: Remove operator Auth; public convert/validate/lint/decode/preview/dissemination
  with abuse controls; retire `DISABLE_AUTH` dual path; keep F8 machine auth private.
- **Source**: #783; [feature-list.md](feature-list.md) F21.

### F22 — Privacy preference center (S023 / EV-017)

- **Purpose**: Solution A privacy notice + settings + GPC; disclose IndexedDB; no CMP/analytics.
- **Source**: #783; [feature-list.md](feature-list.md) F22.

### F8 — Near-realtime ingest (Implemented)

- **Purpose**: Continuous ingest → unified pipeline → store; quarantine on fail;
  &lt;5–15s target; scale workers via Render Background Worker (`apps/worker/`).
- **Status**: **Implemented** (S008 / EV-006 — ADR-018/019). Live staging smoke may be deferred.
- **Non-goals (F8 worker path)**: public machine-ingest auth UX; **automatic** push of ingest
  results. Operator **dissemination push sinks** are **F16–F19** (separate UI/API path), not F8 v1.
- **Source**: [feature-list.md](feature-list.md) F8; ADR-018.

### F16–F19 — Dissemination epic (S019 / EV-014) — Done

- **Purpose**: Unified dissemination **drawer** for sending converted (or drag-dropped) IWXXM/TAC
  to operator-chosen destinations with schema/connectivity preflight.
- **F16**: Multi-DB upload (Postgres, MySQL/MariaDB, SQL Server, SQLite) via one-shot URI;
  DDL/create-if-missing vs versioned writer contract; SSRF + allowlist.
- **F16 deepen (S024 / EV-018 / #785)**: **Export selection** multi-select for current-session
  outputs + dropped files; select-all/clear; empty selection disables Preflight/Send; client
  **N sequential** `/preflight`+`/send` with per-file aggregated results; selection count
  **≤20**; Finished IndexedDB history and batched multi-payload API **out of scope** v1.
  F17–F19 reuse the same selection UI contract.
- **F17**: WIS2 publish — staging wis2box harness for test; live BYOC waived at EV-014 close (Q15).
- **F18**: EDIS-compliant submit to RTH Washington — BYOC SMTP/gateway in drawer; live waived (Q15).
- **F19**: AMHS / SWIM / AFS adapters in the same drawer (staging stubs; live optional).
- **Auth / F5**: Public dissemination (F21 — no operator JWT). Local session may record
  `kv_upload_key` on Finished in IndexedDB only; never store destination secrets.
- **Status**: **Done** (EV-014 closed 2026-07-21; PR #771/#772). Multi-select deepen **in
  progress** (EV-018).
- **ADRs**: ADR-021 amend (destination paste); ADR-029 (SSRF / allowlist); ADR-030
  (`packages/dissemination` + sink/API/wis2box/EDIS).
- **Source**: [feature-list.md](feature-list.md) F16–F19; #729 / #2 / #6; evolve-decisions EV-014;
  **#785; evolve-decisions EV-018**.

### F20 — TAF + SPECI quality bar (S020 / EV-015) — Done

- **Purpose**: F15 sequel — raise **TAF** (#735) and **SPECI** (#734) lint / convert /
  IWXXM-validate quality to the METAR/SPECI bar. Reuse ADR-028 registry; deepen F6.b/F6.c and F12.
- **Encode authority**: WMO `TAC-to-XML-Guidance.txt` + 2025-2 corrections (no `runwayState`);
  FM 205 / Manual on Codes I.3; pinned XSD + Schematron.
- **TAF exceptional rules** (fixtures or explicit deferrals): NIL, CNL, AMD, COR, CAVOK, NSC,
  NSW, VV///, FM/TL/AT, TX/TN on base forecast, change groups FM/BECMG/TEMPO/PROB.
- **SPECI**: Full #734 AC parallel to TAF — shared METAR/SPECI pack + mis-classification guards
  (Auto-detect / product hint never silent-swap SPECI↔METAR).
- **Status**: **Done** (S020 / EV-015; #778).
- **Non-goals**: Sibling product-quality tickets; PyPI bumps; F16–F19 changes; new ADR unless
  registry architecture changes.
- **Source**: [feature-list.md](feature-list.md) F20; #735/#734; [context/aerodrome-quality.md](context/aerodrome-quality.md);
  evolve-decisions EV-015; ADR-028.

### F23 — SIGMET family quality bar (general + VA) (S025 / EV-019) — Done

- **Purpose**: F15/F20 sequel — raise **General SIGMET** (#733) and **VA SIGMET** (#739)
  lint / convert / IWXXM-validate quality. Reuse ADR-028 registry; deepen F6.d and F12.
- **Encode authority**: WMO `TAC-to-XML-Guidance.txt` + 2025-2 corrections; FM 205 /
  Manual on Codes I.3; pinned XSD + Schematron; EUR Doc 014 (public TAC shape) cite-only.
- **General SIGMET exceptional rules** (fixtures or explicit deferrals): CNL, single-point →
  `gml:CircleByCenterPoint` radius zero, single altitude (same lower/upper), STNR, polygon/line
  with declared CRS; sequence / validity / FIR/CTA / phenomenon / movement / intensity.
- **VA SIGMET**: Apply general mapping then volcano identity + ash geometry / forecast;
  `NO VA EXP` → `nothingOfOperationalSignificance`; CNL FIR-moved-ash; root
  `iwxxm:VolcanicAshSIGMET` (not `iwxxm:SIGMET`, not VAA).
- **API**: `product=sigmet` unchanged; root selection is package-side from TAC content
  (E19-13=A). No new routes.
- **Status**: **Done** (S025 / EV-019; PR #792).
- **Journeys / tests**: UJ-034; TC-F23-001..006; matrix themes G1–G3 / V1–V3 / C1.
- **Non-goals**: #738 TC SIGMET; AIRMET / VAA / TCA / SWX / VONA; PyPI bumps; F16–F19;
  new `product` enum (E19-13). FE: **additive catalog filters for SIGMET/VA tags** in scope
  (E19-17=B amends E19-14); new ADR unless registry architecture changes.
- **Source**: [feature-list.md](feature-list.md) F23; #733/#739;
  [context/sigmet-quality.md](context/sigmet-quality.md); evolve-decisions EV-019; ADR-028.

### F24 — AIRMET quality bar (S026 / EV-020) — Done

- **Purpose**: #731 AIRMET quality peer to F23; WMO `airmet-A6-1a-TS` golden under **defaults**.
- **Status**: **Done** (S026 / EV-020; PR #793).
- **Journeys / tests**: UJ-035; TC-F24-001..005.
- **Policy**: ADR-032 (default `canonicalize_xml` equality).
- **Source**: feature-list F24; evolve-decisions EV-020; ADR-028/032.

### F25 — WMO official example parity + UI gate (S026 / EV-020) — Done

- **Purpose**: METAR/SPECI/TAF vendor golden equality under defaults; Examples catalog =
  WMO-passers only (plus SIGMET/AIRMET keepers when green).
- **Status**: **Done** (S026 / EV-020; PR #793).
- **Journeys / tests**: UJ-036; TC-F25-001..004; deepen UJ-032 / TC-F7-008.
- **Policy**: ADR-032.
- **Source**: feature-list F25; evolve-decisions EV-020.

### F26 — VAA quality bar (S027 / EV-021) — Done

- **Purpose**: #736 VAA (`iwxxm:VolcanicAshAdvisory`) quality peer to F23/F24. WMO
  `va-advisory-A7-2` TAC→IWXXM **`canonicalize_xml`-equal** under default convert settings
  (ADR-032). Registry-backed lint (ADR-028). Themes **F26 V1–V3 / C1**. Do not confuse with
  VA SIGMET (`iwxxm:VolcanicAshSIGMET`).
- **Status**: **Done** (S027 / EV-021; PR #794).
- **API**: `product=vaa` already in enum; no new routes.
- **Journeys / tests**: UJ-037; TC-F26-001..006; deepen UJ-032 / TC-F7-008.
- **Fixtures**: Mine TAC themes from `iwxxm-translation` Amd79-80-2023; no Amd79 XML
  byte-match under 2025-2 (E21-D4).
- **Non-goals**: VA SIGMET #739; TCA is F27; SWX #740; VONA #741; translation-failed as
  happy-path golden; PyPI bumps.
- **Source**: feature-list F26; evolve-decisions EV-021; ADR-028/032;
  sessions/S027-vaa-quality/reports/wmo-vaa-tca-examples-inventory.md.

### F27 — TCA quality bar (S027 / EV-021) — Done

- **Purpose**: #737 TCA (`iwxxm:TropicalCycloneAdvisory`) quality peer. WMO
  `tc-advisory-A2-2` golden under defaults. Themes **F27 T1–T3 / C1**. Do not confuse with
  TC SIGMET (`iwxxm:TropicalCycloneSIGMET` — #738 OOS).
- **Status**: **Done** (S027 / EV-021; PR #794).
- **API**: `product=tca` already in enum; no new routes.
- **Journeys / tests**: UJ-038; TC-F27-001..006; deepen UJ-032 / TC-F7-008.
- **Fixtures**: Same translation-package mine policy as F26 (E21-D4).
- **Non-goals**: TC SIGMET #738; VAA is F26; SWX/VONA; translation-failed happy-path; PyPI.
- **Source**: feature-list F27; evolve-decisions EV-021; ADR-028/032;
  sessions/S027-vaa-quality/reports/wmo-vaa-tca-examples-inventory.md.

### S030 / EV-023 — APAC FAQ + codes encode/validate deepen (#800)

- **Purpose**: Cross-cutting encode/lint/SCH deltas from APAC FAQs, codes.wmo.int, and
  iwxxm-translation mining — **deepen F6/F2/F12/F13** (no new Fn). Full #800 P0+P1+actionable P2.
- **Status**: **In progress** (S030 / EV-023).
- **Journeys / tests**: No new UJ; TC-EV023-001..009; deepen UJ-001/005/006/016.
- **API**: No new routes expected; optional convert flag for `translationCentre*` (name in 04).
- **Non-goals**: #740/#741; PDF remine; FAQ/2019 as equal-weight SoT; `.local/` binaries.
- **Source**: feature-list F6/F2/F12/F13 deepen; evolve-decisions EV-023; #800.

### F9 / F10 — Live decode translations + preview clarity (S013 / EV-009)

- **Purpose**: F9 — value-aware decode explanations + deterministic plain-language `summary`
  (packages/tac2iwxxm + decode panel). F10 — side-by-side IWXXM preview pane, plain-language
  soft-fail copy, `MISSING_TERMINATOR` info-level + "Add `=`" quick fix
  (apps/frontend + packages/tac-validate).
- **Status**: **Done** (S013). **S026 deepen (F9)**: extensible glossary registry + optional
  OpenAIP/F3 names (ADR-032; TC-F9-003/004; UJ-020 deepen).
- **Component deltas**: see §packages/tac2iwxxm S013 delta, §packages/tac-validate S013 delta,
  §apps/frontend F9/F10 delta.
- **Non-goals**: LLM-generated text; Layer 1–2 / Schematron semantic changes.
- **Source**: [feature-list.md](feature-list.md) F9/F10; ADR-025; ADR-032;
  [evolve-decisions §EV-009](decisions/evolve-decisions.md) / §EV-020.

## Data Flow

### Unified convert/validate pipeline (API + F7 UI + F8 worker)

| Stage | Input | Transformation | Output |
|-------|-------|----------------|--------|
| 0. Unit | TAC or WMO AHL bulletin | Detect / accept | Ingest unit |
| 1. Split | Bulletin | `tac2iwxxm` bulletin splitter | One TAC report each |
| 2. TAC lint | TAC report | `tac-validate` (+ optional spans) | Issues or pass |
| 2b. Decode | TAC report | `tac2iwxxm` decode segments | Ordered Code\|Explanation |
| 3. Convert | TAC + product + profile + version | `tac2iwxxm` (hard or soft-preview) | IWXXM XML (+ failed markers) |
| 4. IWXXM validate | IWXXM XML (+ profile) | `iwxxm-validate` (XSD + Schematron) | Pass or fail report (+ optional spans) |
| 5a. API path | Results | Backend JSON | UI / client |
| 5b. F8 | Pass | Store (no push sinks in v1) | Published artifact |
| 5c. F8 fail | Fail | Quarantine (no publish) | Error record |

### UI / session overlay (F7 workbench + F5)

| Stage | Input | Transformation | Output |
|-------|-------|----------------|--------|
| U1. Edit | TAC text/files + product/profile/version | CodeMirror workbench | Live editor state |
| U1b. Live assist | Editor text (debounced) | Public POST lint / decode (/ preview) | Spans + decode rows + Failed-TAC cue |
| U2. Auth | — | **Removed (F21)** — public `/api/v1/*` + abuse controls | No JWT for operator UI |
| U3–U4 | Convert / validate | Unified pipeline stages 0–4 | IWXXM + validation |
| U5. Display | JSON response | Frontend render | Copy/download + Source TAC + console |
| U6. Persist | Any of 7 products + results | **IndexedDB** upsert (F7.h) | Draft/WIP/Finished/Failed |
| U6b. My METARs | Filter view | `product IN (metar, speci)` local | F5 UX preserved |
| U7. Send link | Dissemination success | Store `kv_upload_key` locally | Finished status |

## Monorepo Migration

See [migration-plan.md](ops/migration-plan.md) for step-by-step big-bang procedure.

### Submodule → monorepo mapping

| Current submodule / prior target | Target | Strategy |
|----------------------------------|--------|----------|
| `schemas/iwxxm` | `vendor/schemas/iwxxm` | Snapshot from wmo-im/iwxxm |
| `schemas/iwxxm-codelists` | `vendor/schemas/iwxxm-codelists` | Snapshot |
| `schemas/iwxxm-modelling` | `vendor/schemas/iwxxm-modelling` | Snapshot |
| `data/iwxxm-translation` | `vendor/schemas/iwxxm-translation` | Snapshot |
| — | `vendor/schemas/iwxxm-us` | HTTP snapshot of `nws.weather.gov/schemas/iwxxm-us/3.0` + manifest URL/hash (D-S008-05-batch1) |
| `GIFTs` / `packages/gifts` | **removed** | Delete on first tac2iwxxm wire-up PR (ADR-014) |
| — | `packages/tac2iwxxm` | New MIT package (F6) |
| — | `packages/tac-validate` | New package (S008 amend) |
| — | `packages/iwxxm-validate` | New package — F2 engine extract (S008 amend) |
| `frontend` | `apps/frontend` | Full source in monorepo |
| `auth/` (root, not submodule) | `packages/auth` | Library; routes in backend |
| `backend/` | `apps/backend` | Move + wire workspace deps |

### Legacy repositories

Separate GitHub repos (Metartoiwxxmfrontend, GIFTs fork, iwxxm forks) will be **archived read-only** after stable production deploy (REQ-019). Monorepo is the sole active development target. External GIFTs upstream is no longer an in-repo sync target (REQ-014 deprecated).

## Constraints & Assumptions

### Hard Constraints

- iwxxm / iwxxm-* (and iwxxm-us) content is authoritative from upstream — read-only in vendor/.
- Single git clone must be sufficient for local dev (`git clone` — no `--recurse-submodules`).
- Render deploys **three** services: API (backend+auth) + static frontend + F8 Background
  Worker (ADR-018; amends REQ-009 two-service baseline).
- No FastAPI/Supabase imports inside `packages/tac2iwxxm`, `packages/tac-validate`, or
  `packages/iwxxm-validate`.
- After F6 cutover PR: no `packages/gifts` in the tree; API must not import gifts.
- Schematron applies to **IWXXM only**; TAC quality uses `tac-validate`.
- F7 is **in scope** this cycle (S011 / EV-008); F8 worker remains in tree (ADR-018).
- PyO3 native extension + ADR-016 benches hard-pass before F6 cutover (ADR-017).

### Assumptions

- wmo-im continues publishing tagged releases on GitHub.
- NOAA/MDL continues to publish IWXXM-US schemas suitable for vendor pinning.
- Operator Auth removed (F21). Public convert/validate/lint/decode/preview/dissemination share
  one unauthenticated path with abuse controls (defaults in 04).
- F8 worker retains machine auth (service-role JWT) off the public router (ADR-018).
- `DISABLE_AUTH` dual path is **retired** with F21 — no local/CI JWT bypass for operator UX.

## Security & Privacy

- **Public operator API** (F21): no browser JWT; abuse controls on `/api/v1/*`. Privacy notice
  + preference center (F22 / Solution A + GPC) disclose IndexedDB work history.
- **Admin API / `is_admin()` product surface removed** (F7.a / #697). Operator `/auth/*` and
  server session RLS paths removed (F21 / F7.h).
- CORS from `config.*.api.corsOrigins` on backend.
- Minimal `.env` — F8 / dissemination egress secrets only on server; `make env-check` validates
  sync (env-contract full rewrite deferred to 04/12 — stale-until-F21 banner).
- Vendor trees (WMO + IWXXM-US) are public schema data — **no new secrets** for F6 packages.
- F8 worker adds secrets: poller HTTPS URL + Supabase **service role** JWT (ADR-018).
- Dissemination destination credentials remain **memory-only** (ADR-021/029) — never in
  IndexedDB or logs.
- Legacy Supabase `tac_work_sessions` rows: no public API; ~30-day archive post-cutover (E17-5).

## Performance Characteristics

| Operation | Expected Time | Notes |
|-----------|---------------|-------|
| Single METAR/SPECI Annex-3 conversion | < 2s | Typical (unchanged) |
| Unified pipeline (lint + convert + Schematron) | TBD | Target &lt;5–15s informs F8; measure in 04 |
| Batch file upload (10 files) | < 10s | Depends on size |
| SIGMET / AIRMET / VAA / TCA / US-profile | TBD | May exceed METAR until measured (04) |
| Vendor sync PR | Minutes | CI job; not user-facing |
| Live lint/decode (debounced) | &lt; 500ms typical target | Abort in-flight; measure in 04 |
| Soft-preview convert | TBD | May exceed hard convert; UI must cancel |
| Library lint→convert→XSD+SCH (S014) | Beat current lxml baseline | Soft benches in build; hard-fail at PyPI publish (F11/F13) |
| High-churn HTTP DTO (msgspec) | ≤ prior pydantic map path | Hard-fail at publish/cutover (ADR-026) |

## Known Limitations

- Big-bang migration required coordinated downtime or feature freeze during merge PR (historical).
- **Hard cutover**: first tac2iwxxm wire-up PR deletes gifts — production METAR path depends on
  tac2iwxxm immediately (gate with M-parity / goldens).
- US AIRMET/SIGMET fixture depth may lag METAR/TAF.
- PyO3 is **required before cutover** (ADR-017); pure Python may exist during M3–M4 only.
- Accuracy metrics are library/CI only — not exposed on convert API responses in v1.
- Scheduled vendor PRs require review before production pins update.
- F5 not extended as a permanent parallel store — **IndexedDB** unified sessions (R2″ / F7.h);
  My METARs remains METAR/SPECI filter. Historical server `tac_work_sessions` (R2′) retired from
  public API.
- VAA/TCA decode may be residual-heavy in v1 (G4).
- Public machine-ingest auth, push sinks, AMHS/SWIM — out of scope (see feature-list Non-Goals).

## Documentation layout

Standing specs in `docs/` are **project-wide** sources of truth. Bounded work runs in
**pipeline sessions** with ephemeral artifacts under `docs/sessions/SNNN-slug/`.

| Corpus | Location | Examples |
|--------|----------|----------|
| **Project (standing)** | `docs/` root | `spec.md`, `feature-list.md`, `test-plan.md`, `deploy.md`, `api-contract.md` |
| **Session (ephemeral)** | `docs/sessions/{id}/` | `session-brief.md`, `routing-plan.md`, `reports/qa-report.md`, `reports/e2e-report.md` |
| **Scoped context** | `docs/context/{slug}.md` | Feature/workflow discovery briefs (linked from session brief) |

**Entry:** [skill-routing.md](skill-routing.md) — start with **00-context** (recommended) to
open a session, approve a routing plan, then run stages 00–19 per plan.

**State:** repo-root `workflow-state.yaml` §`active_session` and §`sessions[]`.

Full convention: [.cursor/skills/sessions-reference.md](../.cursor/skills/sessions-reference.md).

Standing doc updates during a session use **delta commits** on the session branch with a
§Session changelog footer (session id + date).

## References

- docs/guides/ARCHITECTURE.md (pre-migration product architecture)
- [ARCHIVE/pre-monorepo-deploy/AUTH_MIDDLEWARE_ARCHITECTURE.md](ARCHIVE/pre-monorepo-deploy/AUTH_MIDDLEWARE_ARCHITECTURE.md) (superseded by M4 — see ADR-002)
- docs/decisions/requirements-decisions.md
- ADR-013, ADR-014

### Session changelog

- S008 (2026-07-12): F6 tac2iwxxm architecture; gifts removal; IWXXM-US; UI product/profile; ADR-014
- S008 amend (2026-07-12): `tac-validate` + `iwxxm-validate`; unified pipeline; F7/F8 Planned;
  dashed F8 worker; [context/realtime-tac-ingest.md](context/realtime-tac-ingest.md)
- S008 05 (2026-07-12): F8 worker in-tree; PyO3 cutover gate; iwxxm-us HTTP 3.0 pin; three Render
  services (D-S008-05-batch1)
- S011 / EV-008 (2026-07-13): F7 operator UI architecture; BYO + admin removal; decode/spans/
  soft-preview; CodeMirror workbench; **R2′** unified `tac_work_sessions` + F5 migrate;
  F8 status sync
