# Evolve report — EV-043

**Session**: S052-doks-staging-prod-branch-deploys  
**Issue**: [#886](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/886)  
**Status**: implemented with residuals (DNS + GH admin + node capacity)  
**Closed PRs**: [#940](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/940), [#942](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/942), [#943](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/943), [#941](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/941)

## Delivered

- DOKS staging namespace `metar-iwxxm-staging` + DB `metar_iwxxm_staging`
- Kustomize overlays `deploy/doks/overlays/{staging,prod}`
- Dual CI/CD: `stage`→staging Deploy + Staging smoke; `main`→prod Deploy
- Staging gate (promote-from-stage) with poll for Staging smoke
- ADR-034, F30 AC8–12, skills/rules for dual `env_role`
- Branch `stage` created; promote path exercised

## Residuals

1. **Porkbun DNS** A records for `api.staging` / `app.staging` → `168.144.12.70` (TLS not Ready until then)
2. **GH admin**: Environments + rulesets (`scripts/deploy/apply_gh_branch_rulesets.sh`) — 403 without admin
3. **Node pool**: single node; staging worker kept at 0 replicas to leave headroom for prod

## Evidence

- Staging Deploy + Staging smoke: run `31264462312` SUCCESS  
- Staging gate on promote PR: run `31264463945` SUCCESS (6m12s poll)  
- Prod tip rolled to `20260808153602-018ea72` (manual assist after CD timeout OOM)  
- Prod `/health` 200; staging Host-header `/health` 200  

[Corpus: product §F30] [Corpus: adr/ADR-034] [Corpus: deploy]
