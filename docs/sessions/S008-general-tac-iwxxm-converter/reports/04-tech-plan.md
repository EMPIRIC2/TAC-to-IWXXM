# S008 — 04-tech-plan delta summary

> **Session**: S008-general-tac-iwxxm-converter  
> **Stage**: 04-tech-plan (delta)  
> **Completed**: 2026-07-12  
> **Branch**: `evolve/S008-general-tac-iwxxm-converter`

## Deliverables

| Artifact | Path |
|----------|------|
| Execution plan | [execution-plan.md](./execution-plan.md) |
| ADR-016 | `docs/adr/ADR-016-msgspec-subsecond-perf.md` |
| ADR-017 | `docs/adr/ADR-017-pyo3-cutover-gate.md` |
| ADR-018 | `docs/adr/ADR-018-f8-worker-template.md` |

## Interview batches

| Batch | Topics | Decision IDs |
|-------|--------|--------------|
| 1 | Layout, msgspec, validate extract, bulletin order, cutover | D-S008-04-q1q5 |
| 2 | Bulletin schema, lint-tac, H7 | D-S008-04-q6q10 |
| 3 | Perf, PyO3, iwxxm-us, lint-on-convert, deploy | D-S008-04-q11q15-provisional + clarifications |
| 4 | F8 poller/store/quarantine/worker/auth | D-S008-04-q16q20 |

## Plan shape

- **6 phases / 7 milestones / 44 tasks**
- Cutover hard-gated on **PyO3 + sub-second benches** (ADR-017)
- **F8** `apps/worker` Render Background Worker (ADR-018)
- HTTP convert/lint/validate remain on existing API

## Specs back-updated

- `docs/feature-list.md` — F8 build-this-cycle; M1 `apps/worker`; non-goals amend
- `docs/api-contract.md` — bulletin + lint-tac schemas; `lint` default true
- `docs/dependency-inventory.md` — msgspec + required PyO3
- `docs/adr/README.md` + ADR-015 amendment note

## Next

**05-verify-tech** (delta) — audit execution plan + ADRs against corpus.
