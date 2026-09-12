# Verification report — M1 Auth restore (JWKS) — EV-031 / S038

> **Stage**: 08-verify-build (milestone M1 boundary)  
> **Date**: 2026-08-03  
> **Branch**: `evolve/EV-031-platform-independence-842`  
> **Tip**: `2227c95` (`[T1.4]`)

## Milestone scope

| Task | Status | Commit |
|------|--------|--------|
| T1.1 Auth JWKS + `/auth` contract tests | completed | `43c8f30` |
| T1.2 Restore `packages/auth` JWKS-only + mount | completed | `14fc916` |
| T1.3 Workspace/Docker/CI + JWKS env wire | completed | `da0d2ad` |
| T1.4 Public convert/lint/validate JWT-free | completed | `2227c95` |

## Checks run

| Check | Result |
|-------|--------|
| `tests/unit/auth` + T1.3 wire + M4/M8/M005 migration | **35 passed** |
| TC-EV031-003 + amended F21 + H0i | **20 passed** |
| Ruff on auth + T1.4 modules | **pass** |
| Pre-commit on T1.3 / T1.4 commits | **pass** |

## Connectivity (H0i)

- Convert without Authorization: **PASS**
- `/auth/login` mounted (≠404; may 503 without Auth env): **PASS**
- Work-sessions still absent (M2): **PASS**

## Next

- **M2 / T2.1** — Alembic empty→head + idempotent second `upgrade head` (`TC-EV031-002`)
- Minor PR for M1 optional on same evolve branch (cycle continues on `evolve/EV-031-…`)
