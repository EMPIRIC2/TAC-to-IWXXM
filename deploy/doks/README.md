# DOKS IaC (F30 / #712 / EV-043 #886)

Kustomize **base** + **overlays** for DigitalOcean Kubernetes — API, static FE (nginx), and F8 worker.

| Overlay | Namespace | Hosts |
|---------|-----------|-------|
| `overlays/prod` | `metar-iwxxm` | `api.tac-to-iwxxm.com`, `app.tac-to-iwxxm.com` |
| `overlays/staging` | `metar-iwxxm-staging` | `api.staging.tac-to-iwxxm.com`, `app.staging.tac-to-iwxxm.com` |

LB: `168.144.12.70`. Staging DNS at Porkbun — see [docs/ops/doks-staging-dns-runbook.md](../../docs/ops/doks-staging-dns-runbook.md).
Promote path: [ADR-034](../../docs/adr/ADR-034-doks-staging-promote-from-stage.md).

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

Staging must use DB `metar_iwxxm_staging` (never prod `defaultdb`). Example:

```bash
kubectl -n metar-iwxxm-staging create secret generic metar-api-secrets \
  --from-literal=DATABASE_URL='postgresql+asyncpg://…/metar_iwxxm_staging?ssl=require' \
  --from-literal=SUPABASE_URL='https://….supabase.co' \
  --from-literal=SUPABASE_JWKS_URL='' \
  --from-literal=SUPABASE_PUBLISHABLE_KEY='…' \
  --from-literal=DISSEMINATION_EGRESS_ALLOWLIST='…'
```

Also copy `ghcr-pull` and (if still required) `work-session-ssl-fix` into the staging namespace.

## CD image rollout (EV-034 / EV-043)

| Branch | Namespace | Script env |
|--------|-----------|------------|
| `stage` | `metar-iwxxm-staging` | `DOKS_NAMESPACE=metar-iwxxm-staging` |
| `main` | `metar-iwxxm` | default |

```bash
bash scripts/deploy/doks_rollout_images.sh 20260805003332-5245f8d
DOKS_NAMESPACE=metar-iwxxm-staging bash scripts/deploy/doks_rollout_images.sh 20260805003332-5245f8d
```

See [docs/deploy.md](../../docs/deploy.md) §CD — DOKS image rollout.

## Related

- [docs/deploy.md](../../docs/deploy.md)
- [docs/ops/doks-staging-dns-runbook.md](../../docs/ops/doks-staging-dns-runbook.md)
- ADR-033, ADR-034
