# Deploy smoke — S066 / EV-056 (13-deploy-smoke)

> Date: 2026-08-11  
> Status: **COMPLETE** — awaiting `D-S066-13` user approve  
> PR: [#989](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/989) **MERGED** → `stage` @ `b4a63ab8`  
> Product tip (pre-merge): `d63265c2` · merge: `b4a63ab8ec09f47d8ea95a50008c698fa37b7734`  
> `env_role`: **staging** (`api|app.staging.tac-to-iwxxm.com`; cluster `metar-iwxxm-staging`)  
> CD: [CI/CD Pipeline 31545833142](https://github.com/EMPIRIC2/TAC-to-IWXXM/actions/runs/31545833142) **success** — Deploy (stage) + Staging smoke  
> Corpus: [Corpus: tests] [Corpus: tech-spec] [Corpus: product §F7.q] [Corpus: journeys §UJ-056]  
> Board: #988 → **On stage** (after smoke)

## Sequence

| Step | Result | Notes |
|------|--------|-------|
| Merge #989 → `stage` | PASS | merge `b4a63ab8` (`D-S066-pr=1`) |
| Stage CI + Deploy (stage) | PASS | run 31545833142 |
| Staging smoke (CI) | PASS | job success |
| H0c CORS unit | PASS | 6/6 |
| H1 live API (staging) | PASS | 20 passed, 1 skipped (auth-gated) |
| H2 / Staging health | PASS | API awake; FE `/` via H5 path |
| H3 primary journey | PASS | `GET /api/v1/quality-metrics` + `/{stem}` OK; FE `/quality` + `/quality/:stem` **200** |
| H4 live CORS | PASS | convert + work_sessions PATCH + mass ingest POST |
| H5 FE `config.json` | PASS | `api.baseUrl=https://api.staging.tac-to-iwxxm.com` |
| Live UJ-056 Playwright | deferred | local T0 3/3 PASS at 10-e2e; live optional |

## H4–H5 evidence

```
Live API awake: https://api.staging.tac-to-iwxxm.com
== H0c: CORS policy unit tests == … 6 passed
== H4: Live CORS preflight == … 3 passed
== H5: Frontend runtime config check ==
OK: https://app.staging.tac-to-iwxxm.com/config.json api.baseUrl=https://api.staging.tac-to-iwxxm.com
Connectivity verification complete.
quality-metrics files … pin 2025-2
detail stem metar-A3-1 match equal
FE /quality 200
FE /quality/metar-A3-1 200
Staging smoke: PASS
```

## Rollback

Prior staging DOKS/GHCR tag via Deploy job; no DB migrations this cycle.

## Promote (deferred)

Promote `stage`→`main` only after Staging gate green + explicit user request. **Not** requested at this 13 gate.

## Sign-Off

- [x] #989 merged + Staging Deploy + Staging smoke green
- [x] H0c + H1–H5 on staging
- [ ] User approves 13 complete (`D-S066-13`) — then close EV-056 / S066 on stage
