# Feature List

> **Project**: METAR to IWXXM Converter
> **Repository**: https://github.com/joseph-c-mcguire/metar-to-IWXXM
> **Last updated**: 2026-06-14

## Summary

| # | Feature | Status | Category | Source |
|---|---------|--------|----------|--------|
| F1 | METAR → IWXXM conversion | Implemented | Product | README, backend conversion pipeline |
| F2 | IWXXM validation | Implemented | Product | backend validation routers |
| F3 | Airport data services | Implemented | Product | OpenAIP / reconciliation services |
| F4 | IWXXM version handling | Implemented | Product | docs/IWXXM_VERSION_SWITCHING.md |
| M1 | Monorepo layout (`apps/` + `packages/` + `vendor/`) | Planned | Platform | REQ-002–006 |
| M2 | Vendor snapshot sync (wmo-im iwxxm-*) | Planned | Platform | REQ-002, REQ-010 |
| M3 | GIFTs as in-repo package | Planned | Platform | REQ-003 |
| M4 | Auth merged into backend API | Planned | Platform | REQ-004 |
| M5 | Workspace tooling (uv + pnpm + Makefile) | Planned | Platform | REQ-005 |
| M6 | Vendor upstream sync (wmo-im iwxxm-*) | Planned | Platform | REQ-009 |

**Status key**: Implemented = production-ready, Planned = approved in requirements interview, Experimental = works but not validated

## Product Feature Details

### F1: METAR → IWXXM Conversion

- **What it does**: Converts METAR/SPECI TAC text (file upload or manual input) to IWXXM XML via GIFTs.
- **Inputs**: `.tac` / `.txt` files, manual TAC strings, optional conversion parameters.
- **Outputs**: IWXXM XML per input; batch ZIP download.
- **Limitations**: Depends on GIFTs and vendored IWXXM schemas for target version.
- **Source**: README, `backend/src/utilities/conversion.py`

### F2: IWXXM Validation

- **What it does**: Validates generated IWXXM against schemas and Schematron rules.
- **Inputs**: IWXXM XML, target IWXXM version.
- **Outputs**: Validation report (pass/fail + messages).
- **Limitations**: Schema bundles must match vendored snapshot version.
- **Source**: `backend/src/routers/validation.py`

### F3: Airport Data Services

- **What it does**: Enriches station metadata via OpenAIP and reconciliation across sources.
- **Inputs**: ICAO station identifiers, optional bbox queries.
- **Outputs**: Airport coordinates, elevation, reconciled metadata.
- **Limitations**: External API availability and cache TTL.
- **Source**: docs/OPENAIP_INTEGRATION_PLAN.md, backend services

### F4: IWXXM Version Handling

- **What it does**: Supports multiple IWXXM release lines (e.g. 2023-1, 2025-2) with version-aware formatting.
- **Inputs**: Target version parameter, METAR TAC.
- **Outputs**: Version-appropriate IWXXM XML.
- **Limitations**: Only versions present in `vendor/schemas/` snapshots.
- **Source**: docs/IWXXM_VERSION_SWITCHING.md

## Platform Feature Details (Monorepo Migration)

### M1: Monorepo Layout

- **What it does**: Replaces six git submodules with a single-repo tree: `apps/`, `packages/`, `vendor/`.
- **Inputs**: Current submodule sources (frontend, GIFTs, iwxxm-*).
- **Outputs**: Big-bang PR removing `.gitmodules`; archived legacy GitHub repos.
- **Key parameters**:
  | Parameter | Default | Description |
  |-----------|---------|-------------|
  | `apps/backend` | FastAPI API + merged auth | Single deployable Python service |
  | `apps/frontend` | React/Vite UI | Static deployable |
  | `apps/e2e` | Playwright cross-app tests | Dedicated workspace |
  | `packages/auth` | Supabase middleware library | Imported by backend, not separate service |
  | `packages/gifts` | GIFTs fork source | uv workspace member |
  | `packages/shared` | Types + cross-app utils | TS + Python shared constants |
  | `vendor/schemas/*` | Read-only wmo-im snapshots | No local edits |
- **Limitations**: Big-bang cutover; no product feature rewrites in same effort (non-goal REQ-016).
- **Source**: REQ-006, REQ-007

### M2: Vendor Snapshot Sync

- **What it does**: Copies tagged releases from authoritative wmo-im repos into `vendor/schemas/` per `vendor/manifest.json`.
- **Inputs**: wmo-im GitHub releases/tags for iwxxm, iwxxm-codelists, iwxxm-modelling, iwxxm-translation.
- **Outputs**: Immutable vendored trees; manifest pins repo + tag/SHA.
- **Limitations**: Read-only — no monorepo commits to vendor content except sync PRs.
- **Source**: REQ-002, REQ-012

### M3: GIFTs In-Repo Package

- **What it does**: Moves GIFTs from submodule to `packages/gifts/` as uv workspace member.
- **Inputs**: Current GIFTs fork; upstream mgoberfield/GIFTs.
- **Limitations**: No automated upstream PRs; maintainers merge mgoberfield/GIFTs manually (REQ-014).
- **Source**: REQ-003, REQ-014

### M4: Auth Merged Into Backend

- **What it does**: Collapses auth microservice into backend app using `packages/auth` library.
- **Inputs**: Current `auth/` service code, Supabase env vars.
- **Outputs**: Two deployables (API + frontend); auth routes on same origin as API.
- **Limitations**: Internal Docker/Render topology changes; external frontend contract preserved.
- **Source**: REQ-004, REQ-009

### M5: Workspace Tooling

- **What it does**: Root Makefile orchestrates uv (Python) and pnpm (JS) workspaces.
- **Inputs**: `pyproject.toml` workspace root; `pnpm-workspace.yaml`.
- **Outputs**: `make dev`, `make test`, `make lint` at repo root.
- **Source**: REQ-005

### M6: Upstream Vendor Sync

- **What it does**: Scheduled GitHub Actions open PRs when wmo-im publishes new schema tags (vendor only).
- **Inputs**: wmo-im release tags for iwxxm-* repos.
- **Outputs**: PR updating `vendor/manifest.json` and `vendor/schemas/*`.
- **GIFTs**: Manual merges from mgoberfield/GIFTs only — not automated (REQ-014).
- **Source**: REQ-008, REQ-009

## Feature Matrix

| Feature | Web UI | CLI/API | CI | Render Deploy |
|---------|--------|---------|-----|---------------|
| F1 | Yes | Yes | Yes | Yes |
| F2 | Yes | Yes | Yes | Yes |
| F3 | Partial | Yes | Yes | Yes |
| F4 | Yes | Yes | Yes | Yes |
| M1–M6 | — | — | Yes | Yes |

## Non-Goals (Migration)

- No product feature rewrites during monorepo migration (REQ-016).
- No ongoing edits to authoritative iwxxm schema content in monorepo (vendor is read-only).
- No separate auth deployable after migration completes.

## Planned Features (Post-Migration)

| # | Feature | Priority | Complexity | Notes |
|---|---------|----------|------------|-------|
| P1 | OpenAPI → TS codegen in packages/shared | Medium | Low | After layout stabilizes |
| P2 | Path-filtered CI per app/package | Medium | Medium | Reduce CI time |
