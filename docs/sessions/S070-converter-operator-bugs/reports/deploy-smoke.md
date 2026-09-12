# Deploy smoke — S070 / EV-060 (13-deploy-smoke)

> Date: 2026-08-18  
> Status: **COMPLETE** — `D-S070-13` / `D-S070-close` (promote **held**)  
> PR: [#1007](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/1007) **MERGED** → `stage`  
> Stage tip / merge: `6ef540bc`  
> `env_role`: **staging** (`api|app.staging.tac-to-iwxxm.com`; cluster `metar-iwxxm-staging`)  
> CD: [32183276810](https://github.com/EMPIRIC2/TAC-to-IWXXM/actions/runs/32183276810) — Deploy (stage) + Staging smoke **success**  
> Decisions: merge squash `D-S070-13-merge`; close children #1001–#1006; epic #1000 open for closeout  
> Corpus: [Corpus: product §F7] [Corpus: product §F6] [Corpus: product §F31] [Corpus: journeys] [Corpus: tests] [Corpus: deploy] [Corpus: adr/ADR-034] [Corpus: decisions §EV-060]  
> Board: #1001–#1006 **CLOSED**; epic #1000 **OPEN** (closeout); promote held

## Sequence

| Step | Result | Notes |
|------|--------|-------|
| 12 checklist (no merge) | PASS | `D-S070-12-*` |
| Squash-merge #1007 → `stage` | PASS | merge `6ef540bc`; closed #1001–#1006 |
| Stage CI + Deploy (stage) | PASS | run 32183276810 |
| Staging smoke (CI) | PASS | health + FE + CORS |
| H0c CORS unit | PASS | 6/6 via `verify_connectivity.sh` |
| H1 live API (staging) | PASS | 20 passed, 1 skipped (`make test-live-api`) |
| H2 / Staging health | PASS | API awake + FE `config.json` |
| H3 convert journey | PASS | `test_t72_h3_live_smoke.py` 3/3 |
| H4 live CORS | PASS | 3/3 |
| H5 FE `config.json` | PASS | `api.baseUrl=https://api.staging.tac-to-iwxxm.com` |
| Live UJ-059..063 | PASS | Playwright 11/11 (~13s wall with auth suite) |
| Live TC-EV060-1006 Auth | PASS | Playwright 3/3 (register stub / login persist / logout guest) |

## H4–H5 evidence

```
Live API awake: https://api.staging.tac-to-iwxxm.com
== H0c: CORS policy unit tests == … 6 passed
== H4: Live CORS preflight == … 3 passed
== H5: Frontend runtime config check ==
OK: https://app.staging.tac-to-iwxxm.com/config.json api.baseUrl=https://api.staging.tac-to-iwxxm.com
Connectivity verification complete.
```

## Live Playwright (EV-060)

```
[chromium] TC-EV060-1006-001..003 Auth UAT — passed (3)
[chromium] UJ-059 AHL bulletin (+ lint-tac) — passed (3)
[chromium] UJ-060 IWXXM product pass-through — passed (3)
[chromium] UJ-061 Profile at converter top — passed (1)
[chromium] UJ-062 Bulletin ID / Issuing Center — passed (2)
[chromium] UJ-063 log_level — passed (2)
14 passed (13.5s)
```

## Advisory (out of EV-060 scope)

`tests/live/test_tc_live_f6_030_bulletin.py` posts multipart field `file`; API expects `files`.
Live probe: `files` → **200**; `file` → **400** `empty_bulletin`. Not an EV-060 product
regression (CI Staging smoke green; convert-bulletin works). Follow-up: fix the live test
field name in a small chore/hotfix.

## Rollback

Prior staging GHCR / `stage-latest` predecessor via Deploy job; no DB migrations this cycle.

## Promote (deferred)

Promote `stage`→`main` remains **held** until a separate user re-approve. **Not** opened this turn.

## Sign-Off

- [x] #1007 merged + Staging Deploy + Staging smoke green
- [x] H0c + H1–H5 on staging
- [x] Live UJ-059..063 + TC-EV060-1006 PASS
- [x] Children #1001–#1006 CLOSED; epic #1000 left for closeout
- [x] User approves 13 complete (`D-S070-13`) — session closed (`D-S070-close`); promote still deferred
