# Technical Specification

> **Project**: METAR to IWXXM Converter
> **Repository**: https://github.com/joseph-c-mcguire/metar-to-IWXXM
> **Version**: monorepo migration (pre-implementation)
> **Last updated**: 2026-06-14

## Overview

METAR to IWXXM converts aviation METAR/SPECI TAC messages to WMO IWXXM XML using the GIFTs
library and authoritative IWXXM schema bundles. The system is migrating from a submodule-heavy
multi-repo layout to a **single-git monorepo** with `apps/` (deployables), `packages/`
(libraries), and `vendor/` (read-only upstream snapshots).

## System Architecture

### Runtime (post-migration)

```
Browser
   │
   ▼
apps/frontend (static — Render static site or Vite dev)
   │  VITE_* → API base URL
   ▼
apps/backend (FastAPI — Render web service)
   ├── packages/auth (Supabase JWT middleware, inlined)
   ├── packages/gifts (IWXXM generation)
   └── vendor/schemas/* (read-only XSD/Schematron)
```

### Repository (target tree)

```
metar-to-IWXXM/
├── apps/
│   ├── backend/          # FastAPI — conversion, validation, auth routes
│   ├── frontend/         # React/Vite UI
│   └── e2e/              # Playwright + cross-service integration
├── packages/
│   ├── auth/             # Supabase auth library (not a deployable)
│   ├── gifts/            # GIFTs fork — editable; manual upstream merges
│   └── shared/           # API types, env helpers, constants
├── vendor/
│   ├── manifest.json     # Pins wmo-im repo + tag/SHA per schema bundle
│   └── schemas/
│       ├── iwxxm/
│       ├── iwxxm-codelists/
│       ├── iwxxm-modelling/
│       └── iwxxm-translation/
├── pyproject.toml        # uv workspace root
├── pnpm-workspace.yaml
├── Makefile
└── docker-compose.yml    # backend + frontend (no separate auth service)
```

### Component Overview

| Component | Purpose | Location | Dependencies |
|-----------|---------|----------|--------------|
| Backend API | Conversion, validation, auth | `apps/backend/` | gifts, auth, shared, vendor |
| Frontend | User UI | `apps/frontend/` | shared (types) |
| E2E workspace | Cross-app tests | `apps/e2e/` | backend, frontend |
| Auth library | Supabase middleware | `packages/auth/` | supabase-py |
| GIFTs | TAC → IWXXM | `packages/gifts/` | vendor schemas |
| Shared | Cross-cutting utils/types | `packages/shared/` | — |
| Vendor schemas | Authoritative IWXXM SoT | `vendor/schemas/*` | wmo-im snapshots |
| Work history (F5) | Per-user METAR session persistence | Supabase Postgres + `apps/backend` router | auth, shared |

## Component Details

### apps/backend

- **Purpose**: Single HTTP API for health, conversion, validation, and authentication.
- **Inputs**: HTTP multipart/form, JWT bearer tokens, env config.
- **Outputs**: JSON responses, IWXXM XML, auth session endpoints (formerly on auth service).
- **Algorithm**:
  1. Auth middleware validates JWT via Supabase (packages/auth).
  2. Conversion router normalizes TAC and invokes GIFTs.
  3. Validation router loads schemas from `vendor/schemas/`.
- **Error handling**: HTTP 4xx for auth/validation; 5xx for conversion failures with structured errors.
- **Source**: Current `backend/`, `auth/` — merged per REQ-004.

### packages/gifts

- **Purpose**: IWXXM serialization library (fork of mgoberfield/GIFTs).
- **Inputs**: Normalized METAR TAC, IWXXM version, schema paths pointing to vendor.
- **Outputs**: IWXXM XML strings.
- **Upstream sync**: Manual merge from mgoberfield/GIFTs when maintainers choose; no scheduled Action (REQ-014, audit 02-verify-plan).
- **Source**: Current `GIFTs/` submodule.

### vendor/schemas

- **Purpose**: Read-only copies of wmo-im schema repositories at pinned tags.
- **Inputs**: `vendor/manifest.json` pins; sync script/Action fetches release artifacts.
- **Outputs**: XSD, Schematron, codelist files consumed by GIFTs and validation.
- **Constraints**: **No direct edits** in monorepo except manifest version bumps via sync PRs.
- **Source**: REQ-002, REQ-012.

### packages/shared

- **Purpose**: Shared API types (OpenAPI-derived TS), env URL helpers, constants (CORS origins, version enums).
- **Config loader (S003)**: Loads `config/{local,prod}.json` by `METAR_CONFIG_ENV`; exposes merged
  config to Python and TypeScript; secrets resolved from env only.
