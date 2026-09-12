# E2E Report — S024 / EV-018 (F16 multi-select / UJ-027–030 / #785)

> Generated: 2026-07-28  
> Scope: Dissemination drawer multi-file selection + interleaved Disseminate + progress  
> Branch: `evolve/EV-018-dissemination-file-select` @ `bf90a02`  
> Mode: evolve delta (10-e2e) · Lean+build  
> Mechanism: Playwright (local stack on `:18000` / `:18001`)

## Journey matrix

| Journey / TC | Mechanism | T0 | T2 connectivity | T3 browser |
|--------------|-----------|----|-----------------|------------|
| UJ-027 multi-DB BYOC + retry | Playwright `uj027-030` | **PASS** | **PASS** (13) | **PASS** (13) |
| UJ-027 drag-drop TAC (TC-F16-004) | Playwright | **PASS** | **PASS** | **PASS** |
| UJ-027 multi-select + continue-on-fail + screenshot (TC-F16-005) | Playwright | **PASS** | **PASS** | **PASS** |
| UJ-027 SSRF/allowlist smoke (TC-F16-002) | Playwright | **PASS** | **PASS** | **PASS** |
| UJ-028 WIS2 BYOC params | Playwright | **PASS** | **PASS** | **PASS** |
| UJ-029 EDIS BYOC (mocked; live cycle-close) | Playwright | **PASS** | **PASS** | **PASS** |
| UJ-030 AMHS / SWIM / AFS | Playwright | **PASS** | **PASS** | **PASS** |

## Results

| Suite | Tests | Status |
|-------|-------|--------|
| Playwright UJ-027–030 | **7** passed (31.2s) | **PASS** |
| Progress screenshot baseline | written + re-verified | **PASS** |

Baseline path:

`apps/e2e/uj027-030-dissemination-drawer.e2e.spec.ts-snapshots/dissemination-progress-multi-partial-fail-chromium-darwin.png`

### Playwright command (working)

```bash
# Prefer 127.0.0.1 — localhost (IPv6) can time out webServer health on this host
cd apps/e2e && \
  METAR_CONFIG_ENV=local \
  PLAYWRIGHT_BASE_URL=http://127.0.0.1:18000 \
  PLAYWRIGHT_API_BASE_URL=http://127.0.0.1:18001 \
  pnpm exec playwright test uj027-030-dissemination-drawer.e2e.spec.ts --update-snapshots
# 7 passed (31.2s); snapshot written on first run
```

Re-verify without `--update-snapshots`: screenshot test **PASS**.

### Pitfall

First attempt with default `PLAYWRIGHT_BASE_URL=http://localhost:18000` timed out waiting for `config.webServer` (300s) even though Vite/API logged ready — use **`127.0.0.1`**.

## Connectivity columns

| Column | Status |
|--------|--------|
| T0 local browser (mocked dissemination APIs) | **PASS** |
| T2 H4–H5 / H6′ live | **PASS** — 13-deploy-smoke (2026-07-29); H4–H5 + UJ-027–030 7/7 vs live FE |
| T3 live browser UJ | **PASS** — same H6′ suite (stubbed BYOC) |

**Overall T0: PASS** · **Overall T2/T3 (13): PASS**

## Next

- Cycle close / evolve summary
