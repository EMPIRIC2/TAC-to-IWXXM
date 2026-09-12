# Deploy smoke — S024 / EV-018 (#785)

> Status: **PASS**  
> Date: 2026-07-29  
> Decision: **D-S024-13-deploy-A**  
> PR: [#791](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/791) **merged**  
> Merge commit: `2f552b9`  
> FE deploy: `dep-d9kkjj5bedkc73au0aeg` **live** (deploy_hook)  
> Main CI: [30411047349](https://github.com/EMPIRIC2/TAC-to-IWXXM/actions/runs/30411047349) **success** (Deploy job included)

## Scope

FE-only F16 multi-file dissemination selection — no API image / allowlist / Supabase env changes.

| Surface | URL |
|---------|-----|
| Frontend | https://metar-to-iwxxm-frontend-v4-web.onrender.com |
| API | https://metar-to-iwxxm-api.onrender.com |

## Results

| Tier | Command / check | Result |
|------|-----------------|--------|
| Main CI + Deploy | `gh run 30411047349` | **PASS** |
| FE Render | `dep-d9kkjj5bedkc73au0aeg` live | **PASS** |
| H0c | CORS unit (6) via `verify_connectivity.sh` | **PASS** |
| H4 | Live CORS preflight (2) | **PASS** |
| H5 | `/config.json` → live API host | **PASS** |
| H6′ UJ-027–030 | Playwright vs live FE (stubbed dissemination APIs) | **PASS** 7/7 (~13.8s) |

### H6′ detail

```bash
PLAYWRIGHT_BASE_URL=https://metar-to-iwxxm-frontend-v4-web.onrender.com \
PLAYWRIGHT_API_BASE_URL=https://metar-to-iwxxm-api.onrender.com \
  pnpm exec playwright test uj027-030-dissemination-drawer.e2e.spec.ts
# 7 passed (13.8s)
```

Live BYOC destination demos (TC-F17-002 / TC-F18-002) remain out of this FE-only cycle close (mocked in H6′ per spec).

## Not required

- API image rebuild
- `DISSEMINATION_EGRESS_ALLOWLIST` change
- Supabase env changes

## Rollback

Redeploy prior FE deploy `dep-d9kj1gajobas73fm12c0` (or previous GHCR/frontend tag) via Render.
