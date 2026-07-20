# tac-validate fixture pack (F12 / F15 / TC-F12-001 / TC-F15-003)

Synthetic **negative** TAC and thin **accept** copies for the seven F6 products.
S015 / EV-011 deepens **METAR** and **SPECI** under the F15 issue registry.

## Provenance

- Accept TAC: copied from `packages/tac2iwxxm/tests/fixtures/product_matrix/`
  (themselves trimmed from vendored WMO examples or annex3 goldens).
- Negative TAC: **synthetic minimal** strings designed to trip checklist gates.
  Rule `code` values cite paraphrase tables in
  [`docs/domain/TAC_VALIDATION.md`](../../../../docs/domain/TAC_VALIDATION.md)
  (A3-2, A5-1, A6, A2-1, A2-2). **Do not** paste paywalled Annex 3 / FMH prose
  into fixtures or wheels (E10-21). Prefer short synthetic cases over long
  copied decoder pages (E11-24).

## Layout (F15)

| Path                       | Role                                      |
| -------------------------- | ----------------------------------------- |
| `accept/*.tac`             | Thin accept cases (all products)          |
| `negative/metar/`          | METAR negatives — expand for R1–R8        |
| `negative/speci/`          | SPECI negatives — adjacency + shared pack |
| `negative/{taf,sigmet,…}/` | Other products (template/gate depth)      |
| `manifest.json`            | Cases + `expected_codes`                  |

Convert goldens live under `packages/tac2iwxxm/tests/fixtures/{annex3_golden,iwxxm_us_golden}/`
— do not duplicate full IWXXM XML here.

## Depth

| Product                     | Fixture intent                           |
| --------------------------- | ---------------------------------------- |
| METAR / SPECI               | Full checklist + R1–R8 (HARD this cycle) |
| TAF                         | Full checklist negatives                 |
| SIGMET / AIRMET / VAA / TCA | Template + gate negatives only           |

## Expectation contract

`manifest.json` cases list `expected_codes`. Every code must exist in the
`tac-validate` issue registry after M2 (`docs/domain/rules/ISSUE_CATALOG.md`).
Diagnostics assertions require product-rule codes/spans from
`check_product_rules`.

| Manifest key         | `ok`    | Role                                                        |
| -------------------- | ------- | ----------------------------------------------------------- |
| `accept`             | `true`  | Thin accept / theme accept (R1, R2 SM/9999/meters)          |
| `negative`           | `false` | Error-severity checklist / template gates                   |
| `order_warnings`     | `true`  | Warning-only R1 odd field order (`ODD_FIELD_ORDER`)         |
| `r2_fraction_accept` | `true`  | US SM fractions / M-prefix (encoded in T3.4)                |
| `visibility_errors`  | `false` | R2 malformed visibility (`INVALID_VISIBILITY`)              |
| `weather_errors`     | `false` | R3 malformed present weather (`INVALID_WEATHER`)            |
| `cloud_errors`       | `false` | R4 malformed cloud/VV height/suffix (`INVALID_CLOUD_TOKEN`) |
| `cloud_cb_tcu_info`  | `true`  | R4 CB/TCU convective type (`CLOUD_CB_OR_TCU` info)          |
| `remark_us_info`     | `true`  | R5 known US RMK tokens (`REMARK_US_EXTENSION` info)         |
| `remark_errors`      | `false` | R5 malformed RMK groups (`INVALID_REMARK`)                  |
| `r8_modifier_info`   | `true`  | R8 AUTO/COR/NIL/NOSIG/TEMPO/RVR/VRB·gust info codes         |
| `r8_errors`          | `false` | R8 malformed NIL/RVR/wind (`INVALID_*`)                     |

## Tooling

```bash
make catalog-regen   # refresh ISSUE_CATALOG.md/.json from registry
make catalog-check   # fail if catalog drifts from working tree
```
