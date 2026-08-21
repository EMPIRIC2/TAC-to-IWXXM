# Deploy smoke — S071 / EV-061 (13-deploy-smoke)

> Date: 2026-08-20  
> Status: **COMPLETE** — `D-S071-13` / `D-S071-close` (promote **held**)  
> PR: [#1016](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/1016) **MERGED** → `stage`  
> Docs: [#1018](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/1018) **MERGED** → `stage`  
> Stage tip / merge: `86867a11` (product); docs tip after #1018: `0fb5c113`  
> `env_role`: **staging** (`api|app.staging.tac-to-iwxxm.com`; cluster `metar-iwxxm-staging`)  
> CD: [32398410519](https://github.com/EMPIRIC2/TAC-to-IWXXM/actions/runs/32398410519) — Deploy (stage) + Staging smoke **success**  
> Decisions: `D-S071-12-merge=1`; `D-S071-13=1`; `D-S071-close=1`  
> Corpus: [Corpus: product §F2] [Corpus: product §F6] [Corpus: product §F7] [Corpus: product §F9] [Corpus: product §F10] [Corpus: product §F15] [Corpus: product §F34] [Corpus: journeys] [Corpus: tests] [Corpus: deploy] [Corpus: adr/ADR-034] [Corpus: decisions §EV-061]  
> Board: #1010–#1015 + epic #1009 **CLOSED**; [#1017](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1017) backlog; promote held

## Sequence

| Step | Result | Notes |
|------|--------|-------|
| 11 AC approve | PASS | `D-S071-11-ac=1a` |
| 12 checklist + merge | PASS | `D-S071-12-merge=1`; tip CI @ `a3420f8f` |
| Merge #1016 → `stage` | PASS | merge `86867a11` |
| Stage CI + Deploy (stage) | PASS | run 32398410519 (~2m53s deploy) |
| Staging smoke (CI) | PASS | health + FE + CORS (~27s) |
| H0c CORS unit | PASS | 6/6 via `verify_connectivity.sh` |
| H1 live API (staging) | PASS | 20 passed, 1 skipped (`make test-live-api`) |
| H2 / Staging health | PASS | API awake + FE `config.json` |
| H3 convert journey | PASS | `test_t72_h3_live_smoke.py` 3/3 |
| H4 live CORS | PASS | 3/3 |
| H5 FE `config.json` | PASS | `api.baseUrl=https://api.staging.tac-to-iwxxm.com` |
| Live UJ-064..068 | PASS | Playwright 6/6 (~7.2s) |

## H4–H5 evidence

```
Live API awake: https://api.staging.tac-to-iwxxm.com
== H0c: CORS policy unit tests == … 6 passed
== H4: Live CORS preflight == … 3 passed
== H5: Frontend runtime config check ==
OK: https://app.staging.tac-to-iwxxm.com/config.json api.baseUrl=https://api.staging.tac-to-iwxxm.com
Connectivity verification complete.
```

## Live Playwright (EV-061)

```
[chromium] UJ-064 Validate IWXXM decode — passed
[chromium] UJ-065 AHL convert + INVALID_AHL — passed (2)
[chromium] UJ-066/067 product-profile + params bars — passed (2)
[chromium] UJ-068 Lint & validation catalog — passed
6 passed (7.2s)
```

## Rollback

Prior staging GHCR / `stage-latest` predecessor via Deploy job; no DB migrations this cycle.

## Promote (deferred)

Promote `stage`→`main` remains **held** until admin applies #1015 rulesets (`apply_gh_branch_rulesets.sh`) and a separate user re-approve. **Not** opened this cycle.

## Sign-Off

- [x] #1016 merged + Staging Deploy + Staging smoke green
- [x] H0c + H1–H5 on staging
- [x] Live UJ-064..068 PASS
- [x] User approves 13 complete (`D-S071-13=1`) — session closed (`D-S071-close=1`); promote still deferred
- [x] #1010–#1015 + epic #1009 CLOSED; #1017 backlog
