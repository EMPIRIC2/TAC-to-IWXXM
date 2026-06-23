# Test Plan

> **Project**: METAR to IWXXM Converter
> **Repository**: https://github.com/joseph-c-mcguire/metar-to-IWXXM
> **Last updated**: 2026-06-22 (EV-002 CI consolidation delta)

## Scope

**In scope**: Product features F1–F4; monorepo migration validation M1–M6; connectivity tiers H0c–H6 (local + live Render).

**Out of scope**: Performance benchmarking; load testing; wmo-im schema correctness (upstream responsibility); scheduled CI live jobs (manual/Makefile only).

### Live harness (delta 2026-06-22)

Unified manual live test harness against Render staging:

| Tier | Scope | Makefile target |
|------|-------|-----------------|
| H3 | Live API pytest (health, convert, validate, auth) | `make test-live-api` |
| H4–H5 | CORS preflight + frontend bundle URLs | `make test-live-connectivity` |
| H6 | Playwright UJ-001–003 against live frontend | `make test-live-e2e` |
| All | Sequential H4–H5 → H3 → H6 | `make test-live` |

**Prerequisite**: E2E-001 schema path regression must be resolved before H3 validate and full H6 UJ-002 pass (see [e2e-report.md](e2e-report.md)).

**CI policy**: Manual/local only — no GitHub Actions live job (Render cold-start + secrets).

**Canonical URLs** (see [staging-secrets-matrix.md](staging-secrets-matrix.md)):

- `LIVE_API_URL` — `https://metar-to-iwxxm-api.onrender.com`
- `LIVE_FRONTEND_URL` — `https://metar-to-iwxxm-frontend-v4-web.onrender.com`

## User Journeys (E2E)

| Journey | Feature | Local E2E module | Live E2E | Test plan TC |
|---------|---------|------------------|----------|--------------|
| UJ-001 | F1 | `apps/e2e/tac-file-conversion.e2e.spec.ts`, `apps/e2e/tac-file-upload-database.e2e.spec.ts` (Convert&Send one-click) | `make test-live-e2e` (H6) | TC-001, TC-LIVE-001 |
| UJ-002 | F2 | backend validation tests + UI if exposed | H3 validate + H6 where exposed | TC-002, TC-LIVE-002 |
| UJ-003 | F1 | `apps/e2e/auth.e2e.spec.ts` | `make test-live-e2e` (H6) | TC-003, TC-LIVE-003 |

**Admin dashboard E2E locators**: Each admin panel card (`h3`) and active panel body (`h2`) share the
same title (e.g. `User Approvals`). Use `.first()` for card-only checks on the default approval view;
use `.nth(1)` after clicking a card to assert the panel content heading.

| UJ-DEV-001 | M1,M5 | CI monorepo-smoke job | — | TC-M001 |
| UJ-DEV-002 | M2 | vendor manifest integrity tests | — | TC-M002 |
| UJ-DEV-003 | M3 | gifts + conversion regression | — | TC-M003 |
| UJ-OPS-001 | M4 | deploy smoke H1–H5 | Render staging | TC-OPS-001 |

## Connectivity & Wiring

| Tier | Scope | Command |
|------|-------|---------|
| H0c | CORS policy (in-process) | `pytest apps/backend/tests/unit/test_cors_policy.py` |
| H0i | Cross-service integration | `pytest apps/backend/tests/integration` |
| H3 | Live API smoke (pytest) | `make test-live-api` |
| H4 | Live CORS preflight | `make test-live-connectivity` |
| H5 | Frontend bundle URLs | `make test-live-connectivity` |
| H6 | Live Playwright UJ-001–003 | `make test-live-e2e` |

**Post-migration**: Single API origin simplifies CORS — auth routes on same host as `/api/v1/*`.

**Env wiring** (see config-spec artifact):

- `VITE_API_BASE_URL` — frontend build-time API URL
- `METAR_CORS_ORIGINS` — backend allowed browser origins
- `LIVE_API_URL` — live pytest API base (replaces `STAGING_API_URL`)
- `LIVE_FRONTEND_URL` — live Playwright base + CORS origin (replaces `STAGING_FRONTEND_*`)
- `ADMIN_EMAIL` / `ADMIN_PASSWORD` — runtime JWT via `POST /auth/login` (local `.env` only)

## Test Strategy

