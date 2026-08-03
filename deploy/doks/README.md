# DOKS IaC (F30 / #712 / T6.1)

Kustomize base for DigitalOcean Kubernetes — API, static FE (nginx), and F8 worker.

| Workload | Kind | Image (override) | Public |
|----------|------|------------------|--------|
| `metar-api` | Deployment + Service + Ingress | `ghcr.io/EMPIRIC2/TAC-to-IWXXM/backend:main-latest` | `api.doks.placeholder.metar-iwxxm.local` |
| `metar-frontend` | Deployment + Service + Ingress | `ghcr.io/EMPIRIC2/TAC-to-IWXXM/frontend:main-latest` | `app.doks.placeholder.metar-iwxxm.local` |
| `metar-worker` | Deployment | `ghcr.io/EMPIRIC2/TAC-to-IWXXM/worker:main-latest` | no |

Placeholder hostnames are locked by `D-S038-04-b2` Q1 until **T6.3** pins real DNS.
Do **not** point live `LIVE_*` / `config/prod.json` primary URLs here while Render is primary.

## Secrets (create out-of-band)

```bash
kubectl -n metar-iwxxm create secret generic metar-api-secrets \
  --from-literal=DATABASE_URL='postgresql://…' \
  --from-literal=SUPABASE_URL='https://….supabase.co' \
  --from-literal=SUPABASE_JWKS_URL='' \
  --from-literal=SUPABASE_PUBLISHABLE_KEY='…' \
  --from-literal=DISSEMINATION_EGRESS_ALLOWLIST='…'

kubectl -n metar-iwxxm create secret generic metar-worker-secrets \
  --from-literal=DATABASE_URL='postgresql://…' \
  --from-literal=INGEST_POLLER_URL='https://…'
```

Templated stubs live in `base/secret-*.yaml` for reference only — they are
**not** listed in `kustomization.yaml` (applying stubs would overwrite live secrets).

API `DATABASE_URL` must be `postgresql+asyncpg://…?ssl=require` (not `sslmode=`).

## Apply

```bash
# Secrets first (out-of-band), then:
kubectl apply -k deploy/doks/base
# preview:
kubectl kustomize deploy/doks/base
```

Until EV-031 merges, DOKS API image is pinned to
`ghcr.io/empiric2/tac-to-iwxxm/backend:ev031-doks` (alembic-capable; does not
overwrite Render `main-latest`).

## Release migrate (T6.2)

API Deployment includes an **initContainer** `alembic-upgrade` that runs
`python -m alembic -c alembic.ini upgrade head` against `DATABASE_URL` before the
API container starts (idempotent — same as `make db-migrate` / CI `test-alembic`).

Optional ad-hoc Job: `deploy/doks/base/job-alembic-upgrade.yaml`
(`kubectl apply -f …` or included in `kubectl apply -k`).

## Related

- [docs/deploy.md](../../docs/deploy.md) — topology + secrets
- [docs/ops/doks-cutover-soak-checklist.md](../../docs/ops/doks-cutover-soak-checklist.md)
- ADR-033
