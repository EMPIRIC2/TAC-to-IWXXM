# Deploy Checklist — S040 / EV-032 (Stage 12 / T4.4)

> Generated: 2026-08-04  
> Status: **READY** — 11 approved (`D-S040-11`); mitigations/rollback recorded under `D-S040-12` (recommended defaults; AskQuestion tool unavailable)  
> Deployment plan: [docs/deploy.md](../../../deploy.md)  
> Session: S040-iwxxm-corpus-quality · Evolve: EV-032  
> PR: [#848](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/848) · tip pending T4.4 close commit  
> Lock: **E32-T6** — API + static redeploy; H1–H3; **H4–H5 required** (VONA FE)

## Scope (delta)

| Surface | Change | Deploy action |
|---------|--------|---------------|
| `packages/tac2iwxxm` | VONA encode plugin; A6-2-TC equality deltas | In API image — **redeploy API** |
| `packages/tac-validate` | VONA registry / product rules | In API image — **redeploy API** |
| `packages/iwxxm-validate` | XSD+SCH path (VONA / A6-2) | In API image — **redeploy API** |
| `apps/backend` | Runtime `product=vona` | **Redeploy API** |
| `apps/frontend` | VONA picker + Examples `vona_a7_1` wmoPass | **Rebuild static FE** |
| Docs (#808/#847/#846) | Domain docs only | No runtime |
| Auth/CORS | Unchanged origins | Re-verify H4–H5 post-deploy |
| Worker / dissemination | Unchanged | No worker redeploy |
| Secrets / DB | None new | N/A |

**Pre-merge:** Staging tracks `main`; EV-032 lands after merge of #848 (or interim deploy from evolve image if ops choose).

## Pre-Deploy

- [x] Configuration complete — `render.yaml` static+api+worker; no new services
- [x] Secrets documented — no new keys (`docs/ops/staging-secrets-matrix.md`)
- [x] Data assets — vendor schemas in image; N/A weights
- [x] Resource allocation — unchanged
- [x] Rollback plan — Render prior deploy / pin GHCR tags (see below)
- [x] H0c CORS — 6/6 passed (2026-08-04)
- [x] Frontend `VITE_*` ↔ API matrix — staging-secrets-matrix.md
- [x] `METAR_CORS_ORIGINS` documented (local + prod rows)
- [x] Post-deploy H4–H5 — `bash scripts/deploy/verify_connectivity.sh`
- [x] Connectivity scripts present (`scripts/deploy/verify_connectivity.sh`, `tests/smoke/test_staging_connectivity.py`)
- [x] Local non-deployed preview exercised — http://localhost:18000/ (`D-S040-11` A=1)

## Failure Mitigations

| # | Risk | Mitigation | Status |
|---|------|-----------|--------|
| 1 | Image build failure | CI on PR #848 | **approved** (default / D-S040-12) |
| 2 | VONA convert/lint regression | `make test-vona-quality` + canaries + TC-F32 | **approved** |
| 3 | A6-2-TC equality drift | EV-032 canary + `test-tc-sigmet-quality` | **approved** |
| 4 | FE missing VONA option / Examples | Vitest + local preview + **H4–H5 required** | **approved** |
| 5 | CORS / browser disconnect after FE rebuild | `METAR_CORS_ORIGINS` + verify_connectivity.sh | **approved** |
| 6 | Render cold start | `wake_live_api` in verify_connectivity.sh | **approved** |

## Rollback

- Render Dashboard → prior deploy on **metar-to-iwxxm-api** + **metar-to-iwxxm-frontend-v4-web**
- Or pin prior GHCR tags; re-run `verify_connectivity.sh`
- No DB migrations this cycle

## Redeploy order (T4.5 / 13)

1. Merge #848 to `main` (user approval) **or** deploy evolve branch images if interim.
2. Deploy **metar-to-iwxxm-api**.
3. Rebuild **metar-to-iwxxm-frontend-v4-web**.
4. H1–H3 + `bash scripts/deploy/verify_connectivity.sh` (H4–H5) — TC-EV032-007/008.

## Gate

| Item | Status |
|------|--------|
| 11-verify-impl | **approved** (`D-S040-11`) |
| 12 checklist | **ready** |
| Start 13-deploy-smoke | **awaiting user** (deploy gate) |
