# Deploy State

> Last updated: 2026-08-07  
> Status: **deployed** (S050 / EV-042 — `D-S050-13=1`)

## Deployment Log

| # | Step | Status | Started | Completed | Notes |
|---|------|--------|---------|-----------|-------|
| 1 | Deploy | done | 2026-08-07 | 2026-08-07 | #899 → main `e3d1c7c8`; CI/CD Deploy [31197264636](https://github.com/EMPIRIC2/TAC-to-IWXXM/actions/runs/31197264636) |
| 2 | Smoke tests | done | 2026-08-07 | 2026-08-07 | H0c/H1/H4–H5 + UJ-051..053 6/6; see S050 deploy-smoke.md |
| 3 | Health check | done | 2026-08-07 | 2026-08-07 | `https://api.tac-to-iwxxm.com/health` healthy |
| 4 | Changelog | done | 2026-08-07 | 2026-08-07 | Unreleased S050 / EV-042 |
| 5 | Monitoring baseline | done | 2026-08-07 | 2026-08-07 | Live DOKS prod hostnames |

## Current Deployment

| Field | Value |
|-------|-------|
| App name | metar-api + metar-frontend + metar-worker (DOKS) |
| Deploy URL (API) | `https://api.tac-to-iwxxm.com` |
| Deploy URL (FE) | `https://app.tac-to-iwxxm.com` |
| Deploy mode | Live = prod (sole DOKS); Render suspended |
| Commit | `e3d1c7c8` (merge #899) |
| Branch | `main` |
| Session report | docs/sessions/S050-remove-db-tools-operator-throughput/reports/deploy-smoke.md |
| Prior | S048 / EV-040 workbench lint; see session archive |

## Rollback

Prior DOKS/GHCR image tag via `scripts/deploy/doks_rollout_images.sh`; no DB migrations this cycle.
