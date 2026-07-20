# E2E report — S016 / EV-012 (10-e2e)

**Date**: 2026-07-20  
**Journey**: UJ-025 / TC-F7-007 Manual TAC Input modes  
**Branch**: `evolve/EV-012-manual-tac-input-modes`

## Results

| Tier | Scope | Result |
|------|-------|--------|
| T0 Vitest | `inputKind.test.ts`, `api.test.ts` (bulletin/501), `FileConverter.test.tsx` | **PASS** (139 tests in those files) |
| T2 Playwright | `apps/e2e/f7-manual-tac-input-modes.e2e.spec.ts` T1–T6 | **PASS** (6/6) |
| T2 connectivity | H4–H5 | Deferred to **13-deploy-smoke** |
| T3 live / H6′ | Staging workbench | Deferred to **13-deploy-smoke** |

## Matrix

| Case | Status | Notes |
|------|--------|-------|
| T1 TAC + Auto-detect | PASS | `/convert` only |
| T2 AHL bulletin | PASS | `/convert-bulletin` + `bulletin-summary` |
| T3 auto-switch | PASS | Toast + mode; convert-time toast added |
| T4 COLLECT 501 | PASS | `placeholder-notice` + warning toast |
| T5 `.gz` COLLECT | PASS | Fix: classify after inflate via displayName |
| T6 read-only modes | PASS | Finished session disables mode buttons |

## Code deltas (lean 10)

1. `FileConverter.tsx` — toast on convert-time AHL/COLLECT auto-switch; gzip classify after decompress
2. `f7-manual-tac-input-modes.e2e.spec.ts` — new Playwright suite
3. README E2E badge 43 → 49

## Gaps

- H7 (`make test-live-bulletin` / UJ-011) unchanged — API gate, not replaced
- Live staging AHL + COLLECT 501 → stage **13**
