# Deploy smoke — S068 / EV-058 (13-deploy-smoke)

> Date: 2026-08-17  
> Status: **COMPLETE** — `D-S068-13=1` / `D-S068-close=1` (promote held)  
> PR: [#994](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/994) **MERGED** → `stage`  
> Stage tip / merge: `2c320c45` (feature tip incl. `56cc0564` FE branch-coverage fix)  
> `env_role`: **staging** (`api|app.staging.tac-to-iwxxm.com`; cluster `metar-iwxxm-staging`)  
> CD: [32038222032](https://github.com/EMPIRIC2/TAC-to-IWXXM/actions/runs/32038222032) — Deploy (stage) + Staging smoke **success**  
> Decision: `D-S068-merge=1` (merge #994 → stage, then 13)  
> Corpus: [Corpus: product §F7.q] [Corpus: journeys §UJ-056] [Corpus: tests §UJ-056] [Corpus: deploy] [Corpus: adr/ADR-034]  
> Board: #983 → **Done** (issue CLOSED; promote held)

## Sequence

| Step | Result | Notes |
|------|--------|-------|
| Merge #994 → `stage` | PASS | merge `2c320c45` |
| Stage CI + Deploy (stage) | PASS | run 32038222032 |
| Staging smoke (CI) | PASS | health + FE + CORS |
| H0c CORS unit | PASS | 6/6 |
| H1 live API (staging) | PASS | 20 passed, 1 skipped |
| H2 / Staging health | PASS | API + FE + CORS via `staging_smoke.sh` |
| H3 convert / lint journey | PASS | `test_t72_h3_live_smoke.py` 3/3 |
| H4 live CORS | PASS | 3/3 |
| H5 FE `config.json` | PASS | staging API baseUrl |
| Live UJ-056 (incl. TC-EV058-005) | PASS | 4/4 Playwright (~5.2s) |

## H4–H5 evidence

```
Live API awake: https://api.staging.tac-to-iwxxm.com
== H0c: CORS policy unit tests == … 6 passed
== H4: Live CORS preflight == … 3 passed
== H5: Frontend runtime config check ==
OK: https://app.staging.tac-to-iwxxm.com/config.json api.baseUrl=https://api.staging.tac-to-iwxxm.com
Connectivity verification complete.
```

## Live Playwright (UJ-056 / EV-058)

```
[chromium] UJ-056 open tab → filter METAR → passer detail — passed
[chromium] TC-EV055-007 normalized panes / raw override — passed
[chromium] TC-EV056-005 deep-link /quality/:stem — passed
[chromium] TC-EV058-005 Inline ↔ Side-by-side persist — passed
4 passed (5.2s)
```

## Rollback

Prior staging GHCR/`stage-latest` predecessor via Deploy job; no DB migrations in this PR.

## Promote (deferred)

Promote `stage`→`main` remains **held** until a separate user re-approve. **Not** opened this turn.

## Sign-Off

- [x] #994 merged + Staging Deploy + Staging smoke green
- [x] H0c + H1–H5 on staging
- [x] Live UJ-056 incl. TC-EV058-005 PASS
- [x] Board #983 → On stage
- [x] User approves 13 complete (`D-S068-13=1`) — session closed (`D-S068-close=1`); promote still deferred
