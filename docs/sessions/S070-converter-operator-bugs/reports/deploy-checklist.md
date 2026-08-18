# Deploy Checklist — S070 / EV-060 (12-verify-deploy)

> Generated: 2026-08-18  
> Status: **checklist ready** — **no merge** (`D-S070-12-merge` / `D-S070-12-close`)  
> Deployment: [docs/deploy.md](../../../deploy.md) · dual DOKS (ADR-034)  
> Product tip: `4d29ee0c` · state tip: `c2880375` · PR [#1007](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/1007) → `stage` **OPEN**  
> Tip CI: [CI/CD Pipeline 32171946188](https://github.com/EMPIRIC2/TAC-to-IWXXM/actions/runs/32171946188) **success** @ `4d29ee0c`  
> (prior HARD STOP [32169922030](https://github.com/EMPIRIC2/TAC-to-IWXXM/actions/runs/32169922030) @ `c57eeef1` — auth coverage + OpenAPI drift; fixed in place `D-S070-12-ci-fix`)  
> Follow-up yaml CI: [32180225018](https://github.com/EMPIRIC2/TAC-to-IWXXM/actions/runs/32180225018) **success** @ `c2880375`  
> `env_role`: **staging** (`D-S070-12-env`); promote held  
> Corpus: [Corpus: deploy] [Corpus: adr/ADR-034] [Corpus: product §F7] [Corpus: product §F31] [Corpus: api] [Corpus: tests]

## Scope (delta)

| Surface | Change | Deploy action (when merge approved later) |
|---------|--------|-------------------------------------------|
| `packages/auth` | Restore `POST /auth/logout` + `sign_out` (`D-S070-logout=1a`) | API image rebuild |
| `apps/frontend` | OpenAPI snapshot + generated types include `/auth/logout` | FE rebuild / static deploy |
| `apps/e2e` | UJ-059..063 + TC-EV060-1006 Auth | CI / Staging smoke; live H4–H5 in **13** after merge |
| Env / secrets | No new secrets | Confirm staging CORS includes `https://app.staging.tac-to-iwxxm.com` |
| Worker / DB migrations | None | N/A |

**Path (held):** Merge #1007 → `stage` → Staging Deploy + Staging smoke → **13** H4–H5. Do **not** open feature→`main`. Promote only after separate re-approve. **This 12 close does not merge.**

## Pre-Deploy

- [x] Configuration — no new env knobs; logout already in [Corpus: api]
- [x] Secrets — none new
- [x] Data assets — N/A
- [x] Resource allocation — unchanged (API + static FE + worker)
- [x] Rollback — reviewed (`D-S070-12-rollback`)
- [x] H0c CORS — `tests/unit/test_cors_policy.py` **PASS** 6/6 (09-qa)
- [x] Frontend `VITE_*` ↔ API URL matrix — unchanged; connectivity-gates scripts present
- [x] `METAR_CORS_ORIGINS` documented for staging/prod in [Corpus: tech-spec] / env-contract
- [x] Connectivity scripts — `scripts/deploy/verify_connectivity.sh` + `tests/smoke/test_staging_connectivity.py` present
- [x] Branch pushed — tip `c2880375` (product fix `4d29ee0c`)
- [x] Tip CI green — [32171946188](https://github.com/EMPIRIC2/TAC-to-IWXXM/actions/runs/32171946188) @ `4d29ee0c`; [32180225018](https://github.com/EMPIRIC2/TAC-to-IWXXM/actions/runs/32180225018) @ `c2880375`
- [x] PR open — [#1007](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/1007) **not merged** (`D-S070-12-merge`)
- [ ] Merge + Staging CD — **held** until a later merge decision
- [ ] Post-deploy H1 + **H4–H5** (13) — after merge + Staging smoke (`D-S070-11-t3`)

## Failure Mitigations

| # | Risk | Mitigation | Status |
|---|------|------------|--------|
| 1 | Image/CD failure on stage | Tip CI green on PR #1007 before any merge | **approved** (`D-S070-12-risks`) |
| 2 | Staging CORS / Auth XHR miss for logout | Existing CORS matrix; H4–H5 at 13 after merge | **approved** / verify at 13 |
| 3 | Accidental promote to main | Dual-env: stage smoke + Staging gate; promote held | **approved** |
| 4 | Playwright E2E hang on `playwright install` | Cancel + rerun on a fresh runner (run 32171946188 then succeeded) | **approved** |

## Rollback

- Roll back staging DOKS deployments to prior GHCR tag / `stage-latest` predecessor
- Re-run `bash scripts/deploy/verify_connectivity.sh` with staging URLs
- No DB migrations this cycle
- Prod is untouched (no promote)

**Approved** (`D-S070-12-rollback`).

## Recommended path (held)

1. Tip CI green on `4d29ee0c` / PR #1007 — **done**.
2. User approved this checklist (12) — **`D-S070-12-*`**.
3. **Later:** merge #1007 → `stage` → Staging Deploy + Staging smoke.
4. **13** H1–H3 → **H4–H5** via `verify_connectivity.sh` + live UJ-059..063 / Auth.
5. Promote `stage`→`main` only after Staging gate green + re-approve.

## Sign-Off

- [x] User approved implementation (11)
- [x] `env_role` staging — `D-S070-12-env`
- [x] Risks approved — `D-S070-12-risks`
- [x] Rollback approved — `D-S070-12-rollback`
- [x] CI HARD STOP fixed in place — `D-S070-12-ci-fix`
- [x] No merge #1007 — `D-S070-12-merge` / `D-S070-12-close`
- [ ] Ready for 13-deploy-smoke — **blocked until #1007 merges**
