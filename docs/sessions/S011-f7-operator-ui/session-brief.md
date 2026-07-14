---
session_id: S011-f7-operator-ui
type: feature
status: in_progress
branch: evolve/S011-f7-operator-ui
started_at: 2026-07-13
intent: "F7 multi-product TAC operator UI (7 products) + workbench (#694), decode panel (#702), failed-TAC/partial UX (#665/#666), remove admin / BYO DB (#697); #5 kept as parent tracker"
orchestrator: 16-evolve
evolve_cycle_id: null
context_briefs:
  - docs/context/f7-operator-ui.md
standing_docs_touched: []
---

# Session S011 — F7 operator UI + workbench / decode / admin

## Intent

Flip **F7** from Planned → built, and land the related operator-UX and product-model issues in one
evolve cycle:

| Issue | Theme |
|-------|--------|
| [#702](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/702) | TAC decode panel (Code \| Explanation) for all 7 products |
| [#694](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/694) | Interactive workbench: live validation, span highlight, live IWXXM, console |
| [#665](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/665) | Visual Failed-TAC cue |
| [#666](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/666) | Partial conversion for error highlighting |
| [#697](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/697) | Remove admin dashboard; BYO DB credentials |
| [#5](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/5) | Parent tracker — keep open |

## Scope

### In scope

- Multi-product operator entry UX on top of existing F6.e product/profile pickers
- Decode/annotate API + UI panel (#702)
- Span-aware validation/lint expansion + workbench UX (#694)
- Failed-TAC visual + partial/best-effort convert path (#665/#666)
- Admin dashboard / `/admin/*` retirement + BYO Supabase/DB credentials model (#697)
- Corpus deltas (feature-list F7, api-contract, env-contract, test-plan, ADRs as needed)

### Out of scope

- Extending **F5** My METARs to non-METAR products without an explicit F7 sessions design decision
- AMHS/SWIM/AFS, push sinks (F8 non-goals)
- Teaching/CMS content beyond short decode explanations (#702 v1)
- Rewriting conversion engines beyond span/decode/partial hooks

## Feature mapping

- **F7** — primary home (multi-product operator UI)
- **F6** — engine already Implemented; span/decode/partial are API deltas on F6 packages
- **F5** — METAR/SPECI sessions remain; admin browse path removed by #697
- **M4** — auth shrinks with admin removal

## Phase 0 approvals (2026-07-13)

- **Packaging A:** single session for all listed issues
- **Routing A:** 00→01→02→04→05→07–13 (skip 03, 06)
- **#5 A:** keep open as parent tracker

## Routing plan

See [routing-plan.md](./routing-plan.md).

## Links

- Scoped context: [docs/context/f7-operator-ui.md](../../context/f7-operator-ui.md) (in progress)
- Prior F7 stub: [docs/context/realtime-tac-ingest.md](../../context/realtime-tac-ingest.md)
- F6 engine context: [docs/context/general-tac-iwxxm-converter.md](../../context/general-tac-iwxxm-converter.md)
- Product: [docs/feature-list.md](../../feature-list.md) §F7
