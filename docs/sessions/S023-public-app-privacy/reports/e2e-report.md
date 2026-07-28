# E2E Report — S023 / EV-017 (F21 / F22 / UJ-001/004/033)

> Generated: 2026-07-28  
> Scope: Public convert, Auth-gone, privacy/GPC, IndexedDB work history  
> Branch: `evolve/EV-017-public-app-privacy` @ `836c1a4`  
> Mode: evolve delta (10-e2e) · parallel with 09-qa  
> Mechanism: Playwright (local webServer) + Vitest + backend unit

## Journey matrix

| Journey / TC | Mechanism | T0 | T2 connectivity | T3 browser |
|--------------|-----------|----|-----------------|------------|
| UJ-001 public convert | Playwright `public-app-f21-f22` | **PASS** | PASS (T7.2) | pending 13 / live smoke |
| TC-F21-auth-gone FE/API | Playwright + pytest | **PASS** | PASS (live `/auth` 404) | pending 13 |
| UJ-033 / TC-F22-001..003 | Playwright | **PASS** | — | pending 13 |
| UJ-004 IndexedDB history | Playwright `metar-work-history` | **PASS** | — | pending 13 |
| Preflight F21 | Playwright `00-preflight` | **PASS** | — | — |
| Privacy + IDB Vitest | Vitest | **PASS** (22) | — | — |
| Backend TC-F21 + abuse | pytest unit | **PASS** (10) | — | — |

## Results

| Suite | Tests | Status |
|-------|-------|--------|
| Playwright F21/F22 + preflight + UJ-004 | **8** passed | PASS |
| Vitest privacy + localWorkSessionStore | **22** passed | PASS |
| `test_tc_f21_auth_gone_unit` + abuse | **10** passed | PASS |

### Playwright command (working)

```bash
cd apps/e2e && \
  METAR_CONFIG_ENV=local \
  PLAYWRIGHT_BASE_URL=http://localhost:18000 \
  PLAYWRIGHT_API_BASE_URL=http://localhost:18001 \
  pnpm exec playwright test \
    public-app-f21-f22.e2e.spec.ts \
    00-preflight.e2e.spec.ts \
    metar-work-history.e2e.spec.ts
# 8 passed (14.2s)
```

### Pitfall (QA-002)

Repo `.env` sets `PLAYWRIGHT_BASE_URL=http://localhost:5173`. Playwright `webServer` serves
the monorepo stack on **`:18000`**. Without overriding `PLAYWRIGHT_BASE_URL`, webServer
health wait times out (first attempt this session). Always pass `:18000` for local T0.

## Connectivity columns

| Column | Status |
|--------|--------|
| T0 in-process / local browser | **PASS** |
| T2 H4–H5 | **PASS** (M7 T7.2 live) |
| T3 live browser UJ | pending — 13-deploy-smoke / optional 15 |

**Overall T0: PASS**

## Fix applied during 10

- `apps/backend/tests/infrastructure/test_coverage_boost.py` — import `verify_supabase_token`
  from `src.utilities.security` (F21 `src.api` export removed). Collect-only green.
