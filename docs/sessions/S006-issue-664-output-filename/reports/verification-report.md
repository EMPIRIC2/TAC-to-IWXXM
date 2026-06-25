# Verification Report — S006 / EV-005 (08-verify-build)

> Generated: 2026-06-25  
> Scope: EV-005 delta (`feat/S006-issue-664-output-filename`) — #664 custom output filename  
> Branch: `feat/S006-issue-664-output-filename`

## Summary

| Check | Status | Findings | Auto-Fixed | Tool |
|-------|--------|----------|------------|------|
| Lint (Python) | PASS | 0 | — | `ruff check` |
| Lint (JS) | PASS | 0 | — | `eslint` |
| Format | PASS | 0 | — | `ruff format --check` + `prettier --check` |
| Typecheck | PASS | 0 | — | `basedpyright` + `tsc` |
| Tests (unit) | PASS | 0 failed | — | `make test-unit` |
| CORS policy (H0c) | PASS | 6/6 | — | `tests/unit/test_cors_policy.py` |
| Integration (local) | PASS* | 0 pass, 7 skip | — | `tests/integration` |
| Connectivity artifacts | PASS | Present | — | See below |
| Security (secrets) | PASS | 0 | — | `gitleaks` |
| Security (pip-audit) | PASS | 0 on lockfile | — | `uv export` + `pip-audit` |
| Performance | SKIPPED | — | — | — |
| Data integrity | SKIPPED | — | — | — |
| Template conformance | PASS | `static+api` layout | — | manual |

**Overall: PASS** — all blocking checks green on the EV-005 branch.

## Auto-corrections applied

None required — lint and format were already clean.

## Unit test matrix

| Target | Result | Notes |
|--------|--------|-------|
| Workspace pytest | PASS | 43/43 |
| `packages/shared` (py) | PASS | 65/65 |
| `packages/shared` (js) | PASS | 4/4 |
| `apps/backend` | PASS | 1154/1154, 98.04% cov |
| `packages/auth` | PASS | 228 passed, 31 skipped, 98.73% cov |
| `apps/frontend` | PASS | 530/530, 98.95% stmt cov |
| `packages/gifts` | PASS | 1010 passed, 1 skipped, 98.79% cov |
| `tests/bugs` | PASS | 37/37 |

**Total runtime:** ~7.5 min (`make test-unit`, dominated by frontend Vitest coverage).

## Connectivity (stage 08)

| Artifact | Status |
|----------|--------|
| `tests/unit/test_cors_policy.py` | PASS (6 tests) |
| `tests/smoke/test_staging_connectivity.py` | Present |
| `scripts/deploy/verify_connectivity.sh` | Present |
| `apps/backend` CORS middleware | Configured via `METAR_CORS_ORIGINS` |

Local integration tests (`tests/integration`) all skipped — no live stack credentials in this run (expected).

## Security notes

- **gitleaks:** Passed on all files.
- **pip-audit:** Raw `uv run pip-audit` audited system Python 3.11 (145 CVEs — unrelated OS packages). **Project lockfile** via `uv export --frozen --no-dev` → **0 known vulnerabilities**.

## Template conformance (`static+api`)

| Check | Status |
|-------|--------|
| `apps/backend/` — FastAPI API | OK |
| `apps/frontend/` — Vite static | OK |
| `packages/auth/` — library (not deployable) | OK |
| `packages/gifts/` — no FastAPI/Supabase imports | OK |
| `vendor/schemas/*` — read-only | OK |
| No separate `apps/auth/` deployable | OK |

## EV-005 delta coverage

Frontend-only changes for #664 (output filename sanitizer, FileConverter wiring, persistence, e2e). All new/changed tests pass within the frontend suite (530/530).

## Gate result

**PASS** — ready for **09-qa**.
