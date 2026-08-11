# Build Plan Card — S064 / EV-055

> Updated: 2026-08-11 · Branch: `evolve/EV-055-quality-metrics-2025-2-followups`  
> Active: Phase 1 / M3 complete locally · next M4 · Gate B `D-S064-05=1`

## Goal

Ship W3C C14N Quality-metrics match/diff (#982) with normalized panes (override→raw), and
**hard-fix** 2025-2 Schematron enable (#980) + SCHEMA_IMPORT (#979).

## Constraints

- [Corpus: product §F7] [Corpus: adr/ADR-035] [Corpus: api] [Corpus: tests]
- C14N Python in iwxxm-validate; FE `c14nXml.ts`; ADR-032 untouched for other callers
- **`D-S064-c14n-volatile=1`**: C14N **after** volatile-attr strip (not pure C14N)

## In scope (this batch — M3)

- [x] T3.1 — Test — Generator formatting-only → `match_status=equal` under C14N — Spec: TC-EV055-002
- [x] T3.2 — Impl — Switch generator match to `c14n_xml` — Spec: AC2; ADR-035
- [x] T3.3 — Data/Test — Regen `corpus_metrics.json` + loader smoke — Spec: TC-EV055-006

## Out of scope

Vendor hand-edits; ADR-032 global replace; stage→main.

## Dependencies / blockers

- Prior: M1+M2 complete
- Unblocked: `D-S064-c14n-volatile=1` (pure-C14N trial reverted)

## Acceptance for this batch

- [x] TC-EV055-002 / TC-EV055-006 green (unit + regen; loader 7 passed `--no-cov`)
- [x] Artifact committed with C14N+volatile-strip `match_status` (pending git commit)

## Regen summary (post–volatile strip)

| Product | equal | unequal | deferred |
|---------|------:|--------:|---------:|
| metar | 1 | 0 | 1 |
| speci | 1 | 0 | 0 |
| taf | 2 | 0 | 1 |
| sigmet | 1 | 4 | 0 |
| swxa | 1 | 0 | 2 |
| airmet / tca / vaa / vona | 0 | 1 each | 0 |

## Next

**07-build** M4 — FE panes + diff on C14N peers.
