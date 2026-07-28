# 02-verify-plan — S024 / EV-018 (delta)

**Date**: 2026-07-28  
**Mode**: evolve delta — deepen F16 (#785)  
**Decision**: Gate A PASSED (D-S024-02-phase-a-A)

## Inventory (touched)

| Doc | Role |
|-----|------|
| `docs/feature-list.md` | F16 deepen + F17 reuse note |
| `docs/spec.md` | F16–F19 / frontend drawer |
| `docs/api-contract.md` | Client N-sequential; ≤20; no batch API |
| `docs/user-journeys.md` | UJ-027–030 |
| `docs/test-plan.md` | TC-F16-005; mapping UJ-027 |
| `docs/decisions/evolve-decisions.md` | E18-1..8 + scope lock |

## Consistency checklist (16-evolve)

| Check | Result |
|-------|--------|
| F16 deepen in feature-list has spec + tests | **PASS** — TC-F16-005 / UJ-027 |
| Parameter names match (no new env) | **PASS** — allowlist unchanged |
| api-contract matches preflight/send (no batch) | **PASS** — E18-5 |
| test-plan ↔ journeys same IDs | **PASS** after fix (UJ-027 → TC-F16-001..005) |
| No new dependency | **PASS** |
| execution-plan tasks | **N/A** until 04 |
| ADRs | **PASS** — ADR-021/029/030 cited; no new ADR required for UI-only sequential |
| Template | **PASS** — FE + backend-mediated dissemination |

## Statement audit (changed / high-signal)

### Auto-approved (high — from E18 / issue #785)

| ID | Statement | Verdict |
|----|-----------|---------|
| S1 | Candidates = current-session + drops only | approve (E18-4) |
| S2 | N sequential preflight/send; no batch API v1 | approve (E18-5) |
| S3 | Selection count cap ≤20 + existing body limits | approve (E18-6) |
| S4 | Empty selection disables Preflight/Send | approve (#785 AC) |
| S5 | Per-file results; one failure must not silent-drop rest | approve (#785 AC) |
| S6 | F17–F19 reuse same selection UI contract | approve (E18-2) |
| S7 | BYOC memory-only; allowlist unchanged | approve (security invariant) |
| S8 | Selection panel required when **>1** candidate | approve (#785 AC) |
| S9 | H4–H5 / H6′ UJ-027–030 remain connectivity gates | approve (connectivity) |

### Fixed during 02 (contradictions)

| ID | Issue | Fix |
|----|-------|-----|
| C1 | `test-plan` checklist still `TC-F16-001..004` | → `..005` |
| C2 | UJ-029/030 still **Authenticated user** vs F21 public | → public actor + selection reuse |

### Medium / advisory (no block)

| ID | Statement | Recommendation |
|----|-----------|----------------|
| M1 | Exact UX when **exactly 1** candidate (hide panel vs single checked) | Defer to **04** — recommend auto-select single candidate, panel optional/collapsed |
| M2 | Preflight-all-then-send-all vs per-file preflight→send interleaved | Defer to **04** — recommend preflight all selected, then send only green |

## Connectivity gate statements

- Staging smoke ≠ H4–H5 only health — **denied as sole proof**; H6′ UJ-027–030 required for drawer.
- Vitest alone ≠ live CORS — **denied**; T2/T3 Playwright remains.

## Exit criteria

- [x] Consistency pass on touched corpus
- [x] Contradictions C1–C2 fixed in place
- [x] User Gate A → B (proceed to 04-tech-plan)

## Handoff

Gate A PASSED (**D-S024-02-phase-a-A**, 2026-07-28). Proceed to **04-tech-plan**.

Accepted deferred into 04:

- **M1** — Exact UX when exactly 1 candidate (hide panel vs single checked); recommend auto-select single candidate, panel optional/collapsed
- **M2** — Preflight-all-then-send-all vs per-file preflight→send interleaved; recommend preflight all selected, then send only green
