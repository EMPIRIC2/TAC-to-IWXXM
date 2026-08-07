# E2E Report — S050 / EV-042 (10-e2e)

> Generated: 2026-08-07  
> Scope: delta — F33 + deepen F7 / F16–F19 (UJ-051..053)  
> Branch: `evolve/EV-042-remove-db-tools-operator-throughput` @ `dff22265`  
> Mechanism: mixed (pytest T0/T1 + Playwright browser UJ)  
> Corpus: [Corpus: journeys §UJ-051..053] [Corpus: tests] [Corpus: product §F7/F16–F19/F33]
> [Corpus: api]

## Tier summary

| Tier | What | Result |
|------|------|--------|
| T0 / unit | TC-F33 guards + auth | **PASS** — 20/20 |
| T1 / H0i | Mass ingest OPTIONS + connectivity | **PASS** — 10/10 |
| H0c CORS | `tests/unit/test_cors_policy.py` | **PASS** — 6/6 |
| T0 browser (local) | `uj051-053-ev042-mass-queue.e2e.spec.ts` | **PASS** — 6/6 |
| T2 live H4–H5 | Deployed CORS + FE `api.baseUrl` | **DEFERRED** → 13-deploy-smoke (QA-001) |
| T3 live UJ | Live Playwright vs prod/staging | **DEFERRED** → 13 / 15 |

## Journey results (local browser)

| # | Journey | Mechanism | Cases | Status |
|---|---------|-----------|-------|--------|
| 1 | UJ-053 / TC-EV042-001 | Playwright | Convert&Send + Disseminate absent; convert remains | PASS |
| 2 | UJ-051 / TC-F33-004 | Playwright | Guest Folder mass ingest prompts sign-in | PASS |
| 3 | UJ-051 / TC-F33-005 | Playwright + HTTP | Unauthenticated `POST /ingest/mass` → 401 | PASS |
| 4 | UJ-051 / TC-F33-001 | Playwright | Signed-in zip mass ingest fills work queue | PASS |
| 5 | UJ-052 / TC-EV042-003 | Playwright | Work queue keyboard + batch convert controls | PASS |
| 6 | UJ-052 companion | Playwright | Fixture TAC still queues via Select Files | PASS |

```text
6 passed (16.1s) — PLAYWRIGHT_BASE_URL=http://localhost:18000 (webServer start-dev-servers.sh)
```

## Commands run

```bash
cd apps/backend && uv run pytest \
  tests/unit/test_tc_f33_mass_ingest_guards.py \
  tests/unit/test_tc_f33_mass_ingest_auth.py \
  tests/integration/test_h0i_connectivity.py -q --no-cov
# → 30 passed

uv run pytest tests/unit/test_cors_policy.py -q --no-cov
# → 6 passed

cd apps/e2e && METAR_CONFIG_ENV=local PLAYWRIGHT_BASE_URL=http://localhost:18000 \
  pnpm exec playwright test uj051-053-ev042-mass-queue.e2e.spec.ts
# → 6 passed
```

## Advisories for 11-verify-impl

| ID | Note |
|----|------|
| E2E-001 | Live H4–H5 / T3 not exercised here — same as QA-001; gate at 13 |
| E2E-002 | Operator UJ-027–030 still skipped until #898 (QA-004) |
| E2E-003 | Prefer `PLAYWRIGHT_BASE_URL=http://localhost:18000` (QA-002) |

## Overall: **PASS** (local T0/T1 + browser UJ); live T2/T3 deferred to 13
