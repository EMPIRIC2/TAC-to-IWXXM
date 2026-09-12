# E2E Report — S047 / EV-039 (10-e2e)

> Generated: 2026-08-06  
> Branch: `evolve/EV-039-sql-ingest-live-e2e`  
> Stack: Docker `metar-iwxxm-backend` / `frontend` / `db` + Compose BYOC  
> Corpus: [Corpus: journeys §UJ-027] [Corpus: tests] TC-F16-LIVE [Corpus: product §F16]

## Tier summary

| Tier | What | Result |
|------|------|--------|
| T0 / H6′ mocked | `uj027-030-dissemination-drawer.e2e.spec.ts` | **PASS** — 7/7 |
| T3 local LIVE | `uj027-f16-live-sql.e2e.spec.ts` via `make test-e2e-f16-live-sql` | **PASS** — 3/3 run; 1 skipped |
| T2 staging connectivity | H4–H5 remote | **SKIPPED** — local Docker only this cycle |

## Mocked H6′ (UJ-027–030)

```
7 passed (5.7s)
```

Includes SSRF/allowlist drawer smoke (TC-F16-002).

## LIVE SQL (TC-F16-LIVE)

| Case | Result |
|------|--------|
| LIVE-001 Postgres | PASS |
| LIVE-002 MySQL | PASS |
| LIVE-003 SQL Server | SKIPPED (`F16_SKIP_SQLSERVER=1`) |
| LIVE-004 SQLite | PASS |

Env: `PLAYWRIGHT_SKIP_WEBSERVER=1`, `F16_DOCKER_API=1`, allowlist with `byoc-*` + `172.16.0.0/12`.

## Notes

- Playwright did **not** start host `start-dev-servers` (Colima-safe).
- BYOC project torn down after suite; API/FE Docker stack left running.
