# 08-verify-build — M4 OpenAPI typed FE client

> Cycle: EV-052 · Session: S061 · 2026-08-09

## Result

**PASS** — T4.1–T4.3 complete; TC-EV052-009 green locally.

## Evidence

| Check | Result |
|-------|--------|
| Snapshot | `apps/frontend/openapi/openapi.json` matches `app.openapi()` |
| Types | `src/generated/openapi.d.ts` via `openapi-typescript` |
| Drift | `pnpm openapi:check` + CI step on frontend matrix |
| FE wire | `openapiTypes.ts` → `api.ts` convert + new `validateIwxxm` |
| Tests | `test_tc_ev052_openapi_snapshot_drift.py` (3); `tc-ev052-009-openapi-types.test.ts` (3); validate unit in `api.test.ts` |
| Typecheck | `pnpm --filter @metar/frontend typecheck` PASS |

## Corpus

[Corpus: product §M5] [Corpus: tests §TC-EV052-009] [Corpus: tech-spec]
