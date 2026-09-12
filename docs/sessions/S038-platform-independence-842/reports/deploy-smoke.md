# Deploy & smoke — 13-deploy-smoke (EV-031 / S038)

> **Date**: 2026-08-03  
> **Status**: **APPROVED** — `D-S038-13` = 1 (13 PASS; Phase D / cycle closeout)  
> **Decisions**: `D-S038-12` = 1 · `D-S038-t63-waive` · `D-S038-t65-waive`  
> **Branch**: `evolve/EV-031-platform-independence-842`  
> **Checklist**: [deploy-checklist.md](deploy-checklist.md) (approved)

## Deploy mode

**Validate existing provisional DOKS primary** (no new image push this gate).  
Compute already cut over in M6; Render remains suspended.

| Field | Value |
|-------|-------|
| Namespace | `metar-iwxxm` |
| LB | `168.144.12.70` |
| API Host | `api.doks.placeholder.metar-iwxxm.local` |
| FE Host | `app.doks.placeholder.metar-iwxxm.local` |
| Pods | `metar-api`, `metar-frontend`, `metar-worker` — **Running** 1/1, 0 restarts |

## Pre-deploy (T1)

| Check | Result |
|-------|--------|
| H0c CORS unit | **6/6 PASS** |
| 12 checklist | **APPROVED** (`D-S038-12`) |

## Smoke results (2026-08-03 re-verify)

| Tier / check | Command | Result |
|--------------|---------|--------|
| H1 Host-header API+FE | `bash scripts/deploy/doks_host_header_smoke.sh` | **5/5 PASS** |
| H0c (in verify script) | `make test-live-connectivity-doks-provisional` | **6/6 PASS** |
| H4 CORS live | same | **2/2 PASS** |
| H5 `config.json` | same | **PASS** (`api.baseUrl` → placeholder API host) |
| H3-lite topology | `make test-live-topology-doks-provisional` | **3/3 PASS** |
| Render suspended | `GET …onrender.com/health` | **503** (expected) |
| Resources | `kubectl -n metar-iwxxm get pods` | **3/3 Running**, 0 restarts |

### Host-header detail

- API `/health` 200 · `POST /api/v1/convert` 200  
- FE `/` 200 · `/config.json` 200  
- CORS Allow-Origin `http://app.doks.placeholder.metar-iwxxm.local`

## Residuals (non-blocking under waives)

- Real DNS / HTTPS — `D-S038-t63-waive`
- GHCR republish `backend:ev031-doks` + `frontend:ev031-doks` (remove ConfigMap sslmode / FE hot-copy)
- Evolve PR → `main` after Phase D close

## Rollback

Per [deploy-checklist.md](deploy-checklist.md): prior GHCR tags + `kubectl rollout undo`; **do not** unsuspend Render as primary without a new decision.

## Recommendation

Mark **13 PASS** (provisional DOKS deployed + H1–H5 connectivity green) and proceed to Phase D / cycle close AskQuestion.
