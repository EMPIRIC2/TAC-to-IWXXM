# Deploy Checklist — S071 / EV-061 (12-verify-deploy)

> Generated: 2026-08-20  
> Status: **APPROVED** — `D-S071-12-merge=1` (commit docs → merge #1016 → stage → 13)  
> Prior: 11 **APPROVED** (`D-S071-11-ac=1a`)  
> Deployment: [docs/deploy.md](../../../deploy.md) · dual DOKS (ADR-034)  
> Tip: `dba4e21a` · PR [#1016](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/1016) → `stage`  
> Tip CI: [CI/CD Pipeline 32370411164](https://github.com/EMPIRIC2/TAC-to-IWXXM/actions/runs/32370411164) **success** @ `dba4e21a`  
> `env_role`: **staging** first (PR → `stage` → cluster `metar-iwxxm-staging`); promote held  
> Corpus: [Corpus: deploy] [Corpus: adr/ADR-034] [Corpus: product §F7] [Corpus: product §F15]
> [Corpus: product §F34] [Corpus: tests] [Corpus: decisions §EV-061]

## Scope (delta)

| Surface | Change | Deploy action |
|---------|--------|---------------|
| `apps/frontend` | Validate decode UX; Product/Profile/param bars; Lint & validation catalog tab | FE rebuild on `stage` |
| `apps/backend` + packages | AHL decode/convert; catalog API fields; validate decode payloads | API image `stage-latest` |
| `apps/e2e` / tests | UJ-064..068; TC-EV061-*; promote-gate contracts | CI; live H4–H5 in **13** |
| `.github/workflows` | Lint / Typecheck / E2E Full jobs (#1015) | Active on tip; rulesets **admin apply** before promote |
| Env / secrets | No new secrets | Confirm staging CORS includes `https://app.staging.tac-to-iwxxm.com` |
| Worker / DB migrations | None | N/A |

**Path:** Merge #1016 → `stage` → Staging Deploy + Staging smoke → **13** H4–H5.  
Do **not** open feature→`main`. Promote only after Staging gate + admin rulesets + re-approve.

**Out of this merge:** #1017 catalog sources/sort-filter (post-promote).

## Pre-Deploy

- [x] Configuration — no new env knobs; additive API/FE only
- [x] Secrets — none new
- [x] Data assets — N/A
- [x] Resource allocation — unchanged (DOKS staging)
- [x] Rollback — prior GHCR / `stage-latest` predecessor on staging DOKS
- [x] H0c CORS — `tests/unit/test_cors_policy.py` **6/6 PASS** (2026-08-20)
- [x] Connectivity scripts — `scripts/deploy/verify_connectivity.sh` + `tests/smoke/test_staging_connectivity.py` present
- [x] Branch pushed — tip `dba4e21a`
- [x] Tip CI green — [32370411164](https://github.com/EMPIRIC2/TAC-to-IWXXM/actions/runs/32370411164) @ `dba4e21a`
- [x] PR open — [#1016](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/1016) **MERGEABLE**
- [x] Merge + Staging CD — `D-S071-12-merge=1`; CD [32398410519](https://github.com/EMPIRIC2/TAC-to-IWXXM/actions/runs/32398410519) success
- [x] Post-deploy H1 + **H4–H5** (13) — UJ-064..068 PASS — see `reports/deploy-smoke.md`

## Failure Mitigations

| # | Risk | Mitigation | Status |
|---|------|------------|--------|
| 1 | Image/CD failure on stage | Tip CI green on PR #1016 before merge | **approved** (`D-S071-12-risks=1a` proposed) |
| 2 | Staging CORS / XHR miss for new UI | Existing CORS matrix; H4–H5 at 13 | **approved** / verify at 13 |
| 3 | Accidental promote to main | Dual-env; Staging gate; promote held | **approved** |
| 4 | Promote without #1015 rulesets | Admin: `bash scripts/deploy/apply_gh_branch_rulesets.sh` before real promote | **approved** (QA-003) |

## Rollback

- Roll back staging DOKS deployments to prior GHCR tag / `stage-latest` predecessor
- Re-run `bash scripts/deploy/verify_connectivity.sh` with staging URLs
- No DB migrations this cycle
- Revert merge commit on `stage` if needed (prefer image rollback first)

**Proposed** `D-S071-12-rollback=1a`.

## Recommended path (13)

1. Tip CI green on `dba4e21a` / PR #1016 — **done**.
2. User approve this checklist + **merge #1016 → stage**.
3. Watch Deploy(stage) + Staging smoke.
4. **13** — H1–H3 → **H4–H5** + live UJ-064..068.
5. Later: promote `stage`→`main` only after Staging gate green + admin rulesets + re-approve.

## Sign-Off

- [x] User approved implementation (11) — `D-S071-11-ac=1a`
- [x] Scope — staging via #1016 (`D-S071-12-scope=1a` proposed)
- [x] Risks — standard mitigations (`D-S071-12-risks=1a` proposed)
- [x] Rollback — GHCR/DOKS (`D-S071-12-rollback=1a` proposed)
- [x] Merge #1016 → `stage` — **approved** (`D-S071-12-merge=1`); merged `86867a11`
- [x] Ready for 13 after Staging CD green — **done**; await `D-S071-13`
