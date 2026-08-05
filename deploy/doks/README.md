# DOKS IaC (F30 / #712 / T6.1)

Kustomize base for DigitalOcean Kubernetes — API, static FE (nginx), and F8 worker.

| Workload | Kind | Image (override) | Public |
|----------|------|------------------|--------|
| `metar-api` | Deployment + Service + Ingress | `ghcr.io/EMPIRIC2/TAC-to-IWXXM/backend:main-latest` | `api.doks.placeholder.metar-iwxxm.local` |
| `metar-frontend` | Deployment + Service + Ingress | `ghcr.io/EMPIRIC2/TAC-to-IWXXM/frontend:main-latest` | `app.doks.placeholder.metar-iwxxm.local` |
| `metar-worker` | Deployment | `ghcr.io/EMPIRIC2/TAC-to-IWXXM/worker:main-latest` | no |

Placeholder hostnames remain until real DNS. **`D-S038-t63-waive`** pins provisional
`LIVE_*` / `liveE2e` to these hosts + LB `168.144.12.70` (Host-header or `/etc/hosts`).
Public `config/prod.json` `api.baseUrl` stays on Render until real DNS.
FE runtime `/config.json` is overridden by ConfigMap `metar-frontend-runtime-config`.
Smoke: `bash scripts/deploy/doks_host_header_smoke.sh`.

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
Sync work-sessions rewrite `ssl=` → `sslmode=` in code; until `backend:ev031-doks` is
republished, apply `bash scripts/ops/apply_doks_work_session_ssl_fix.sh`.

Provisional live harness (Host-header / Chromium resolver-rules; see
`scripts/deploy/doks_provisional_live_env.sh`):

- Playwright F31 (T7.1): `make test-live-e2e-doks-provisional`
- H4–H5 (T7.2): `make test-live-connectivity-doks-provisional`
- TC-EV031 topology (T7.3): `make test-live-topology-doks-provisional`

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

## CD image rollout (EV-034 / TC-F30-007)

On push to `main`, `.github/workflows/ci-cd.yml` **Deploy** runs
`scripts/deploy/doks_rollout_images.sh <TIMESTAMP-SHA>` after GHCR push (requires
Actions secret `KUBE_CONFIG` — base64 kubeconfig). Manual equivalent:

```bash
bash scripts/deploy/doks_rollout_images.sh 20260805003332-5245f8d
```

See [docs/deploy.md](../../docs/deploy.md) §CD — DOKS image rollout.

## Related

- [docs/deploy.md](../../docs/deploy.md) — topology + secrets + CD
- [docs/ops/doks-cutover-soak-checklist.md](../../docs/ops/doks-cutover-soak-checklist.md)
- ADR-033
