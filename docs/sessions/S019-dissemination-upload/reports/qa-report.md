# QA Report — S019 / EV-014 (F16–F19 delta)

> Generated: 2026-07-21  
> Scope: Dissemination epic F16–F19 (M1–M6 complete; Phase D bookkeeping)  
> Evidence tip: `main` @ `#772` merge `c61273a`  
> Mode: evolve / Full routing (09-qa bookkeeping; reuses T6.4 + CI)

## Summary

| Check | Status | Notes |
|-------|--------|-------|
| Format / lint / typecheck | PASS | T6.4 `verification-report.md`; CI Validate green on #772 |
| Unit / package tests | PASS | CI matrix: backend, auth, shared, tac2iwxxm, tac-validate, iwxxm-validate, dissemination, frontend, bugs, integration |
| Dissemination package | PASS | CI Test (dissemination); mock BYOC smoke **134** (`make test-mock-byoc-smoke`) |
| H0c CORS | PASS | T6.4 + T6.6 `verify_connectivity.sh` |
| H0i integration | PASS (CI) | Test (integration) green on #772; local Docker engines optional |
| Secrets in git | PASS | `.env` gitignored; fixtures are fake shapes only |
| Staging H4–H5 | PASS | Exercised at T6.6 / 13 (`deploy-smoke.md`) |

**Overall: PASS** (advisories below)

## Blocking

None.

## Advisories

1. **QA-LIVE-BYOC** — Live destination Postgres/WIS2/EDIS demos waived under
   `D-S019-EV014-Q15-mock-waive`; mock/harness evidence substitutes for EV-014 close.
2. **QA-RENDER-ALLOWLIST** — Live Render `DISSEMINATION_EGRESS_ALLOWLIST` left empty
   (fail-closed) until operator sets exact BYOC hosts (`deploy-checklist.md`).
3. **QA-H3-AUTH** — Authenticated live H3 against Render waived (fake login cannot hit
   Supabase); API unit paths use `DISABLE_AUTH` + mocked user.

## Connectivity (stage 09)

| Tier | Result |
|------|--------|
| H0c | PASS |
| H0i | PASS (CI) |
| H4–H5 | PASS (13 / T6.6) |
