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

## Backlog (deferred slices)

P2: api.py router split · product_rules split · annex3 split  
P3: shared xsdata move · FileConverter decomposition · edge API retirement  
P4: GIFTs naming · .archive delete · doc hygiene
