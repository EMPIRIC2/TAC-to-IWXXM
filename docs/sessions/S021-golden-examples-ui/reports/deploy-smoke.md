# Deploy Smoke — S021 / EV-016 (F7.g golden examples)

> Date: 2026-07-27  
> Status: **completed with waiver** (live UJ-032 / H4–H5 deferred to #781)  
> Commit on `main`: `c49f22b` (PR #782 merged; #780 closed)  
> Waiver: user chose option **3** (2026-07-27) — close EV-016; live goldens H4–H5 with #781

## Pre-deploy

| Check | Result |
|-------|--------|
| PR #782 | MERGED 2026-07-27 |
| Issue #780 | CLOSED |
| Main CI tests | PASS (`30227888075`) |
| Deploy job | FAIL — empiric2 GHCR push OK; Render hook **400** (old imagePath) |

## What shipped to GHCR (EMPIRIC2)

| Image | Tags |
|-------|------|
| `ghcr.io/empiric2/tac-to-iwxxm/backend` | `20260727004311-c49f22b`, `main-latest` |
| `ghcr.io/empiric2/tac-to-iwxxm/frontend` | `20260727004311-c49f22b`, `main-latest` |
| `ghcr.io/empiric2/tac-to-iwxxm/worker` | `20260727004311-c49f22b`, `main-latest` |

## Live Render (not updated this cycle)

| Service | URL | imagePath |
|---------|-----|-----------|
| API | https://metar-to-iwxxm-api.onrender.com | `ghcr.io/joseph-c-mcguire/metar-to-iwxxm/backend:main-latest` |
| Frontend | https://metar-to-iwxxm-frontend-v4-web.onrender.com | `ghcr.io/joseph-c-mcguire/metar-to-iwxxm/frontend:main-latest` |

Live FE remains pre–F7.g (no Examples catalog in the served bundle).

## Smoke matrix

| Tier | Status | Notes |
|------|--------|-------|
| H0c | waived | FE-only delta; CORS unchanged |
| H1–H3 | waived | API image not required for F7.g |
| H4–H5 | **waived → #781** | User decision 3; blocked on GHCR/Render cutover |
| UJ-032 live goldens UI | **waived → #781** | Code on `main` @ `c49f22b`; Vitest T0 PASS in-cycle |

## Waiver record

- **Decision id**: `D-S021-EV016-13-waive-live-h4h5`
- **Rationale**: Empiric2 GHCR images exist; Render cannot pull until #781 registry/imagePath cutover. User explicitly waived live goldens proof to close EV-016.
- **Required follow-up**: [#781](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/781) — retarget Render `imagePath` → `ghcr.io/empiric2/tac-to-iwxxm/*`, redeploy FE, then `make test-live-connectivity` + browser UJ-032 Examples load.

## Gate

| Gate | Result |
|------|--------|
| Deploy (EV-016) | **waived** (live FE not @ `c49f22b`) |
| Cycle close | allowed under user waiver 3 |
