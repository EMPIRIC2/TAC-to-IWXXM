# 13-deploy-smoke — S042 / EV-034

**Date:** 2026-08-05  
**Commit:** `d3f4bb95` (merge #868)  
**CI Deploy:** [31003268652](https://github.com/EMPIRIC2/TAC-to-IWXXM/actions/runs/31003268652) **success**  
**DOKS tag:** `20260805115809-d3f4bb9`

## CD rollout (TC-F30-007)

```
DOKS rollout ns=metar-iwxxm tag=20260805115809-d3f4bb9
  metar-api      -> …/backend:20260805115809-d3f4bb9
  metar-frontend -> …/frontend:20260805115809-d3f4bb9
  metar-worker   -> …/worker:20260805115809-d3f4bb9
deployment "metar-api" successfully rolled out
deployment "metar-frontend" successfully rolled out
deployment "metar-worker" successfully rolled out
```

doctl exec-auth guard ran before rollout (no error).

## Live smoke

| Check | Result |
|-------|--------|
| `GET https://api.tac-to-iwxxm.com/health` | **200** |
| OpenAPI `/auth/login`, `/auth/me` | present |
| `GET https://app.tac-to-iwxxm.com/` | **200** |
| H0ci (main CI) | **pass** (full pipeline success) |
| H4–H5 re-run | waived this cycle (no UI change; prior public DNS pass) |

## Overall

**Technical PASS** — automated DOKS CD proven end-to-end.

Awaiting user approve to close EV-034 / S042.
