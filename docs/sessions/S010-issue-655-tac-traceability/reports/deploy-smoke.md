# Deploy smoke — S010 / EV-007 (#655)

**Date**: 2026-07-13  
**Frontend**: https://metar-to-iwxxm-frontend-v4-web.onrender.com  
**API**: https://metar-to-iwxxm-api.onrender.com  
**PR**: [#715](https://github.com/joseph-c-mcguire/metar-to-IWXXM/pull/715) (merged)

## Checks

| Check | Result |
|-------|--------|
| Prod API convert returns `tac_input` | **PASS** — `POST /api/v1/convert` with `{metars:[…]}` returned `tac_input` matching input |
| Frontend redeploy live | **PASS** — `metar-to-iwxxm-frontend-v4-web` deploy `live` at 2026-07-13T00:13:40Z (post-merge) |
| UI Source TAC after Convert | **PASS** — logged in as admin; manual METAR converted; result card showed header `METAR KJFK 121251Z`, **SOURCE TAC** panel with full TAC `METAR KJFK 121251Z 18004KT 10SM FEW250 24/18 A3012`, plus IWXXM XML |
| Guest convert | Blocked on prod (auth required) — not a #655 regression |

## Verdict

**M2 / 13-deploy-smoke satisfied.** Issue #655 closed; no further product work for S010.
