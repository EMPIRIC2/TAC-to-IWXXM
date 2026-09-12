# Deploy Checklist — S037 / EV-030 (Stage 12 / T4.3)

> Generated: 2026-08-03  
> Status: **APPROVED** — `D-S037-12` = 1 (mitigations + rollback + start 13)  
> Deployment plan: [docs/deploy.md](../../../deploy.md)  
> Session: S037-quality-residuals-831 · Evolve: EV-030  
> PR: [#832](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/832) · tip `3889e4c`  
> Lock: **E30-T6** — API redeploy; H1–H3; **H4–H5 required** (FE catalog unlock)

## Scope (delta)

| Surface | Change | Deploy action |
|---------|--------|---------------|
| `packages/tac2iwxxm` | VAA/TCA structured decode + AHL; **0.2.4** | In API image — **redeploy API** |
| `packages/tac-validate` | TC SIGMET lint codes (#829) | In API image — **redeploy API** |
| `tests/quality_matrices/` | F29 harness (CI only) | No deployable |
| `apps/frontend` | Unlock `sigmet-A6-2-TC` as `wmoReference` | **Rebuild static FE** |
| Auth/CORS | Unchanged origins | Re-verify H4–H5 post-deploy |
| Worker / dissemination | Unchanged | No worker redeploy |
| Secrets / DB | None new | N/A |

**Pre-merge:** Staging tracks `main`; EV-030 lands after merge of #832 (or interim deploy from evolve image if ops choose).

## Pre-Deploy

- [x] Configuration complete — `render.yaml` static+api+worker; no new services
- [x] Secrets documented — no new keys
- [x] Data assets — vendor schemas in image; N/A weights
- [x] Resource allocation — unchanged
- [x] Rollback plan — user approved 2026-08-03 (`D-S037-12` = 1)
- [x] H0c CORS — 6/6 passed
- [x] Frontend `VITE_*` ↔ API matrix — staging-secrets-matrix.md
- [x] `METAR_CORS_ORIGINS` documented
- [x] Post-deploy H4–H5 — `bash scripts/deploy/verify_connectivity.sh`
- [x] Connectivity scripts present

## Failure Mitigations

| # | Risk | Mitigation | Status |
|---|------|-----------|--------|
| 1 | Image build failure | CI on PR #832 | **approved** |
| 2 | Decode/lint regression | T0 matrices + EV030 TCs + unit cov ≥95% | **approved** |
| 3 | FE catalog missing A6-2-TC | Vitest + **H4–H5 required** | **approved** |
| 4 | Equality residual (#835) mistaken for fail | Documented `wmoReference` not `wmoPass` | **approved** |
| 5 | Render cold start | `wake_live_api` in verify_connectivity.sh | **approved** |

## Rollback

- Render Dashboard → prior deploy on API + FE static
- Or pin prior GHCR tags; re-run `verify_connectivity.sh`
- No DB migrations this cycle

## Redeploy order (T4.4)

1. Merge #832 to `main` (user approval) **or** deploy evolve branch images if interim.
2. Deploy **metar-to-iwxxm-api**.
3. Rebuild **metar-to-iwxxm-frontend-v4-web**.
4. H1–H3 + `bash scripts/deploy/verify_connectivity.sh` (H4–H5).

## Gate (AskQuestion after 11)

1. Approve mitigations?
2. Approve rollback?
3. Ready for 13-deploy-smoke?
