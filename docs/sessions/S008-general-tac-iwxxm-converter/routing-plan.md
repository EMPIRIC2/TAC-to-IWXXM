# Routing plan — S008-general-tac-iwxxm-converter

**Amended 2026-07-12** (`D-S008-realtime-amend-q1q2q3`): reopen scoped **00-context** + delta **01-requirements** for realtime ingest + data-entry.

**Updated 2026-07-12** (`D-S008-01-realtime-amend-complete`): **01-requirements** delta `S008-realtime-ingest` **completed**; next **04-tech-plan**.

| Stage | Required | Mode | Status | Skip / reopen rationale |
|-------|----------|------|--------|-------------------------|
| 00-context | yes | scoped (`realtime-tac-ingest`) | **completed** | Scoped refresh done; prior `general-tac` brief retained |
| 01-requirements | yes | delta (`S008-realtime-ingest`) | **completed** | Amend complete — 7/7 interviews; ADR-015; prior F6 delta historical |
| 02-verify-plan | no | — | skipped | Tooling/corpus already mature; delta docs verified in 05 |
| 03-plan-tooling | no | — | skipped | Hooks/rules exist; build tooling deferred to 04/06 if chosen |
| 04-tech-plan | yes | delta | **pending** | Next — package layout, ingest pipeline, Schematron/F2 gate, metrics |
| 05-verify-tech | yes | delta | pending | Audit tech plan against vendor + gifts/tac2iwxxm constraints |
| 16-evolve | yes | full | pending | Evolve cycle EV-00N — feature ids, ADR, execution plan |
| 07-build | yes | full | pending | After evolve plan approved |
| 08-verify-build | yes | full | pending | Milestone gates |
| 09-qa | yes | full | pending | Quality suite |
| 10-e2e | yes | delta | pending | Only if API/UI surface changes |
| 11-verify-impl | yes | full | pending | Corpus parity |
| 12-verify-deploy | no | — | skipped | Until package/ingest is wired into deployables |
| 13-deploy-smoke | no | — | skipped | Until deploy wiring exists |

## Amend resolutions (Q1–Q3)

| Q | Choice | Meaning |
|---|--------|---------|
| Q1 | A | Amend S008 (reopen 00+01); do not open a new session |
| Q2 | B | Realtime = **ingest pipeline** (continuous feed → near-RT convert + Schematron) |
| Q3 | A | Schematron is **IWXXM-only** (extend F2); TAC uses separate syntax/business checks |

## Approved

- Initial routing: 2026-07-12 (close S007 + open S008).
- Amend reopen 00/01: 2026-07-12 (`D-S008-realtime-amend-q1q2q3`).
- 01 realtime amend complete: 2026-07-12 (`D-S008-01-api-q51q54` / `D-S008-01-realtime-amend-complete`).
