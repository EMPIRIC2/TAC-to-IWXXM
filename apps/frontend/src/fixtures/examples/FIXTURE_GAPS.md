# Golden examples — fixture gaps (F7.g / #780)

Per E16-8 / E16-13: use in-repo package goldens only; do **not** invent TAC.

| Product | TAC examples in catalog                | Gap                          |
| ------- | -------------------------------------- | ---------------------------- |
| METAR   | ≥2 (annex3 + iwxxm_us)                 | none                         |
| SPECI   | ≥2 (annex3 + iwxxm_us)                 | none                         |
| TAF     | ≥2 (annex3)                            | none                         |
| SIGMET  | 2 (product_matrix + iwxxm_us)          | none                         |
| AIRMET  | 2 (product_matrix + iwxxm_us)          | none                         |
| **VAA** | **1** (`product_matrix/vaa_basic.tac`) | Second in-repo golden absent |
| **TCA** | **1** (`product_matrix/tca_basic.tac`) | Second in-repo golden absent |

Also required (present):

- ≥1 AHL bulletin (`metar_multi_ahl.txt`)
- ≥1 happy-path IWXXM (`annex3_golden/metar_basic.golden.xml` → `collect_iwxxm`)

## Adding a golden

1. Prefer a fixture already under `packages/tac2iwxxm/tests/fixtures/`.
2. Copy the file into `apps/frontend/src/fixtures/examples/bodies/`.
3. Register it in `examplesCatalog.ts` with `provenance` pointing at the package path.
4. If a product reaches ≥2 TAC examples, remove its row from `FIXTURE_GAPS` in the catalog module and this table.
