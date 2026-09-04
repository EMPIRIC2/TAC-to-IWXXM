# Scoped context: ConversionProfile contract (#924)

> **Status**: active  
> **Created**: 2026-09-03  
> **Session**: `EV-924-conversion-profile-contract` (slice #924)  
> **Tickets**: [#924](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/924) · [#922](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/922)  
> **Corpus**: [Corpus: product] F6 · [Corpus: adr] ADR-013, ADR-036 · [Corpus: api]

## Goal

Validate the **executable ConversionProfile contract** from #924 against the current split registries + code plugins. Decide custom/operator overlay trust boundaries (#906). Deliver spike write-up + ADR — no production ship.

## Prerequisite

#914 closed → **ADR-036 Accepted** (semantic vs exchange split). #924 unblocked.

## Current implementation (seed)

| Piece | Location |
|-------|----------|
| Semantic IDs | `packages/tac2iwxxm/profile_registry.py` |
| Exchange IDs | `packages/dissemination/exchange_registry.py` |
| HTTP wire | `apps/backend/src/utilities/profile_wire.py` |
| Lint profiles | `packages/tac-validate/profiles.py` |
| Profile catalog | `docs/domain/profiles/catalog.yaml` |
| Content stubs | `docs/domain/profiles/semantic/*.md`, `exchange/*.md` |

## Hard boundaries

1. Semantic profile ≠ exchange profile (ADR-036)
2. Dissemination credentials / destinations stay memory-only (ADR-021/029)
3. Unknown profile ids fail closed (HTTP 400)
4. No FastAPI/Supabase in MET packages

## Recommendation (draft — pending gate)

Accept normative contract doc (ADR-038); defer runtime loader + operator overlays to #933.

## Out of scope

#912 national content · #925 pipeline result · #933 editor · code changes this spike

## Next

Complete draft-docs (ADR-038) → feasibility → gate.
