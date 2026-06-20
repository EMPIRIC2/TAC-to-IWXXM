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
- **Source**: REQ-010.

## Data Flow

| Stage | Input | Transformation | Output |
|-------|-------|----------------|--------|
| 1. Upload | TAC files/text | Frontend form | POST /api/v1/convert |
| 2. Auth | JWT | packages/auth middleware | Authorized request context |
| 3. Convert | TAC | GIFTs + vendor schemas | IWXXM XML |
| 4. Validate | IWXXM XML | Schematron/XSD | Validation result |
| 5. Display | JSON response | Frontend render | Copy/download UI |

## Monorepo Migration

See [migration-plan.md](migration-plan.md) for step-by-step big-bang procedure.

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

- Supabase credentials remain server-side only (packages/auth in backend process).
- CORS configured on backend for frontend origin (`METAR_CORS_ORIGINS`).
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

## References

- docs/ARCHITECTURE.md (pre-migration product architecture)
- [ARCHIVE/pre-monorepo-deploy/AUTH_MIDDLEWARE_ARCHITECTURE.md](ARCHIVE/pre-monorepo-deploy/AUTH_MIDDLEWARE_ARCHITECTURE.md) (superseded by M4 — see ADR-002)
- docs/requirements-decisions.md
