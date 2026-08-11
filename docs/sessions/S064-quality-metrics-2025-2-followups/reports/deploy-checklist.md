# Deploy Checklist — S064 / EV-055 (12-verify-deploy)

> Generated: 2026-08-11  
> Status: **IN PROGRESS** — PR open; tip CI pending  
> Prior: 11 **APPROVED** (`D-S064-11=1`)  
> Deployment: [docs/deploy.md](../../../deploy.md) · dual DOKS (ADR-034)  
> Tip: `abeba590` · PR [#985](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/985) → `stage`  
> Tip CI: pending  
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

**Path:** Merge PR → `stage` → Staging Deploy + Staging smoke → **13** H4–H5. Do **not** open feature→`main`.

## Pre-Deploy

- [x] Configuration — no new env knobs; C14N in iwxxm-validate + FE
- [x] Secrets — none new
- [x] Data assets — regenerated `corpus_metrics` committed
- [x] Resource allocation — unchanged
- [x] Rollback — prior GHCR/DOKS tag on staging
- [x] H0c CORS — `tests/unit/test_cors_policy.py` **6/6 PASS** (09-qa)
- [x] Connectivity scripts — `scripts/deploy/verify_connectivity.sh` + `tests/smoke/test_staging_connectivity.py` present
- [x] Branch pushed — tip `abeba590`
- [ ] Tip CI green — pending on [#985](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/985)
- [x] PR open — [#985](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/985)
- [ ] Merge + Staging CD — pending user merge after CI
- [ ] Post-deploy H1 + **H4–H5** (13)

## Failure Mitigations

| # | Risk | Mitigation | Status |
|---|------|------------|--------|
| 1 | Image/CD failure on stage | Tip CI on PR before merge | pending CI |
| 2 | Staging CORS miss for Quality metrics XHR | Existing CORS matrix; H4 at 13 | verify at 13 |
| 3 | Native Schematron/XSD path regression on stage image | TC-EV055-004/005 + unit gates | approved (local) |
| 4 | C14N pane/override UX miss | UJ-056 T0 PASS; live at 13 | verify at 13 |
| 5 | Accidental promote to main | Dual-env rule: stage smoke + Staging gate only | approved |

## Rollback

- Roll back staging DOKS deployments to prior GHCR tag
- Re-run `bash scripts/deploy/verify_connectivity.sh` with staging URLs
- No DB migrations this cycle

## Recommended path (13)

1. Tip CI green on PR → `stage`.
2. User approve this checklist (12).
3. **Merge** PR → `stage` (explicit approval) → Staging Deploy + Staging smoke.
4. H1–H3 → **H4–H5** via `verify_connectivity.sh` + optional live UJ-056.
5. Later: promote `stage`→`main` only after Staging gate green (not this AskQuestion).

## Sign-Off

- [x] User approved implementation (11) — `D-S064-11=1`
- [ ] User approved deploy strategy (this checklist) — pending
- [ ] Ready for 13-deploy-smoke after merge + CI green
