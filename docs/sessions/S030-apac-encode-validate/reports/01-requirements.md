# 01-requirements report — S030 / EV-023

**Date**: 2026-07-30  
**Mode**: delta  
**Cycle**: EV-023 · **Issue**: [#800](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/800)

## Phase 0 lock (E23-1..4)

| ID | Decision |
|----|----------|
| E23-1 | Deepen F6 + F2 + F12 (+ F13); no new Fn |
| E23-2 | **All ticket backlog** — P0 + P1 + actionable P2 |
| E23-3 | Lean+build (`01→02→04→07→08→10`) |
| E23-4 | Include **13** when convert/validate behavior ships |
| E23-ui | N/A — engine + goldens |

## Documents updated

| Doc | Delta |
|-----|-------|
| `docs/feature-list.md` | F6/F2/F12/F13 deepen section + P0–P2 acceptance |
| `docs/decisions/evolve-decisions.md` | §EV-023 scope lock |
| `docs/decisions/requirements-decisions.md` | EV-023 table |
| `docs/test-plan.md` | TC-EV023-001..009 + gate |
| `docs/config-spec.md` | translationCentre omit/gate + offline vocab |
| `docs/user-journeys.md` | No new UJ; deepen note for UJ-001/005/006/016 |
| Session brief / routing-plan | Locked |

## Standing domain (already promoted; not rewritten in 01)

Mining → `IWXXM_CONVERSION.md` / `IWXXM_VALIDATION.md` / `TAC_VALIDATION.md` /
`COVERAGE_MATRIX.md` / `RULE_SOURCE_URLS.md` (from #797/#798 docs PRs).

## Handoff

**Next**: **02-verify-plan** (delta consistency on touched corpus) → Gate A → **04-tech-plan**.

## Close decision

Pending AskQuestion E23-E1 (mark 01 complete → start 02).
