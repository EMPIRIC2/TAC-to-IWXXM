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
| A | `staging` | `143.244.202.13` | 300 |

(`$STAGING_LB_IP` as of EV-044 provision 2026-08-08 — re-check if LB is replaced.)

Host `staging` is the short redirect host (`staging.tac-to-iwxxm.com` →
`app.staging.tac-to-iwxxm.com` via Ingress `metar-frontend-staging-short`).
**Required** when a prod wildcard `*.tac-to-iwxxm.com` points at the prod LB — otherwise
`staging` incorrectly resolves to prod.

(Or CNAME both to the same LB hostname if preferred.)

**Do not** point staging hosts at the prod LB `168.144.12.70` (EV-043 shared-LB path
retired after EV-044 dual-cluster cutover).

## Verify

```bash
dig +short api.staging.tac-to-iwxxm.com
dig +short app.staging.tac-to-iwxxm.com
dig +short staging.tac-to-iwxxm.com
# expect $STAGING_LB_IP (143.244.202.13) — staging must NOT be 168.144.12.70

curl -fsS https://api.staging.tac-to-iwxxm.com/health
curl -fsSI https://app.staging.tac-to-iwxxm.com/ | head -5
curl -sI "https://staging.tac-to-iwxxm.com/foo?bar=1" | egrep -i '^(HTTP|location):'
# expect 301/308 → https://app.staging.tac-to-iwxxm.com/foo?bar=1

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
competing with prod for the single prod node. Shared-cluster ns `metar-iwxxm-staging` on
prod was torn down (T3.3).

## Promote to main (after DNS/TLS)

Do **not** open or merge `stage`→`main` until:

1. Porkbun A records resolve to `$STAGING_LB_IP` (or Host-header smoke is explicitly accepted).
2. **Staging smoke** is green for the tip SHA on `stage`.
3. PR head is **`stage`** and CI **Staging gate** passes (`scripts/ci/staging_gate.sh`).
4. **Release prep (recommended):** semver bumps for changed publishable packages +
   `docs/CHANGELOG.md` on `stage`; after merge, tag `vYYYY.MM.DD-deploy` (+ PyPI tags if
   publishing). See [docs/deploy.md](../deploy.md) §Release checklist.

See [docs/deploy.md](../deploy.md) §Promote and [ADR-034](../adr/ADR-034-doks-staging-promote-from-stage.md).

## GitHub admin (403 for non-admins)

Create Environments + rulesets in the GitHub UI (or as a repo admin):

1. Settings → Environments → `staging`, `production` (no required reviewers for solo-dev).
2. Per-environment kubeconfig secrets (staging ≠ prod) after dual-cluster cutover.
3. Settings → Rules → New ruleset targeting `stage` and `main`:
   - Require pull request before merging
   - Block force pushes
   - Required status checks (exact job `name:` strings from `ci-cd.yml`):
     - **Both `stage` and `main`:** full `Test (*)` matrix (shared/auth/backend/frontend/
       tac2iwxxm/iwxxm-validate/tac-validate/dissemination/worker/bugs + alembic),
       `Lint`, `Typecheck`, Rust crates / maturin / Converter perf
     - **`main` only (promote):** also `Staging gate` and `E2E Full (Playwright)`
       (not `E2E Smoke (Playwright)` — smoke-only is insufficient for EV-061 / #1015)
4. Re-apply after #1015 / EV-061 so live rulesets match the script (admin token required).

Script (admin token): `bash scripts/deploy/apply_gh_branch_rulesets.sh`

Canonical name inventory: [docs/deploy.md](../deploy.md) §Promote (EV-061 table).
[Corpus: deploy] [Corpus: tests §TC-EV061-1015]
