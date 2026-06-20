# Verification Report

> Generated: 2026-06-18
> Scope: M7 milestone boundary (Phase 3 — Apps & Auth Merge)
> Branch: `feat/M7-e2e-workspace`

## Summary

| Check | Status | Findings | Auto-Fixed | Tool |
|-------|--------|----------|------------|------|
| Lint | PASS | 0 errors; 5 invalid `# noqa` warnings in `packages/gifts/gifts/*.py` | 0 | Ruff + ESLint |
| Format | FAIL | 491 files would be reformatted | 0 | `ruff format --check` |
| Typecheck | FAIL | ≥313 errors (full run timed out >8 min); `packages/shared` + `packages/auth` alone: 313 errors | 0 | basedpyright |
| Tests (workspace) | PASS | 34/34 after dev-dep fix | — | `make test-unit` |
| Tests (migration) | FAIL | 1 failed: TC-M001 `.gitmodules` still present; 89 passed | — | `pytest tests/migration` |
| Tests (legacy) | FAIL | Frontend: 5 failed / 353 (env contract drift post-M4) | — | `make test-unit-legacy` |
| Tests (H0c CORS) | PASS | `tests/unit/test_cors_policy.py` — 6/6 | — | pytest |
| Tests (H0i integration) | PASS* | 7/7 logic pass; coverage gate fails when run in isolation (22.79% < 95%) | — | `apps/backend/tests/integration/test_h0i_connectivity.py` |
| Security (pip-audit) | PASS | No known CVEs in resolved PyPI deps | — | pip-audit |
| Security (secrets) | PASS | No obvious committed secret patterns | — | ripgrep |
| Security (patterns) | ADVISORY | `eval()` in legacy `packages/gifts/gifts/common/tpg.py` | — | ripgrep |
| Security (npm) | ADVISORY | 11 npm audit issues during `make lint-frontend` | — | npm |
| Performance | SKIPPED | No perf thresholds in active milestone | — | — |
| Data | SKIPPED | Vendor snapshots present; no integrity script run | — | — |
| Modal smoke | SKIPPED | Not M10+ / no GPU budget requested | — | — |
| Template conformance | PASS* | Monorepo layout matches `static+api`; legacy paths (`backend/`, `frontend/`, `auth/`, `GIFTs/`) still coexist (transitional per migration plan) | — | manual |
| Connectivity artifacts | PRESENT | `tests/smoke/test_staging_connectivity.py`, `scripts/deploy/verify_connectivity.sh` | — | — |

**Overall: FAIL**

## Blocking issues

### 1. Workspace dev dependency gap (fixed locally, uncommitted)

`metar-backend` was missing from root `[dependency-groups].dev` in `pyproject.toml`. Without it, `uv sync` does not install `python-multipart`, and importing `apps/backend/src/api.py` fails in H0c / TC-M005 tests.

**Local fix applied:** `uv add --dev metar-backend` — CORS and auth-merge tests then pass. This change is **not committed** (awaiting approval).

### 2. Format — 491 files

Copied legacy trees (`apps/backend`, `packages/gifts`, `packages/auth`, `backend/`) were never run through `ruff format`. Mass reformat is a large diff unrelated to product behavior (REQ-016).

### 3. Typecheck — basedpyright strict

Scoped run on `packages/shared` + `packages/auth`: **313 errors**, 359 warnings. Notable: `packages/shared/src/metar_shared/xml_canonical.py:81` return-type mismatch. Full-repo run (`uv run basedpyright`) did not complete within 8 minutes.

### 4. Frontend unit tests — env contract drift (M4)

Legacy `frontend/` Vitest suite expects pre-merge env vars:

| Test file | Failure |
|-----------|---------|
| `src/test/env-validation.test.ts` | Expects `VITE_AUTH_SERVICE_URL=http://localhost:8003` and related vars |
| `src/test/vite-api-base-url.client.test.ts` | Suite error (import/config) |

Post-M4 topology uses unified `VITE_API_BASE_URL` on the merged backend host. Tests need updating per `docs/deploy.md` / M6 frontend layout work.

### 5. TC-M001 — `.gitmodules` still present

`tests/migration/test_tc_m001_monorepo_clone_smoke.py::test_no_gitmodules_file` fails because `.gitmodules` exists at repo root. Expected until M11 big-bang cutover per execution plan.

## Passing highlights

- **Lint:** Ruff clean on `backend/`, `auth/`, `packages/gifts/`; ESLint clean on `frontend/`.
- **Workspace unit gate:** `make test-unit` — 34 Python + 26 shared + 2 JS tests, all green after `metar-backend` dev dep.
- **H0c connectivity:** CORS policy unit tests pass including in-process `CORSMiddleware` check against `apps/backend`.
- **H0i connectivity:** Integration tests in `apps/backend/tests/integration/test_h0i_connectivity.py` pass (auth + convert + OPTIONS preflight).
- **TC-M005 auth merge:** All 6 tests pass after dev-dep fix.
- **Legacy Python:** `backend/` 965 tests @ 95.30% coverage; `auth/` 187 tests @ 97.97% coverage.
- **pip-audit:** No known vulnerabilities in installable PyPI packages.
- **Connectivity artifacts:** Smoke test module and `verify_connectivity.sh` present per connectivity-gates §Stage 08.

## Toolchain notes

- Node in environment: v20.20.0 (spec pins Node 22) — pnpm warns but tests still run.
- `pip-audit` was not in dev deps; installed ad hoc for this run.
- `make test-integration` not run (requires Supabase env + docker-compose).

## Recommended next actions

1. Commit `metar-backend` in root dev dependency group (unblocks workspace pytest).
2. Update `frontend/` Vitest env tests for M4 merged API URL contract.
3. Schedule `ruff format` as a dedicated chore commit per package (or defer to M11 cutover).
4. Budget basedpyright remediation starting with `packages/shared` strict errors.
5. Re-run stage 08 after above; TC-M001 will remain red until `.gitmodules` removal (M11).
