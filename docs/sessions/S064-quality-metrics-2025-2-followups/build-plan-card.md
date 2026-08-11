# Build Plan Card — S064 / EV-055

> Updated: 2026-08-11 · Branch: `evolve/EV-055-quality-metrics-2025-2-followups`  
> Active: Phase 1 / M4 complete · next M5 · Gate B `D-S064-05=1`

## Goal

Ship W3C C14N Quality-metrics match/diff (#982) with normalized panes (override→raw), and
**hard-fix** 2025-2 Schematron enable (#980) + SCHEMA_IMPORT (#979).

## Constraints

- [Corpus: product §F7] [Corpus: adr/ADR-035] [Corpus: api] [Corpus: tests] [Corpus: journeys]
- C14N after volatile-attr strip (`D-S064-c14n-volatile=1`)
- Panes default C14N; override → raw; diff always C14N peers (`D-S064-gateA-M2=override`)

## In scope (this batch — M4)

- [x] T4.1 — Vitest: default panes C14N; toggle raw; formatting stem diff empty — Spec: TC-EV055-001
- [x] T4.2 — Wire `QualityMetricsDetail` C14N panes + override + `unifiedLineDiff` on C14N — Spec: AC1/AC6
- [x] T4.3 — Validate chips enabled/fixed disposition; operator copy clean — Spec: AC6

## Out of scope

Vendor hand-edits; ADR-032 global replace; Playwright (M5); stage→main.

## Acceptance for this batch

- [x] TC-EV055-001 Vitest green
- [x] Default panes C14N; override shows raw; diff uses C14N peers
- [x] Validate chips: Schematron evaluated / schema import resolved (skip codes → not OK)

## Next

**07-build** M5 — Playwright UJ-056 deepen + docs/CI closeout.
