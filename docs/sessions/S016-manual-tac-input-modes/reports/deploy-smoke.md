# Deploy smoke — S016 / EV-012 (Manual TAC Input modes)

> Date: 2026-07-20  
> Status: **deployed** — 13-deploy-smoke PASS  
> PR: [#746](https://github.com/joseph-c-mcguire/metar-to-IWXXM/pull/746) (merged `37be5f8`)  
> Main tip: `37be5f8` → CI/CD run [`29766213356`](https://github.com/joseph-c-mcguire/metar-to-IWXXM/actions/runs/29766213356) Deploy **SUCCESS**  
> API: https://metar-to-iwxxm-api.onrender.com (`dep-d9f69f3bc2fs7397bqig` live, image `…/backend:20260720180925-37be5f8`)  
> Frontend: https://metar-to-iwxxm-frontend-v4-web.onrender.com (`dep-d9f69fjbc2fs7397brq0` live, image `…/frontend:20260720180925-37be5f8`)

## Pre-deploy

| Check | Result |
|-------|--------|
| Routing | Lean + 13 (12-verify-deploy waived by D-S016-EV012-route-1) |
| Merge approval | User: merge |
| PR #746 CI | All required checks SUCCESS |
| Merge → main | `37be5f8` |
| Path A | Push + PR then smoke after deploy (D-S016-EV012-13-path-A) |

## Smoke results

| Tier | What | Result |
|------|------|--------|
| H0ci | CI/CD on `main` @ `37be5f8` (incl. Deploy) | **PASS** |
| H1 | API `/health` (via H3 suite) | **PASS** |
| H0c | CORS policy unit tests | **PASS** 6/6 |
| H3 | `make test-live-api` | **PASS** 21/21 |
| H4 | Live CORS preflight | **PASS** 2/2 |
| H5 | Frontend `/config.json` → API | **PASS** |
| UJ-025 AHL | Auth multipart `POST /convert-bulletin` (manual_text) | **PASS** 200, 2 reports |
| UJ-025 COLLECT | Auth multipart `POST /ingest-collect` | **PASS** **501** placeholder |
| H6′ workbench | Live Playwright: AHL summary + COLLECT placeholder notice/toast | **PASS** (~12s) |

Commands:

```bash
make test-live-connectivity   # H0c + H4 + H5
make test-live-api            # H3
# AHL + COLLECT: authenticated multipart against LIVE_API_URL
# Workbench: loginAndOpenConverter + input-mode-* testids (ephemeral live smoke)
```

## Notes

- FE App chunk (`App-OwDZEakI.js`) contains Manual TAC Input mode strings (`AHL`, `COLLECT`, `placeholder-notice`).
- `make test-live-bulletin` (H7 harness) still posts form field `file` (singular) and gets `empty_bulletin` 400; **not a regression of this PR** — UJ-025 AHL gate verified via `manual_text` multipart + live workbench instead.
- F7 remains **Planned**; COLLECT stays 501 (no member extract).

## Health

- API + FE live on `37be5f8`
- Mode toggle, convert-bulletin happy path, and COLLECT 501 UX confirmed on staging workbench

## Rollback

- Redeploy prior GHCR digests (`…-cad9502`) for API then frontend
- Re-run `verify_connectivity.sh` + AHL/COLLECT probes

## Verdict

**13-deploy-smoke complete.** Manual TAC Input modes validation (UJ-025 / TC-F7-007) live on Render.
