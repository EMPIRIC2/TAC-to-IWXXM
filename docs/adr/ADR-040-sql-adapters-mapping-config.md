# ADR-040: SQL adapters — symmetric source/sink with mapping config (spike #926)

> **Status**: Accepted (EV-926 / #926)  
> **Date**: 2026-09-03  
> **Related**: [ADR-030](ADR-030-dissemination-package-architecture.md), [ADR-037](ADR-037-platform-logical-layers.md), [ADR-021](ADR-021-byo-credentials-admin-removal.md), [ADR-029](ADR-029-dissemination-ssrf-allowlist.md)  
> **Issues**: [#926](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/926), [#896](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/896), [#922](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/922)

## Context

Spike [#926](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/926) asks for SQL databases as **symmetric sources and sinks** via adapter + **record mapping configuration**, without prescribing a national MET DB schema.

[ADR-030](ADR-030-dissemination-package-architecture.md) shipped F16 **sink-only** support:

- `writer_contract` v1 — fixed `iwxxm_reports` DDL (postgres, mysql/mariadb, mssql, sqlite)
- `db_preflight` — allowlist + schema diff
- `SinkAdapter` protocol — preflight/send for drawer sinks

Gaps:

- No **source-side** DB poll adapter (F8 uses HTTP poller)
- No **operator-defined column mapping** — only contract v1 columns
- Oracle not in dialect matrix
- #896 connector spike is transport — needs mapping layer on top

## Decision

1. **Extend `packages/dissemination`** — do **not** create `packages/adapters` (ADR-037 logical layer alias only).

2. **Accept MappingConfig contract** — declarative source query + field map and sink table + column map. Does **not** define national MET tables; operator BYOC only.

3. **Backward compatibility:** absent mapping → **writer-contract v1** default (`iwxxm_reports` + existing columns).

4. **SourceAdapter protocol (Planned):** mirror `SinkAdapter` — `poll()` / `ack()` with allowlist + memory-only URI. Implementation deferred to F8/workflow issues; #926 documents interface only.

5. **Engine matrix v1:** postgres, mysql/mariadb, sqlserver, sqlite — **sink and source**. **Oracle deferred** — document gap; no DDL until driver/dialect decision.

6. **MariaDB:** use **mysql** dialect + DDL path (already in `writer_contract_ddl`).

7. **#896 hybrid:** connector URI/auth separate from MappingConfig; preflight validates connectivity + optional schema/mapping sanity.

8. **Security unchanged:** ADR-021 memory-only credentials; ADR-029 allowlist; worker source poll not browser-mediated.

9. **#935 UI:** unblocked with MappingConfig shape for sink (and later source) editor fields.

## MappingConfig sketch

See [Context: sql-adapters-mapping-926](../context/sql-adapters-mapping-926.md) for full YAML example.

Logical fields:

| Direction | Required mapping keys |
|-----------|----------------------|
| Source → platform | `message`, `externalId`; optional `station`, `timestamp`, `product` |
| Platform → sink | `iwxxm`, `sourceId`; optional `valid`, `profile`, `convertedAt`, `product`, `icao` |

## Alternatives considered

| # | Alternative | Why rejected |
|---|-------------|--------------|
| A | Prescribe standard MET table schema | Violates BYOC / national diversity (#926 non-goal) |
| B | New adapters package | ADR-037 Option C — keep dissemination home |
| C | URI-only without mapping | Insufficient for real customer DBs (#896) |
| D | **MappingConfig + extend dissemination** | **Accepted** |

## Consequences

### Positive

- Symmetric narrative for epic #922 Adapters layer
- #935 / #896 can align on one config shape
- Writer-contract v1 remains default — no break

### Negative / follow-ups

- Source poll implementation + F8 integration = new evolve/build cycle
- Custom mapping insert/upsert paths add test matrix per engine
- Oracle remains explicit gap

## References

- EV-926 session report `926-sql-adapters-mapping.md`
- [ADR-039](ADR-039-staged-validation-pipeline.md) Adapters row in system-spec
