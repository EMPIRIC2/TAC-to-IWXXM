# EV-080 — Parameterizable conversion templates (decisions)

**Date:** 2026-09-14  
**Session:** `EV-080-param-conversion-templates`  
**Ticket:** [#1146](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1146)  
**Corpus:** [Corpus: product §F7.w] [Corpus: adr/ADR-038] [Corpus: api] [Corpus: tests] [Corpus: journeys]

## Locked choices

| ID | Decision |
|----|----------|
| D-EV080-req | Requirements delta locked (`D-EV080-req=1`) — phase-1 templates + bridge only |
| D-SCOPE-01 | Deepen F7.w via #1146 (no new Fn) |
| D-PHASE-01 | Ship conversion templates + TAC→IWXXM bridge UI only |
| D-TRUST-01 | JWT owner custom CRUD; first-party view+fork only |
| D-DEC-01 | Separate Decoding library long-term; reuse `decode_tac`; out of phase-1 ship |
| D-DISS-01 | N/A phase-1; dissem UX timing still D-DISS-UX-01 when dissem ships |
| D-PRESET-01 | Extend EV-1051 refs pattern; preset UX deepen deferred if it blocks phase-1 |
| D-UI-preview | No non-deployed UI preview during requirements (`R2=2`) |
| CORPUS | Deltas into existing rows; ADR-038 amend (not new CORPUS member) |

## Directions accepted

See session `evidence/intake-decisions.md` (D-CONV-*, D-UX-*, D-UI-*, D-LIB-01, D-MATCH-01, D-DISS-UX-01).

## Standing doc updates (this cycle)

- `docs/feature-list.md` — F7.w EV-080 AC
- `docs/user-journeys.md` — UJ-072e
- `docs/test-plan.md` — TC-EV080-001..006 + matrix
- `docs/api-contract.md` — §EV-080 routes
- `docs/adr/ADR-038-conversion-profile-contract.md` — EV-080 amend
- `docs/spec.md` — F7.w EV-080 delta
- `docs/engineering/NOW.md` — #1146 active EV-080
