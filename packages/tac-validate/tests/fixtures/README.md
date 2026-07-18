# tac-validate fixture pack (F12 / TC-F12-001 / T2.1)

Synthetic **negative** TAC and thin **accept** copies for the seven F6 products.

## Provenance

- Accept TAC: copied from `packages/tac2iwxxm/tests/fixtures/product_matrix/`
  (themselves trimmed from vendored WMO examples or annex3 goldens).
- Negative TAC: **synthetic minimal** strings designed to trip checklist gates.
  Rule `code` values cite paraphrase tables in
  [`docs/domain/TAC_VALIDATION.md`](../../../../docs/domain/TAC_VALIDATION.md)
  (A3-2, A5-1, A6, A2-1, A2-2). **Do not** paste paywalled Annex 3 / FMH prose
  into fixtures or wheels (E10-21).

## Depth (E10-21)

| Product                     | Fixture intent                                    |
| --------------------------- | ------------------------------------------------- |
| METAR / SPECI / TAF         | Full checklist negatives (group presence / shape) |
| SIGMET / AIRMET / VAA / TCA | Template + gate negatives only                    |

## Expectation contract

`manifest.json` cases list `expected_codes` (error severity unless noted).
Diagnostics assertions are `xfail(strict=True)` until T2.2 encodes
`check_product_rules`.
