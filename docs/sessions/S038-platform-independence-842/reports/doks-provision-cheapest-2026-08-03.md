# DOKS / DO Postgres provision (cheapest) — 2026-08-03

> EV-031 / S038 — CLI provision via `doctl` (user approved cheapest viable).

## Resources

| Resource | Name | ID | Spec | Region |
|----------|------|-----|------|--------|
| Managed Postgres | `metar-iwxxm` | `d50b2bd5-9466-4b24-9051-84c9b304fc71` | `db-s-1vcpu-1gb` / PG 16 | `nyc1` |
| DOKS | `metar-iwxxm` | `3efe7b00-1c56-4eb8-bc6f-0bce8838bb7b` | 1× `s-2vcpu-4gb` (k8s 1.34.10) | `nyc1` |
| Ingress LB | nginx | — | EXTERNAL-IP `168.144.12.70` | `nyc1` |

**Why not 1× `s-1vcpu-2gb`:** API+worker request 512Mi each (+ FE + system) will not schedule on 2 GiB. `s-2vcpu-4gb` is the cheapest node that can fit the declared requests.

## Data plane

- Alembic `upgrade head` applied to DO Postgres (revision `20260803_0001`).
- Supabase → DO migrate **apply + VERIFY PASS**: sessions 39, ingest 77, quarantine 2.
- `.env`: `MIGRATE_SOURCE_DATABASE_URL` (Supabase pooler), `MIGRATE_TARGET_DATABASE_URL` (DO). Local `DATABASE_URL` left on Supabase until cutover.
- DB firewall: DOKS cluster + operator IP `70.181.17.23`.

## Workloads (unblocked 2026-08-03 evening)

- Namespace `metar-iwxxm`; ConfigMaps + Ingress (placeholder hosts) applied from `deploy/doks/base`.
- Secrets out-of-band (`metar-api-secrets`, `metar-worker-secrets`); API uses
  `postgresql+asyncpg://…?ssl=require` (plain `sslmode=` breaks asyncpg).
- `imagePullSecrets: ghcr-pull` from `.env` `GHCR_TOKEN` (classic PAT + `read:packages`).
- API / FE / worker **Running**; external smoke via LB + Host header **200**.
- Backend image pin for DOKS: `ghcr.io/empiric2/tac-to-iwxxm/backend:ev031-doks`
  (also immutable `20260804-b83b6e54`; includes `alembic==1.18.5`). Does **not** overwrite
  Render `main-latest`.
- Alembic **initContainer re-enabled** on API Deployment (`python -m alembic upgrade head`).
- Ingress nginx: disabled `use-proxy-protocol` (DO LB annotation removed) so plain HTTP works.

## T6.3 / DNS

Placeholder hosts still in Ingress:

- `api.doks.placeholder.metar-iwxxm.local`
- `app.doks.placeholder.metar-iwxxm.local`

Provisional LB: `168.144.12.70` (Host-header smoke only; do not pin `LIVE_*` until real DNS).

```bash
curl -H "Host: api.doks.placeholder.metar-iwxxm.local" http://168.144.12.70/health
curl -H "Host: app.doks.placeholder.metar-iwxxm.local" http://168.144.12.70/
```

## Next

1. T6.3 pin real DNS + `config/prod.json` / CORS when hostnames ready.
2. After EV-031 merges to `main`, switch DOKS image pin back to `main-latest`.
