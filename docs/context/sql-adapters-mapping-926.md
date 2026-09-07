# Scoped context: SQL adapters + mapping config (#926)

> **Status**: active  
> **Created**: 2026-09-03  
> **Session**: `EV-926-sql-adapters-mapping`  
> **Tickets**: [#926](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/926) · [#922](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/922)  
> **Corpus**: [Corpus: product] F16 · [Corpus: adr] ADR-030, ADR-040

## Goal

Validate SQL as symmetric **source and sink** with **MappingConfig** (not national schema). Spike only.

## Recommendation

Extend `packages/dissemination`; ADR-040 MappingConfig; SourceAdapter protocol (Planned); Oracle deferred.

## Current sink stack

`writer_contract` v1 · `db_preflight` · postgres/mysql/sqlserver/sqlite · `SinkAdapter`

## Gap

No source DB poll · no custom column mapping · Oracle unsupported

See session `reports/926-sql-adapters-mapping.md` for full matrix and YAML sketch.
