# HANDOFF — S021 / EV-016 (F7.g / #780)

**Date**: 2026-07-26  
**Branch**: `evolve/EV-016-golden-examples-ui`  
**Build**: M1–M2 complete (catalog + Examples UX); M3 gate docs

## Deploy notes (FE-only)

- No API routes, env vars, or DB migrations.
- Redeploy **frontend** static site only for 13-deploy-smoke.
- H4–H5 connectivity smoke when FE ships (`make test-live-connectivity`).
- Skip 12-verify-deploy per Lean+build unless checklist forced.

## Verification

| Check           | Command / note                                                                                |
| --------------- | --------------------------------------------------------------------------------------------- |
| TC-F7-008 C1    | `pnpm --filter @metar/frontend exec vitest run src/fixtures/examples/examplesCatalog.test.ts` |
| TC-F7-008 C2–C5 | FileConverter + GoldenExamplesSelect Vitest                                                   |
| Full FE unit    | `pnpm --filter @metar/frontend test`                                                          |

## Gaps

See `apps/frontend/src/fixtures/examples/FIXTURE_GAPS.md` (VAA/TCA 1-fixture).

## Next stages

11-verify-impl **approved** (E16-19) → minor PR → **13-deploy-smoke** (H4–H5).
