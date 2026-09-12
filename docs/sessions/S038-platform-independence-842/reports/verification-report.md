# Verification report — 08-verify-build (C→D gate)

> **Stage**: 08-verify-build · **Cycle**: EV-031 · **Session**: S038  
> **Mode**: evolve delta (post-T6.5 / Phase C close)  
> **Date**: 2026-08-03  
> **Decision**: `D-S038-phase-c` → Phase D  
> **Tip (pre-fix)**: `2cb0e562`

## Scope

Delta after Render decommission (`D-S038-t65-waive`): `config/prod.json` HTTP DOKS
placeholders, CI GHCR-only Deploy, live harness defaults, related unit guards.

## Results

| Check | Result | Notes |
|-------|--------|-------|
| Format (`make format-check`) | **PASS** | ruff + prettier |
| Lint (`make lint`) | **PASS** | ruff scoped paths + eslint |
| Typecheck (`make typecheck`) | **PASS** | basedpyright + tsc (warnings only in tac2iwxxm) |
| H0c CORS (`test_cors_policy.py`) | **PASS** | DOKS FE origins |
| H5 config (`test_h5_runtime_config.py`) | **PASS** | `api.baseUrl` == `liveE2e.apiUrl` |
| Render-retire bug guard | **PASS** | `test_bug_2026_08_03_*` |
| Workspace unit (`make test-unit-workspace`) | **PASS** | after test fixes below |
| Connectivity artifacts | **PASS** | `tests/smoke/test_staging_connectivity.py` present; `verify_connectivity.sh` present |
| CORS wiring | **PASS** | `CORSMiddleware` in `apps/backend/src/api.py` |
| Live topology | **PASS** | DOKS Host-header `/health` **200**; Render **503** |

## Fix-in-place (08)

| Failure | Fix |
|---------|-----|
| `test_get_frontend_url_from_config_prod` assumed `https://` | Allow provisional DOKS `http://` placeholders |
| `test_t62_*_alembic` expected bare `alembic` CLI | Align to `python -m alembic` (deploy manifests) |

## Prior M7 evidence (retained)

- T7.1 Playwright F31 13/13 · T7.2 H4–H5 · T7.3 topology — see `verification-report-M7.md`

## Gate C→D

| Criterion | Status |
|-----------|--------|
| All Fn build tasks done | **PASS** (35/35) |
| Latest 08 PASS | **PASS** (this report) |

**Overall: PASS** — proceed to 09-qa + 10-e2e.
