# EV-037 — Tech-debt pass: validation stack consolidation

> **Orchestrator:** evolve · **Started:** 2026-08-26 · **Primary deliverable:** TD-1

[Corpus: product] F2, F6, M1 · [Corpus: adr/ADR-015] · [Corpus: system-spec]

## Intake

| Topic | Decision | Status |
|-------|----------|--------|
| Goals | Architectural cleanup + modularization + library extraction | confirmed |
| Primary target | TD-1 — validation stack consolidation | confirmed |
| Constraint | No operator-visible behavior change | confirmed |
| Success | One high-impact refactor shipped | confirmed |
| Scale | standard (tech-plan + verify-tech) | confirmed |

## TD-1 scope

| In | Out |
|----|-----|
| IWXXM layers 3–7 into `packages/iwxxm-validate` | Remove `/api/v1/validation/*` routes |
| Backend adapter; orchestrator thinned | TAC layers 1–2 → tac-validate |
| Wire-identical HTTP for validate + convert preview | Frontend / api.py full split |
| Delta validation docs | shared xsdata extraction |

## Build acceptance

- All validation-related tests pass unchanged
- No `utilities/{xsd,schematron,gml}_validator` imports on IWXXM hot paths ✅ (Phase D)
- Package boundary tests pass (no FastAPI in packages)

## Phase D (2026-08-26)

- Removed `apps/backend/src/utilities/{xsd,schematron,gml}_validator.py`
- Layer result dataclasses consolidated in `schemas/validation.py`
- Deleted legacy backend validator unit tests; coverage in `packages/iwxxm-validate/tests`
- Updated `docs/domain/validation/COMPREHENSIVE_VALIDATION.md`

## Merge (2026-08-26)

- **PR #1074** → `stage` (squash merge `cf2c721d`)
- CI green: lint, typecheck, backend/iwxxm-validate/tac2iwxxm tests, E2E smoke, Schemathesis
- Staging gate skipped (PR targets `stage`, not `main`)

## Backlog (deferred slices)

P2: api.py router split · product_rules split · annex3 split  
P3: shared xsdata move · FileConverter decomposition · edge API retirement  
P4: GIFTs naming · .archive delete · doc hygiene

## TD-2 (2026-08-26)

| Slice | Status | Notes |
|-------|--------|-------|
| annex3_products split | ✅ | `profiles/annex3_emit/` per-product modules; shim in `annex3_products.py` |
| product_rules split | ✅ | `product_rules_pkg/` per-family modules; dispatcher in `product_rules.py` |
| api.py router split | deferred | Route move breaks `src.api.*` monkeypatch sites (~200 unit tests); retry with wire-only helper extraction first |

## TD-2b — api.py wire helper extraction (2026-08-26)

| Item | Status | Notes |
|------|--------|-------|
| `api_wire.py` | ✅ | CORS helpers, multipart/validate wire, bulletin split mapper (~630 lines) |
| `api.py` | ✅ | Routes unchanged; re-exports wire names for `src.api.*` patches |
| Route router split | still deferred | All **1391** backend unit tests pass with wire-only extraction |

**Patch contract:** `_call_iwxxm_validate` resolves `iwxxm_validate_fn` via lazy `api` lookup so tests patching `src.api.iwxxm_validate_fn` still work.

## TD-3 — api_deps adapter + router split (scoped 2026-08-26)

| Phase | Status | Notes |
|-------|--------|-------|
| TD-3a `api_deps.py` | ✅ | Centralized 14 patchable symbols; `api` re-exports preserve monkeypatch contract |
| TD-3b router extraction | pending | Move 11 routes from `api.py` → domain routers |
| TD-3c test migration | optional | `api_module.X` → `api_deps.X`; remove re-exports later |

**Blocker resolved by TD-3a:** 225 `monkeypatch.setattr(api_module, …)` sites across 30 test files. Router move (TD-3b) is safe only after handlers resolve collaborators through `api_deps` at call time.

**PR #1075** (TD-1 + TD-2) → `stage`. TD-3 can land as follow-up commits on same branch or post-merge slice.

Full scope: session `reports/td-3-scope.md`.
