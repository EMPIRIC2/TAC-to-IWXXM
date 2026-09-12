# Verification Report — S071 / EV-061 M5 (#1014)

> Generated: 2026-08-20  
> Scope: 07-build M5 Lint & validation catalog tab  
> Branch: `evolve/EV-061-pre-promote-ux-catalog`  
> Corpus: [Corpus: product §F7] [Corpus: product §F15] [Corpus: journeys §UJ-068]
> [Corpus: api] [Corpus: tests §TC-EV061-1014]

## Summary

| Check | Status | Findings | Auto-Fixed | Tool |
|-------|--------|----------|------------|------|
| Lint | PASS | Catalog API + FE page | no | `ruff check` / eslint |
| Format | PASS | Prettier + ruff format | no | `make validate-fast` |
| Typecheck (delta) | PASS | FE + basedpyright | no | `tsc` / basedpyright |
| Tests (delta) | PASS | TC-EV061-1014-001..004 + F15 catalog + EV-048 OpenAPI | no | pytest / vitest |
| Tests (frontend catalog+App) | PASS | 11 passed | no | vitest |
| H0c CORS | PASS | `tests/unit/test_cors_policy.py` 6 passed | no | pytest `--no-cov` |
| H0i | PASS | 10 passed in `test_h0i_connectivity.py` | no | pytest `--no-cov` |
| Security | N/A | No new deps | — | — |
| Template | N/A | No new deployable | — | — |

## M5 acceptance

- Top-level **Lint & validation catalog** shell tab opens a dedicated page (not only the workbench panel).
- `GET /api/v1/lint-issue-catalog` returns TAC lint rows (`family=lint`) and IWXXM validation rows (`family=iwxxm`) with additive `source_type` / `status` / related fields; optional `family` query filter.
- Operator `source_url` for `status=verified` are HTTP landings (not `codes.wmo.int/49-2*` semantic paths).
- OpenAPI + FE types refreshed; EV-048 OpenAPI guard green; catalog page copy free of planning ids.

## Next

08-verify-build M5 PASS. Push M5 commits onto [#1016](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/1016) (same evolve branch → `stage`). Then 07-build **M6 #1015** (stricter stage→main gate). Promote held until #1015.
