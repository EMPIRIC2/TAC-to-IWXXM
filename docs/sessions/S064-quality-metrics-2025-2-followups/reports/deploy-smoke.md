# Deploy smoke — S064 / EV-055 (13-deploy-smoke)

> Date: 2026-08-11  
> Status: **COMPLETE** — `D-S064-13=1`  
> PR: [#985](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/985) **MERGED** → `stage` @ `4b48c8d8`  
> Product tip (pre-merge): `a648f486` (`D-S064-12=1`) · merge: `4b48c8d85ff88b16641cd7f7fa66b1450dfbe6a3`  
> `env_role`: **staging** (`api|app.staging.tac-to-iwxxm.com`; cluster `metar-iwxxm-staging`)  
> CD: [CI/CD Pipeline 31534191417](https://github.com/EMPIRIC2/TAC-to-IWXXM/actions/runs/31534191417) **success** — Deploy (stage) + Staging smoke  
> Corpus: [Corpus: tests] [Corpus: tech-spec] [Corpus: product §F7] [Corpus: product §F2] [Corpus: product §F13]  
> Board: #982 / #980 / #979 → **Done** (session close)

## Sequence

| Step | Result | Notes |
|------|--------|-------|
| 12 strategy sign-off | PASS | `D-S064-12=1` |
| Merge #985 → `stage` | PASS | merge `4b48c8d8` |
| Stage CI + Deploy (stage) | PASS | run 31534191417 |
| Staging smoke (CI) | PASS | job ~29s |
| H0c CORS unit | PASS | 6/6 |
| H1 live API (staging) | PASS | 13 passed, 8 skipped (auth-gated) |
| H2 / Staging health | PASS | API `/health` 200; FE `/` 200 |
| H3 primary journey | PASS | `/api/v1/quality-metrics` OK; `/api/v1/versions` includes **2025-2** default |
| H4 live CORS | PASS | convert + work_sessions PATCH + mass ingest POST |
| H5 FE `config.json` | PASS | `api.baseUrl=https://api.staging.tac-to-iwxxm.com` |
| Live UJ-056 Playwright | deferred | local T0 PASS at 10/11; live optional waived at close |

## H4–H5 evidence

```
Live API awake: https://api.staging.tac-to-iwxxm.com
== H0c: CORS policy unit tests == … 6 passed
== H4: Live CORS preflight == … 3 passed
== H5: Frontend runtime config check ==
OK: https://app.staging.tac-to-iwxxm.com/config.json api.baseUrl=https://api.staging.tac-to-iwxxm.com
Connectivity verification complete.
Staging smoke: PASS
```

## Rollback

Prior staging DOKS/GHCR tag via Deploy job / `doks_rollout_images.sh`; no DB migrations this cycle.

## Promote (deferred)

Promote `stage`→`main` only after Staging gate green + explicit user request (release prep recommended). **Not** requested at `D-S064-13=1`.

## Sign-Off

- [x] Deploy strategy verified (12) — `D-S064-12=1`
- [x] #985 merged + Staging Deploy + Staging smoke green
- [x] H0c + H1–H5 on staging
- [x] User approves 13 complete (`D-S064-13=1`) — EV-055 / S064 closed on stage
