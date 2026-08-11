# Build Plan Card — S064 / EV-055

> Updated: 2026-08-11 · Branch: `evolve/EV-055-quality-metrics-2025-2-followups`  
> Active: Phase 1 / M3 / T3.1 · Gate B `D-S064-05=1`

## Goal

Ship W3C C14N Quality-metrics match/diff (#982) with normalized panes (override→raw), and
**hard-fix** 2025-2 Schematron enable (#980) + SCHEMA_IMPORT (#979).

## Constraints

- [Corpus: product §F7] [Corpus: adr/ADR-035] [Corpus: api] [Corpus: tests]
- C14N Python in iwxxm-validate; FE `c14nXml.ts`; ADR-032 untouched for other callers

## In scope (this batch — M3)

- [ ] T3.1 — Test — Generator formatting-only → `match_status=equal` under C14N — Spec: TC-EV055-002
- [ ] T3.2 — Impl — Switch generator match to `c14n_xml` — Spec: AC2; ADR-035
- [ ] T3.3 — Data/Test — Regen `corpus_metrics.json` + loader smoke — Spec: TC-EV055-006

## Out of scope

Vendor hand-edits; ADR-032 global replace; stage→main.

## Dependencies / blockers

- Prior: M1+M2 complete
- Native build recommended for validate issues in regen

## Acceptance for this batch

- [ ] TC-EV055-002 / TC-EV055-006 green
- [ ] Artifact committed with C14N match_status

## Next

**07-build** M3 — generator + regen.
