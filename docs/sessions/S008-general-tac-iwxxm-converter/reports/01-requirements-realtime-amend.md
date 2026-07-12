# S008 — 01-requirements realtime amend summary

> **Session**: S008-general-tac-iwxxm-converter  
> **Stage**: 01-requirements (delta `S008-realtime-ingest`)  
> **Completed**: 2026-07-12  
> **Decision**: D-S008-01-api-q51q54 / D-S008-01-realtime-amend-complete

## Interview plan (7/7)

| Document | Status |
|----------|--------|
| Feature List | Done — F6.bulletin; F7/F8 Planned; F2→iwxxm-validate |
| Spec | Done — tac-validate + iwxxm-validate; unified pipeline |
| User Journeys | Done — UJ-011/012 + stubs UJ-013/014; UJ-DEV-004 |
| Test Plan | Done — TC-F6-030–033; **H7** live bulletin gate |
| Dependency Inventory | Done — both packages MIT |
| API Contract | Done — `/lint-tac`, `/convert-bulletin` |
| ADRs | **ADR-015** accepted |

Skipped: Config Spec, Deploy (per Q23).

## Key decisions (Q51–Q54 + RT-R1–R16)

| Q / R | Choice | Meaning |
|-------|--------|---------|
| Q51 | A | `/validate` thin wrapper over `iwxxm-validate` |
| Q52 | B | New `POST /api/v1/lint-tac` → `tac-validate` |
| Q53 | B | New `POST /api/v1/convert-bulletin`; `/convert` single-report |
| Q54 | A | Write API contract + ADR-015 |
| RT-R1–R16 | confirmed | See `docs/decisions/requirements-decisions.md` |

**This cycle build**: package APIs + backend thin wrappers only. F7/F8 Planned (not built). Auth/sinks/AMHS postponed.

## Docs touched

- `docs/feature-list.md`
- `docs/spec.md`
- `docs/user-journeys.md`
- `docs/test-plan.md`
- `docs/dependency-inventory.md`
- `docs/api-contract.md`
- `docs/adr/ADR-015-validate-packages-bulletin-api-f7-f8.md`
- `docs/decisions/requirements-decisions.md` (RT-R1–R16)
- `docs/context/realtime-tac-ingest.md` (prior 00 brief)

## Next

**04-tech-plan** (delta, pending) — package layout, bulletin multi-result schema, lint-tac content-type, H7 harness, pydantic/msgspec for tac-validate.
