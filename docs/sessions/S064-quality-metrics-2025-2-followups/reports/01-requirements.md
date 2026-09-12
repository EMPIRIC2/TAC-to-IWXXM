# 01-requirements — S064 / EV-055

**Status**: completed — `D-S064-01-ac=1`  
**Date**: 2026-08-11  
**Mode**: delta (deepen F7.q + F2/F13 — #982 / #980 / #979)  
**Issues**: [#982](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/982),
[#980](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/980),
[#979](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/979)

## Corpus

[Corpus: product §F7] [Corpus: product §F2] [Corpus: product §F13]
[Corpus: api] [Corpus: journeys] [Corpus: tests] [Corpus: decisions §EV-055]

## Standing doc deltas

| Doc | Change |
|-----|--------|
| `docs/feature-list.md` | F7.q EV-055 AC1–AC7; F2/F13 deepen notes; summary rows |
| `docs/user-journeys.md` | **UJ-056** deepen (normalize + validate disposition) |
| `docs/test-plan.md` | **TC-EV055-001..007**; UJ-056 map update |
| `docs/api-contract.md` | `match_status` normalized equality; session changelog |
| `docs/decisions/requirements-decisions.md` | EV-055 table |
| `docs/decisions/evolve-decisions.md` | 01 decisions + AC table |

## Skipped

- `spec.md` / `config-spec.md` / `deploy.md` (`D-S064-01-manifest=1`)
- New UJ-057 — deepen UJ-056 only (`D-S064-uj=1`)
- UI preview (`D-S064-ui-preview=2`)

## Locked decisions

| ID | Choice |
|----|--------|
| D-S064-01-manifest | **1** — feature-list + journeys + test-plan + api-contract + decisions |
| D-S064-ui-preview | **2** — Docs/repo only |
| D-S064-uj | **1** — Deepen UJ-056 |
| D-S064-01-ac | **1** — AC1–AC7 |
| D-S064-regen | **1** — Regenerate corpus_metrics |
| D-S064-normalize | **1** — (prior) both sides; match_status normalized |
| D-S064-spike-pref | **3** — (prior) prefer Schematron enable |
| D-S064-engine | **1** — (prior) F2/F13 engine-in |

## Acceptance criteria

| AC | Criterion | TC |
|----|-----------|-----|
| AC1 | Whitespace-only diffs no longer dominate; semantic remain | TC-EV055-001 |
| AC2 | match_status = normalized equality | TC-EV055-002 |
| AC3 | Normalize helper + golden; vendor read-only | TC-EV055-003 |
| AC4 | #980 matrix; prefer Schematron enable | TC-EV055-004 |
| AC5 | #979 root cause; fix optional | TC-EV055-005 |
| AC6 | Validate chips reflect disposition | TC-EV055-004..005 / 007 |
| AC7 | corpus_metrics regen + UJ-056 smoke | TC-EV055-006..007 |

## Next

**02-verify-plan** (Gate A).
