# 04-tech-plan — S047 / EV-039

> Completed: 2026-08-06 · Mode: delta · `D-S047-04-plan`=1

## Locked tech answers (`D-S047-04`)

| Q | Reply | Locked meaning |
|---|-------|----------------|
| Q1 | **1** | `down -v --remove-orphans` + orphan assert |
| Q2 | **1** | Async-driver write assertion after UI success |
| Q3 | **1+3** | `make test-e2e-f16-live-sql` **and** `F16_LIVE_SQL=1` on `test-live-e2e` |
| Q4 | **1+2+3 (local only)** | **Local:** LIVE in `make test-live` + all four dialects required. **CI:** opt-in; SQL Server skippable; LIVE off default CI |

## Artifacts

| Path | Role |
|------|------|
| [execution-plan.md](execution-plan.md) | Phase 1 · M1–M2 · T1.1–T2.5 (10 tasks) — **approved** |
| [../build-plan-card.md](../build-plan-card.md) | Active batch = M1 / T1.1 |

## Next

**05-verify-tech** (Gate B) — audit drafted; awaiting `D-S047-05-gate-b`.