| Level | Framework | Scope | Run Command | Location |
|-------|-----------|-------|-------------|----------|
| Unit | pytest / Vitest | packages/*, apps/backend, apps/frontend components | `make test-unit` | per workspace |
| Integration | pytest | API + auth + conversion | `make test-integration` | apps/backend/tests |
| E2E (T2) | Playwright | UJ-001–003 local stack | `make test-e2e-playwright` | apps/e2e/ |
| Live E2E (T3) | Playwright + pytest | UJ-001–003 on Render | `make test-live` | apps/e2e/ + live pytest |
| Vendor | pytest | manifest + schema presence | `pytest tests/vendor` | tests/vendor |
| CI | GitHub Actions | validate + test (matrix) + deploy; path filters deferred (P2) | `.github/workflows/ci-cd.yml` | root |
| Pre-commit | pre-commit framework | fast gates (format/lint/typecheck/secrets/yaml) | `.pre-commit-config.yaml` | root |

**Coverage**: 95% on all packages and apps (ADR-007) — pytest for Python, Vitest for frontend.

## Migration Test Cases

### TC-M001: Monorepo Clone Smoke

- **Objective**: Verify single clone builds and tests without submodules.
- **Preconditions**: Clean environment; no `.gitmodules`.
- **Steps**:
  1. Clone repo.
  2. `make install && make test-unit`.
  3. `make dev` (or docker-compose) and hit `/health`.
- **Pass criteria**: Health 200; core unit tests green.
- **Source**: UJ-DEV-001

### TC-M002: Vendor Manifest Integrity

- **Objective**: `vendor/manifest.json` pins match checked-in tree checksums.
- **Steps**:
  1. Run manifest validation script/test.
  2. Confirm each schema bundle directory exists and matches pinned tag/SHA.
- **Pass criteria**: No drift between manifest and tree.
- **Source**: UJ-DEV-002

### TC-M003: GIFTs Conversion Regression

- **Objective**: Representative METAR set converts identically pre/post migration.
- **Preconditions**: Golden fixtures in `test-data/`.
- **Steps**:
  1. Run conversion on fixture set.
  2. Compare normalized canonical XML (whitespace/order insensitive).
- **Pass criteria**: Zero unexpected diffs (normalized canonical XML comparison).
- **Source**: UJ-DEV-003

### TC-M004: No Submodule References

- **Objective**: Big-bang PR removes all submodule machinery.
- **Steps**:
  1. Assert `.gitmodules` absent.
  2. Assert CI/docs contain no `git submodule` instructions.
  3. Grep for `.git/modules` paths in scripts.
- **Pass criteria**: All checks pass.
- **Source**: M1 layout / Phase 4 finalize (T11.1)

### TC-M005: Auth Merge Behavior

- **Objective**: Auth endpoints available on backend; separate auth service removed from compose.
- **Steps**:
  1. `POST /auth/login` (or equivalent) on backend port.
  2. Use JWT on `/api/v1/convert`.
  3. Confirm docker-compose has two app services (backend, frontend) not three.
- **Pass criteria**: UJ-003 passes; no auth container required.
- **Source**: M4, REQ-004

## Product Test Cases

### TC-001: File Conversion E2E

- **Objective**: UJ-001 happy path
- **Input**: Sample `.tac` in test-data
- **Pass criteria**: IWXXM XML returned; HTTP 200
- **Source**: apps/e2e/tac-file-conversion.e2e.spec.ts

### TC-002: Validation Pass

- **Objective**: UJ-002 for known-good output
- **Pass criteria**: validation status `pass` or equivalent

### TC-003: Auth Gate

- **Objective**: UJ-003 — unauthorized blocked, authorized allowed
- **Pass criteria**: 401 without token; 200 with valid JWT

## Live Test Cases (T3 / H3–H6)

Manual signoff before release — not a PR merge gate. Developer runs `make test-live` from repo root with `.env` populated.

### TC-LIVE-001: Live Health & Convert

- **Objective**: H3 — API health and METAR conversion against Render
- **Preconditions**: E2E-001 schema path fixed; `LIVE_API_URL` set; JWT obtained via login fixture
- **Steps**:
  1. `curl -sf "${LIVE_API_URL}/health"` — expect 200, `gifts_available: true`
  2. `pytest apps/backend/tests/infrastructure/test_live_api_health.py -m live_api`
- **Pass criteria**: All live_api tests green; cold-start retries (3×, 30s backoff) succeed
- **Resilience**: Exponential backoff on HTTP 429
- **Source**: UJ-001, H3

### TC-LIVE-002: Live Validation

- **Objective**: H3 — validation endpoint against Render
- **Preconditions**: E2E-001 resolved; valid JWT; sample IWXXM from convert step
- **Steps**:
  1. POST `/api/v1/validation/validate` with converted XML
  2. Assert validation status pass for selected IWXXM version
- **Pass criteria**: HTTP 200; validation pass for known-good fixture
- **Source**: UJ-002, H3

### TC-LIVE-003: Live Connectivity (H4–H5)

- **Objective**: CORS preflight and frontend bundle embed correct API URL
- **Preconditions**: `LIVE_API_URL`, `LIVE_FRONTEND_URL` set
- **Steps**:
  1. `make test-live-connectivity` (wraps `verify_connectivity.sh` + CORS pytest)
  2. Confirm H4 preflight from frontend origin → API returns allowed headers
  3. Confirm H5 bundle contains `LIVE_API_URL` host
- **Pass criteria**: H0c-equivalent live checks pass (script exit 0)
- **Source**: UJ-OPS-001, H4–H5

### TC-LIVE-004: Live Playwright UJ-001–003

- **Objective**: H6 — full product journeys against Render frontend
- **Preconditions**: E2E-001 resolved; `PLAYWRIGHT_BASE_URL=${LIVE_FRONTEND_URL}`; `DISABLE_AUTH=false`; admin credentials in `.env`
- **Steps**:
  1. Run `00-preflight.e2e.spec.ts` first (wake + health)
  2. `make test-live-e2e` — auth login UI, METAR conversion UI, validation where exposed
  3. Playwright config disables local `webServer` when base URL is remote
- **Pass criteria**: All UJ-001–003 specs green against live URLs
- **Resilience**: Cold-start retry in preflight; serial execution (no parallel live requests)
- **Source**: UJ-001–003, H6

### TC-LIVE-005: Stale Test Migration

- **Objective**: Remove auth-v2 references from legacy live Playwright
- **Steps**:
  1. Update `tests/test_playwright_e2e.py` to target merged API at `LIVE_API_URL`
  2. Deprecate `metar-to-iwxxm-auth-v2.onrender.com` references
- **Pass criteria**: No tests target suspended auth-v2 service
- **Source**: [Context: live-e2e-integration](context/live-e2e-integration.md)

## CI/CD (Monorepo)

**Policy (EV-002)**: Single workflow file for PR/push; ≤3 jobs; all checks dual-run locally via
pre-commit fast hooks where applicable. Scheduled workflows (`vendor-sync`, load/e2e) unchanged.

| Trigger | Workflow | Jobs | Checks |
|---------|----------|------|--------|
| PR / push `main`, `dev` | `ci-cd.yml` | **validate** | ruff format/check, prettier, eslint, basedpyright, tsc, gitleaks, actionlint/yamllint, config-guard (`tests/test_config_placeholders.py`), frontend npm audit |
| PR / push `main`, `dev` | `ci-cd.yml` | **test** | matrix unit+coverage (backend, auth, gifts, frontend, shared @ 98%), integration matrix (docker compose), Codecov upload (95% gate) |
| push `main` only | `ci-cd.yml` | **deploy** | Docker build/push GHCR, Render deploy hooks |
| Schedule | `vendor-sync.yml` | vendor-sync | wmo-im schema sync PR (M6) |
| Manual / schedule | `load-tests.yml`, `e2e-tests.yml` | — | out of EV-002 scope |

### Pre-commit (local fast gates)

| Hook | Tool | CI equivalent |
|------|------|---------------|
| Python format | `ruff format --check` | validate job |
| Python lint | `ruff check` | validate job |
| Python types | `basedpyright` | validate job |
| JS format | `prettier --check` | validate job |
| JS lint | `eslint` | validate job |
| JS types | `tsc --noEmit` | validate job |
| Secrets | `gitleaks` | validate job (replaces `secret-scan.yml`) |
| Workflow YAML | `actionlint`, `yamllint` | validate job (replaces `github-yaml-lint.yml`) |

Slow checks (`make ci` integration, full unit matrix) remain CI-only; optional via `pre-commit` `make-ci` hook.

### Removed workflows (EV-002)

- `secret-scan.yml` — merged into validate
- `github-yaml-lint.yml` — merged into validate
- `frontend-audit.yml` — merged into validate (monorepo `apps/frontend` paths)

## Test Data

| Dataset | Source | Location |
|---------|--------|----------|
| Sample METAR TAC | repo fixtures | `test-data/` |
| IWXXM schemas | wmo-im vendored | `vendor/schemas/` |
| Golden XML | generated baseline | `test-data/golden/` (optional) |

## Metrics & Thresholds

| Metric | Threshold | Context |
|--------|-----------|---------|
| Backend unit coverage | **95% all packages/apps** | ADR-007 universal gate |
| E2E pass rate | 100% on T2 before merge | Big-bang gate |
| Live E2E (T3) | Manual signoff before release | `make test-live` — not CI-gated |
| Vendor sync PR | human review required | No auto-merge to main |

## Big-Bang Merge Gate

All must pass before merging migration PR:

- [ ] TC-M001 through TC-M005
- [ ] TC-001 through TC-003 (full E2E suite in apps/e2e/)
- [ ] H0c CORS unit tests
- [ ] H4 CORS preflight + H5 bundle verification on staging
- [ ] CI green on PR branch
- [ ] render.yaml updated for two-service topology
