# E2E Behavior Report — 10-e2e (S071 / EV-061)

> Generated: 2026-08-20  
> Mechanism: Playwright Chromium vs local `:18000` / `:18001`  
> Branch: `evolve/EV-061-pre-promote-ux-catalog`  
> Corpus: [Corpus: journeys] [Corpus: tests] [Corpus: product §F7] [Corpus: product §F2]
> [Corpus: product §F6] [Corpus: product §F9] [Corpus: product §F10] [Corpus: product §F15]
> [Corpus: product §F34] [Corpus: api] [Corpus: decisions §EV-061]

## Summary

| Tier | Scope | Result |
|------|-------|--------|
| T0 | EV-061 unit/Vitest (see 09-qa) | PASS |
| T2 local browser + API | UJ-064..068 (`tc-ev061-uj064-068.e2e.spec.ts`) | **6 passed** |
| T2 connectivity H4–H5 | staging frontend | **DEFERRED** → 12/13 |
| T3 live | staging/prod | **DEFERRED** → 13 / 15 |
| UJ-DEV-009 | CI promote gate (#1015) | PASS via TC-EV061-1015 (not browser) |

**Overall (local T2 for EV-061):** **PASS**.

## Journey matrix (delta)

| Journey | Spec | T0 | T2 local | T3 |
|---------|------|----|----------|----|
| UJ-064 Validate decode | `tc-ev061-uj064-068.e2e.spec.ts` + Vitest/backend 1010 | PASS | **PASS** (1) | deferred |
| UJ-065 AHL decode/convert | same + backend/tac2iwxxm 1012 | PASS | **PASS** (2) | deferred |
| UJ-066 Product/Profile bars | same + Vitest 1013 | PASS | **PASS** (2 with UJ-067) | deferred |
| UJ-067 Params bar | same | PASS | **PASS** (shared with 066) | deferred |
| UJ-068 Catalog tab | same + Vitest/backend 1014 | PASS | **PASS** (1) | deferred |
| UJ-DEV-009 Promote gate | `tests/test_tc_ev061_1015_promote_gate.py` | PASS | N/A (CI) | N/A |

## Execution

Started `make dev` (FE `:18000`, API `:18001` `/health` both 200). `METAR_CONFIG_ENV=local`.
`PLAYWRIGHT_SKIP_WEBSERVER=1` with explicit base URLs (avoid QA-001 `:5173` residual).

```bash
cd apps/e2e && \
  METAR_CONFIG_ENV=local \
  PLAYWRIGHT_SKIP_WEBSERVER=1 \
  PLAYWRIGHT_BASE_URL=http://localhost:18000 \
  PLAYWRIGHT_API_BASE_URL=http://localhost:18001 \
  pnpm exec playwright test tc-ev061-uj064-068.e2e.spec.ts
```

Result: **6 passed** (13.2s). First UJ-064 attempt failed on METAR editor label; fixed to
`Enter IWXXM XML manually` (parity with `uj058-validate-iwxxm.e2e.spec.ts`).

## Journey details

### UJ-064 — PASS

Validate IWXXM mode → report panel visible; decode-segments asserted when present (no raw `<?xml` dump).

### UJ-065 — PASS

AHL convert → bulletin summary “2 report”; malformed convert-bulletin → `INVALID_AHL` (422).

### UJ-066 / UJ-067 — PASS

At 1280px: product-profile + conversion-params bars visible; computed `flex-wrap: nowrap`.
At 800px: both bars still visible (stack OK).

### UJ-068 — PASS

Shell catalog tab → list with HTTPS source links; no `codes.wmo.int/49-2`; no planning ids in copy.

## Notes for 11-verify-impl

- Non-deployed UI preview offered at 11 (`D-S071-e2` remind).
- README E2E badge updated to **108**.
- Admin ruleset apply still required before real promote (QA-003).
