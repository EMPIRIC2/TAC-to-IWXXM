# S008 — 01-requirements summary

> **Session**: S008-general-tac-iwxxm-converter  
> **Stage**: 01-requirements (delta)  
> **Completed**: 2026-07-12

## Interview plan

| Document | Status |
|----------|--------|
| Feature List | Done — F6 |
| Spec | Done — tac2iwxxm architecture |
| User Journeys | Done — UJ-001/002/005–010, DEV-003b |
| Test Plan | Done — TC-F6-*, H6 expansion |
| Dependency Inventory | Done |
| API Contract | Done |
| Config Spec | Done — no new env/keys |
| ADRs | ADR-014 (+ ADR-013/004 status) |

## Key decisions

- **F6** `packages/tac2iwxxm` (MIT): 7 products (FAA five + VAA + TCA); profiles `annex3` / `iwxxm_us`
- Pure Python v0; optional **Rust/PyO3** (not Cython) — ADR-014
- Hard cutover: first wire-up PR **deletes gifts**; API never calls gifts
- UI product/profile pickers; T3 all 7 products annex3; US METAR/SPECI/TAF where applicable
- Convert: `product` **required** (multipart); `profile` optional default annex3
- Metrics library/CI only; no convert-response metrics
- No new config/env; no feature flag

## Artifacts

- `docs/feature-list.md`, `docs/spec.md`, `docs/user-journeys.md`, `docs/test-plan.md`
- `docs/dependency-inventory.md`, `docs/api-contract.md`, `docs/config-spec.md`, `docs/env-contract.md`
- `docs/adr/ADR-014-tac2iwxxm-rust-gifts-removal.md`
- `docs/decisions/requirements-decisions.md` (F6-R* table)

## Next

**04-tech-plan** (delta) — IR library choice, iwxxm-us pin URL/tag, PyO3 layout, gifts removal tasking.
(Routing skips 02/03 per S008 plan.)
