# E2E Behavior Report — S063 / EV-054

> Generated: 2026-08-10  
> Mechanism: Playwright (local Chromium) + API unit coverage  
> Tip: `be9e3b07`  
> Corpus: [Corpus: journeys §UJ-056] [Corpus: tests] [Corpus: product §F7]

## Summary

| Tier | Scope | Result |
|------|-------|--------|
| T0 local | UJ-056 / TC-EV054-007 Playwright | **PASS** (1/1) |
| T1 integration | `tests/integration` | 10 skipped (no live stack) — exit 0 |
| T2 connectivity | H4–H5 staging | **DEFERRED** → 12/13 |
| T3 live browser | Staging / prod | **DEFERRED** → 13 / 15 |

**Overall (local E2E for EV-054):** PASS

## Journey matrix (delta)

| Journey | Feature | Mechanism | T0 | T2 | Notes |
|---------|---------|-----------|----|----|-------|
| UJ-056 Quality metrics tab | F7 deepen / F7.q | Playwright `uj056-quality-metrics.e2e.spec.ts` | PASS | pending | open tab → filter METAR → passer detail + deferred gap label |

## Execution

```bash
# Same-shell FE :18000 + API :18001, then:
cd apps/e2e && \
  METAR_CONFIG_ENV=local \
  PLAYWRIGHT_SKIP_WEBSERVER=1 \
  PLAYWRIGHT_SKIP_LOCAL_HEALTH_WAIT=1 \
  PLAYWRIGHT_BASE_URL=http://127.0.0.1:18000 \
  PLAYWRIGHT_API_BASE_URL=http://127.0.0.1:18001 \
  pnpm exec playwright test uj056-quality-metrics.e2e.spec.ts --reporter=list
# → 1 passed (887ms)
```

API path confirmed in local stack logs: `quality_metrics` router included; list/detail served for UJ-056.

## AC6 note

Local Playwright satisfies AC6 smoke for #836. Live **H4–H5** remains stages **12/13** after PR → `stage`.

## Exit

→ **11-verify-impl** (collect with `qa-report.md`)