- **Source**: REQ-010, ADR-010.

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
- **Business rules**:
  - **History model**: Current state on one row per session — no append-only status audit table in v1.
  - Multiple **Draft** (and **Failed**, same slot rules as Draft) sessions per user; at most one **WIP**.
  - Guests may use converter without login; persistence (auto-save, history) requires auth.
  - On login, if the converter has unsaved guest input, **auto-create a new Draft** from current
    state before resume logic; then auto-resume most recent non-Finished, non-deleted session
    (or leave the new Draft active if none to resume).
  - **WIP** rows stay **WIP** when the user edits TAC/files before re-convert (content updates;
    IWXXM may be stale until re-convert).
  - **New METAR** button creates a fresh Draft without deleting prior sessions.
  - Sidebar click loads that session into the converter; an existing **WIP** row stays **WIP** in DB.
  - **Finished** only after successful operational DB send; convert-only stays **WIP**; send failure stays **WIP**.
  - **Finished** sessions are read-only when opened from history (no re-edit in v1); Convert and
    Convert&Send are disabled — user must click **New METAR** to start fresh work.
  - Auto-save: last-write-wins across tabs/devices (no conflict UI in v1).
  - Draft TTL: pg_cron hard-deletes Draft rows where `updated_at < now() - 30 days`.
  - Soft-delete: user trash with 30-day restore window, then hard-delete.
- **Frontend**: Debounced draft sync (~3s); converter sidebar (**5 recent**) + `/history` (My METARs) with status/date filters;
  `/admin/work-sessions` read-only admin browse; #555 error log panel + persisted `errors`/`issues` on row.
- **Source**: F5 requirements delta 2026-06-23; [metar-work-history.md](context/metar-work-history.md)

## Data Flow

| Stage | Input | Transformation | Output |
|-------|-------|----------------|--------|
| 1. Upload | TAC files/text | Frontend form | POST /api/v1/convert |
| 2. Auth | JWT | packages/auth middleware | Authorized request context |
| 3. Convert | TAC | GIFTs + vendor schemas | IWXXM XML |
| 4. Validate | IWXXM XML | Schematron/XSD | Validation result |
| 5. Display | JSON response | Frontend render | Copy/download UI |
| 6. Persist (F5) | TAC + results + errors | Backend upsert → Postgres | Session row (Draft/WIP/Finished/Failed) |
| 7. Send link (F5) | KV upload success | Store `kv_upload_key` on session | Finished status |

## Monorepo Migration

See [migration-plan.md](ops/migration-plan.md) for step-by-step big-bang procedure.

### Submodule → monorepo mapping

| Current submodule | Target | Strategy |
|-------------------|--------|----------|
| `schemas/iwxxm` | `vendor/schemas/iwxxm` | Snapshot from wmo-im/iwxxm |
| `schemas/iwxxm-codelists` | `vendor/schemas/iwxxm-codelists` | Snapshot |
| `schemas/iwxxm-modelling` | `vendor/schemas/iwxxm-modelling` | Snapshot |
| `data/iwxxm-translation` | `vendor/schemas/iwxxm-translation` | Snapshot |
| `GIFTs` | `packages/gifts` | Full source; manual upstream merges |
| `frontend` | `apps/frontend` | Full source in monorepo |
| `auth/` (root, not submodule) | `packages/auth` | Library; routes in backend |
| `backend/` | `apps/backend` | Move + wire workspace deps |

### Legacy repositories

Separate GitHub repos (Metartoiwxxmfrontend, GIFTs fork, iwxxm forks) will be **archived read-only** after stable production deploy (REQ-019). Monorepo is the sole active development target.

## Constraints & Assumptions

### Hard Constraints

- iwxxm / iwxxm-* content is authoritative from wmo-im — read-only in vendor/.
- Single git clone must be sufficient for local dev (`git clone` — no `--recurse-submodules`).
- Render deploys two services: API (backend+auth) + static frontend (REQ-009).

### Assumptions

- wmo-im continues publishing tagged releases on GitHub.
- mgoberfield/GIFTs remains the GIFTs upstream for manual merges when chosen (REQ-014).
- Supabase auth model unchanged; only service topology changes.

## Security & Privacy

- Supabase **publishable** key available to browser via runtime `/config.json`; **secret** key
  server-only (`SUPABASE_SECRET_KEY`) — Auth Admin scripts only (ADR-010).
- Admin API routes use caller JWT + RLS (`is_admin()`), not secret-key bypass.
- CORS from `config.*.api.corsOrigins` on backend.
- Minimal `.env` — five secrets; `make env-check` validates sync across local/Render/CI.
- Vendor trees are public schema data — no secrets.

## Performance Characteristics

| Operation | Expected Time | Notes |
|-----------|---------------|-------|
| Single METAR conversion | < 2s | Typical |
| Batch file upload (10 files) | < 10s | Depends on size |
| Vendor sync PR | Minutes | CI job; not user-facing |

## Known Limitations

- Big-bang migration requires coordinated downtime or feature freeze during merge PR.
- GIFTs upstream merges are manual — no scheduled sync (REQ-014).
- Scheduled vendor PRs (wmo-im only) require review before production pins update.

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
