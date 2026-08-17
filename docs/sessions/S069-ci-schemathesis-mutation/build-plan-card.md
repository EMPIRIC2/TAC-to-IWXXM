# Build Plan Card — S069 / EV-059

> Cycle: EV-059 | Session: S069-ci-schemathesis-mutation | Updated: 2026-08-17  
> Spec→Build: **open** | Status: **M1 in progress** (`D-S069-07-start=1a..6a`)

## Goal (07)

Ship F34 Schemathesis (#727) as PR1 → `stage`, then mutation (#874) as PR2. Keep CI cheap.

## Startup (locked)

| ID | Choice |
|----|--------|
| D-S069-07-start | **1a–6a** — M1 Schemathesis through 08+PR; T1.1–T1.6 only; locked budgets; proceed |

## Milestones

### M1 — Schemathesis (#727) — **active**

| Task | Description | Spec / TC | Status |
|------|-------------|-----------|--------|
| T1.1 | Pin `schemathesis==4.24.3`; inventory pin note | [Corpus: tech-spec] | done |
| T1.2 | Pytest + Schemathesis ASGI suite + auth override | TC-F34-001 | done |
| T1.3 | `make test-schemathesis` + knobs (max-examples ≤ 25) | TC-F34-002 / 007 | done |
| T1.4 | Path-filtered required CI + gate job (timeout ≤ 10 min) | TC-F34-002 / 007 | done |
| T1.5 | Findings: allow documented 501; exclusions documented | AC5; D-S069-e5 | done |
| T1.6 | 08-verify-build + PR → `stage` for #727 only | AC6 | in_progress |

### M2 — Mutation (#874) — after M1 PR

| Task | Description | Spec / TC | Status |
|------|-------------|-----------|--------|
| T2.1 | pytest-gremlins + Stryker configs / make targets | TC-F34-003..005 | pending |
| T2.2 | Nightly / workflow_dispatch matrix (Python + TS) | D-S069-01-matrix | pending |
| T2.3 | Kill survivors or waive; 08 + PR → `stage` for #874 | AC5–AC6 | pending |

## In scope (M1 batch)

T1.1–T1.6 only — do **not** bundle #874.

## Out of scope (unchanged)

Mutation every PR; Rust mutation; live staging/prod Schemathesis merge gate; product UI; weaken ≥95%; promote; replace hand-written UJ/pytest.

## PR cadence

1. Minor PR: Schemathesis → `stage` (closes #727 path)
2. Minor PR: Mutation → `stage` (closes #874; then #841)
3. Promote held
