# Build Plan Card — S064 / EV-055

> Updated: 2026-08-11 · Branch: `evolve/EV-055-quality-metrics-2025-2-followups`  
> Active: Phase 1 / M2 / T2.1 · Plan approved `D-S064-04-plan=1` · Gate B `D-S064-05=1`

## Goal

Ship W3C C14N Quality-metrics match/diff (#982) with normalized panes (override→raw), and
**hard-fix** 2025-2 Schematron enable (#980) + SCHEMA_IMPORT (#979).

## Constraints

- [Corpus: product §F7] [Corpus: product §F2] [Corpus: product §F13]
  [Corpus: api] [Corpus: journeys §UJ-056] [Corpus: tests] [Corpus: decisions §EV-055]
- Branch base `stage@4fd51e39`; PR → `stage` only
- Vendor schemas read-only; no new npm; C14N Python in iwxxm-validate (`D-S064-c14n-host=1`)
- Hard: C14N always; #980 enable; #979 fix; generator+FE helper semantics

## In scope (this batch — M2)

- [ ] T2.1 — Test — Python W3C C14N helper + golden — Spec: TC-EV055-003
- [ ] T2.2 — Impl — `c14n_xml` in `packages/iwxxm-validate` — Spec: AC3; `D-S064-c14n-host=1`
- [ ] T2.3 — Test/Impl — FE TS C14N helper + Vitest parity — Spec: TC-EV055-003
- [ ] T2.4 — Docs — ADR: Quality metrics C14N vs ADR-032 — Spec: `D-S064-adr-c14n`

## Out of scope (explicit)

Vendor hand-edits; redo #836 shell; ADR-032 global replace; DOKS; stage→main; new npm C14N.

## Dependencies / blockers

- Data: vendor 2025-2 pin (staged)
- Prior: M1 complete (TC-EV055-004..005)
- Tooling: 06 skipped

## Acceptance for this batch

- [ ] TC-EV055-003 green (Py + FE)
- [ ] ADR recorded; shared semantics for generator + FE

## Milestones (07 order)

| M | Goal | Exit |
|---|------|------|
| M1 | Engine #980/#979 hard | **done** TC-EV055-004..005 |
| M2 | C14N helpers Py+FE + ADR | TC-EV055-003 |
| M3 | Generator + regen | TC-EV055-002/006 |
| M4 | FE panes + diff + chips | TC-EV055-001; AC6 |
| M5 | Playwright + docs/CI | TC-EV055-007 |

## Execution plan

`docs/sessions/S064-quality-metrics-2025-2-followups/reports/execution-plan.md` (17 tasks T1.1–T5.3)

## Next

**07-build** M2 — T2.1–T2.4 C14N helpers.
