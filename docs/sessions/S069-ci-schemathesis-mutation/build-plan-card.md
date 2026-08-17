# Build Plan Card — S069 / EV-059

> Cycle: EV-059 | Session: S069-ci-schemathesis-mutation | Updated: 2026-08-17  
> Spec→Build: **open** | Status: **M2 in progress** (`D-S069-m1-merge=1a`)

## Goal (07)

Ship F34 Schemathesis (#727) as PR1 → `stage`, then mutation (#874) as PR2. Keep CI cheap.

## Startup (locked)

| ID | Choice |
|----|--------|
| D-S069-07-start | **1a–6a** — M1 Schemathesis through 08+PR; T1.1–T1.6 only; locked budgets; proceed |
| D-S069-m1-merge | **1a** — merge #997; start M2 mutation #874 |

## Milestones

### M1 — Schemathesis (#727) — **done** (PR #997 merged)

| Task | Description | Spec / TC | Status |
|------|-------------|-----------|--------|
| T1.1–T1.6 | Schemathesis suite + CI + PR → `stage` | TC-F34-001..002 / 007 | **done** |

### M2 — Mutation (#874) — **active**

| Task | Description | Spec / TC | Status |
|------|-------------|-----------|--------|
| T2.1 | pytest-gremlins + Stryker configs / make targets | TC-F34-003..005 | done |
| T2.2 | Nightly / workflow_dispatch matrix (Python + TS) | D-S069-01-matrix | done |
| T2.3 | Kill survivors or waive; 08 + PR → `stage` for #874 | AC5–AC6 | in_progress |

## In scope (M2 batch)

T2.1–T2.3 — mutation only (do not rebundle Schemathesis).

## Out of scope (unchanged)

Mutation every PR; Rust mutation; live staging/prod Schemathesis merge gate; product UI; weaken ≥95%; promote; replace hand-written UJ/pytest.

## PR cadence

1. ~~Minor PR: Schemathesis → `stage`~~ (#997 merged)
2. Minor PR: Mutation → `stage` (closes #874; then #841)
3. Promote held
