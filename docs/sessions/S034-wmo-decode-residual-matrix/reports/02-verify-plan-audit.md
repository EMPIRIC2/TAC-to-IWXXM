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

## Medium confidence (Batch F — pending)

| ID | Statement | Options |
|----|-----------|---------|
| S02.M1 | Expected-residual **allowlist SoT** is a package test artifact (module/YAML next to fixtures); `FIXTURE_GAPS.md` stays catalog/load gaps only | 1 Approve · 2 Put allowlist in FIXTURE_GAPS · 3 Explain |
| S02.M2 | **METAR/SPECI/TAF** happy-path official peers must reach `residuals == []` to close Gate C; **VAA/TCA (G4)** may remain on allowlist + child issue without blocking close | 1 Approve · 2 All seven must be empty · 3 Explain |
| S02.L1 | Inventory SoT for TC-EV027-001 is **pytest-discovered** vendor/mirrored TAC peers (checked-in list or discovery helper), not a hand-only docs table | 1 Approve · 2 Docs-only inventory OK · 3 Explain |

## Gate A

Pending Batch F answers (`D-S034-02-phase-a`).
