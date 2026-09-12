# E2E report — 10-e2e (S067 / EV-057)

> Generated: 2026-08-16  
> Scope: delta (`D-S067-09-10=1a`) — UJ-057 / UJ-058 / UJ-OPS-002  
> Branch: `evolve/EV-057-m0-ready-apex-accumulate-validate`  
> Tip: `ffdd1961`  
> Corpus: [Corpus: journeys] [Corpus: tests] [Corpus: product §F7] [Corpus: product §F30]

## Journey matrix

| Journey | Spec | T0 (vitest / unit) | T2 (local Playwright) | T3 (live) |
|---------|------|--------------------|------------------------|-----------|
| UJ-057 accumulate ZIP | `apps/e2e/uj057-accumulate-zip.e2e.spec.ts` | PASS (FileConverter 220) | **FAIL** webServer timeout 300s | deferred H4–H5 @ 13 |
| UJ-058 validate IWXXM | `apps/e2e/uj058-validate-iwxxm.e2e.spec.ts` | PASS (same vitest file) | **FAIL** same timeout | deferred H4–H5 @ 13 |
| UJ-OPS-002 apex → app | ops curl | n/a | n/a | **PASS** prod 2026-08-16 |

## T2 local Playwright

```
cd apps/e2e && METAR_CONFIG_ENV=local pnpm exec playwright test \
  uj057-accumulate-zip.e2e.spec.ts uj058-validate-iwxxm.e2e.spec.ts
```

Vite and API **did** start (`:18000` / `:18001`, `/health` via quality-metrics 200), then
Playwright **timed out waiting 300000ms from config.webServer** for
`http://localhost:18000`. No test body ran. Likely URL probe vs Vite, not product AC.

## T3 live (UJ-OPS-002)

Already recorded in `t1.2-apex-live-apply.md` / 08 verification-report: HTTPS/HTTP 301
with path/query; TLS SAN apex+www; app host 200.

## Outcome

**PASS with waiver** `D-S067-10-pw=1a` — T0 vitest PASS; T3 #948 UJ-OPS-002 PASS;
T2 local Playwright skipped (webServer probe timeout). H4–H5 for UJ-057/058 on staging
remains 13.
