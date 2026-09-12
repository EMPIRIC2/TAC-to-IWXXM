# 01-requirements summary — S044 / EV-036

**Mode:** delta · **Date:** 2026-08-05  
**Features:** deepen **M5** (no new Fn)  
**UI preview:** N/A — no UI  
**Status:** **COMPLETE** — R1=local Compose; AC=1 → handoff **02-verify-plan**

## Locked decisions

| ID | Decision |
|----|----------|
| Q1–Q3 / B1–B4 / G1–G2 | Phase 0 + routing |
| R1 | Remove remote Compose/`integration`; run on local pre-push via `make ci` |
| AC | M5 ACs + TC-EV036-001..003 approved |

## Resource model (final — Gate A amend)

| Tier | Hook | Jobs |
|------|------|------|
| Fast + medium | pre-commit | fast + `validate-ci-medium` |
| Long local | pre-push | `make ci` = `ci-prepush` + Compose integration |
| Remote | `ci-cd.yml` | units + coverage + PR comment; native / e2e-smoke / alembic / deploy; **no** validate / Compose |

## Standing doc deltas

| Doc | Change |
|-----|--------|
| `[Corpus: product]` | M5 EV-036 deepen + approved ACs |
| `[Corpus: tests]` | CI/CD EV-036; TC-EV036-001..003 |
| `[Corpus: decisions]` | §EV-036 R1 + AC |

## Handoff

**02-verify-plan** Gate A next (Lean → then 07-build; no 04).
