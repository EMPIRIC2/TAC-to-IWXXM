# Deploy smoke — S013 / EV-009 (F9 + F10)

> Date: 2026-07-17
> Status: **deployed** — all smoke tiers PASS
> PR: [#723](https://github.com/joseph-c-mcguire/metar-to-IWXXM/pull/723) (merged `4660602`)
> Main tip: `4660602` (merge) → CI/CD run `29615395066` Deploy success
> API: https://metar-to-iwxxm-api.onrender.com (`dep-d9da4kbtqb8s73cvrkog` live 2026-07-17T21:45:22Z)
> Frontend: https://metar-to-iwxxm-frontend-v4-web.onrender.com (`dep-d9da4l58nd3s73drqo00` live 2026-07-17T21:45:05Z)

## Pre-deploy

| Check | Result |
|-------|--------|
| 12-verify-deploy checklist | Approved (D-S013-EV009-deploy-check-A) |
| PR #723 CI | All checks green |
| Merge → main | `4660602` |
| GHCR image build + Render deploy hooks | CI Deploy job success; both services `live` |

## Smoke results

| Tier | What | Result |
|------|------|--------|
| H1 | API `/health` 200 + `tac2iwxxm_available` | **PASS** |
| H0c | `pytest tests/unit/test_cors_policy.py` | **PASS** 6/6 |
| H3 | `make test-live-api` (21 live infrastructure tests) | **PASS** 21/21 |
| H4 | Live CORS preflight (frontend origin + work-sessions PATCH) | **PASS** 2/2 |
| H5 | Frontend `/config.json` `api.baseUrl` → API | **PASS** |
| H6′ UJ-020 | Live `POST /api/v1/decode-tac` — 8 value-aware segments + flowing `summary` (KJFK / 180° / 24 °C / A3011) | **PASS** |
| H6′ UJ-021 | Live `POST /api/v1/lint-tac` — `ok: true`, `MISSING_TERMINATOR` severity `info`, `add_terminator` fix ending in `=` | **PASS** |

Commands:

```bash
make test-live-connectivity   # H0c + H4 + H5
make test-live-api            # H3
# H6′: admin login + multipart decode-tac / lint-tac with manual_text (see session notes)
```

## Health

- API reachable; convert/auth/validate paths green in H3 suite
- No new origins/endpoints; CORS matrix unchanged
- FE config points at production API

## Rollback

- Redeploy prior Render deploy / previous GHCR tag for API + frontend
- Last known good pre-EV-009: `main` @ `4b6cff8` (PR #722)
- No DB migrations this cycle — image-only rollback

## Verdict

**T4.5 / 13-deploy-smoke satisfied.** F9 and F10 are live in production.
