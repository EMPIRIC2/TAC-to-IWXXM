---
session_id: S043-rule-source-traceability
type: feature
status: in_progress
branch: evolve/EV-035-rule-source-traceability
started_at: 2026-08-05
intent: "Re-analyze reviewed domain docs + extracted rules; link each rule to sources; standing provenance under docs/domain/rules/; raise unfindable rules; dense asserts"
orchestrator: 16-evolve
evolve_cycle_id: EV-035
prior_session: S042-doks-cd-rollout
context_briefs:
  - docs/context/rule-source-traceability.md
standing_docs_touched:
  - docs/domain/rules/
  - docs/domain/TAC_VALIDATION.md
  - docs/domain/IWXXM_CONVERSION.md
  - docs/domain/IWXXM_VALIDATION.md
  - docs/domain/mining/
  - docs/feature-list.md
  - docs/test-plan.md
  - docs/decisions/evolve-decisions.md
feature_ids: []
deepen_feature_ids:
  - F6
  - F12
  - F15
  - F2
feature_note: "Deepen-only (G1=2) — provenance map under docs/domain/rules/; no new Fn"
route_status: approved_G2
---

# Session S043 — rule-source-traceability

## Intent

Re-analyze documents already mined/reviewed and rules already extracted; **link every
rule back to its source**; establish **ongoing provenance tracking** under
`docs/domain/rules/` (**no new Fn**); raise any rule without a findable normative cite.
For every rule we cite or revisit, ship **dense automated asserts**.

## Phase 0 + gates (locked)

| ID | Decision |
|----|----------|
| Q1 | Both — audit+link **and** standing provenance under domain/rules |
| Q2 | Full stack — ISSUE_CATALOG + encode/SCH + bulletin AHL/ops |
| Q3 | Open S043 → EV-035 |
| Q4 | Standard + dense asserts |
| G1 | Deepen **F6/F12/F15/F2** only — **no F33** |
| G2 | Standard routing approved |
| G3 | Path-cite `[docs/domain/…]` — no CORPUS membership |
| G4 | Proceed 01 → 02 |

## Scope

### In

- Inventory digs ↔ RULE_SOURCE_URLS ↔ canonicals ↔ COVERAGE_MATRIX ↔ ISSUE_CATALOG
- Standing provenance map under `docs/domain/rules/` + index updates
- Gap list raised to user / tickets
- Dense CI asserts (TC-EV035-001..006); reuse F29 patterns
- Deepen F6 / F12 / F15 / F2 cite parity

### Out

- New product Fn; browser UI; vendor schema hand-edits; closing all #846 children

## Routing (approved)

`00 → 16 → 01 → 02 → 04 → 07 → 08 → 09 → 11 → 12 → 13`  
Skip: `03`, `05`, `06`, `10`

## Branch

`evolve/EV-035-rule-source-traceability`

## Progress

| Stage | Status |
|-------|--------|
| 00-context | completed |
| 01-requirements | completed — `reports/01-requirements-summary.md` |
| 02-verify-plan | **next** |

## UI preview

**N/A** — no browser UI.
