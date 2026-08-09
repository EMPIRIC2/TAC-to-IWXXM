# 01-requirements — S059 / EV-050

**Mode:** delta (Standard)  
**Date:** 2026-08-09  
**Issue:** [#959](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/959)  
**Parent:** [#889](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/889) Validated  
**Corpus:** [Corpus: product] [Corpus: tests] [Corpus: tech-spec] [Corpus: decisions]

## Intake lock

| ID | Choice | Meaning |
|----|--------|---------|
| D-S059-route | 1 | Standard as drafted |
| D-S059-families | 1a | Weather + recent + cloud + SIGMET/AIRMET phenomena + nilReason |
| D-S059-fixtures | 2c | Aggressive fixture expansion (RE*, AIRMET `_`, SpaceWx, TCU) |
| D-S059-882 | 3a | #882 design-only compose note |
| D-S059-01-ac | 4a | Lock AC1–AC6 |
| D-S059-profiles | **1b** | All F6 products; `iwxxm_us` N/A where unsupported; AC7–AC8 |
| D-S059-01-next | **2a** | Commit locally (no push) → 02 Gate A |

## Document manifest (delta)

| Document | Action |
|----------|--------|
| `docs/decisions/evolve-decisions.md` §EV-050 | Scope + AC1–AC8 |
| `docs/decisions/requirements-decisions.md` | EV-050 intake rows |
| `docs/feature-list.md` | Summary deepen + EV-050 block (F6+) |
| `docs/test-plan.md` | TC-EV050-001..008 + verify gate |
| Domain harvest / RULE_SOURCE_URLS / COVERAGE_MATRIX | Deferred to 04/07 |
| User journeys / API / deploy | N/A — no UI/API/deploy |

## UI preview

N/A — no browser UI.

## AC confirmation

**`D-S059-01-ac=4a`** + **`D-S059-profiles=1b`** — AC1–AC8 locked.

| AC | Summary |
|----|---------|
| AC1 | Offline harvest → membership sets for CI |
| AC2 | Happy + sad membership for v1 families |
| AC3 | Cadence vs `iwxxm-codelists` pin |
| AC4 | Aggressive fixtures close EV-046 gap rows |
| AC5 | #889 Validated satisfied or re-scoped |
| AC6 | #882 design-only compose note |
| AC7 | All-F6 annex3 vs iwxxm_us compare; N/A where US unsupported |
| AC8 | Fix true errors with regressions; cite intentional L5 / N/A |

## Exit

- [x] Route + intake locked (incl. profiles 1b)
- [x] Evolve-decisions AC1–AC8
- [x] Feature-list deepen (F6 + quality bars)
- [x] Test-plan TC-EV050-001..008
- [x] Commit locally (`2a`) — no push
- [ ] Gate A — **02-verify-plan**
