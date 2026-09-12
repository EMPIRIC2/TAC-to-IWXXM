# 01-requirements report — S034 / EV-027

**Date**: 2026-07-31  
**Mode**: delta  
**Cycle**: EV-027 · **Issue**: [#815](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/815)

## Phase 0 lock (E27-1..4)

| ID | Decision |
|----|----------|
| E27-1 | S034 / EV-027; #815 inventory + residual matrix + CI |
| E27-2 | Lean+build (+13 when ships) |
| E27-3 | UI preview deferred until after build |
| E27-4 | Fix when cheap; else allowlist + child issue |
| E27-M | **1** — lean feature-list + UJ-042 + test-plan |
| E27-UJ | **1** — new UJ-042; deepen UJ-039 / UJ-020 |
| E27-TC | **1** — new TC-EV027-001..005 |

## Documents updated

| Doc | Delta |
|-----|-------|
| `docs/feature-list.md` | EV-026 → Done; new S034/EV-027 deepen F25/F9/F7.g |
| `docs/user-journeys.md` | **UJ-042** + deepen UJ-039 / UJ-020 |
| `docs/test-plan.md` | TC-EV027-001..005 + EV-027 gate; EV-026 gate checked |
| `docs/decisions/evolve-decisions.md` | §EV-027 + E27-M/UJ/TC |
| `docs/decisions/requirements-decisions.md` | EV-027 table |
| Session brief / routing / context | Phase 0 artifacts |

## Skipped (manifest)

Spec · Config Spec · API Contract · Deploy plan — no contract/env surface expected.

## Handoff

**Next**: **02-verify-plan** (delta consistency on touched corpus) → Gate A → **04-tech-plan**.

## Close decision

`D-S034-E27-E1` — mark 01 completed; start 02-verify-plan.
