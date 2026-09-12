# docs-execute report — S007-docs-minimize

**Date:** 2026-07-12  
**Branch:** `docs/S007-docs-minimize`  
**Layout:** conservative (standing specs remain at `docs/` root)

## Result

| Metric | Before | After |
|--------|--------|-------|
| Root `*.md` files | ~42 | **12** standing + **README.md** |
| New folders | — | `decisions/`, `ops/`, `guides/`, `domain/`, `reports/` |
| Merged | `docs/iwxxm/` → `domain/iwxxm/`; `docs/validation/` → `domain/validation/` |

## Moves

| Destination | Files |
|-------------|-------|
| `decisions/` | product/tech/requirements/evolve decisions + audits |
| `ops/` | DEVELOPMENT, env-sync-runbook, staging-secrets-matrix, migration-plan |
| `guides/` | API, ARCHITECTURE, IMPLEMENTATION, Supabase, OpenAIP |
| `domain/iwxxm/` | version/formatting/ICAO/elevation (+ prior `iwxxm/*`) |
| `domain/validation/` | validation domain docs (+ prior `validation/*`) |
| `reports/` | qa / e2e / verification / implementation-verification |
| `testing/` | TESTING_STRATEGY.md |

## Link updates

- Rewrote `docs/<old>` paths under `.cursor/`, `docs/`, root `README.md`, and key `apps/` / `scripts/` READMEs
- Updated `sessions-reference.md`, `pipeline-preamble.md`, `considerations.md` for decision-log locations
- Added [docs/README.md](../../README.md) as the tree index

## Out of scope (deferred)

- Nesting standing specs (`feature-list.md`, `spec.md`, …) — aggressive option
- Deleting ARCHIVE content

## Next

- Optional: open PR + `18-pr-review`
- Commit when user requests
