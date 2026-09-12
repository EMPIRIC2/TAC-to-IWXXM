# Deploy smoke — S048 / EV-040

**Date:** 2026-08-06 (local) / 2026-08-07 UTC  
**PR:** https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/893  
**Branch tip:** `65ad32d7` (`evolve/EV-040-workbench-lint-ux`)  
**Live stack:** DOKS `api.tac-to-iwxxm.com` / `app.tac-to-iwxxm.com` (pre-merge tip)

## Sequence

| Step | Result | Notes |
|------|--------|-------|
| Push + local `make ci` | PASS | Pre-push green |
| GitHub CI (PR) | PASS | Frontend coverage fix; run 31134161218 green |
| H0c (CORS unit) | PASS | via `verify_connectivity.sh` |
| H1–H3 live API | PASS | `make test-live-api` — 20 passed, 1 skipped |
| H4–H5 | PASS | `bash scripts/deploy/verify_connectivity.sh` |
| Tip CD of EV-040 UI | **blocked on merge** | DOKS CD on `main`; merge needs explicit approval |

## H4–H5 evidence

```
Live API awake: https://api.tac-to-iwxxm.com
== H0c: CORS policy unit tests == … 6 passed
== H4: Live CORS preflight == … 2 passed
== H5: Frontend runtime config check ==
OK: https://app.tac-to-iwxxm.com/config.json api.baseUrl=https://api.tac-to-iwxxm.com
Connectivity verification complete.
```

## UI preview (AC / Q4)

Local non-deployed preview accepted (`:18000`) — EV-040 workbench UX verified in Vitest + local preview; live FE tip still prior commit until merge.

## Corpus

[Corpus: tests] H-tiers · [Corpus: product] F7/F10/F15 · [Corpus: tech-spec] deploy/liveE2e
