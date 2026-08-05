---
session_id: S040-iwxxm-corpus-quality
type: feature
status: suspended
branch: evolve/EV-032-iwxxm-corpus-quality
started_at: 2026-08-04
suspended_at: 2026-08-04
suspended_for: S041-worker-poller-hardening
intent: "Official IWXXM corpus quality / WMO source parity — #846 epic; #835 A6-2 wmoPass; F32 VONA (#741); #808 release-line adoptability; corpus children."
orchestrator: 16-evolve
evolve_cycle_id: EV-032
github_issues:
  - 846
  - 835
  - 741
  - 808
prior_session: S039-doks-dns-cutover
context_briefs:
  - docs/context/iwxxm-corpus-quality-846.md
standing_docs_touched: []  # filled after 01/04
feature_ids: [F32, F23, F6, F2, F4, F13]
feature_note: "D-S040-open — F32 VONA (#741) + deepen F23 (#835) + F4/F6/F2/F13 (#808 + corpus)"
ask_question: written interview — D-S040-open = 1,1,1,1
ui_preview: pending — AskQuestion at routing gate (engine-heavy; default docs/repo)
---

# Session S040 — iwxxm-corpus-quality

> **Suspended 2026-08-04** for [S041-worker-poller-hardening](../S041-worker-poller-hardening/session-brief.md) / EV-033.
> Not completed or cancelled. Resume at `13-deploy-smoke` / T4.5 after S042 (CD session);
> do not auto-resume now. EV-032 remains `in_progress`.

## Intent

Raise and prove quality against the **official WMO IWXXM corpus** and related WMO sources,
under epic [#846](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/846), in this order:

| Order | Issue | Focus |
|------:|-------|--------|
| 1 | [#835](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/835) | TC SIGMET A6-2-TC ADR-032 equality → `wmoPass` (S037 residual) |
| 2 | [#741](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/741) | **F32** VONA quality bar (lint / convert / validate) |
| 3 | [#808](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/808) | Maintainability of adopting new IWXXM release lines |
| 4 | Corpus track | Child gaps vs iwxxm / iwxxm-translation / iwxxm-codelists / codes.wmo.int / iwxxm-modelling |

## Prior session

| Item | Disposition |
|------|-------------|
| S039 / DOKS DNS | **Completed** — public HTTPS api\|app.tac-to-iwxxm.com |
| S037 / EV-030 | **Completed** — F29; residual **#835** open |
| S036 | VONA / SIGWX / QVACI were **OOS** — #741 is new scope |

## Scope (locked — D-S040-open = 1,1,1,1)

### In

1. **#846** — Epic roll-up; file corpus children as discovered
2. **#835** — `canonicalize_xml` equality vs vendor A6-2-TC; catalog → `wmoPass`
3. **#741 / F32** — VONA encode cookbook + fixtures + lint/validate path (guidance silent)
4. **#808** — Adopt/deprecate checklists + blast-radius assessment (no re-pin in-ticket)
5. Corpus / WMO-source parity gaps filed as children of #846

### Out

- Metrics UI [#836](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/836) / workbench epic [#840](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/840)
- Hand-editing `vendor/schemas/*` outside sync PRs
- Shipping a new IWXXM pin inside #808
- Platform / Dissemination / DOKS work unrelated to encode quality

## Routing

**Preset:** Standard — `00→16→01→02→04→07→08→09→10→11→12→13` (`D-S040-route` = 1)  
**Skip:** `03, 05, 06` unless 04 surfaces new deps/tooling  
See [routing-plan.md](routing-plan.md).

## Branch note

`D-S040-branch` = 1 — cut `evolve/EV-032-iwxxm-corpus-quality` from `main`. EV-031/S039 dirty
worktree parked in stash (not carried onto this branch).

## Links

- Epic: [#846](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/846)
- Scoped brief: [iwxxm-corpus-quality-846](../../context/iwxxm-corpus-quality-846.md)
- Standing: [feature-list.md](../../feature-list.md), [CORPUS.md](../../CORPUS.md)
