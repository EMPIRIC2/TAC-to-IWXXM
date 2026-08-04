# E2E Behavior Report — 10-e2e (EV-031 / S038 delta)

> **Generated**: 2026-08-03  
> **Mechanism**: mixed (Playwright local T0 + provisional DOKS T3 evidence)  
> **Overall**: **PASS**  
> **Features**: F30, F31 (UJ-045..048)

## Summary

| # | Journey | Mechanism | Tier | Status | Notes |
|---|---------|-----------|------|--------|-------|
| 1 | TAC file conversion (smoke) | Playwright | T0 | **PASS** 8/8 | Local FE:18000 API:18001 |
| 2 | UJ-045 guest + notice | Playwright | T3 | **PASS** | T7.1 provisional DOKS 13/13 pack |
| 3 | UJ-046 login + auto-upload | Playwright | T3 | **PASS** | T7.1 |
| 4 | UJ-047 privacy prefs | Playwright | T3 | **PASS** | T7.1 + public-app F21/F22 specs |
| 5 | UJ-048 DOKS cutover | Ops / live | T3 | **PASS** | T6.4 smoke + T6.5 Render suspend + T7.2 H4–H5 |
| 6 | Public convert (UJ-001) | Live API | T3 | **PASS** | Host-header DOKS `/health`+convert (T7) |

## T0 — Local Playwright smoke

```
make test-e2e-playwright-smoke
→ tac-file-conversion.e2e.spec.ts — 8 passed (16.3s)
  (servers pre-started; reuseExistingServer — avoids coverage-watch thrash)
```

## T2 connectivity

Deferred to **13-deploy-smoke** / retained **T7.2** provisional:

| Tier | Result |
|------|--------|
| H0c | PASS (09) |
| H4–H5 provisional | PASS (T7.2) |
| Full HTTPS H4–H5 | Deferred (`D-S038-t63-waive`) |

## T3 — Live (provisional DOKS)

| Evidence | Result |
|----------|--------|
| [t7.1-playwright-live-provisional.md](t7.1-playwright-live-provisional.md) | 13/13 PASS |
| [t7.2-h4-h5-connectivity-provisional.md](t7.2-h4-h5-connectivity-provisional.md) | H0c 6/6, H4 2/2, H5 PASS |
| [t6.5-render-decommission.md](t6.5-render-decommission.md) | Render 503 / DOKS 200 |

## Notes

- First `make test-e2e-playwright-smoke` timed out when Vite watched `apps/frontend/coverage/**` after concurrent coverage run — fixed by ignoring coverage in Vite watch + starting clean servers.
- Browser MCP live walk not re-run this stage (T7.1 evidence accepted for delta).
