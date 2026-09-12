# Teardown audit — S047 / EV-039 (T2.4 / T2.5 · AC5/AC6)

> Date: 2026-08-06  
> Branch: `evolve/EV-039-sql-ingest-live-e2e`  
> [Corpus: product §F16] [Corpus: tests] TC-F16-LIVE-004 [Corpus: tech-spec]

## Scope

Audit disposal for:

1. Dissemination Testcontainers fixtures (Postgres / MySQL / SQL Server)
2. SQLite temp files from LIVE-004 / unit helpers
3. Compose `metar-iwxxm-mock-byoc` project (`down -v --remove-orphans`)

## Findings

| Layer | Mechanism | Result |
|-------|-----------|--------|
| Postgres/MySQL fixtures | `with PostgresContainer` / `with MySqlContainer` + `engine.dispose()` in `finally` | **OK** — contract in `test_f16_live_teardown_audit.py` |
| SQL Server fixture | `with SqlServerContainer` + `dispose()` in `finally` | **OK** |
| LIVE-004 SQLite | `mkdtempSync` + `rmSync(..., { recursive: true })` in `finally` | **OK** |
| Compose project | `compose-mock-byoc-down` → `down -v --remove-orphans` on `-p metar-iwxxm-mock-byoc` | **OK** (T1.1) |
| Compose SQL Server wait | On Apple Silicon / QEMU, `byoc-sqlserver` can stay unhealthy and block `--wait` | **Fixed** — `F16_SKIP_SQLSERVER=1` / `F16_LIVE_SQL_SERVER=0` omits sqlserver from `compose-mock-byoc-up` wait set (S05.L1) |

## Waivers

| ID | Item | Waiver |
|----|------|--------|
| W-S047-mssql-local | Full four-dialect local close on hosts where SQL Server 2022 cannot run (QEMU VA layout) | Allowed to skip LIVE-003 via `F16_SKIP_SQLSERVER=1`; CI opt-in remains; document in tech-spec / this report |

## Evidence

- Unit: `tests/unit/test_f16_live_teardown_audit.py` (green)
- Makefile: `F16_SKIP_SQLSERVER` branch in `compose-mock-byoc-up` + `test-e2e-f16-live-sql`
- Playwright: `apps/e2e/uj027-f16-live-sql.e2e.spec.ts` LIVE-004 `finally` teardown

## Residual

- Run `F16_SKIP_SQLSERVER=1 make test-e2e-f16-live-sql` against local FE/API with allowlist/CORS recipe for green LIVE-001/002/004 evidence (operator machine dependent).
