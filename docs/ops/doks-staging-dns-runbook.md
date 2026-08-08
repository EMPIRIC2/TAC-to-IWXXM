# DOKS staging DNS runbook (EV-043 / EV-044)

[Corpus: deploy] [Corpus: adr/ADR-034]

Domain `tac-to-iwxxm.com` uses **Porkbun** nameservers (not DigitalOcean DNS).
Staging Ingress + cert-manager HTTP-01 require public A records before TLS becomes Ready.

After **EV-044**, staging has its **own** DOKS LB (not the prod LB `168.144.12.70`).
Set `STAGING_LB_IP` from:

```bash
kubectl --context <staging> -n ingress-nginx get svc ingress-nginx-controller \
  -o jsonpath='{.status.loadBalancer.ingress[0].ip}{"\n"}'
```

## Records to create/update (Porkbun)

| Type | Host | Answer | TTL |
|------|------|--------|-----|
| A | `api.staging` | `143.244.202.13` | 300 |
| A | `app.staging` | `143.244.202.13` | 300 |

(`$STAGING_LB_IP` as of EV-044 provision 2026-08-08 — re-check if LB is replaced.)

(Or CNAME both to the same LB hostname if preferred.)

**Transitional (EV-043 shared LB):** if staging still shares prod LB before cutover,
Answer may temporarily be `168.144.12.70`. Update to `$STAGING_LB_IP` when the staging
cluster Ingress is live.

## Verify

```bash
dig +short api.staging.tac-to-iwxxm.com
dig +short app.staging.tac-to-iwxxm.com
# expect $STAGING_LB_IP

curl -fsS https://api.staging.tac-to-iwxxm.com/health
curl -fsSI https://app.staging.tac-to-iwxxm.com/ | head -5

kubectl --context <staging> -n metar-iwxxm-staging get certificate
# READY=True after ACME succeeds
```

Until DNS exists, Host-header probes against the staging LB still work:

```bash
curl -sS -H "Host: api.staging.tac-to-iwxxm.com" http://$STAGING_LB_IP/health
```

## DO Projects (EV-044)

| Project | Resources |
|---------|-----------|
| **TAC-to-IWXXM** | Prod DOKS `metar-iwxxm` + Postgres `metar-iwxxm` |
| **Staging TAC-to-IWXXM** | Staging DOKS `metar-iwxxm-staging` + Postgres `metar-iwxxm-staging` |

## Capacity note

With a **dedicated** staging cluster (EV-044), staging worker may run at 1 replica without
competing with prod for the single prod node. Until cutover completes, the EV-043 shared-cluster
mitigation (staging worker at 0) may still apply on the prod cluster leftover ns.

## GitHub admin (403 for non-admins)

Create Environments + rulesets in the GitHub UI (or as a repo admin):

1. Settings → Environments → `staging`, `production` (no required reviewers for solo-dev).
2. Per-environment kubeconfig secrets (staging ≠ prod) after dual-cluster cutover.
3. Settings → Rules → New ruleset targeting `stage` and `main`:
   - Require pull request before merging
   - Block force pushes
   - Required status checks: CI Test jobs; on `main` also **Staging gate**

Script (admin token): `bash scripts/deploy/apply_gh_branch_rulesets.sh`
