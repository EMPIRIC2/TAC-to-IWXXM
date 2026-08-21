# 10-e2e — UJ-056 / TC-EV056 (S066 / EV-056)

**Date**: 2026-08-11  
**Env**: local non-deployed http://127.0.0.1:18000/ + API :18001  
**Result**: **PASS** — 3/3 Playwright

| Test | Result |
|------|--------|
| open tab → filter → detail `/quality/:stem` + back | PASS |
| TC-EV055-007 normalized panes + chips | PASS |
| TC-EV056-005 deep-link `/quality/:stem` | PASS |

**Command**:
```bash
PLAYWRIGHT_BASE_URL=http://127.0.0.1:18000 \
PLAYWRIGHT_API_BASE_URL=http://127.0.0.1:18001 \
PLAYWRIGHT_SKIP_WEBSERVER=1 \
pnpm exec playwright test uj056-quality-metrics.e2e.spec.ts
```

Live H4–H5 → **13-deploy-smoke** after PR → stage.
