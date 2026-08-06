# Context — SQL ingest live e2e (S047 / EV-039)

> Scoped brief for deepen F16 live local multi-DB upload + teardown. [Corpus: product §F16]

## Background

- F16 Done (EV-014 / S019): drawer + writer-contract for **Postgres, MySQL/MariaDB, SQL
  Server, SQLite**; live destination BYOC was **mock-waived** at cycle close.
- Package layer already uses Testcontainers (`packages/dissemination/tests/`) with `yield`
  teardown for PG/MySQL/SQL Server.
- Playwright `uj027-030-dissemination-drawer.e2e.spec.ts` exercises UI with **routed mocks**
  for `/api/v1/dissemination/preflight` and `/send` — not live DB writes.

## User ask (2026-08-06)

1. Local Postgres, MySQL, and all other supported dialects.
2. Playwright against live local DBs for upload success.
3. Integration + e2e + local tests must tear down artifacts/processes.

## Locked choices (`D-S047-open`)

All four dialects · full teardown layers · Compose + Playwright · no UI preview.

## Related corpus

| Id | Use |
|----|-----|
| product §F16 | Scope / acceptance deepen |
| journeys §UJ-027 | Operator dissemination drawer |
| tests | H6′ / new TC rows / teardown gates |
| tech-spec | Compose / env / allowlist |
| api | preflight + send shapes (unchanged expected) |
| adr/ADR-029, ADR-030 | Memory-only BYOC; egress allowlist / SSRF |
