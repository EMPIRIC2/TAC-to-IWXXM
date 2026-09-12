---
session_id: S068-quality-metrics-diff-layout
type: feature
status: active
branch: evolve/EV-058-quality-metrics-diff-layout
orchestrator: 16-evolve
evolve_cycle_id: EV-058
github_issues: [983]
prior_session: S067-m0-ready-apex-accumulate-validate
opened: 2026-08-17
---

# Session brief — S068-quality-metrics-diff-layout

> **Cycle**: EV-058 · **Type**: feature · **Opened**: 2026-08-17  
> **Branch**: `evolve/EV-058-quality-metrics-diff-layout` @ `stage@c2ca9a3f`  
> **Orchestrator**: **16-evolve** · **Preset**: Lean  
> **Issue**: [#983](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/983) → **In progress**  
> **Corpus**: [Corpus: product §F7.q] [Corpus: journeys §UJ-056] [Corpus: tests §UJ-056]

## Goal

Add a user-selectable **inline (unified)** vs **side-by-side** XML diff layout on the F7.q Quality metrics detail page (`/quality/:stem`), with preference persistence and synced-scroll polish, without changing C14N match semantics.

## Intent

Natural follow-on to [S066 / EV-056 / #988](../S066-quality-metrics-diff-page/session-brief.md) (unified + collapsible context on stage). Operators reviewing noisy/large peers need an explicit layout choice; smaller blast radius than multi-issue M0 packs.

| Decision | Choice |
|----------|--------|
| D-S068-e0 | **1a/2b/3a/4a/5a** — evolve #983; persist preference + synced-scroll as AC; stage only; no blockers; proceed |
| D-S068-e1e2 | **recommended** — feature/16-evolve; #983 normal; operator pain; F7.q + UJ-056 fence |
| D-S068-e3e4 | **1a–4a** — product/journeys/tests/evolve-decisions; no CORPUS gap; Lean Spec; FE-only Build intent |
| D-S068-e5e6 | **1a–4a** — UI-only out-of-scope fence; compatible; H4–H5; local preview yes |
| D-S068-route | **1a/2a/3a** — Lean Spec `00→16→01→02`; Lean Build `10→13` blocked; open Spec-only |
| D-S068-ui-preview | **1** — non-deployed local UI at http://127.0.0.1:18000/ |
| D-S068-board | **1** — #983 → In progress |

## Out of scope

- API / backend contract changes
- New npm `diff` package (reuse `unifiedLineDiff` / existing helpers)
- C14N / `match_status` / fixture generator semantics
- Whitespace-normalize (#982) and non–Quality-metrics UI
- Promote `stage` → `main` unless separately approved

## Features

- Deepen **F7.q** — selectable side-by-side vs inline XML diff on detail page  
  ([Corpus: product §F7.q])
- Journey / tests: deepen **UJ-056** for both layout modes  
  ([Corpus: journeys §UJ-056] [Corpus: tests §UJ-056])

## Acceptance (seed — refine in 01)

| ID | Criterion |
|----|-----------|
| AC1 | Operator can switch Inline (unified) ↔ Side-by-side without reload |
| AC2 | Default remains unified (UJ-056 backward compatible unless journey updated) |
| AC3 | Side-by-side uses existing line-diff util; optional synced scroll; no new npm `diff` |
| AC4 | Layout preference persists (sessionStorage or localStorage) |
| AC5 | Raw TAC / diagnostics / collapse-equal-context remain; Vitest + Playwright cover both modes |

## Implementation notes

- Primary surface: `apps/frontend` `QualityMetricsDetail.tsx` + `unifiedLineDiff` / `collapseEqualContext`
- Operator copy: no internal doc refs (EV-048)
- PR target: `stage`; promote held

## Board

- Project [#7 TAC-to-IWXXM](https://github.com/orgs/EMPIRIC2/projects/7)
- #983 → **In progress** (`D-S068-board=1`)

## Routing plan

See [routing-plan.md](./routing-plan.md).
