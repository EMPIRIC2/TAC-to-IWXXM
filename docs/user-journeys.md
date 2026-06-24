# User Journeys

> **Project**: METAR to IWXXM Converter
> **Source**: feature-list.md, requirements interview 2026-06-14
> **Last updated**: 2026-06-23

Product-facing journeys (UJ-*) describe end-user flows. Developer journeys (UJ-DEV-*)
describe monorepo workflows introduced by migration features M1–M6.

## Journey Index

| ID | Journey | Entry point | Feature | E2E tier |
|----|---------|-------------|---------|----------|
| UJ-001 | Convert METAR via UI | apps/frontend | F1 | T2 (local) / **T3 (Render)** |
| UJ-002 | Validate IWXXM output | apps/frontend / API | F2 | T2 / **T3** |
| UJ-003 | Register and login | apps/frontend | F1 (auth) | T2 / **T3** |
| UJ-004 | Resume & browse METAR work history | apps/frontend | F5 | T2 / **T3** |
| UJ-DEV-001 | Clone and run monorepo | `git clone` + `make dev` | M1, M5 | T0 |
| UJ-DEV-002 | Sync vendor schemas | Scheduled Action / manual script | M2, M6 | CI |
| UJ-DEV-003 | Merge GIFTs upstream (manual) | Maintainer workflow | M3 | CI |
| UJ-OPS-001 | Deploy two-service Render stack | render.yaml | M4 | T3 (staging) |

**E2E tiers**:

- **T0** — Unit + package tests; no running services.
- **T2** — Local docker-compose or `make dev`; Playwright in `apps/e2e/`.
- **T3** — Deployed Render stack; Playwright + pytest against live URLs (manual `make test-live`).

Run local E2E: `make test-e2e-playwright`  
Run live E2E: `make test-live` (requires `.env` with `ADMIN_EMAIL` / `ADMIN_PASSWORD`)

**T3 URLs** (canonical):

| Role | Env var | URL |
|------|---------|-----|
| API | `LIVE_API_URL` | `https://metar-to-iwxxm-api.onrender.com` |
| Frontend | `LIVE_FRONTEND_URL` / `PLAYWRIGHT_BASE_URL` | `https://metar-to-iwxxm-frontend-v4-web.onrender.com` |

**Prerequisite for T3**: E2E-001 schema path fix must land before full UJ-002 validation passes live.

---

## Product Journeys

### UJ-001: Convert METAR via UI

**Actor**: User (authenticated for persistence; guests may convert without save — F5-R22)

**Goal**: Upload or paste METAR TAC and receive IWXXM XML.

**Steps**:

1. Open frontend in browser.
2. Optionally log in (UJ-003) — required for work history persistence (UJ-004).
3. Drag-drop `.tac` file or paste manual text.
4. Choose an action:
   - **Convert** — conversion only; view, copy, or download IWXXM result.
   - **Convert&Send** — conversion then immediate upload to primary database (IWXXM format, fixed defaults).
   - **Upload to Database** — upload already-converted files with format/destination options (dialog).
5. View conversion output; for send actions, confirm success/failure via toast.
6. **#555 (EV-004)**: On **successful** convert, result cards **replace** the prior batch (not append).
7. On convert failure or partial success, open collapsible **error log panel** from API `errors`/`issues`
   (also persisted on the active F5 session row when logged in).

**Acceptance**: At least one METAR converts without error; output passes schema/Schematron validation for the selected IWXXM version; successful convert clears prior result cards; error log is previewable on failure.

**Automated tests**: `apps/e2e/tac-file-conversion.e2e.spec.ts` (T2); `make test-live-e2e` (T3)

**T3 browser steps** (Render):

1. Open `https://metar-to-iwxxm-frontend-v4-web.onrender.com`.
2. Log in with real Supabase credentials (UJ-003).
3. Drag-drop `.tac` file or paste METAR text.
4. Submit conversion; verify IWXXM output displays.
5. Copy or download result.

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

**Automated tests**: backend validation tests + E2E where exposed in UI (T2); H3 pytest + H6 where exposed (T3)

