# Verification Report — S071 / EV-061 M4 (#1013)

> Generated: 2026-08-19  
> Scope: 07-build M4 Product/Profile + param bars  
> Branch: `evolve/EV-061-pre-promote-ux-catalog`  
> Corpus: [Corpus: product §F7] [Corpus: journeys §UJ-066] [Corpus: journeys §UJ-067]
> [Corpus: tests §TC-EV061-1013]

## Summary

| Check | Status | Findings | Auto-Fixed | Tool |
|-------|--------|----------|------------|------|
| Lint | PASS | FileConverter layout only | no | `ruff check` / eslint |
| Format | PASS | Prettier + ruff format | no | `make validate-fast` |
| Typecheck (delta) | PASS | `FileConverter.tsx` 0 errors | no | `tsc --noEmit` |
| Tests (delta) | PASS | TC-EV061-1013-001..003 + related picker/param files (225) | no | vitest |
| Tests (frontend) | PASS | 1121 passed, 4 skipped (112 files) | no | vitest |
| H0c CORS | PASS | `tests/unit/test_cors_policy.py` 6 passed | no | pytest `--no-cov` |
| H0i | PASS | 10 passed in `test_h0i_connectivity.py` | no | pytest `--no-cov` |
| Security | N/A | No new deps | — | — |
| Template | N/A | No new deployable | — | — |

## M4 acceptance

- Product Type + Profile live on `product-profile-bar` with `flex-col` below 1024px and `lg:flex-row lg:flex-nowrap` at ≥1024px; they are not mixed with input-mode buttons.
- Input mode selects live on `input-mode-bar` with the same stack / no-wrap contract.
- Conversion parameters (Bulletin ID, Issuing Center, and expanded fields) share `conversion-params-bar` with the same contract.
- Accessible names unchanged: Product, Profile, Input mode, Expand/Collapse parameters, Bulletin ID, Issuing Center.

## Next

08-verify-build M4 PASS. Push M4 commits onto [#1016](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/1016) (same evolve branch → `stage`). Then 07-build **M5 #1014** (Lint & validation catalog tab). Promote held until #1015.
