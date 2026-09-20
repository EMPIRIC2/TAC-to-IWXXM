# EV-pack-fill-delete-gate — draft-docs decisions

**Session:** `EV-pack-fill-delete-gate`  
**Date:** 2026-09-20  
**Issue:** [#1214](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1214)  
**Corpus:** [Corpus: product §F6] [Corpus: product §F9] [Corpus: api] [Corpus: tests] [Corpus: journeys] [Corpus: adr/ADR-045] [Corpus: decisions] [Corpus: tech-spec]

## What changed

| Document | Delta |
|---|---|
| `docs/feature-list.md` | F6/F9 deepen notes for fill+wire + selective delete-gate |
| `docs/spec.md` | `tac-decoding` + `tac2iwxxm` deepen bullets |
| `docs/adr/ADR-045-shared-tac-pack-engine.md` | Amend 2026-09-20 (selective delete-gate, mapper independence, stricter peers) |
| `docs/test-plan.md` | TC-EV-PFDG-001..005 |
| `docs/user-journeys.md` | UJ-077 deepen note |
| `docs/api-contract.md` | Endpoint review — no wire change |
| `docs/config-spec.md` | `TAC2IWXXM_CONVERT_IR_SOURCE` auto expands per flipped products |
| `docs/decisions/evolve-decisions.md` | Cycle locks D-PFDG-* |
| `docs/context/pack-fill-delete-gate.md` | Scoped context |

## Not in this delta

- New required Render secrets
- New WMO example files
- HTTP field additions
- Package merge

## Verify cite-duty (F76 / skill-compliance)

Session HANDOFF Evidence cites `reports/memory-context.md` when hooks are enabled.
Documenting twin: this note states the memory-context / HANDOFF Evidence cite duty for
skill-compliance.
