# Deploy Checklist — S064 / EV-055 (12-verify-deploy)

> Generated: 2026-08-11  
> Status: **APPROVED** (`D-S064-12=1`) — merge #985 → `stage` → 13  
> Prior: 11 **APPROVED** (`D-S064-11=1`)  
> Deployment: [docs/deploy.md](../../../deploy.md) · dual DOKS (ADR-034)  
> Tip: `1099fb5c` · PR [#985](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/985) → `stage`  
> Tip CI: [CI/CD Pipeline 31533338595](https://github.com/EMPIRIC2/TAC-to-IWXXM/actions/runs/31533338595) **success** @ `1099fb5c` (code tip also green [31532920375](https://github.com/EMPIRIC2/TAC-to-IWXXM/actions/runs/31532920375) @ `442a13a6`)  
> `env_role`: **staging** first (PR → `stage` → cluster `metar-iwxxm-staging`); promote to prod later via `stage`→`main` only  
> Corpus: [Corpus: tech-spec] [Corpus: product §F7] [Corpus: product §F2] [Corpus: product §F13] [Corpus: tests]  
> connectivity-gates §12–13

## Scope (delta)

| Surface | Change | Deploy action |
|---------|--------|---------------|
| `packages/iwxxm-validate` | C14N helper; 2025-2 Schematron/XSD enable (#980/#979) | API image rebuild (engine dep) on merge to `stage` |
| `apps/backend` | Native-first validate path; quality-metrics generator C14N match | API image rebuild on merge to `stage` |
| `apps/frontend` | Quality metrics C14N panes + raw override + validate chips | FE rebuild / static deploy on `stage` |
| `apps/e2e` | UJ-056 deepen TC-EV055-007 | CI / staging smoke |
| Env / secrets | No new secrets | Confirm staging CORS includes `https://app.staging.tac-to-iwxxm.com` |
| Worker / DB migrations | None | N/A |

**Path:** Merge #985 → `stage` → Staging Deploy + Staging smoke → **13** H4–H5. Do **not** open feature→`main`.

## Pre-Deploy

- [x] Configuration — no new env knobs; C14N in iwxxm-validate + FE
- [x] Secrets — none new
- [x] Data assets — regenerated `corpus_metrics` committed
- [x] Resource allocation — unchanged
- [x] Rollback — prior GHCR/DOKS tag on staging
- [x] H0c CORS — `tests/unit/test_cors_policy.py` **6/6 PASS** (09-qa)
- [x] Connectivity scripts — `scripts/deploy/verify_connectivity.sh` + `tests/smoke/test_staging_connectivity.py` present
- [x] Branch pushed — tip `1099fb5c`
- [x] Tip CI green — [31533338595](https://github.com/EMPIRIC2/TAC-to-IWXXM/actions/runs/31533338595) @ `1099fb5c` (prior fail `31532484425` fixed: orchestrator native-path coverage)
- [x] PR open — [#985](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/985)
- [x] Merge + Staging CD — approved (`D-S064-12=1`); merge in progress / follow 13
- [ ] Post-deploy H1 + **H4–H5** (13)

## Failure Mitigations

| # | Risk | Mitigation | Status |
|---|------|------------|--------|
| 1 | Image/CD failure on stage | Tip CI on PR #985 before merge | **approved** (CI green) |
| 2 | Staging CORS miss for Quality metrics XHR | Existing CORS matrix; H4 at 13 | verify at 13 |
| 3 | Native Schematron/XSD path regression on stage image | TC-EV055-004/005 + unit gates + CI coverage | approved |
| 4 | C14N pane/override UX miss | UJ-056 T0 PASS; live at 13 | verify at 13 |
| 5 | Accidental promote to main | Dual-env rule: stage smoke + Staging gate only | approved |

## Rollback

- Roll back staging DOKS deployments to prior GHCR tag
- Re-run `bash scripts/deploy/verify_connectivity.sh` with staging URLs
- No DB migrations this cycle

## Recommended path (13)

1. Tip CI green on `1099fb5c` / PR #985 — **done**.
2. User approve this checklist (12) — **`D-S064-12=1`**.
3. **Merge** #985 → `stage` (explicit approval) → Staging Deploy + Staging smoke.
4. H1–H3 → **H4–H5** via `verify_connectivity.sh` + optional live UJ-056.
5. Later: promote `stage`→`main` only after Staging gate green (not this AskQuestion).

## Sign-Off

- [x] User approved implementation (11) — `D-S064-11=1`
- [x] User approved deploy strategy (this checklist) — `D-S064-12=1`
- [x] Ready for 13-deploy-smoke after merge + Staging CD
