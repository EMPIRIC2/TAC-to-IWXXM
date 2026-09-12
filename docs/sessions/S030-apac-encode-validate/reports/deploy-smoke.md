# Deploy smoke — S030 / EV-023 (#800 APAC encode–validate)

> Status: **PASS**  
> Date: 2026-07-30  
> Decision: merge #801 + live smoke (T7.4 / E23-4)  
> PR: [#801](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/801) **merged**  
> Merge commit: `af98690`  
> Main CI: [30586719518](https://github.com/EMPIRIC2/TAC-to-IWXXM/actions/runs/30586719518) **success** (Deploy included)  
> API deploy: `dep-d9lsvabm8hqs739dpqlg` **live**

## Scope

API/library deepen for F6 / F2 / F12 / F13 (no new UI): NSC exclusivity, Guidance nils,
`translationFailedTAC` quarantine, dual-register colour/nil offline policy,
`emit_translation_centre` gate, Amd79 informative suite (soft/xfail), FIR / “S OF” helpers,
COLLECT multi-version NS hooks.

| Surface | URL |
|---------|-----|
| Frontend | https://metar-to-iwxxm-frontend-v4-web.onrender.com |
| API | https://metar-to-iwxxm-api.onrender.com |

## Results

| Tier | Command / check | Result |
|------|-----------------|--------|
| Main CI + Deploy | `gh run 30586719518` | **PASS** |
| API Render | `dep-d9lsvabm8hqs739dpqlg` live | **PASS** |
| H1 | `GET /health` 200 + `tac2iwxxm_available` | **PASS** |
| H0c | CORS unit (6) via `verify_connectivity.sh` | **PASS** |
| H3 | `make test-live-api` | **PASS** 13 passed / 8 skipped (auth retired F21) |
| H4 | Live CORS preflight (2) | **PASS** |
| H5 | `/config.json` → live API host | **PASS** |
| EV-023 convert themes | Live multipart convert (see below) | **PASS** |

### Live EV-023 theme smoke (T7.4)

Unauthenticated public convert (F21) against live API:

| Check | Result |
|-------|--------|
| Default convert omits `translationCentre*` | **PASS** |
| `emit_translation_centre=true` + designator/name | **PASS** |
| NSC METAR → no `<iwxxm:CloudLayer>` | **PASS** |
| Unreliable METAR → `@translationFailedTAC` quarantine (HTTP 200) | **PASS** |
| `validate_output=true` on good METAR | **PASS** |

```bash
export LIVE_API_URL=https://metar-to-iwxxm-api.onrender.com
export LIVE_FRONTEND_URL=https://metar-to-iwxxm-frontend-v4-web.onrender.com
make test-live-connectivity   # H0c + H4 + H5
make test-live-api            # H3
# + live multipart convert checks above (NSC / quarantine / translationCentre)
```

## Health

- API healthy; EV-023 convert/validate deepen live on `…af98690` image
- FE `/config.json` points at live API
- Auth login skips expected under F21 public app

## Rollback

- Redeploy prior GHCR digests for API then FE (previous live: `dep-d9lpa60u01pc738l02ig`)
- Re-run `verify_connectivity.sh` + `/health` + EV-023 convert theme checks

## Verdict

**T7.4 / 13-deploy-smoke complete.** S030 / EV-023 APAC encode–validate deepen live on Render;
M7 / 24/24 tasks ready to close.
