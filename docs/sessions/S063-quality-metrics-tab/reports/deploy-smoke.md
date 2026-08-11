# Deploy smoke — S063 / EV-054 (13-deploy-smoke)

> Date: 2026-08-10  
> Status: **COMPLETE (pending user sign-off)** — awaiting `D-S063-13`  
> PR: [#977](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/977) **MERGED** @ `4fd51e39` → `stage`  
> Tip before merge: `f7cdafb1` · merge: `4fd51e397ccf91f9cefeb0d367b811eb0c09fbb1`  
> `env_role`: **staging** (`api|app.staging.tac-to-iwxxm.com`)  
> CD: [CI/CD Pipeline 31453072506](https://github.com/EMPIRIC2/TAC-to-IWXXM/actions/runs/31453072506) **success** (Deploy (stage) + Staging smoke)  
> Corpus: [Corpus: tests] [Corpus: tech-spec] [Corpus: product §F7] [Corpus: api]  
> Board: #836 → **On stage**

## Sequence

| Step | Result | Notes |
|------|--------|-------|
| 12 strategy sign-off | PASS | `D-S063-12=1` |
| Merge #977 → `stage` | PASS | `4fd51e39` |
| Stage CI + Deploy (stage) | PASS | run 31453072506 |
| Staging smoke (CI) | PASS | same run |
| H0c CORS unit | PASS | 6/6 |
| H1 live API `/health` | PASS | 200 healthy |
| H3 convert `POST /api/v1/convert` | PASS | 200 with `metars` |
| H3′ quality-metrics | PASS | list + detail `metar-A3-1` 200 |
| H4 live CORS | PASS | 3/3 |
| H5 FE `config.json` | PASS | `api.baseUrl=https://api.staging.tac-to-iwxxm.com` |
| Live UJ-056 Playwright | PASS | 1/1 vs `app.staging.tac-to-iwxxm.com` |

## H4–H5 evidence

```
Live API awake: https://api.staging.tac-to-iwxxm.com
== H0c: CORS policy unit tests == … 6 passed
== H4: Live CORS preflight == … 3 passed
== H5: Frontend runtime config check ==
OK: https://app.staging.tac-to-iwxxm.com/config.json api.baseUrl=https://api.staging.tac-to-iwxxm.com
Connectivity verification complete.
```

## Live UJ-056

```
apps/e2e/uj056-quality-metrics.e2e.spec.ts — 1 passed (1.4s)
  open tab → filter METAR → passer detail + deferred gap label
```

## Rollback

Prior staging GHCR/DOKS tag via previous Deploy on `stage`; no DB migrations this cycle.

## Sign-Off

- [x] Deploy + Staging smoke green
- [x] H1–H5 (incl. quality-metrics probe) green
- [x] Live UJ-056 PASS on staging
- [ ] User approved smoke results — pending AskQuestion
- Promote `stage`→`main` **not** in this step (separate gate)
