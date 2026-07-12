# Feature List

> **Project**: METAR to IWXXM Converter
> **Repository**: https://github.com/joseph-c-mcguire/metar-to-IWXXM
> **Last updated**: 2026-06-23

## Summary

| # | Feature | Status | Category | Source |
|---|---------|--------|----------|--------|
| F1 | METAR → IWXXM conversion | Implemented | Product | README, backend conversion pipeline |
| F2 | IWXXM validation | Implemented | Product | backend validation routers |
| F3 | Airport data services | Implemented | Product | OpenAIP / reconciliation services |
| F4 | IWXXM version handling | Implemented | Product | docs/domain/iwxxm/IWXXM_VERSION_SWITCHING.md |
| F5 | User METAR work history | Planned | Product | docs/context/metar-work-history.md, S004 |
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
- **Outputs**: IWXXM XML per input; batch ZIP download; optional database upload ("send").
- **UI actions** (main converter):
  - **Convert** — TAC → IWXXM only.
  - **Convert&Send** — TAC → IWXXM then upload to primary database with IWXXM format (fixed defaults; no dialog).
  - **Upload to Database** — upload previously converted files with configurable format/destination (dialog).
- **#555 UX (EV-004)**: On **successful** convert, replace (not append) result cards; show collapsible
  error log panel from API `errors`/`issues` on failure or partial success (also persisted on F5 session row).
- **Custom output filename (EV-005 / #664)**: Optional "Output filename" input near the manual TAC
  textarea. When set, manual-input results download as `<base>.xml` (multi-line: `<base>_1.xml`,
  `<base>_2.xml`, …) and the batch ZIP archive is named `<base>.zip`; blank ⇒ `manual_input` default.
  Applies to **manual input only** (file-upload outputs keep their filename). The name persists across
  reload (guest + logged-in) via the existing `conversion_params` payload — no API/schema change.
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
- **Source**: docs/guides/OPENAIP_INTEGRATION_PLAN.md, backend services

### F4: IWXXM Version Handling

- **What it does**: Supports multiple IWXXM release lines (e.g. 2023-1, 2025-2) with version-aware formatting.
- **Inputs**: Target version parameter, METAR TAC.
- **Outputs**: Version-appropriate IWXXM XML.
- **Limitations**: Only versions present in `vendor/schemas/` snapshots.
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
  for soft-deleted sessions; separate **admin page** for read-only browse of all users' sessions.
- **Retention**: Auto-purge **Draft** rows older than 30 days (Supabase pg_cron); WIP/Finished/Failed kept until user soft-deletes.
- **Admin**: Existing admin role — read-only browse on dedicated admin page (no edit/delete in v1).
- **Delivery**: Merged into **S004 / EV-004** with remaining #555 UX (replace results + error log panel) and S003 Supabase config.
- **Limitations**: Persistence requires login (guests may convert without save; login auto-creates Draft
  from in-browser content); no append-only status audit trail in v1; WIP stays WIP when input edited
  before re-convert; Finished sessions disable convert/send (use **New METAR**); send failure keeps
  **WIP**; last-write-wins on multi-tab auto-save; no backfill from existing KV uploads; backend REST
  only (no direct browser Postgres writes).
- **Source**: GitHub #555 follow-on, requirements interview 2026-06-23 (F5 delta)

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
- **S003 security delta (2026-06-23)**: Publishable/Secret keys, runtime `config.json`, env sync
  (Render ↔ Supabase ↔ local). ADR-010.
- **Limitations**: Internal Docker/Render topology changes; external frontend contract preserved.
- **Source**: REQ-004, REQ-009

### M5: Workspace Tooling

- **What it does**: Root Makefile orchestrates uv (Python) and pnpm (JS) workspaces; pre-commit
  runs fast quality gates locally; GitHub Actions runs the full validate + test + deploy pipeline.
- **Inputs**: `pyproject.toml` workspace root; `pnpm-workspace.yaml`; `.pre-commit-config.yaml`.
- **Outputs**:
  - Local: `make dev`, `make test`, `make lint`, `make ci` (full suite)
  - Local fast: `pre-commit run` — ruff format/check, prettier, eslint, basedpyright/tsc,
    gitleaks, actionlint/yamllint (on `.github/` changes)
  - CI: single `ci-cd.yml` with ≤3 jobs on PR (validate → test; deploy on main push only)
- **CI job layout** (EV-002):
  | Job | Checks |
  |-----|--------|
  | validate | format, lint, typecheck, gitleaks, yaml lint, config-guard, frontend npm audit |
  | test | matrix unit+coverage (backend, auth, gifts, frontend, shared), integration, Codecov |
  | deploy | Docker build/push + Render hooks (main only) |
- **Dual-run policy**: fast checks run in pre-commit locally **and** in CI validate job (defense in depth).
- **Source**: REQ-005; EV-002

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
| F5 | Yes | Yes | Yes | Yes |
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
