# DOKS IaC (F30 / #712 / EV-043 #886 / EV-044)

Kustomize **base** + **overlays** for DigitalOcean Kubernetes — API, static FE (nginx), and F8 worker.
**Dual cluster** (EV-044): staging and prod are separate DOKS clusters + DO Projects.

| Overlay | Namespace | Hosts |
|---------|-----------|-------|
| `overlays/prod` | `metar-iwxxm` | `api.tac-to-iwxxm.com`, `app.tac-to-iwxxm.com`, apex/`www` → app via `metar-frontend-apex` + `metar-apex-redirect` |
| `overlays/staging` | `metar-iwxxm-staging` | `api.staging.tac-to-iwxxm.com`, `app.staging.tac-to-iwxxm.com` |

| Env | Cluster | LB |
|-----|---------|-----|
| prod | `metar-iwxxm` | `168.144.12.70` |
| staging | `metar-iwxxm-staging` (DO Project **Staging TAC-to-IWXXM**) | `143.244.202.13` |

Staging DNS at Porkbun — see [docs/ops/doks-staging-dns-runbook.md](../../docs/ops/doks-staging-dns-runbook.md).
Promote path: [ADR-034](../../docs/adr/ADR-034-doks-staging-promote-from-stage.md).
Apply overlays with the matching kube context (`do-nyc1-metar-iwxxm` vs `do-nyc1-metar-iwxxm-staging`).

## Apply

```bash
# Secrets first (out-of-band), then:
kubectl apply -k deploy/doks/overlays/staging
kubectl apply -k deploy/doks/overlays/prod
# preview:
kubectl kustomize deploy/doks/overlays/staging
```

`deploy/doks/base` remains the shared resource set; prefer overlays for apply.

## Secrets (create out-of-band)

Staging must use the **staging** Postgres instance `metar-iwxxm-staging` (never prod
`metar-iwxxm` / prod `defaultdb`). Example:

```bash
kubectl --context do-nyc1-metar-iwxxm-staging -n metar-iwxxm-staging create secret generic metar-api-secrets \
  --from-literal=DATABASE_URL='postgresql+asyncpg://…@metar-iwxxm-staging-….db.ondigitalocean.com:25060/defaultdb?ssl=require' \
  --from-literal=SUPABASE_URL='https://….supabase.co' \
  --from-literal=SUPABASE_JWKS_URL='' \
  --from-literal=SUPABASE_PUBLISHABLE_KEY='…' \
  --from-literal=DISSEMINATION_EGRESS_ALLOWLIST='…'
```

Also copy `ghcr-pull` into the staging namespace. Do **not** remount
`work_session_service.py` via ConfigMap (`work-session-ssl-fix` was a T7.1
interim only — removed after BUG-2026-08-10; sslmode rewrite is in-image).

## CD image rollout (EV-034 / EV-043 / EV-044)

| Branch | Cluster | Namespace | Script env |
|--------|---------|-----------|------------|
| `stage` | `metar-iwxxm-staging` | `metar-iwxxm-staging` | `DOKS_NAMESPACE=metar-iwxxm-staging` + staging kubeconfig |
| `main` | `metar-iwxxm` | `metar-iwxxm` | default + prod kubeconfig |

Promote to `main` only after Staging smoke green — see ADR-034 / `docs/deploy.md` §Promote.

```bash
bash scripts/deploy/doks_rollout_images.sh 20260805003332-5245f8d
DOKS_NAMESPACE=metar-iwxxm-staging bash scripts/deploy/doks_rollout_images.sh 20260805003332-5245f8d
```

See [docs/deploy.md](../../docs/deploy.md) §CD — DOKS image rollout.

## Related

- [docs/deploy.md](../../docs/deploy.md)
- [docs/ops/doks-staging-dns-runbook.md](../../docs/ops/doks-staging-dns-runbook.md)
- ADR-033, ADR-034
