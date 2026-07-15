---
session_id: S011-f7-operator-ui
type: feature
status: in_progress
branch: evolve/S011-f7-operator-ui
started_at: 2026-07-13
intent: "F7 multi-product TAC operator UI (7 products) + workbench (#694), decode panel (#702), failed-TAC/partial UX (#665/#666), remove admin / BYO DB (#697); #5 kept as parent tracker"
orchestrator: 16-evolve
evolve_cycle_id: EV-008
context_briefs:
  - docs/context/f7-operator-ui.md
standing_docs_touched: []
phase3_resolutions:
  R1: "milestone #697 → #702/spans → #665/#666 → #694"
  R2: "OVERRIDDEN by R2′ — unified tac_work_sessions + migrate F5 (was: separate F7 table; F5 METAR-only)"
  R2_prime: "unified tac_work_sessions; migrate metar_work_sessions; My METARs = filter"
  R3: "CodeMirror 6"
  R4: "decode-tac + lint/validate start/end spans"
  R5: "soft-fail preview with best-effort XML + failed markers"
  R6: "BYO-only (Supabase + Postgres/DATABASE_URL); no shared multi-tenant admin"
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
- Multi-product F7 work sessions via **unified** `tac_work_sessions` (R2′; migrate F5) — F5 My METARs stays a METAR/SPECI filter
- Decode/annotate API + UI panel (#702)
- Span-aware validation/lint expansion + workbench UX (#694)
- Failed-TAC visual + partial/best-effort convert path (#665/#666)
- Admin dashboard / `/admin/*` retirement + **BYO-only** credentials (Supabase **and**
  Postgres/`DATABASE_URL` / SQL URIs via deploy env) — R6
- Corpus deltas (feature-list F7, api-contract, env-contract, test-plan, ADRs as needed)

### Out of scope

- Quietly extending **F5** as a permanent parallel store (rejected — R2′ unify + migrate)
- AMHS/SWIM/AFS, push sinks (F8 non-goals)
- Teaching/CMS content beyond short decode explanations (#702 v1)
- Per-user paste-keys UI; rewriting conversion engines beyond span/decode/partial hooks

### Milestone order (R1)

1. #697 BYO + admin removal  
2. #702 decode + spans (+ CodeMirror 6)  
3. #665/#666 failed-TAC + partial preview  
4. #694 live workbench  
5. F7 unified sessions + F5 migrate (R2′)  
6. Verify & deploy (08–13)

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

- Scoped context: [docs/context/f7-operator-ui.md](../../context/f7-operator-ui.md) (**active**)
- Prior F7 stub: [docs/context/realtime-tac-ingest.md](../../context/realtime-tac-ingest.md)
- F6 engine context: [docs/context/general-tac-iwxxm-converter.md](../../context/general-tac-iwxxm-converter.md)
- Product: [docs/feature-list.md](../../feature-list.md) §F7
