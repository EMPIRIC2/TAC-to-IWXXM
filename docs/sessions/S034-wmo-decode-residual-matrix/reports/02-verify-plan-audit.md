# 02-verify-plan audit — S034 / EV-027

**Date**: 2026-07-31  
**Mode**: delta  
**Issue**: [#815](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/815)

## Scope audited

`feature-list.md` (EV-026 Done + EV-027 deepen) · `user-journeys.md` (UJ-042 + UJ-039/020) ·
`test-plan.md` (TC-EV027-001..005 + EV-027 gate) · `requirements-decisions.md` ·
`evolve-decisions.md` §EV-027 · session brief / context

## Consistency checklist

| Check | Result |
|-------|--------|
| Feature ↔ Journey | **PASS** — F25/F9/F7.g deepen ↔ UJ-042 |
| Journey ↔ Test | **PASS** — UJ-042 ↔ TC-EV027-001..005 |
| EV-026 vs EV-027 status | **PASS** — EV-026 Done; EV-027 In progress |
| TC ids | **PASS** — new TC-EV027-001..005 (`E27-TC=1`) |
| UJ id | **PASS** — new UJ-042 (`E27-UJ=1`); deepens UJ-039/UJ-020 |
| ADR-025 / ADR-032 | **PASS** — decode residuals + catalog tiers unchanged |
| Out of scope | **PASS** — encode equality / US menu / new products excluded |
| Spec/Config/API skipped | **PASS** — lean manifest; no contract surface |
| Connectivity | **PASS** — H4–H5 via TC-EV027-005 when_ships; same origins as UJ-039/020 |
| Supersedes S029 | **PASS** — noted in feature-list + evolve-decisions |

## Auto-approved (high confidence) — 12

Derived from D-S034-open / E27-* / corpus deltas already locked:

1. #815 = inventory + load path + decode residual matrix + CI
2. No new Fn — deepen F25 / F9 / F7.g
3. New UJ-042 + TC-EV027-001..005
4. Lean+build; skip 03/05/06/09/11/12
5. UI preview deferred until after build
6. Triage: fix when cheap; else allowlist + child issue (no silent leftovers)
7. Encode equality promotion out of scope
8. IWXXM-US not in WMO sample menu
9. No inventing TAC; F6 seven only
10. TC-SIGMET A6-2 / SWX/VONA/WAFS deferred unless already catalogued
11. S029/EV-022 parked work superseded/broadened by #815
12. 13-deploy-smoke only when FE/decode chrome ships

## Medium confidence (Batch F — locked)

| ID | Statement | Decision |
|----|-----------|----------|
| S02.M1 | Expected-residual **allowlist SoT** is a package test artifact (module/YAML next to fixtures); `FIXTURE_GAPS.md` stays catalog/load gaps only | **1** Approve — `D-S034-EV027-s02m1-1` |
| S02.M2 | All seven products target `residuals == []` for happy-path official peers to close Gate C; allowlist entries allowed **only** when standing docs mark residuals intentional (F9 **G4** / ADR-025 sparse best-effort) + linked child issue — check docs, no silent leftovers | **2** (+ doc check) — `D-S034-EV027-s02m2-2` |
| S02.L1 | Inventory SoT for TC-EV027-001 is **pytest-discovered** vendor/mirrored TAC peers (checked-in list or discovery helper), not a hand-only docs table | **1** Approve — `D-S034-EV027-s02l1-1` |

### S02.M2 doc evidence

| Source | Intentional residual policy |
|--------|------------------------------|
| `feature-list.md` F9 **G4** | VAA/TCA decode spans: best-effort + **explicit residuals** in v1 |
| F9 acceptance / ADR-025 | Sparse products best-effort; residuals named in “Not decoded: …” |
| #815 / E27-4 | Unexpected residuals = defect; expected = allowlist (now gated on doc intent) |

## Gate A

**PASS** (`D-S034-02-phase-a`) — Batch F **1, 2, 1**; Lean → **04-tech-plan**.
