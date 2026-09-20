# EV-pack-ir-convert-wire — draft-docs decisions

**Session:** `EV-pack-ir-convert-wire`  
**Date:** 2026-09-20  
**Corpus:** [Corpus: product §F6] [Corpus: product §F9] [Corpus: api] [Corpus: tests] [Corpus: journeys] [Corpus: adr/ADR-045] [Corpus: decisions]

## What changed

| Document | Delta |
|---|---|
| `docs/feature-list.md` | F6/F9 deepen notes for pack fill + convert emit / default flip |
| `docs/spec.md` | `tac-decoding` + `tac2iwxxm` deepen bullets |
| `docs/adr/ADR-045-shared-tac-pack-engine.md` | Amend 2026-09-20 (span boundary, flip ≠ delete) |
| `docs/test-plan.md` | TC-EV-PACKIR-001..005; UJ-077 mapping |
| `docs/user-journeys.md` | UJ-077 deepen note |
| `docs/api-contract.md` | Endpoint review — no wire change |
| `docs/decisions/evolve-decisions.md` | Cycle locks |
| `docs/context/pack-ir-convert-wire.md` | Scoped context |

## Not in this delta

- New required Render secrets
- New WMO example files
- HTTP field additions
- `products/*.py` deletion
