# Deploy smoke — S050 / EV-042 (13-deploy-smoke)

> Date: 2026-08-07  
> Status: **COMPLETE** — `D-S050-13=1` (2026-08-07)  
> PR: [#899](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/899) **MERGED** @ `e3d1c7c8`  
> Product tip: `5558c7e4` (signed 12) · merge: `e3d1c7c84836751ea070cb6162df749b218d2ef2`  
> `env_role`: **live = prod** (sole DOKS)  
> CD: [CI/CD Pipeline 31197264636](https://github.com/EMPIRIC2/TAC-to-IWXXM/actions/runs/31197264636) **success** (Deploy job green)  
> Corpus: [Corpus: tests] [Corpus: tech-spec] [Corpus: product §F7/F16–F19/F33]  
> **OOS:** Sync database migrations CI fail (accepted)

## Sequence

| Step | Result | Notes |
|------|--------|-------|
| 12 strategy sign-off | PASS | `D-S050-12=1` |
| Commit + push signed 12 | PASS | `5558c7e4` |
| Merge #899 | PASS | `D-S050-merge=1` → `e3d1c7c8` on `main` |
| Main CI + DOKS Deploy | PASS | run 31197264636 |
| H0c CORS unit | PASS | 6/6 |
| H1 live API | PASS | `make test-live-api` — 20 passed, 1 skipped |
| H4 live CORS (incl. `/api/v1/ingest/mass`) | PASS | 3/3 incl. mass preflight |
| H5 FE `config.json` | PASS | `api.baseUrl=https://api.tac-to-iwxxm.com` |
| Live stack convert/CORS/auth | PASS | 5/6 functional; see advisory |
| Live UJ-051..053 Playwright | PASS | **6/6** against `app.tac-to-iwxxm.com` |
| H7 bulletin (TC-LIVE-F6-030) | FAIL / OOS | `empty_bulletin` — not EV-042 surface |
| Sync DB migrations | FAIL / OOS | not EV-042 gate |

## H4–H5 evidence

```
Live API awake: https://api.tac-to-iwxxm.com
== H0c: CORS policy unit tests == … 6 passed
== H4: Live CORS preflight == … 3 passed
  (convert + work_sessions PATCH + ingest/mass POST)
== H5: Frontend runtime config check ==
OK: https://app.tac-to-iwxxm.com/config.json api.baseUrl=https://api.tac-to-iwxxm.com
Connectivity verification complete.
```

## Live UJ-051..053

```
apps/e2e/uj051-053-ev042-mass-queue.e2e.spec.ts — 6 passed (7.6s)
  UJ-053 destinations absent (incl. Upload to Database)
  UJ-051 guest prompt + unauth deny + signed-in zip queue
  UJ-052 work queue keyboard/batch + Select Files companion
```

## Advisories

1. `test_live_env_defaults_match_render_stack` — fails when parent shell exports prod `LIVE_*` (asserts DOKS placeholder defaults). Not a live stack regression; functional live tests passed.
2. H7 bulletin — multipart field name / API contract mismatch (`empty_bulletin`); out of scope for F33/destinations hide. Track separately if needed.
3. `.env` line 55 parse noise (`to: command not found`) during `load_dotenv` — pre-existing; did not block smokes.

## Rollback

Prior DOKS/GHCR tag via `doks_rollout_images.sh` / previous Deploy run; no DB migrations this cycle.

## Sign-Off

- [x] Deploy strategy verified (12)
- [x] #899 merged + DOKS CD green
- [x] H0c + H1 + H4–H5 (mass) + live UJ-051..053
- [x] User approves 13 complete (`D-S050-13=1`) — S050 / EV-042 closed
