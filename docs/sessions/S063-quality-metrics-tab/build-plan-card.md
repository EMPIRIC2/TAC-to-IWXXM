# Build Plan Card — S063 / EV-054

> Updated: 2026-08-10 · Branch: `evolve/EV-054-quality-metrics-tab`

## Goal

Ship a primary **Quality metrics** shell tab backed by public precomputed
`GET /api/v1/quality-metrics*` and a unified XML diff detail pane ([#836](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/836)).

## Out of scope

Live WMO fetch; FE-only bundle; encode-tier promotion; replace CI matrices; new npm
diff package (v1); #840 epic; stage→main unless approved.

## Milestones (07 order)

| M | Goal | Exit |
|---|------|------|
| M1 | Generator + `corpus_metrics.json` | Artifact + loader test |
| M2 | Public quality-metrics API + OpenAPI/FE client | TC-EV054-008 |
| M3 | Shell nav + list/summary UI | AC1/AC5 Vitest |
| M4 | Detail + unified line diff | AC2/AC3 Vitest |
| M5 | Playwright + CI/docs | UJ-056 / AC6 |

## Execution plan

`docs/sessions/S063-quality-metrics-tab/reports/execution-plan.md` (15 tasks T1.1–T5.3)

## Active batch (07)

| Task | Status |
|------|--------|
| T1.1–T1.3 | **completed** — M1 artifact + tests |
| T2.1–T2.3 | **completed** — public API + OpenAPI + FE clients |
| T3.1–T3.3 | **completed** — shell nav + list/summary + Vitest |
| T4.1–T4.3 | **completed** — detail panes + unifiedLineDiff + Vitest |
| T5.1 | next — Playwright UJ-056 |

## Next

**07-build** M5 — Playwright + CI/docs closeout

## Corpus

[Corpus: product §F7] [Corpus: api] [Corpus: journeys §UJ-056] [Corpus: tests]
[Corpus: decisions §EV-054]
