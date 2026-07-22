# Phase A checkpoint — S020 / EV-015

**Date**: 2026-07-22  
**Phase completed**: A (Product — 01 + 02; 03 skipped)

## Digest

**Feature IDs:** F20 (Planned) + deepen F6.b / F6.c / F12  
**Stages run:** 00-context, 01-requirements, 02-verify-plan  
**Skipped:** 03-plan-tooling (Lean+build)  
**Specs touched:** feature-list, spec, user-journeys, test-plan, api-contract, COVERAGE_MATRIX, evolve/requirements decisions, plan-adherence  
**Session/branch:** `S020-aerodrome-quality` / `evolve/EV-015-aerodrome-quality` (renamed per S1.M2)  
**Code:** none yet (Phase B = 04-tech-plan)  
**Open issues:** none blocking

### What changed (plain language)

F20 is allocated for TAF (#735) + full SPECI (#734) quality bars on the EV-011 stack
(registry / goldens / coverage matrix). UJ-031 and TC-F20-001..006 define acceptance.
API wire shapes unchanged. 02 PASS with full HARD themes + skip-05 confirmed.

### Gate A→B criteria

| Criterion | Status |
|-----------|--------|
| Fn in feature-list | PASS — F20 Planned |
| Delta specs | PASS |
| 02-verify-plan | PASS |
| 03 if routed | N/A — skipped |

### Next

**04-tech-plan** (delta) — execution plan for TAF/SPECI rules → goldens → matrix; kill-switch for blocked themes (S1.M1).
