---
session_id: S026-airmet-quality-wmo-examples
type: feature
status: in_progress
branch: evolve/EV-020-airmet-quality
started_at: 2026-07-29
intent: "AIRMET #731 + METAR/SPECI/TAF WMO byte-golden parity + UI only passers + 7-product decode glossary (registry + OpenAIP)"
orchestrator: 16-evolve
evolve_cycle_id: EV-020
github_issues:
  - 731
context_briefs: []
standing_docs_touched:
  - docs/decisions/evolve-decisions.md
  - docs/feature-list.md
feature_ids:
  - F24
  - F25
feature_note: "F24 AIRMET quality; F25 WMO METAR/SPECI/TAF parity + UI gate; deepen F9/F7.g/F6/F3"
---

# Session S026 — airmet-quality-wmo-examples

## Intent

Raise **AIRMET** to the F15/F20/F23 quality bar (#731) and bring **METAR / SPECI / TAF**
(and AIRMET) convert output to **strict byte-identical** match against WMO IWXXM `2025-2`
vendor examples. Operator **Examples** catalog lists **only** demos that pass that bar.
Deepen **F9** decode to a full **7-product** plain-English glossary via an **extensible
registry**, with **OpenAIP / F3** name enrichment when available.

## Prior session

| Item | Disposition |
|------|-------------|
| S025 / EV-019 | **Completed** — F23 SIGMET; PR #792 (`afffe86`) — SIGMET A6-1a/CNL already WMO-identical |
| S021 / EV-016 | F7.g golden examples UI (#780) |
| S013 / EV-009 | F9 value-aware decode |

## Scope (locked — E20-1..6 / E20-A / E20-B)

### In

- [#731](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/731) AIRMET quality → WMO `airmet-A6-1a-TS` byte-identical
- METAR/SPECI/TAF WMO official example byte-identical (`metar-A3-1`, `speci-A3-2`, `taf-A5-*` as planned in 04)
- UI catalog: only WMO-passing examples (hide/remove non-passers for in-scope products)
- Decode glossary: all 7 products; YAML/JSON registry; OpenAIP/F3 names when resolvable
- Keep F23 SIGMET passers green

### Out (unless added later)

- TC SIGMET #738, new SWX/VONA quality bars, PyPI release bumps
- Local UI preview at session open (E20-6=No)

## Routing

See [routing-plan.md](./routing-plan.md). Initial preset Lean+build; **amend pending** because
encode scope (E20-A=2) is multi-milestone.

## Current stage

**00-context / 16-evolve Phase 0–1** — intake locked; Fn proposed; routing amend AskQuestion;
then 01-requirements.

## Links

- Issue: [#731](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/731)
- Decisions: [evolve-decisions.md](../../decisions/evolve-decisions.md) §EV-020
- Vendor goldens: `vendor/schemas/iwxxm/2025-2/IWXXM/examples/`
