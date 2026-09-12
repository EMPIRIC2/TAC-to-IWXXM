# Evolve summary — EV-032 / S040 (IWXXM corpus quality)

> Date: 2026-08-05 (resumed after S042; closed same day)  
> Status: **completed** (`D-S040-close` = 1)  
> Branch: `evolve/EV-032-iwxxm-corpus-quality` → **PR #848 merged** @ `dfecba46`  
> Features: **F32** VONA; deepen F23 (#835), F4/F6/F2/F13 (#808/#847)  
> Live re-verify: DOKS tag `20260805115809-d3f4bb9` (post–EV-034 CD)

## What shipped

| Track | Result |
|-------|--------|
| #835 A6-2-TC ADR-032 → `wmoPass` | **closed** |
| #741 F32 VONA lint/convert/validate + FE Examples | **closed** |
| #808 / #847 release-line adoptability docs | **closed** |
| #846 epic children (M0 gaps) | filed; epic **remains open** for residual corpus work |

Merged via **PR #848**.

## Stages

| Stage | Result |
|-------|--------|
| 00→16→01→02→04→07→08→09→10→11→12 | **completed** (pre-suspend) |
| 13-deploy-smoke (T4.5) | **PASS** 2026-08-04; **re-confirmed** 2026-08-05 on current DOKS |
| T4.6 evolve summary + session close | **completed** this resume |

## Live proof (T4.5 + resume)

| Check | 2026-08-04 | 2026-08-05 resume |
|-------|------------|-------------------|
| Tag | `20260804214648-dfecba4` | `20260805115809-d3f4bb9` |
| `/health` | PASS | PASS |
| VONA convert-bulletin | PASS | PASS (`VolcanoObservatoryNoticeForAviation`) |
| FE `vona_a7_1` / `vona-A7-1` | `App-BkEPMp_C.js` | `App-CNHsL_15.js` |
| H4 CORS preflight | PASS | PASS (manual) |
| H5 `/config.json` → API | PASS | PASS |

Note: `scripts/deploy/verify_connectivity.sh` currently fails under `set -u` (`api_curl_headers[@]` unbound) — tracked as follow-up; manual H4–H5 + unit CORS used for close.

## Artifacts

- `reports/deploy-smoke.md`, `verify-impl.md`, `qa-report.md`, `e2e-report.md`
- `reports/execution-plan.md` (28 tasks; T4.5–T4.6 completed on close)
- M0–M4 verification + closeout reports under `reports/`

## Follow-ups (remain under #846)

Open children include VONA deepen (#849/#850), release-line automation (#851–#855), corpus gaps (#856–#861). Not blocking EV-032 close.

## Decisions

| ID | Choice |
|----|--------|
| D-S040-13 | 1 — push+merge #848 → DOKS → H1–H5 |
| D-S040-resume | 1 — resume after S042 close |
| D-S040-close | 1 — approve T4.5 re-verify + close S040 / EV-032 |
