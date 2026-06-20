# User Journeys

> **Project**: METAR to IWXXM Converter
> **Source**: feature-list.md, requirements interview 2026-06-14
> **Last updated**: 2026-06-14

Product-facing journeys (UJ-*) describe end-user flows. Developer journeys (UJ-DEV-*)
describe monorepo workflows introduced by migration features M1–M6.

## Journey Index

| ID | Journey | Entry point | Feature | E2E tier |
|----|---------|-------------|---------|----------|
| UJ-001 | Convert METAR via UI | apps/frontend | F1 | T2 (local stack) |
| UJ-002 | Validate IWXXM output | apps/frontend / API | F2 | T2 |
| UJ-003 | Register and login | apps/frontend | F1 (auth) | T2 |
| UJ-DEV-001 | Clone and run monorepo | `git clone` + `make dev` | M1, M5 | T0 |
| UJ-DEV-002 | Sync vendor schemas | Scheduled Action / manual script | M2, M6 | CI |
| UJ-DEV-003 | Merge GIFTs upstream (manual) | Maintainer workflow | M3 | CI |
| UJ-OPS-001 | Deploy two-service Render stack | render.yaml | M4 | T3 (staging) |

**E2E tiers**:

- **T0** — Unit + package tests; no running services.
- **T2** — Local docker-compose or `make dev`; Playwright in `apps/e2e/`.
- **T3** — Deployed Render staging/production.

Run local E2E: `make tests:e2e` (target command — to be implemented in 04-tech-plan)

---

## Product Journeys

### UJ-001: Convert METAR via UI

**Actor**: Authenticated user

**Goal**: Upload or paste METAR TAC and receive IWXXM XML.

**Steps**:

1. Open frontend in browser.
2. Log in (UJ-003).
3. Drag-drop `.tac` file or paste manual text.
4. Submit conversion.
5. View, copy, or download IWXXM result.

**Acceptance**: At least one METAR converts without error; output passes schema/Schematron validation for the selected IWXXM version.

**Automated tests**: `apps/e2e/tac-file-conversion.e2e.spec.ts` (T2)

**Browser wiring**: Frontend calls API on configured `VITE_API_BASE_URL`; CORS must allow frontend origin (H4).

---

### UJ-002: Validate IWXXM Output

**Actor**: Authenticated user or API client

**Goal**: Confirm generated XML passes schema/Schematron validation.

**Steps**:

1. Obtain IWXXM XML from conversion (UJ-001).
2. Trigger validation endpoint or UI action.
3. Review pass/fail and error messages.

**Acceptance**: Valid sample METAR produces validation pass for selected IWXXM version.

**Automated tests**: backend validation tests + E2E where exposed in UI (T2)

---

### UJ-003: Register and Login

**Actor**: New or returning user

**Goal**: Obtain session/JWT to access protected conversion endpoints.

**Steps**:

1. Navigate to login page.
2. Register or enter credentials.
3. Backend (via packages/auth) validates with Supabase.
4. Frontend stores session; subsequent API calls include JWT.

**Acceptance**: Protected `/api/v1/*` returns 401 without token, 200 with valid token.

**Automated tests**: `apps/e2e/auth.e2e.spec.ts`, `apps/e2e/workflow-auth-admin-readiness.e2e.spec.ts` (T2)

**Post-migration note**: Auth routes served from same backend origin; frontend may use single API base URL.

---

## Developer Journeys

### UJ-DEV-001: Clone and Run Monorepo

**Actor**: Developer

**Goal**: Start full stack from single clone without submodules.

**Steps**:

1. `git clone https://github.com/joseph-c-mcguire/metar-to-IWXXM.git`
2. `cp .env.example .env` — fill Supabase vars.
3. `make install` — uv sync + pnpm install across workspaces.
4. `make dev` — backend, frontend, optional docker-compose.
5. Verify `curl localhost:<api-port>/health` and frontend loads.

**Acceptance**: No `git submodule update` required; health checks pass.

**Automated tests**: CI job `monorepo-smoke` (TC-M001)

---

### UJ-DEV-002: Sync Vendor Schemas

**Actor**: Maintainer (or scheduled bot)

**Goal**: Update read-only iwxxm snapshots when wmo-im releases new tags.

**Steps**:

1. Scheduled Action detects new wmo-im release tag.
2. Action runs vendor sync script; updates `vendor/schemas/*` and `vendor/manifest.json`.
3. Opens PR with diff + manifest bump.
4. Maintainer reviews; CI runs validation tests against new schemas.
5. Merge updates pinned versions.

**Acceptance**: manifest.json SHA/tags match vendored tree; validation tests pass.

**Automated tests**: `tests/vendor/test_manifest_integrity.py` (TC-M002)

---

### UJ-DEV-003: Merge GIFTs Upstream (Manual)

**Actor**: Maintainer

**Goal**: Pull mgoberfield/GIFTs changes into `packages/gifts/` when desired.

**Steps**:

1. Maintainer checks mgoberfield/GIFTs for changes worth merging.
2. Merges upstream into `packages/gifts/` (merge or cherry-pick).
3. CI runs GIFTs + conversion test suite.
4. Maintainer resolves conflicts if fork diverged.

**Acceptance**: Conversion regression tests pass after merge (TC-M003).

**Automated tests**: packages/gifts test suite + backend conversion tests (TC-M003)

---

## Operations Journeys

### UJ-OPS-001: Deploy Two-Service Render Stack

**Actor**: Release engineer

**Goal**: Deploy merged backend (API+auth) and static frontend to Render.

**Steps**:

1. Merge to `main`; CI builds Docker image for API and static bundle for frontend.
2. Render deploys API service (port binding `0.0.0.0:$PORT`).
3. Render deploys static site with `VITE_*` pointing to API URL.
4. Verify H1 health, H4 CORS preflight, H5 bundle URLs.

**Acceptance**: UJ-001 succeeds against staging URL.

**Automated tests**: deploy smoke H1–H5 per connectivity-gates.md (T3)

**Redeploy order**: API first (CORS origins), then frontend (VITE_* rebuild).
