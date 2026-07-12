# E2E Report — S008 / EV-006 Phase D

> **Generated**: 2026-07-12  
> **Skill**: 10-e2e (delta)  
> **Session**: S008-general-tac-iwxxm-converter  
> **Cycle**: EV-006  
> **Branch**: `evolve/S008-general-tac-iwxxm-converter`

## Tier summary

| Tier | Status | Notes |
|------|--------|-------|
| **T0** Local Playwright smoke | **FAIL** | 10 passed, **2 failed** (COR → `reportStatus="CORRECTION"`) |
| **T1** Integration (H0i) | PASS* | 6 CORS + 7 integration skipped (no live env) |
| **T2** Deploy smoke H1–H5 | SKIPPED | 12/13 not in routing; staging live not required this cycle |
| **T3** Live UJ / H6 | SKIPPED | Deferred with deploy stages |

\*Recorded under 09-qa connectivity as well.

## T0 — commands

```bash
# Servers must be up first (Playwright webServer url probe flaky on localhost vs 127.0.0.1)
./start-dev-servers.sh --kill
# then:
cd apps/e2e && METAR_CONFIG_ENV=local \
  PLAYWRIGHT_BASE_URL=http://127.0.0.1:18000 \
  PLAYWRIGHT_API_BASE_URL=http://127.0.0.1:18001 \
  pnpm exec playwright test \
    auth-service-integration.e2e.spec.ts \
    tac-file-conversion.e2e.spec.ts
```

## T0 — results (`make test-e2e-playwright-smoke` equivalent)

| Spec | Result |
|------|--------|
| auth-service-integration (4) | PASS |
| tac-file-conversion — manual METAR | PASS |
| tac-file-conversion — COR METAR → CORRECTION | **FAIL** |
| tac-file-conversion — ICAO COR-after-time → CORRECTION | **FAIL** |
| tac-file-conversion — clear / mocked paths (6) | PASS |

**Totals: 10 passed, 2 failed**

### Failure detail

Both failures: locator `pre` with `/iwxxm|metar:/i` not visible after convert — expected XML with `reportStatus="CORRECTION"`.

Related: unit suite marks BUG-594 COR-after-time as **xfail**; post–gifts cutover tac2iwxxm may not emit CORRECTION the same way. Escalate to 11-verify-impl / optional hotfix.

### Infra note

Playwright `webServer` waiting on `http://localhost:18000` timed out twice even when curl returned 200. Workaround: start stack manually + `PLAYWRIGHT_BASE_URL=http://127.0.0.1:18000` (reuseExistingServer).

## Overall

**FAIL** (blocking for full 10 green) — 2 COR e2e assertions. Non-COR smoke and auth integration green.

Hand to **11-verify-impl**: waive COR e2e until COR plugin parity, or open hotfix.
