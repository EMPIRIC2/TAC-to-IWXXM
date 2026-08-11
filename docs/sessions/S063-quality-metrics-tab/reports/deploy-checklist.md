# Deploy Checklist — S063 / EV-054 (12-verify-deploy)

> Generated: 2026-08-10  
> Status: **APPROVED** (`D-S063-12=1`) — tip CI green; merge #977 → stage then 13  
> Prior: 11 **APPROVED** (`D-S063-11=1`)  
> Deployment: [docs/deploy.md](../../../deploy.md) · dual DOKS (ADR-034)  
> Tip: `6dd76b66` · PR [#977](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/977) → `stage`  
> Tip CI: [CI/CD Pipeline 31449643455](https://github.com/EMPIRIC2/TAC-to-IWXXM/actions/runs/31449643455) **success**  
> `env_role`: **staging** first (PR → `stage` → cluster `metar-iwxxm-staging`); promote to prod later via `stage`→`main` only  
> Corpus: [Corpus: tech-spec] [Corpus: product §F7] [Corpus: api] [Corpus: tests]  
> connectivity-gates §12–13

## Scope (delta)

| Surface | Change | Deploy action |
|---------|--------|---------------|
| `apps/backend` | Public `GET /api/v1/quality-metrics*` + fixture `corpus_metrics.json` | API image rebuild on merge to `stage` |
| `apps/frontend` | Shell tab + Quality metrics page/detail + unified XML diff | FE rebuild / static deploy on `stage` |
| `apps/e2e` | UJ-056 Playwright | CI / staging smoke |
| Env / secrets | No new secrets; uses existing public CORS + API host | Confirm staging CORS includes `https://app.staging.tac-to-iwxxm.com` |
| Worker / DB migrations | None | N/A |

**Path:** Merge #977 → `stage` → Staging Deploy + Staging smoke → **13** H4–H5. Do **not** open feature→`main`.

## Pre-Deploy

- [x] Configuration — no new env knobs; fixture shipped in image/data path
- [x] Secrets — none new
- [x] Data assets — precomputed JSON in repo (`apps/backend/data/quality_metrics/`)
- [x] Resource allocation — unchanged
- [x] Rollback — prior GHCR/DOKS tag on staging
- [x] H0c CORS — `tests/unit/test_cors_policy.py` **6/6 PASS** (09-qa)
- [x] Connectivity scripts — `scripts/deploy/verify_connectivity.sh` + `tests/smoke/test_staging_connectivity.py` present
- [x] Branch pushed — tip `6dd76b66`
- [x] Tip CI green — [31449643455](https://github.com/EMPIRIC2/TAC-to-IWXXM/actions/runs/31449643455) @ `6dd76b66`
- [x] PR open — [#977](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/977)
- [ ] Merge + Staging CD — pending user merge after CI
- [ ] Post-deploy H1 + **H4–H5** (13)

## Failure Mitigations

| # | Risk | Mitigation | Status |
|---|------|------------|--------|
| 1 | Image/CD failure on stage | Tip CI on PR #977 before merge | **approved** (CI green) |
| 2 | Staging CORS miss for Quality metrics XHR | Existing CORS matrix; H4 at 13 | verify at 13 |
| 3 | Fixture missing in image | Artifact committed under `apps/backend/data/quality_metrics/` | approved |
| 4 | FE tab not reachable / wrong shell | UJ-056 T0 PASS; live Playwright at 13 | verify at 13 |
| 5 | Accidental promote to main | Dual-env rule: stage smoke + Staging gate only | approved |

## Rollback

- Roll back staging DOKS deployments to prior GHCR tag
- Re-run `bash scripts/deploy/verify_connectivity.sh` with staging URLs
- No DB migrations this cycle

## Recommended path (13)

1. Tip CI green on `6dd76b66` / PR #977.
2. User approve this checklist (12).
3. **Merge** #977 → `stage` (explicit approval) → Staging Deploy + Staging smoke.
4. H1–H3 → **H4–H5** via `verify_connectivity.sh` + optional live UJ-056.
5. Later: promote `stage`→`main` only after Staging gate green (not this AskQuestion).

## Sign-Off

- [x] User approved implementation (11) — `D-S063-11=1`
- [ ] User approved deploy strategy (this checklist) — pending
- [ ] Ready for 13-deploy-smoke after merge + CI green
