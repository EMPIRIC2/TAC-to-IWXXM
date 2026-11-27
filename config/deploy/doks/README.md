# DOKS IaC (F30 / #712 / EV-043 #886 / EV-044)

Kustomize **base** + **overlays** for DigitalOcean Kubernetes: API, static FE (nginx), and F8 worker.
**Dual cluster** (EV-044): staging and prod are separate DOKS clusters + DO Projects.

| Overlay | Namespace | Hosts |
|---------|-----------|-------|
| `overlays/prod` | `metar-iwxxm` | `api.tac-to-iwxxm.com`, `app.tac-to-iwxxm.com`, apex/`www` → app via `metar-frontend-apex` + `metar-apex-redirect` |
| `overlays/staging` | `metar-iwxxm-staging` | `api.staging.tac-to-iwxxm.com`, `app.staging.tac-to-iwxxm.com` |

| Env | Cluster | LB |
|-----|---------|-----|
| prod | `metar-iwxxm` | `168.144.12.70` |
| staging | `metar-iwxxm-staging` (DO Project **Staging TAC-to-IWXXM**) | `143.244.202.13` |

### Supabase Auth projects (do not share)

| Env | Project ref | Auth URL (non-secret) | Role |
|-----|-------------|------------------------|------|
| prod | `ktvxijislbtgqapllmuk` | `https://ktvxijislbtgqapllmuk.supabase.co` | Production Auth only |
| staging | `zvfhtcxjopwuesrozpvu` | `https://zvfhtcxjopwuesrozpvu.supabase.co` | Staging Auth only (`staging-env` preview; same ref as Supabase Sync on `stage`) |

Staging frontend ConfigMap and `config/deploy/profiles/staging.json` must use the
staging URL. Production overlays and `prod.json` must keep the production URL.
Live keys (`SUPABASE_PUBLISHABLE_KEY`, optional `SUPABASE_SECRET_KEY`, JWKS if
overridden) stay in out-of-band secrets — never commit them. See
[docs/ops-contract.md](../../docs/ops-contract.md) §Staging and production and
[docs/env-variable.md](../../docs/env-variable.md).

Staging DNS at Porkbun; see [docs/ops/doks-staging-dns-runbook.md](../../docs/ops/doks-staging-dns-runbook.md).
Promote path: [](../../docs/adr/-doks-staging-promote-from-stage.md).
Apply overlays with the matching kube context (`do-nyc1-metar-iwxxm` vs `do-nyc1-metar-iwxxm-staging`).

## Apply

```bash
# Secrets first (out-of-band), then:
kubectl apply -k config/deploy/doks/overlays/staging
kubectl apply -k config/deploy/doks/overlays/prod
# preview:
kubectl kustomize config/deploy/doks/overlays/staging
```

`config/deploy/doks/base` remains the shared resource set; prefer overlays for apply.

## Secrets (create out-of-band)

Staging must use the **staging** Postgres instance `metar-iwxxm-staging` (never prod
`metar-iwxxm` / prod `defaultdb`) and the **staging** Supabase Auth project
`zvfhtcxjopwuesrozpvu` (never production `ktvxijislbtgqapllmuk`). Example:

```bash
kubectl --context do-nyc1-metar-iwxxm-staging -n metar-iwxxm-staging create secret generic metar-api-secrets \
  --from-literal=DATABASE_URL='postgresql+asyncpg://…@metar-iwxxm-staging-….db.ondigitalocean.com:25060/defaultdb?ssl=require' \
  --from-literal=SUPABASE_URL='https://zvfhtcxjopwuesrozpvu.supabase.co' \
  --from-literal=SUPABASE_JWKS_URL='' \
  --from-literal=SUPABASE_PUBLISHABLE_KEY='…' \
  --from-literal=DISSEMINATION_EGRESS_ALLOWLIST='…' \
  --from-literal=OPENAIP_API_KEY='…'
```

### Rotate staging Supabase Auth keys

1. In the Supabase dashboard for project `zvfhtcxjopwuesrozpvu`, rotate the
   publishable (anon) key and, if used, the secret (service-role) key.
2. Patch `metar-api-secrets` in namespace `metar-iwxxm-staging`:
   `SUPABASE_URL`, `SUPABASE_PUBLISHABLE_KEY`, optional `SUPABASE_SECRET_KEY`,
   optional `SUPABASE_JWKS_URL` (blank uses `{SUPABASE_URL}/auth/v1/.well-known/jwks.json`).
3. If the frontend ConfigMap injects `supabase.publishableKey` at apply time,
   re-apply the staging overlay (or patch `metar-frontend-runtime-config`) with the
   new publishable key — do not commit the key.
4. Set GitHub Environment **staging** secrets used by Deploy bake-time Vite Auth
   fallback: `FRONTEND_VITE_SUPABASE_URL`,
   `FRONTEND_VITE_SUPABASE_PUBLISHABLE_DEFAULT_KEY` (and any staging-scoped
   `SUPABASE_PUBLISHABLE_KEY` / `SUPABASE_SECRET_KEY` if the Environment holds them).
5. Roll API + frontend pods so they pick up the new secret / ConfigMap.
6. Confirm login on `https://app.staging.tac-to-iwxxm.com` and that
   `https://api.staging.tac-to-iwxxm.com` accepts staging JWTs. Do **not** change
   production secrets or the production project.

Also copy `ghcr-pull` into the staging namespace (dockerconfig for `ghcr.io` with a
`read:packages` PAT). CD refreshes that secret each Deploy with the live
`GITHUB_TOKEN` (`scripts/deploy/doks_refresh_ghcr_pull_secret.sh`) so a revoked
static PAT does not block DOKS pulls. Do **not** remount
`work_session_service.py` via ConfigMap (`work-session-ssl-fix` was a T7.1
interim only, removed after BUG-2026-08-10; sslmode rewrite is in-image).

## CD image rollout (EV-034 / EV-043 / EV-044)

| Branch | Cluster | Namespace | Script env |
|--------|---------|-----------|------------|
| `stage` | `metar-iwxxm-staging` | `metar-iwxxm-staging` | `DOKS_NAMESPACE=metar-iwxxm-staging` + staging kubeconfig |
| `main` | `metar-iwxxm` | `metar-iwxxm` | default + prod kubeconfig |

Promote to `main` only after Staging smoke green; see (local) and
[docs/tech-spec.md](../../docs/tech-spec.md).

```bash
bash scripts/deploy/doks_rollout_images.sh 20260805003332-5245f8d
DOKS_NAMESPACE=metar-iwxxm-staging bash scripts/deploy/doks_rollout_images.sh 20260805003332-5245f8d
```

## Rollback

Roll back by re-applying a prior image digest on the DOKS cluster
(`https://api.staging.tac-to-iwxxm.com` / `https://app.staging.tac-to-iwxxm.com`
for staging; `https://api.tac-to-iwxxm.com` / `https://app.tac-to-iwxxm.com` for
prod). Do not redeploy a Render service.

## Related

- [docs/tech-spec.md](../../docs/tech-spec.md)
- [docs/env-variable.md](../../docs/env-variable.md)
- , (local `docs/adr/` when present)
