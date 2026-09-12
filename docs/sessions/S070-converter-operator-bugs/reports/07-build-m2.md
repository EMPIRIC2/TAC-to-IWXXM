# 07-build M2 — IWXXM product pass-through (#1003 / F7.t)

**Status:** implementation complete; awaiting 08-verify-build  
**Corpus:** [Corpus: product §F7] [Corpus: api] [Corpus: tests §TC-EV060-1003]

## Tasks

| ID | Result |
|----|--------|
| T2.1 | Red→green tests in `test_tc_ev060_1003_iwxxm_product.py` (lint/convert/bulletin + OpenAPI) |
| T2.2 | `_API_PRODUCTS` + `iwxxm_pass_through`; `/lint-tac` + `/convert` (+ bulletin) pass-through; `NOT_XML`; OpenAPI snapshot refresh |
| T2.3 | Product select **IWXXM**; Lint & validate button label; help copy; Convert&Send hidden |
| T2.4 | FileConverter hydrate via `isConvertProductSelection`; convert `product=IWXXM`; accumulate inherits via shared convert path; F7.s Validate mode kept |

## Notes

- No new npm/PyPI deps. Operator copy has no planning ids (`iwxxmProductCopy` in `operatorVisibleCopy`).
- F7.s `validate_iwxxm` input mode unchanged.
- Optional F2 on convert uses `iwxxm_validate_fn` when `validate_output` / schema levels set.
- Quality metrics honor = no new QM chrome; XML validate path unchanged (`D-S070-honor`).
- PR #1007 (M1) remains open; M2 commits stack on the same evolve branch.
