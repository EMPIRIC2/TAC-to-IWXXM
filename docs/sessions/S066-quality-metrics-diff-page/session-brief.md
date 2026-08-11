---
session_id: S066-quality-metrics-diff-page
type: feature
status: in_progress
branch: evolve/EV-056-quality-metrics-diff-page
orchestrator: 16-evolve
evolve_cycle_id: EV-056
github_issues: [988]
prior_session: S065-quality-metrics-diff-long-line
opened: 2026-08-11
---

# Session brief — S066-quality-metrics-diff-page

> **Cycle**: EV-056 · **Type**: feature · **Opened**: 2026-08-11  
> **Branch**: `evolve/EV-056-quality-metrics-diff-page` (base `stage@340b3cf6`)  
> **Orchestrator**: **16-evolve** · **Preset**: Lean (user-requested)  
> **Issue**: [#988](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/988)  
> **Prior**: S065 pretty-print hotfix ([#987](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/987) merged)  
> **Corpus**: [Corpus: product §F7.q] [Corpus: tests §UJ-056] [Corpus: journeys §UJ-056]

## Goal

Add a dedicated Quality metrics detail page with GitHub-style collapsible unified XML diffs (expand/collapse unchanged context), keeping C14N equality semantics.

## Intent

Follow-up from [S065 FOLLOWUP.md](../S065-quality-metrics-diff-long-line/FOLLOWUP.md) after pretty-print C14N display landed. Operators need a shareable stem route and readable hunk folding — not another change to match semantics.

| Decision | Choice |
|----------|--------|
| D-S065-close | **1** — merge #987; close S065; open this evolve |
| D-S066-route | **1** — Lean as drafted (`00 → 16 → 01 → 02 → 10 → 13`) |
| D-S066-ui-preview | **1** — non-deployed local UI at http://127.0.0.1:18000/ |
| D-S066-board | **1** — #988 → In progress (WIP 0→1) |

## Out of scope

- Changing `match_status` / C14N equality / fixture generator semantics
- New npm diff library unless AskQuestion approves (reuse `unifiedLineDiff.ts` + hunk fold helper)
- Promote `stage` → `main` unless explicitly approved
- API contract change unless shell routing genuinely requires it

## Features

- Deepen **F7.q** — Quality metrics dedicated detail route + collapsible diffs  
  ([Corpus: product §F7.q])
- Journey / tests: deepen **UJ-056** ([Corpus: journeys §UJ-056] [Corpus: tests §UJ-056])

## Acceptance (seed from FOLLOWUP — refine in 01)

| ID | Criterion |
|----|-----------|
| AC1 | List row opens a dedicated detail route (shareable URL) with back-to-list |
| AC2 | Official/Converted/TAC panes remain; normalized = pretty C14N |
| AC3 | Diff shows collapsible equal-context hunks (GitHub-like expand N lines / expand all) |
| AC4 | Unequal SIGMET stems remain navigable and readable on staging |
| AC5 | UJ-056 / related TCs updated; FE unit + optional Playwright smoke |

## Implementation notes

- Reuse `unifiedLineDiff` + `qualityMetricsDisplayXml` / `prettyPrintXml`
- Add hunk folding helper (e.g. `collapseEqualContext(lines, { context: 3 })`)
- Wire route in frontend shell next to Quality metrics tab
- Operator copy: no internal doc refs (EV-048)

## Board

- Project [#7 TAC-to-IWXXM](https://github.com/orgs/EMPIRIC2/projects/7)
- #988 → **In progress**
- Ready queue remains 3–5 (currently 4: #948, #958, #981, #983)

## Routing plan

See [routing-plan.md](./routing-plan.md).
