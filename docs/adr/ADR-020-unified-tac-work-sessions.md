# ADR-020: Unified `tac_work_sessions` (override R2 separate F7 table)

> **Status**: Accepted  
> **Date**: 2026-07-13  
> **Deciders**: User (S011 Spec Batch 2 contradiction resolution option A)  
> **Stage**: 01-requirements  
> **Related**: ADR-011, ADR-012; feature-list.md F5/F7; spec.md §F5/F7  
> **Session**: S011-f7-operator-ui / EV-008  
> **Decision id**: D-S011-01-spec-r2-prime

## Context

Phase 0 **R2** kept F5 on `metar_work_sessions` (METAR/SPECI-only) and planned a **separate**
F7 sessions model for seven products. Spec Batch 2 initially offered separate vs unified
tables; the user selected **unified** (option C), then confirmed overriding R2 after the
contradiction was surfaced.

## Decision

1. **Canonical table** is `tac_work_sessions` with a `product` column for all seven F6 products.
2. **Migrate** existing `metar_work_sessions` rows into `tac_work_sessions`
   (`product` = `metar` | `speci`); deprecate and drop `metar_work_sessions` after cutover.
3. **My METARs** remains METAR/SPECI UX as a **filter** on the unified table.
4. **Workbench history** shows all products.
5. **RLS**: `auth.uid() = user_id` only (admin `is_admin()` browse removed with #697).
6. **WIP uniqueness**: default **one WIP per user total** across products (04 may refine).
7. **`kv_upload_key` / send**: retained for products that already support Upload (at least
   METAR/SPECI).
8. Record this as **R2′** in feature-list, spec, context brief, and session brief.

## Alternatives Considered

| # | Alternative | Why rejected |
|---|-------------|--------------|
| 1 | Separate F7 table; leave F5 untouched (original R2) | User chose unified persistence |
| 2 | Soft-unify later; dual tables in v1 | Extra long-term complexity; user confirmed migrate now |
| 3 | Quietly widen `metar_work_sessions` without rename/migrate plan | Ambiguous naming; R2′ requires explicit migration |

## Consequences

- Larger F7.e slice: schema migration, dual-write/cutover plan in 04-tech-plan, API retarget.
- F5 acceptance journeys (UJ-004) must be updated to unified storage + My METARs filter.
- ADR-011/012 remain authoritative for access/retention patterns where they do not conflict;
  amend or supersede details in 04 if retention cron must retarget table name.
