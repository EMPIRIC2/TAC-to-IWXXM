# DOKS staging DNS runbook (EV-043 / #886)

[Corpus: deploy] [Corpus: adr/ADR-034]

Domain `tac-to-iwxxm.com` uses **Porkbun** nameservers (not DigitalOcean DNS).
Staging Ingress + cert-manager HTTP-01 require public A records before TLS becomes Ready.

## Records to create (Porkbun)

| Type | Host | Answer | TTL |
|------|------|--------|-----|
| A | `api.staging` | `168.144.12.70` | 300 |
| A | `app.staging` | `168.144.12.70` | 300 |

(Or CNAME both to the same LB hostname if preferred.)

## Verify

```bash
dig +short api.staging.tac-to-iwxxm.com
dig +short app.staging.tac-to-iwxxm.com
# expect 168.144.12.70

curl -fsS https://api.staging.tac-to-iwxxm.com/health
curl -fsSI https://app.staging.tac-to-iwxxm.com/ | head -5

kubectl -n metar-iwxxm-staging get certificate
# READY=True after ACME succeeds
```

Until DNS exists, Host-header probes still work:

```bash
curl -sS -H "Host: api.staging.tac-to-iwxxm.com" http://168.144.12.70/health
```

## Single-node capacity

Cluster `metar-iwxxm` currently has **one** worker node. Running full API+FE+worker in
**both** namespaces can OOM-schedule (`Insufficient memory`). Mitigations:

1. Keep staging `metar-worker` at **0** replicas until the node pool is enlarged, or
2. Lower staging resource requests (overlay `patch-resources.yaml`), or
3. Scale the DOKS default node pool (`doctl kubernetes cluster node-pool …`).

Prod Deploy timeouts on rollout usually mean the new pod cannot schedule — free memory
(scale staging down briefly) then re-run `doks_rollout_images.sh`.

## GitHub admin (403 for non-admins)

Create Environments + rulesets in the GitHub UI (or as a repo admin):

1. Settings → Environments → `staging`, `production` (no required reviewers for solo-dev).
2. Settings → Rules → New ruleset targeting `stage` and `main`:
   - Require pull request before merging
   - Block force pushes
   - Required status checks: CI Test jobs; on `main` also **Staging gate**

Script (admin token): `bash scripts/deploy/apply_gh_branch_rulesets.sh`
