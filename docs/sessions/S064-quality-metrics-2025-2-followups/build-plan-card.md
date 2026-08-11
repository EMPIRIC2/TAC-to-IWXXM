# Build Plan Card — S064 / EV-055

> Updated: 2026-08-11 · Branch: `evolve/EV-055-quality-metrics-2025-2-followups`  
> Active: Phase 1 / M1 / T1.1 · Plan approved `D-S064-04-plan=1`

## Goal

Ship W3C C14N Quality-metrics match/diff (#982) with normalized panes (override→raw), and
**hard-fix** 2025-2 Schematron enable (#980) + SCHEMA_IMPORT (#979).

## Constraints

- [Corpus: product §F7] [Corpus: product §F2] [Corpus: product §F13]
  [Corpus: api] [Corpus: journeys §UJ-056] [Corpus: tests] [Corpus: decisions §EV-055]
- Branch base `stage@4fd51e39`; PR → `stage` only
- Vendor schemas read-only; no new npm; no new runtime deps unless amended
- Hard: C14N always; #980 enable; #979 fix; shared generator+FE helper

## In scope (this batch — M1)

- [ ] T1.1 — Test — Red: no `SCHEMATRON_SKIPPED` close for 2025-2 — Spec: TC-EV055-004
- [ ] T1.2 — Impl — Enable Schematron (native) + matrix doc — Spec: AC4 / #980
- [ ] T1.3 — Test — Red: SCHEMA_IMPORT_WARNING fixed path — Spec: TC-EV055-005
- [ ] T1.4 — Impl — Fix XSD import + backend parity — Spec: AC5 / #979

## Out of scope (explicit)

Vendor hand-edits; redo #836 shell; ADR-032 global replace; DOKS; stage→main; new npm C14N.

## Dependencies / blockers

- Data: vendor 2025-2 pin (staged)
- Prior: Gate A PASS; 04 plan approval
- Tooling: 06 skipped unless native enable invents a dep

## Acceptance for this batch

- [ ] TC-EV055-004 / TC-EV055-005 green
- [ ] Engine matrix documented; no soft-skip-as-success for this cycle
- [ ] Connectivity: no new CORS; H4–H5 later via 12/13

## Milestones (07 order)

| M | Goal | Exit |
|---|------|------|
| M1 | Engine #980/#979 hard | TC-EV055-004..005 |
| M2 | C14N helpers Py+FE + ADR | TC-EV055-003 |
| M3 | Generator + regen | TC-EV055-002/006 |
| M4 | FE panes + diff + chips | TC-EV055-001; AC6 |
| M5 | Playwright + docs/CI | TC-EV055-007 |

## Execution plan

`docs/sessions/S064-quality-metrics-2025-2-followups/reports/execution-plan.md` (17 tasks T1.1–T5.3)

## Next Plan prompt

```
Refine S064 M1 batch only.
Read build-plan-card.md + execution-plan M1 tasks.
Produce ordered tasks, parallel groups (T1.1∥T1.3), risks if native Schematron enable fails.
Do not implement.
```

## Next

**05-verify-tech** (Gate B) → then **07-build** M1.
