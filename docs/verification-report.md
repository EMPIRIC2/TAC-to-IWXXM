# Verification Report

> Generated: 2026-06-20
> Scope: standalone (post-M11 on `main`) — re-verified after user-approved fixes
> Branch: `main`

## Summary

| Check | Status | Findings | Auto-Fixed | Tool |
|-------|--------|----------|------------|------|
| Lint | PASS | `make lint` green; 5 invalid `# noqa` warnings in `packages/gifts/gifts/*.py` (advisory) | 1 (E712) | Ruff + ESLint |
| Format | PASS | 291 files reformatted (chore) | 291 | `ruff format` |
| Typecheck | FAIL | `packages/shared`+`packages/auth`: 313 errors; `apps/backend/src`: 818 errors | 0 | basedpyright |
| Tests (workspace) | PASS | 151 passed, 1 skipped | — | pytest |
| Tests (`make test-unit`) | PASS | 34 Python + 26 shared cov + 2 JS | — | make |
| Tests (H0c CORS) | PASS | `tests/unit/test_cors_policy.py` — 6/6 | — | pytest |
| Tests (H0i integration) | PASS | 7/7 logic (`--no-cov`; coverage gate fails on isolated subset with default `--cov`) | — | pytest |
| Security (pip-audit) | PASS | No known CVEs after `pydantic-settings` 2.14.2 bump | — | pip-audit |
| Security (secrets) | PASS | No committed private keys / API key patterns | — | ripgrep |
| Security (patterns) | ADVISORY | `eval()` in `packages/gifts/gifts/common/tpg.py` (upstream GIFTs) | — | ripgrep |
| Security (npm) | ADVISORY | ESLint 22 warnings in full-tree scan; `make lint` uses `--max-warnings 0` on `src/` only — PASS | — | ESLint |
| Performance | SKIPPED | No perf thresholds in active milestone | — | — |
| Data | SKIPPED | Vendor snapshots present; no integrity script run | — | — |
| Modal smoke | SKIPPED | Not M10+ / no GPU budget requested | — | — |
| Template conformance | PASS | Monorepo layout matches `static+api` | — | manual |
| Connectivity artifacts | PRESENT | `tests/smoke/test_staging_connectivity.py`, `scripts/deploy/verify_connectivity.sh` | — | — |

**Overall: FAIL** (typecheck only)

## Fixes applied this run

| Change | Detail |
|--------|--------|
| Makefile | `lint-frontend` / `lint-fix-frontend` → `apps/frontend` via pnpm |
| Security | `pydantic-settings` 2.14.1 → 2.14.2 in `apps/backend/pyproject.toml` + lockfile |
| Format | `ruff format apps packages tests` — 291 files |
| Lint auto-fix | E712 in `packages/gifts/validation/codeListsToSchematron.py` |

All changes are **uncommitted** pending your commit instruction.

## Remaining blocker

### Typecheck — basedpyright strict

| Scope | Errors | Warnings |
|-------|--------|----------|
| `packages/shared` + `packages/auth` | 313 | 359 |
| `apps/backend/src` | 818 | 915 |

Notable: `packages/shared/src/metar_shared/xml_canonical.py:81` return-type mismatch. `pyrightconfig.json` still references removed `GIFTs/` path — update before full-repo runs.

**Recommended:** Budget remediation starting with `packages/shared`; update `pyrightconfig.json` excludes.

## Passing highlights

- Migration gates TC-M001–M005 pass on `main`.
- H0c + H0i connectivity tests pass.
- `make lint`, `make test-unit`, and `ruff format --check` all green post-fix.
- pip-audit clean after CVE bump.

## Toolchain notes

- Node v20.20.0 in environment (spec pins Node 22) — pnpm warns but tests run.
- `make test-integration` not run (requires Supabase env + docker-compose).

## Recommended next actions

1. Commit fixes as atomic commits: `[chore] fix Makefile lint paths`, `[chore] bump pydantic-settings`, `[chore] ruff format monorepo Python`.
2. Update `pyrightconfig.json` to drop legacy `GIFTs`/`backend`/`auth` paths.
3. Budget basedpyright remediation from `packages/shared`.
4. Re-run stage 08 after typecheck remediation for overall PASS.
