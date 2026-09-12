---
session_id: S030-apac-encode-validate
type: feature
status: in_progress
branch: evolve/EV-023-apac-encode-validate
started_at: 2026-07-30
intent: "Implement encode/validate/lint deltas from APAC FAQ + codes.wmo.int + WMO-306 historical digs (#800) — engine + goldens under vendor pin v2025-2"
orchestrator: 16-evolve
evolve_cycle_id: EV-023
github_issues:
  - 800
context_briefs: []
standing_docs_touched:
  - docs/feature-list.md
  - docs/test-plan.md
  - docs/config-spec.md
  - docs/user-journeys.md
  - docs/decisions/evolve-decisions.md
  - docs/decisions/requirements-decisions.md
feature_ids: [F6, F2, F12, F13]
feature_note: "Deepen F6/F2/F12/F13 — no new Fn; full #800 P0+P1+actionable P2"
---

# Session S030 — apac-encode-validate

## Intent

Implement concrete **encode / lint / Schematron / fixture** deltas surfaced by completed
mining sessions, per [#800](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/800). Digs are
**done** — this cycle is engine + goldens only under runtime SoT `vendor/manifest.json` →
IWXXM **v2025-2**.

## Prior session

| Item | Disposition |
|------|-------------|
| S029 / EV-022 | **Cancelled/parked** (D-S029-park) — F9 decode deferred; work may already be on main via #799 |
| S027 / EV-021 | **Completed** — F26/F27 VAA+TCA; PR #794 |
| #797 | **Superseded** by #800 |
| #798 | **Closed** (dig); optional encode QA folded into #800 |

## Scope (locked — E23-1..E23-4)

### In — full #800 backlog

**P0:** NSC vs layered cloud; missing WX / Guidance nils; `translationFailedTAC` quarantine  
**P1:** Dual-register colour/nil (offline); iwxxm-translation informative suite; `translationCentre*` gate  
**P2:** SIGMET FIR/“S OF” helpers (#738 coord); COLLECT/multi-version (F16–F19); optional #798 QA; coverage matrix confirm  

### Out

Ticket Out-of-scope section; #740/#741; PDF remine; AMHS/FTBP ops; FAQ/2019 as equal-weight SoT;
`.local/` binaries; SAF/runway-state under 2025-2

## Routing

See [routing-plan.md](./routing-plan.md). **Approved** Lean+build + 13 when behavior ships (E23-3/4).

## Current stage

**01-requirements** — delta written; pending close → **02-verify-plan**.

## Links

- Issue: [#800](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/800)
- Report: [reports/01-requirements.md](./reports/01-requirements.md)
