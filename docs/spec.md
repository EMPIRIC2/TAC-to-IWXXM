# Technical Specification

> **Project**: METAR to IWXXM Converter
> **Repository**: https://github.com/joseph-c-mcguire/metar-to-IWXXM
> **Version**: monorepo + F6 tac2iwxxm + validate packages (S008 amend)
> **Last updated**: 2026-07-12

## Overview

METAR to IWXXM converts aviation TAC messages (AIRMET, METAR, SIGMET, SPECI, TAF, VAA, TCA)
to WMO IWXXM XML via `packages/tac2iwxxm`, lints TAC via `packages/tac-validate`, and
validates IWXXM via `packages/iwxxm-validate` (XSD + Schematron) against authoritative WMO
and optional NOAA IWXXM-US schema bundles under `vendor/schemas/`. The system is a
**single-git monorepo** with `apps/` (deployables), `packages/` (libraries), and `vendor/`
(read-only upstream snapshots). **F7** (multi-product operator entry) remains **Planned**.
**F8** (near-realtime ingest worker) is **built this cycle** (ADR-018).

## System Architecture

### Runtime (post–F6 cutover; this amend)

```
Browser
   │
   ▼
apps/frontend (static — Render static site or Vite dev)
   │  VITE_* / runtime config → API base URL
   ▼
apps/backend (FastAPI — Render web service)
   ├── packages/auth (Supabase JWT middleware, inlined)
   ├── packages/tac-validate (TAC lint / rules)
   ├── packages/tac2iwxxm (TAC → IWXXM; bulletin split; product + profile)
   ├── packages/iwxxm-validate (XSD + Schematron; F2 engine)
   └── vendor/schemas/{iwxxm*, iwxxm-us} (read-only)

apps/worker (Render Background Worker — F8)
   └── same packages (poller → lint → convert → Schematron → store/quarantine)
```

`packages/gifts` is **absent** after the first PR that wires tac2iwxxm to `/api/v1/convert`
(ADR-014).

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
| Backend API | Conversion, validation, auth (thin wrappers) | `apps/backend/` | tac2iwxxm, tac-validate, iwxxm-validate, auth, shared, vendor |
| Frontend | User UI (product/profile/version) | `apps/frontend/` | shared (types) |
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

- **Purpose**: Single HTTP API for health, conversion, validation, and authentication.
- **Inputs**: HTTP multipart/form (TAC + `product` + `profile` + version), JWT bearer tokens, env config.
- **Outputs**: JSON responses, IWXXM XML, auth session endpoints.
- **Algorithm**:
  1. Auth middleware validates JWT via Supabase (`packages/auth`).
  2. Conversion router may run **`tac-validate`**, then **`tac2iwxxm`** (bulletin split when
     needed) via adapters (replaces `gifts_adapter` in the gifts-delete PR — ADR-014).
  3. Validation router is a **thin wrapper** over **`packages/iwxxm-validate`** (WMO; combined
     WMO + iwxxm-us when `profile=iwxxm_us`).
- **Error handling**: HTTP 4xx for auth/validation; 5xx for conversion failures with structured errors.
- **Source**: REQ-004; F6 / ADR-014; S008 realtime amend.

### packages/tac2iwxxm

- **Purpose**: General TAC→IWXXM library (F6). Python public API → **bulletin split** (WMO AHL)
  → versioned IR → product plugins → profile plugins (`annex3` / `iwxxm_us`) → XML writer;
  library/CI metrics via companion validate packages.
- **Products (v1)**: AIRMET, METAR, SIGMET, SPECI, TAF, VAA, TCA.
- **Inputs**: TAC string/files **or bulletins**; `product`; `profile`; `iwxxm_version`; schema paths under vendor.
- **Outputs**: IWXXM XML bytes/strings (per report); metrics reports in tests/CI only (not convert API fields).
- **SoC**: **No** FastAPI or Supabase imports.
- **Runtime**: Pure Python v0; optional **Rust/PyO3** hotspots after benchmarks (not Cython).
- **License**: MIT.
- **IR**: Spec requires a **versioned IR**; concrete library (msgspec / pydantic / dataclasses)
  chosen in 04-tech-plan.
