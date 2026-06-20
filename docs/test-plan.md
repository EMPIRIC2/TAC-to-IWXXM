# Test Plan

> **Project**: METAR to IWXXM Converter
> **Repository**: https://github.com/joseph-c-mcguire/metar-to-IWXXM
> **Last updated**: 2026-06-14

## Scope

**In scope**: Product features F1–F4; monorepo migration validation M1–M6; connectivity tiers H0c–H5.

**Out of scope**: Performance benchmarking; load testing; wmo-im schema correctness (upstream responsibility).

## User Journeys (E2E)

| Journey | Feature | Local E2E module | Live E2E | Test plan TC |
|---------|---------|------------------|----------|--------------|
| UJ-001 | F1 | `apps/e2e/tac-file-conversion.e2e.spec.ts` | staging Playwright | TC-001 |
| UJ-002 | F2 | backend validation tests + UI if exposed | optional | TC-002 |
| UJ-003 | F1 | `apps/e2e/auth.e2e.spec.ts` | staging | TC-003 |
| UJ-DEV-001 | M1,M5 | CI monorepo-smoke job | — | TC-M001 |
| UJ-DEV-002 | M2 | vendor manifest integrity tests | — | TC-M002 |
| UJ-DEV-003 | M3 | gifts + conversion regression | — | TC-M003 |
| UJ-OPS-001 | M4 | deploy smoke H1–H5 | Render staging | TC-OPS-001 |

## Connectivity & Wiring

| Tier | Scope | Command |
|------|-------|---------|
| H0c | CORS policy (in-process) | `pytest apps/backend/tests/unit/test_cors_policy.py` |
| H0i | Cross-service integration | `pytest apps/backend/tests/integration` |
| H4 | Live CORS preflight | Playwright / curl against staging |
| H5 | Frontend bundle URLs | `scripts/deploy/verify_connectivity.sh` |

**Post-migration**: Single API origin simplifies CORS — auth routes on same host as `/api/v1/*`.

**Env wiring** (see config-spec artifact):

- `VITE_API_BASE_URL` — frontend build-time API URL
- `METAR_CORS_ORIGINS` — backend allowed browser origins

## Test Strategy

| Level | Framework | Scope | Run Command | Location |
|-------|-----------|-------|-------------|----------|
| Unit | pytest / Vitest | packages/*, apps/backend, apps/frontend components | `make test-unit` | per workspace |
| Integration | pytest | API + auth + conversion | `make test-integration` | apps/backend/tests |
| E2E | Playwright | UJ-001–003 | `make tests:e2e` | apps/e2e/ |
| Vendor | pytest | manifest + schema presence | `pytest tests/vendor` | tests/vendor |
| CI | GitHub Actions | full matrix; path filters deferred (P2) | `.github/workflows/ci-cd.yml` | root |

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

## CI/CD (Monorepo)

| Trigger | Paths | Jobs |
|---------|-------|------|
| PR / push main | `apps/backend/**` | backend lint, test |
| PR / push main | `apps/frontend/**` | frontend lint, test, build |
| PR / push main | `packages/**` | affected package tests |
| PR / push main | `vendor/**` | TC-M002 + validation suite |
| Schedule | upstream check | vendor iwxxm sync PR workflow (wmo-im only) |
| PR / push main | `apps/e2e/**` | Playwright (T2) |

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
| Vendor sync PR | human review required | No auto-merge to main |

## Big-Bang Merge Gate

All must pass before merging migration PR:

- [ ] TC-M001 through TC-M005
- [ ] TC-001 through TC-003 (full E2E suite in apps/e2e/)
- [ ] H0c CORS unit tests
- [ ] H4 CORS preflight + H5 bundle verification on staging
- [ ] CI green on PR branch
- [ ] render.yaml updated for two-service topology
