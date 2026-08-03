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

Or apply the templated stubs in `base/secret-*.yaml` after filling values
(never commit real credentials).

## Apply

```bash
kubectl apply -k deploy/doks/base
# preview:
kubectl kustomize deploy/doks/base
```

## Release migrate (T6.2)

API rollout must run idempotent `alembic upgrade head` against `DATABASE_URL`
(init container or release Job — see T6.2). Same command as `make db-migrate` / CI.

## Related

- [docs/deploy.md](../../docs/deploy.md) — topology + secrets
- [docs/ops/doks-cutover-soak-checklist.md](../../docs/ops/doks-cutover-soak-checklist.md)
- ADR-033
