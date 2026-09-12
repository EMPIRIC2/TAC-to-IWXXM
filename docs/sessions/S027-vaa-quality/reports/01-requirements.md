# 01-requirements — S027 / EV-021 (delta)

**Started**: 2026-07-29  
**Completed**: 2026-07-29  
**Mode**: evolve delta  
**Features**: F26, F27 + deepen F6.f / F12 / F7.g  
**Status**: **completed**

## Document Manifest — approved (E21-D1=2)

| Doc | Delta |
|-----|-------|
| `docs/feature-list.md` | F26 + F27 Planned + deepen notes |
| `docs/user-journeys.md` | UJ-037, UJ-038 |
| `docs/test-plan.md` | TC-F26-001..006, TC-F27-001..006 |
| `docs/domain/rules/COVERAGE_MATRIX.md` | F26 V1–V3/C1; F27 T1–T3/C1 |
| `docs/api-contract.md` | S027 endpoint review (no wire changes) |
| `docs/config-spec.md` | §F26/F27 — no new env |
| ADR-028 / ADR-032 | Related + golden bar extends to VAA/TCA |
| Session AC | `reports/acceptance-criteria.md` |
| Inventory | `reports/wmo-vaa-tca-examples-inventory.md` (E21-3) |

## Batch D — locked

| ID | Decision |
|----|----------|
| E21-D1 | **2** — all recommended docs |
| E21-D2 | **1** — UJ-037 + UJ-038; TC-F26/F27; deepen UJ-032/TC-F7-008 |
| E21-D3 | **1** — VAA V1–V3+C1; TCA T1–T3+C1 |
| E21-D4 | **1** — mine translation TAC themes; no Amd79 XML byte-match under 2025-2 |
| E21-E1 | **1** — close 01 → 02-verify-plan |

## Exit criteria

- [x] Manifest approved
- [x] Journeys + tests written
- [x] AC + coverage + api + config + ADR notes drafted
- [x] Close 01 → **02-verify-plan**
