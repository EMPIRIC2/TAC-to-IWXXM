# 01-requirements report — S031 / EV-024

**Date**: 2026-07-30  
**Mode**: delta  
**Cycle**: EV-024 · **Issues**: [#804](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/804),
[#807](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/807),
[#773](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/773) (exclude #806)

## Phase 0–1 lock

| ID | Decision |
|----|----------|
| E24-1 | 1a+Build — open S031; Lean+build |
| E24-2 | 2b — #804 + #807 + #773 |
| E24-3 | 3a — full ticket AC |
| E24-4 | 4b — Lean+build; 13 when catalog/API ships |
| E24-ui | UIb — no non-deployed UI preview |
| E24-M | **M3** — lean manifest + **new UJ-039** |
| E24-C | **C3+C2+C1 hybrid** — discovery + validate/CI + **WMO examples in sample menu**; ADR-032 amend |

## Documents updated

| Doc | Delta |
|-----|-------|
| `docs/feature-list.md` | S031 deepen (F6/F2/F4/F12/F13/F25); EV-023 → Done |
| `docs/user-journeys.md` | **UJ-039** + UJ-036 deepen |
| `docs/test-plan.md` | TC-EV024-001..008 + gate |
| `docs/adr/ADR-032-wmo-default-golden-glossary.md` | Catalog gate amend (strict vs WMO reference) |
| `docs/decisions/evolve-decisions.md` | E24-M / E24-C |
| `docs/decisions/requirements-decisions.md` | EV-024 table |
| Session brief / routing-plan | Locked |

## Catalog policy (operator ask)

WMO IWXXM official examples with TAC peers for product-in-scope **must load from the
Examples / sample menu**. Strict `wmoPass` (canonicalize equality) remains; non-equal
official stems load as **WMO reference** samples. Encode gaps → child issues (do not block
menu listing). Translation-failed stay out of happy-path; IWXXM-US not mixed into WMO catalog.

## Handoff

**Next**: **02-verify-plan** (delta consistency on touched corpus) → Gate A → **04-tech-plan**.

## Close decision

Pending AskQuestion E24-E1 (mark 01 complete → start 02).