**T3 note**: Live validation requires E2E-001 schema path fix; run after `make test-live-api` convert step produces XML.

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

**Automated tests**: `apps/e2e/auth.e2e.spec.ts`, `apps/e2e/workflow-auth-admin-readiness.e2e.spec.ts` (T2); `make test-live-e2e` (T3)

**T3 browser steps** (Render, `DISABLE_AUTH=false`):

1. Navigate to live frontend login page.
2. Enter `ADMIN_EMAIL` / `ADMIN_PASSWORD` from local `.env`.
3. Backend validates via Supabase at merged API (`POST /auth/login` on `LIVE_API_URL`).
4. Frontend stores session; subsequent `/api/v1/*` calls include JWT.

**Post-migration note**: Auth routes served from same backend origin; frontend uses single `VITE_API_BASE_URL`.

---

### UJ-004: Resume & Browse METAR Work History

**Actor**: Authenticated user (admin has read-only browse of all users' sessions)

**Goal**: Persist converter work across sessions; resume Draft/WIP/Failed work on login; review past Finished sends.

**Steps**:

1. Log in (UJ-003) — or continue as guest (convert only, no persistence).
2. On login, if the converter holds unsaved guest input, **auto-create a new Draft** from current
   state; then **auto-resume** the most recent non-Finished, non-deleted session (manual text + file
   queue restored from Postgres) unless the new Draft is the active session.
3. While typing or adjusting the file queue, **Draft auto-saves** to Supabase (via backend API, ~3s debounce after typing stops) when authenticated. Editing a **WIP** session before re-convert keeps status **WIP** (content updates; IWXXM may be stale).
4. Use **New METAR** to start a fresh Draft without losing prior sessions.
5. **Convert** or **Convert&Send**:
   - Full success without send → status **WIP** (at most one WIP per user; multiple Drafts still allowed).
   - Convert failure or partial failure → status **Failed** (stays Failed until user edits input and re-converts).
   - Successful send (Convert&Send or Upload to Database) → status **Finished**; row stores reference to KV upload key.
   - Send failure → status stays **WIP** (user may retry send).
6. Browse history via **compact sidebar** (5 recent) on the converter and **My METARs** page (filter by status + date range).
7. Click a sidebar/history row to **load** that session into the converter (existing WIP row unchanged in DB).
8. Optionally rename session (default title: first METAR ICAO + timestamp).
9. Open **Finished** sessions read-only (TAC, IWXXM, errors, KV reference — no edit in v1); Convert
   and Convert&Send disabled — use **New METAR** to start fresh.
10. Soft-delete unwanted sessions; restore from trash within 30 days.
11. **Admin**: separate admin page lists all users' sessions read-only.

**Acceptance**: Login → type → Draft persisted → convert → WIP → send → Finished; send failure leaves WIP; resume-on-login restores open work; Finished is read-only; admin can list all users' sessions read-only.

**Automated tests**: `apps/e2e/metar-work-history.e2e.spec.ts` (T2, planned); `make test-live-e2e` UJ-004 delta (T3)

**T3 browser steps** (Render):

1. Log in on live frontend.
2. Paste METAR text; wait for draft auto-save indicator.
3. Log out and back in; confirm input restored.
4. Convert; confirm WIP status in sidebar.
5. Convert&Send; confirm Finished status and history entry.

**Browser wiring**: Frontend calls `GET/POST/PATCH/DELETE /api/v1/work-sessions*` on configured API base URL; CORS must allow frontend origin (H4). Admin browse uses `/admin/work-sessions` with admin JWT.

**Relationship to UJ-001**: UJ-001 conversion/send actions drive F5 status transitions; S004 (#555)
delivers in-app error log UX; F5 persists that log on the session row.

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
5. Run `make test-live` for full T3 signoff (manual, pre-release).

**Acceptance**: UJ-001 succeeds against staging URL; `make test-live` all tiers green.

**Automated tests**: deploy smoke H1–H5 per connectivity-gates.md (T3); `make test-live` umbrella

**Redeploy order**: API first (CORS origins), then frontend (VITE_* rebuild).
