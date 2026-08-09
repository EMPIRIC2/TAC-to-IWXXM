# 01-requirements — S059 / EV-050

**Mode:** delta (Standard)  
**Date:** 2026-08-09  
**Issue:** [#959](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/959)  
**Parent:** [#889](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/889) Validated  
**Corpus:** [Corpus: product] [Corpus: tests] [Corpus: tech-spec] [Corpus: decisions]

## Intake lock (batch 1)

| ID | Choice | Meaning |
|----|--------|---------|
| D-S059-route | 1 | Standard as drafted |
| D-S059-families | 1a | Weather + recent + cloud + SIGMET/AIRMET phenomena + nilReason |
| D-S059-fixtures | 2c | Aggressive fixture expansion (RE*, AIRMET `_`, SpaceWx, TCU) |
| D-S059-882 | 3a | #882 design-only compose note |
| D-S059-01-ac | 4a | Lock AC1–AC6; write 01 deltas |

## Document manifest (delta)

| Document | Action |
|----------|--------|
| `docs/decisions/evolve-decisions.md` §EV-050 | Scope + AC1–AC6 |
| `docs/decisions/requirements-decisions.md` | EV-050 intake rows |
| `docs/feature-list.md` | Summary deepen + EV-050 block |
| `docs/test-plan.md` | TC-EV050-001..006 + verify gate |
| Domain harvest / RULE_SOURCE_URLS / COVERAGE_MATRIX | Deferred to 04/07 (implementation + refresh of %) |
| User journeys / API / deploy | N/A — no UI/API/deploy |

## UI preview

N/A — no browser UI (`ui_preview: n/a`).

## AC confirmation

**`D-S059-01-ac=4a`** — AC1–AC6 confirmed with 1a/2c/3a amendments.

| AC | Summary |
|----|---------|
| AC1 | Offline harvest → membership sets for CI |
| AC2 | Happy + sad membership for v1 families |
| AC3 | Cadence vs `iwxxm-codelists` pin |
| AC4 | Aggressive fixtures close EV-046 gap rows; residual deferrals cited |
| AC5 | #889 Validated satisfied or re-scoped |
| AC6 | #882 design-only compose note |

## Exit

- [x] Route + intake locked
- [x] Evolve-decisions AC1–AC6
- [x] Feature-list deepen (incl. F24/F28 for fixtures)
- [x] Test-plan TC-EV050-001..006
- [ ] Gate A — **02-verify-plan** (next; not run in this preview)
- [ ] Commit / push — **held for user preview** (no push)
