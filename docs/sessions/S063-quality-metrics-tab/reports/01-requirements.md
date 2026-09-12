# 01-requirements — S063 / EV-054

**Status**: completed — `D-S063-01-ac=1`  
**Date**: 2026-08-10  
**Mode**: delta (deepen F7 / F7.q — Quality metrics tab)  
**Issues**: [#836](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/836)

## Corpus

[Corpus: product §F7] [Corpus: product §F25] [Corpus: journeys] [Corpus: tests]
[Corpus: adr/ADR-032] [Corpus: adr/ADR-025] [Corpus: decisions §EV-054]

## Standing doc deltas

| Doc | Change |
|-----|--------|
| `docs/feature-list.md` | F7 summary + **F7.q** slice; EV-054 deepen + AC1–AC7 |
| `docs/user-journeys.md` | **UJ-056** index + detail (primary shell tab) |
| `docs/test-plan.md` | TC-EV054-001..007 |
| `docs/decisions/evolve-decisions.md` | Phase 0–1 + 01 decisions / AC table |

## Skipped (N/A unless 04 invents HTTP refresh)

- `api-contract.md` / `config-spec.md` / `deploy.md` (precomputed FE fixtures default)
- New top-level Fn (F34) — F7.q sub-id only
- UI preview (`D-S063-ui-preview=2`)

## Locked decisions

| ID | Choice |
|----|--------|
| D-S063-01-manifest | **1** — feature-list + journeys + test-plan + decisions |
| D-S063-01-ac | **1** — AC1–AC7 |
| D-S063-diff | **2** — Unified XML diff in v1 |
| D-S063-shell-tab | **1** — Separate primary app-shell tab (not FileConverter panel) |
| D-S063-compute | **1** — Precomputed metrics JSON (prior) |
| D-S063-fn | **1** — F7 deepen + F7.q note (prior) |

## Acceptance criteria

| AC | Criterion | TC |
|----|-----------|-----|
| AC1 | Separate primary tab; corpus by product | TC-EV054-001..002 |
| AC2 | Match + unified XML diff + inspectable TAC/XML | TC-EV054-003 |
| AC3 | Residuals / lint / validate panels | TC-EV054-004 |
| AC4 | Summary counts ↔ precomputed fixture | TC-EV054-005 |
| AC5 | Gap stems labeled | TC-EV054-002 |
| AC6 | Playwright / H4–H5 smoke (UJ-056) | TC-EV054-007 |
| AC7 | Offline default (no network/Supabase) | TC-EV054-006 |

## Next

**02-verify-plan** (Gate A).
