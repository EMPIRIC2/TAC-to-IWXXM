# 01-requirements report — S032 / EV-025

**Date**: 2026-07-31  
**Mode**: delta  
**Cycle**: EV-025 · **Issues**: [#810](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/810),
[#811](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/811),
[#812](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/812),
[#809](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/809)

## Phase 0 lock (E25-*)

| ID | Decision |
|----|----------|
| E25-1 | S032 / EV-025; #810+#811+#812 (+ expanded) one cycle |
| E25-2 | Full ticket AC |
| E25-3 | Lean+build (+13 when ships) |
| E25-4b | Dual lane: US REMARKS + #809 |
| E25-4c | All dig ❌ US types |
| E25-ui | N/A — no UI |
| E25-M | **2** — lean + journeys (UJ-040/041) |

## Documents updated

| Doc | Delta |
|-----|-------|
| `docs/feature-list.md` | EV-024 → Done; S032/EV-025 deepen F6.b/F12/F2/F13/F23 |
| `docs/user-journeys.md` | **UJ-040**, **UJ-041**; deepen UJ-010/026/034/039 |
| `docs/test-plan.md` | TC-EV025-001..010 + gate |
| `docs/decisions/evolve-decisions.md` | §EV-025 + E25-M |
| `docs/decisions/requirements-decisions.md` | EV-025 table |
| Session brief / routing / context | Phase 0 artifacts |

## Skipped (manifest)

Spec · Config Spec · API Contract · Deploy plan — no contract/env surface expected.

## Domain (07-build)

Update `COVERAGE_MATRIX` / `IWXXM_CONVERSION` / `TAC_VALIDATION` / `IWXXM_VALIDATION` as
encode lands — not rewritten in 01 beyond journey/test refs.

## Handoff

**Next**: **02-verify-plan** (delta consistency on touched corpus) → Gate A → **04-tech-plan**.

## Close decision

Pending AskQuestion E25-E1 (mark 01 complete → start 02).
