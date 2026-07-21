# Technical Specification

> **Project**: METAR to IWXXM Converter
> **Repository**: https://github.com/joseph-c-mcguire/metar-to-IWXXM
> **Version**: monorepo + F6 tac2iwxxm + F7 operator UI (S011 / EV-008)
> **Last updated**: 2026-07-21 (S019 / EV-014 F16–F19 Planned)

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
Browser (CodeMirror 6 workbench)
   │  debounce + AbortController (JWT)
   ▼
apps/frontend (static — Render static site or Vite dev)
   │  convert UI + decode panel + F7 sessions — no /admin
   │  VITE_* / runtime config → API base URL
   ▼
apps/backend (FastAPI — Render web service)
   ├── packages/auth (Supabase JWT; /admin/* removed — #697)
   ├── packages/tac-validate (TAC lint; optional start/end spans)
   ├── packages/tac2iwxxm (convert; decode segments; soft-preview)
   ├── packages/iwxxm-validate (XSD + Schematron; F2 engine)
   └── vendor/schemas/{iwxxm*, iwxxm-us} (read-only)

apps/worker (Render Background Worker — F8)
   └── same packages (poller → lint → convert → Schematron → store/quarantine)
```

`packages/gifts` is **absent** after the first PR that wires tac2iwxxm to `/api/v1/convert`
(ADR-014). Operator deploy env supplies **BYO** Supabase URL/keys and optional
`DATABASE_URL` / Postgres URI (R6 / #697).

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
| Backend API | Conversion, validation, auth; **Planned** F16–F19 dissemination preflight/send (BYOC, memory-only) | `apps/backend/` | tac2iwxxm, tac-validate, iwxxm-validate, auth, shared, vendor |
| Frontend | Operator UI (workbench, decode, F7 sessions; **Planned** dissemination drawer) | `apps/frontend/` | shared (types); CodeMirror 6 |
| E2E workspace | Cross-app tests | `apps/e2e/` | backend, frontend |
| Auth library | Supabase middleware | `packages/auth/` | supabase-py |
| tac2iwxxm | TAC → IWXXM (7 products, bulletin split, profiles) | `packages/tac2iwxxm/` | tac-validate (optional), vendor; PyO3 required at cutover (ADR-017) |
| tac-validate | TAC lint / shared rule pack | `packages/tac-validate/` | — (no FastAPI/Supabase) |
| iwxxm-validate | XSD + Schematron (F2 engine) | `packages/iwxxm-validate/` | vendor schemas (read-only) |
| Shared | Cross-cutting utils/types | `packages/shared/` | — |
| Vendor schemas | Authoritative IWXXM SoT | `vendor/schemas/*` | wmo-im + iwxxm-us snapshots |
| Work history (F5) | Per-user METAR session persistence | Supabase Postgres + `apps/backend` router | auth, shared |
| Worker (F8) | Near-RT ingest poller → store/quarantine | `apps/worker/` | same packages as backend; Supabase service role |

## Component Details

### apps/backend

- **Purpose**: Single HTTP API for health, conversion, validation, lint, decode, soft-preview,
  auth, and F5/F7 work sessions. **Planned (F16–F19)**: backend-mediated dissemination
  preflight/send for one-shot BYOC destinations (memory-only; ADR-029 allowlist). Route shapes
  deferred to api-contract / 04. **No** `/admin/*` product surface after F7.a (#697).
- **Inputs**: HTTP multipart/JSON (TAC + `product` + `profile` + version; decode/lint bodies),
  JWT bearer tokens, env config (BYO Supabase + optional `DATABASE_URL`; Planned
  `DISSEMINATION_EGRESS_ALLOWLIST`).
- **Outputs**: JSON responses, IWXXM XML, auth session endpoints, span-aware issue lists,
  decode segments, soft-preview payloads; Planned structured preflight/send results (no
  destination secrets persisted).
- **Algorithm**:
  1. Auth middleware validates JWT via Supabase (`packages/auth`); local/CI may use
     `DISABLE_AUTH` (G1).
  2. Conversion router may run **`tac-validate`**, then **`tac2iwxxm`** (bulletin split when
     needed); soft-preview path returns best-effort IWXXM + failed-span markers (exact route
     shape in api-contract / 04).
  3. Validation / lint routers are **thin wrappers** over **`iwxxm-validate`** /
     **`tac-validate`**; issue objects may include optional integer `start`/`end`.
  4. Decode router (`POST /api/v1/decode-tac`) wraps tac2iwxxm decode/annotate segments.
- **S014 / EV-010 delta (F11, ADR-026)**: High-churn route **responses**
  (`/convert`, `/convert-zip`, `/convert-bulletin`, `/validate`, `/lint-tac`, `/decode-tac`)
  encode with **msgspec**; multipart **request** intake stays FastAPI `Form`/`File`. Auth and
  work-sessions remain **pydantic**. OpenAPI kept via thin pydantic aliases/export (no dual
  runtime validation). FE types updated same cycle.
- **Error handling**: HTTP 4xx for auth/validation; 5xx for conversion failures with structured
  errors; soft-preview is not a hard 5xx for parse failures when preview mode is selected.
- **Source**: REQ-004; F6 / ADR-014; S011 / EV-008; S014 / ADR-026.

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
- **SoC**: **No** FastAPI or Supabase imports.
- **Runtime**: Pure Python v0; optional **Rust/PyO3** hotspots after benchmarks (not Cython).
- **License**: MIT.
- **IR**: **msgspec.Struct** (ADR-016); HTTP high-churn paths also msgspec (ADR-026).
- **Source**: [feature-list.md](feature-list.md) F6/F14; ADR-013; ADR-014; ADR-026;
  [context/general-tac-iwxxm-converter.md](context/general-tac-iwxxm-converter.md);
  [context/package-publish-validation.md](context/package-publish-validation.md).

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
- **SoC**: **No** FastAPI or Supabase imports.
- **Source**: feature-list F6/F12/F15; S011 / EV-008; S013 / EV-009; S014 / EV-010;
  S015 / EV-011.

### packages/iwxxm-validate

- **Purpose**: F2 engine — XSD + Schematron validation of IWXXM XML against vendored schemas.
- **Inputs**: IWXXM XML; `iwxxm_version`; optional `profile` (US catalogs when `iwxxm_us`).
- **Outputs**: Validation report (pass/fail + messages).
- **S014 / EV-010 delta (F13)**: **Rust core** (well-formed + XSD + native Schematron/SVRL)
  via PyO3; Python SDK; pinned schemas **bundled** in the wheel; PyPI `iwxxm-validate` `0.1.0`.
  Parity suite vs historical lxml isoschematron. Optional **XSD-derived** typed models
  (codegen; F11) — UML modelling is provenance only; TAC has no official model.
- **SoC**: **No** FastAPI or Supabase imports; **read-only** consumption of `vendor/schemas/*`
  (and bundled copies in published wheels).
- **Source**: feature-list F2/F13; [context/realtime-tac-ingest.md](context/realtime-tac-ingest.md);
  [context/package-publish-validation.md](context/package-publish-validation.md).

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

- **Purpose**: Operator converter UI (product/profile/version), CodeMirror 6 workbench, decode
  panel, Failed-TAC / soft-preview UX, F5 My METARs, and F7 multi-product sessions.
  **Planned (F16–F19)**: Dissemination drawer (sink chooser, one-shot URI/params, preflight,
  Send blocked until green; convert-then-send and drag-drop). **No** AdminDashboard or
  `/admin/*` routes after F7.a.
- **F6 delta**: Product select (7 values + auto-detect), profile select (`annex3` | `iwxxm_us`),
  version control; values passed via `conversion_params` / multipart to `/api/v1/convert`.
- **F7 delta (S011)**: Debounced JWT calls to lint/decode/validate/preview with AbortController;
  span highlight + hover; collapsible Code|Explanation decode panel; toggleable live IWXXM;
  pull-up console; F7 session persist/resume (separate from F5).
- **F7 convert-params (ADR-023)**: Hard Convert maps Bulletin ID, Issuing Center, On Error →
  `stop_on_error`, and Strict Validation → `validate_output`/`validation_level`. Soft-preview
  skips post-convert validation. Console Log Level filters workbench lines client-side.
  Upload accept: `.txt`, `.metar`, `.tac`.
- **F7 input modes (ADR-024)**: TAC | AHL bulletin (`/convert-bulletin`) | IWXXM COLLECT
  (`/ingest-collect` 501 placeholder). Accept `.xml`/`.gz` (inflate). `log_level` +
  `include_nil_reasons` on Convert. Log Level filters Conversion log + console for lint/validate
  process messages. **Validation**: UJ-025 / TC-F7-007 (S016 / EV-012 / #730) — auto-switch
  required; COLLECT 501 honest UX; F7 status unchanged.
- **F5**: Unchanged product scope — METAR/SPECI work sessions only (not extended to other
  products); admin browse path removed.
- **F9/F10 delta (S013)**: Decode panel gains a top **"Plain language"** block rendering the
  backend `summary` live (existing debounce path). New **side-by-side IWXXM preview pane**
  (stacked < `lg`) anchors Soft-preview / Live IWXXM output — pretty-printed XML + status
  badge ("Soft preview — not for publish" plain-language copy vs "Passed") + failed-span
  count linked to editor highlights. Lint console renders `info` severity distinctly with a
  one-click **"Add `=`"** quick fix (also as editor affordance on the hint span). ADR-025.
- **Source**: F6-R5; feature-list F6/F7/F9/F10; [context/f7-operator-ui.md](context/f7-operator-ui.md).

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

### F5 — User METAR work history (S004 / EV-004; unified under F7 in S011)

- **Purpose**: Durable per-user converter **work history** (current session state, not an
  append-only audit log) in Supabase Postgres, linked to `auth.users` via RLS; exposed through
  backend REST (not direct browser DB access).
- **Canonical table (S011 / R2′)**: `tac_work_sessions` with `product` covering all seven F6
  products. Existing `metar_work_sessions` rows **migrate** to `tac_work_sessions`
  (`product` = `metar` | `speci`); `metar_work_sessions` deprecated then dropped after cutover.
- **Columns** (product-generalized from F5):
  - `user_id`, `product`, `status` (`draft` | `wip` | `finished` | `failed`)
  - `title` (auto ICAO + time / product hint; user-renamable)
  - `manual_tac`, `pending_files` JSONB (name + inline TAC content)
  - `converted_results`, `errors`, `issues`, `conversion_params` JSONB
  - `kv_upload_key` (nullable — set when send succeeds; METAR/SPECI and any product that already supports Upload)
  - `deleted_at` (nullable — soft delete / trash)
  - `created_at`, `updated_at`
- **RLS**: `auth.uid() = user_id` for user CRUD; `service_role` for pg_cron Draft purge.
  **Admin read via `is_admin()` is removed** with F7.a / #697.
- **Business rules**: Same Draft/WIP/Finished/Failed lifecycle as S004 F5 (WIP uniqueness per user
  applies across products unless 04 says otherwise — default: **one WIP per user total**).
- **Frontend**: Debounced draft sync (~3s); converter sidebar (**5 recent**, all products or
  filtered); **My METARs** = filter `product IN (metar, speci)` on unified table; workbench
  history lists all products; #555 error log panel; **no** `/admin/work-sessions`.
- **Migration**: One-time copy + dual-read/dual-write window as needed; finalize in 04-tech-plan;
  no silent dual-table forever.
- **Source**: F5 requirements delta 2026-06-23; [metar-work-history.md](context/metar-work-history.md);
  S011 Spec Batch 2 A (R2′ override).

### F7 — Multi-product operator UI / sessions (S011 / EV-008)

- **Purpose**: Operator UI for all seven F6 products — workbench, decode, soft-preview,
  Failed-TAC cue — plus **unified work sessions** on `tac_work_sessions` (R2′). Built this cycle.
- **Status**: **Planned (build-ready)** — flips Implemented after verify/deploy gate.
- **Slices**: F7.a #697 → F7.b #702 → F7.c #665/#666 → F7.d #694 → F7.e unified sessions migrate →
  F7.f verify.
- **Sessions (R2′)**: Single canonical `tac_work_sessions` table (see F5 section). F5 My METARs
  becomes a product filter; do **not** keep a parallel F7-only sessions table.
- **API companions**: `POST /api/v1/decode-tac`; lint/validate `start`/`end`; soft-preview convert;
  session CRUD retargeted to unified table (route names may keep F5 paths for METAR UX or
  generalize — finalize in api-contract / 04).
- **Editor**: CodeMirror 6.
- **BYO / admin**: Deploy-env credentials only; AdminDashboard deleted; clean cut for former
  shared-project users (G3).
- **ADR**: Document R2′ unified sessions + F5 migration (new ADR in 01 ADR pass).
- **Source**: [feature-list.md](feature-list.md) F7; [context/f7-operator-ui.md](context/f7-operator-ui.md);
  D-S011-01-spec-r2-prime.

### F8 — Near-realtime ingest (Implemented)

- **Purpose**: Continuous ingest → unified pipeline → store; quarantine on fail;
  &lt;5–15s target; scale workers via Render Background Worker (`apps/worker/`).
- **Status**: **Implemented** (S008 / EV-006 — ADR-018/019). Live staging smoke may be deferred.
- **Non-goals (F8 worker path)**: public machine-ingest auth UX; **automatic** push of ingest
  results. Operator **dissemination push sinks** are **F16–F19** (separate UI/API path), not F8 v1.
- **Source**: [feature-list.md](feature-list.md) F8; ADR-018.

### F16–F19 — Dissemination epic (S019 / EV-014) — Planned

- **Purpose**: Unified dissemination **drawer** for sending converted (or drag-dropped) IWXXM/TAC
  to operator-chosen destinations with schema/connectivity preflight.
- **F16**: Multi-DB upload (Postgres, MySQL/MariaDB, SQL Server, SQLite) via one-shot URI;
  DDL/create-if-missing vs versioned writer contract; SSRF + allowlist.
- **F17**: WIS2 publish — staging wis2box harness for test; live BYOC node for close gate.
- **F18**: EDIS-compliant submit to RTH Washington — BYOC SMTP/gateway in drawer.
- **F19**: AMHS / SWIM / AFS adapters in the same drawer.
- **Auth / F5**: Supabase Auth + `tac_work_sessions` unchanged; never store destination secrets
  (`kv_upload_key` only on success).
- **Close gate**: Live BYOC demos for **Postgres + WIS2 + EDIS** before EV-014 close
  (Q15=A / Q21=A); staging evidence may merge earlier. F19 staging/test path required; F19 live
  demo optional with AskQuestion waive (S-EV014-M2).
- **ADRs**: ADR-021 amend (destination paste); ADR-029 (SSRF / allowlist).
- **Source**: [feature-list.md](feature-list.md) F16–F19; #729 / #2 / #6; evolve-decisions EV-014.

### F9 / F10 — Live decode translations + preview clarity (S013 / EV-009)

- **Purpose**: F9 — value-aware decode explanations + deterministic plain-language `summary`
  (packages/tac2iwxxm + decode panel). F10 — side-by-side IWXXM preview pane, plain-language
  soft-fail copy, `MISSING_TERMINATOR` info-level + "Add `=`" quick fix
  (apps/frontend + packages/tac-validate).
- **Status**: **Planned (build this cycle)** — flips Implemented after verify/deploy gate.
- **Component deltas**: see §packages/tac2iwxxm S013 delta, §packages/tac-validate S013 delta,
  §apps/frontend F9/F10 delta.
- **Non-goals**: LLM-generated text; new endpoints; Layer 1–2 / Schematron semantic changes.
- **Source**: [feature-list.md](feature-list.md) F9/F10; ADR-025;
  [evolve-decisions §EV-009](decisions/evolve-decisions.md).

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
| U1b. Live assist | Editor text (debounced) | POST lint / decode (/ preview) | Spans + decode rows + Failed-TAC cue |
| U2. Auth | JWT | packages/auth middleware | Authorized request context |
| U3–U4 | Convert / validate | Unified pipeline stages 0–4 | IWXXM + validation |
| U5. Display | JSON response | Frontend render | Copy/download + Source TAC + console |
| U6. Persist | Any of 7 products + results | Backend upsert → `tac_work_sessions` | Draft/WIP/Finished/Failed |
| U6b. My METARs | Filter view | `product IN (metar, speci)` | F5 UX preserved |
| U7. Send link | KV upload success | Store `kv_upload_key` on session | Finished status |

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
- Auth remains Supabase JWT; topology is BYO (operator project + keys) after #697 — not a
  shared multi-tenant admin product.
- Local/CI may continue `DISABLE_AUTH` patterns (G1).

## Security & Privacy

- Supabase **publishable** key available to browser via runtime `/config.json`; **secret** key
  server-only (`SUPABASE_SECRET_KEY`) — Auth Admin scripts only (ADR-010).
- **Admin API / `is_admin()` product surface removed** (F7.a / #697). Session RLS is
  `auth.uid() = user_id` only for F5/F7 user data.
- CORS from `config.*.api.corsOrigins` on backend.
- Minimal `.env` — operator-owned secrets (BYO); `make env-check` validates sync across
  local/Render/CI.
- Vendor trees (WMO + IWXXM-US) are public schema data — **no new secrets** for F6 packages.
- F8 worker adds secrets: poller HTTPS URL + Supabase **service role** JWT (ADR-018).
- TAC/IWXXM still flow through existing API auth model (guest convert policy unchanged unless
  tightened in 04); workbench live calls use JWT when persistence or gated endpoints require it.
- Signup / invite policy is the **operator’s Supabase project setting** (G2) — app does not add
  invite gates.
- Former shared-project data is **not** migrated by the product (G3).

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
- F5 not extended as a permanent parallel store — unified `tac_work_sessions` (R2′); My METARs
  is a product filter after migration.
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