- **Source**: [feature-list.md](feature-list.md) F6; ADR-013; ADR-014;
  [context/general-tac-iwxxm-converter.md](context/general-tac-iwxxm-converter.md);
  [context/realtime-tac-ingest.md](context/realtime-tac-ingest.md).

### packages/tac-validate

- **Purpose**: TAC linting and shared **business-rule pack** for all seven product TAC forms
  (parse gate + rules). **Not** Schematron.
- **Inputs**: TAC text or bulletin fragments; product hint when known.
- **Outputs**: Structured issue list (severity, code, message, location).
- **SoC**: **No** FastAPI or Supabase imports.
- **Source**: feature-list F6/F2 amend; [context/realtime-tac-ingest.md](context/realtime-tac-ingest.md).

### packages/iwxxm-validate

- **Purpose**: F2 engine — XSD + Schematron validation of IWXXM XML against vendored schemas.
- **Inputs**: IWXXM XML; `iwxxm_version`; optional `profile` (US catalogs when `iwxxm_us`).
- **Outputs**: Validation report (pass/fail + messages).
- **SoC**: **No** FastAPI or Supabase imports; **read-only** consumption of `vendor/schemas/*`.
- **Source**: feature-list F2; [context/realtime-tac-ingest.md](context/realtime-tac-ingest.md).

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

- **Purpose**: Converter UI and auth screens.
- **F6 delta**: **Product** select (7 values + auto-detect), **profile** select
  (`annex3` | `iwxxm_us`), existing **version** control; values passed via
  `conversion_params` / multipart to `/api/v1/convert`.
- **F5**: Unchanged — METAR/SPECI work sessions only (not extended to other products in F6 v1).
- **Source**: F6-R5; feature-list F6.

### Runtime configuration (`config/`)

- **Purpose**: Non-secret per-environment settings (URLs, CORS, validation flags).
- **Files**: `config/local.json`, `config/prod.json` (committed).
- **Frontend**: Static host serves `/config.json` (prod copy + publishable key injected at deploy).
- **Source**: [config-spec.md](config-spec.md), S003 session.

### F5 — User METAR work history (S004 / EV-004)

- **Purpose**: Durable per-user converter **work history** (current session state, not an
  append-only audit log) in Supabase Postgres, linked to `auth.users` via RLS; exposed through
  backend REST (not direct browser DB access).
- **Table** (proposed): `metar_work_sessions`
  - `user_id`, `status` (`draft` | `wip` | `finished` | `failed`)
  - `title` (auto ICAO + time; user-renamable)
  - `manual_tac`, `pending_files` JSONB (name + inline TAC content)
  - `converted_results`, `errors`, `issues`, `conversion_params` JSONB
  - `kv_upload_key` (nullable — set when send succeeds)
  - `deleted_at` (nullable — soft delete / trash)
  - `created_at`, `updated_at`
- **RLS**: `auth.uid() = user_id` for user CRUD; admin read via `is_admin()` policy; `service_role` for pg_cron Draft purge.
- **Business rules**: Unchanged from S004 (see prior F5 section history in decisions log).
- **F6**: Do not extend F5 to non-METAR products in v1.
- **Frontend**: Debounced draft sync (~3s); converter sidebar (**5 recent**) + `/history` (My METARs);
  `/admin/work-sessions` read-only admin browse; #555 error log panel.
- **Source**: F5 requirements delta 2026-06-23; [metar-work-history.md](context/metar-work-history.md)

### F7 — Multi-product operator entry (Planned)

- **Purpose**: Operator UI / sessions for all seven F6 products sharing the unified pipeline below.
- **Status**: **Planned — not this build**. F5 remains METAR/SPECI-only.
- **Source**: [feature-list.md](feature-list.md) F7; [context/realtime-tac-ingest.md](context/realtime-tac-ingest.md).

### F8 — Near-realtime ingest (Planned)

- **Purpose**: Continuous ingest → unified pipeline → store + push; quarantine on fail;
  &lt;5–15s target; scale workers. Future dashed component: Render Background Worker.
- **Status**: **Planned — not this build**. Auth, sinks, AMHS/SWIM adapters postponed.
- **Source**: [feature-list.md](feature-list.md) F8; [context/realtime-tac-ingest.md](context/realtime-tac-ingest.md).

## Data Flow

### Unified convert/validate pipeline (API now; F7/F8 later)

| Stage | Input | Transformation | Output |
|-------|-------|----------------|--------|
| 0. Unit | TAC or WMO AHL bulletin | Detect / accept | Ingest unit |
| 1. Split | Bulletin | `tac2iwxxm` bulletin splitter | One TAC report each |
| 2. TAC lint | TAC report | `tac-validate` | Issues or pass |
| 3. Convert | TAC + product + profile + version | `tac2iwxxm` | IWXXM XML |
| 4. IWXXM validate | IWXXM XML (+ profile) | `iwxxm-validate` (XSD + Schematron) | Pass or fail report |
| 5a. API path | Results | Backend JSON | UI / client |
| 5b. F8 later | Pass | Store + push | Published artifact |
| 5c. F8 fail | Fail | Quarantine (no publish) | Error record |

### UI / session overlay (current)

| Stage | Input | Transformation | Output |
|-------|-------|----------------|--------|
| U1. Upload | TAC files/text + product/profile/version | Frontend form | POST /api/v1/convert |
| U2. Auth | JWT | packages/auth middleware | Authorized request context |
| U3–U4 | — | Unified pipeline stages 0–4 | IWXXM + validation |
| U5. Display | JSON response | Frontend render | Copy/download UI |
| U6. Persist (F5) | TAC + results + errors | Backend upsert → Postgres | Session row (Draft/WIP/Finished/Failed) |
| U7. Send link (F5) | KV upload success | Store `kv_upload_key` on session | Finished status |

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
- F7 not required for this cycle; F8 worker **is** in scope (ADR-018).
- PyO3 native extension + ADR-016 benches hard-pass before F6 cutover (ADR-017).

### Assumptions

- wmo-im continues publishing tagged releases on GitHub.
- NOAA/MDL continues to publish IWXXM-US schemas suitable for vendor pinning.
- Supabase auth model unchanged; only service topology / converter package changes.

## Security & Privacy

- Supabase **publishable** key available to browser via runtime `/config.json`; **secret** key
  server-only (`SUPABASE_SECRET_KEY`) — Auth Admin scripts only (ADR-010).
- Admin API routes use caller JWT + RLS (`is_admin()`), not secret-key bypass.
- CORS from `config.*.api.corsOrigins` on backend.
- Minimal `.env` — five secrets; `make env-check` validates sync across local/Render/CI.
- Vendor trees (WMO + IWXXM-US) are public schema data — **no new secrets** for F6 packages.
- F8 worker adds secrets: poller HTTPS URL + Supabase **service role** JWT (ADR-018).
- TAC/IWXXM still flow through existing API auth model (guest convert policy unchanged).

## Performance Characteristics

| Operation | Expected Time | Notes |
|-----------|---------------|-------|
| Single METAR/SPECI Annex-3 conversion | < 2s | Typical (unchanged) |
| Unified pipeline (lint + convert + Schematron) | TBD | Target &lt;5–15s informs F8; measure in 04 |
| Batch file upload (10 files) | < 10s | Depends on size |
| SIGMET / AIRMET / VAA / TCA / US-profile | TBD | May exceed METAR until measured (04) |
| Vendor sync PR | Minutes | CI job; not user-facing |

## Known Limitations

- Big-bang migration required coordinated downtime or feature freeze during merge PR (historical).
- **Hard cutover**: first tac2iwxxm wire-up PR deletes gifts — production METAR path depends on
  tac2iwxxm immediately (gate with M-parity / goldens).
- US AIRMET/SIGMET fixture depth may lag METAR/TAF.
- PyO3 is **required before cutover** (ADR-017); pure Python may exist during M3–M4 only.
- Accuracy metrics are library/CI only — not exposed on convert API responses in v1.
- Scheduled vendor PRs require review before production pins update.
- F5 not extended to non-METAR products in F6 v1.
- F7, public machine-ingest auth, push sinks, AMHS/SWIM — out of this build (F8 worker in).

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
