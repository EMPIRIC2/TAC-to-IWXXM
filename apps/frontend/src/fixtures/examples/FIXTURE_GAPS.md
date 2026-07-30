# Golden examples — fixture gaps (F7.g / #780 / F25–F27)

Per E16-8 / E16-13 / S02.M2: use in-repo WMO-passer package goldens only; do **not** invent TAC.

| Product | TAC examples in catalog              | Gap                           |
| ------- | ------------------------------------ | ----------------------------- |
| METAR   | 1 (`annex3_golden/metar_a3_1.tac`)   | Second WMO METAR deferred     |
| SPECI   | 1 (`annex3_golden/speci_a3_2.tac`)   | Second WMO SPECI deferred     |
| TAF     | 2 (`taf_a5_1` + `taf_a5_2`)          | none                          |
| SIGMET  | 2 (A6-1a-TS + A6-1b-CNL)             | none                          |
| AIRMET  | 1 (`airmet_a6_1a_ts`)                | CNL peer deferred             |
| **VAA** | **1** (`annex3_golden/vaa_a7_2.tac`) | Second WMO VAA deferred (F26) |
| **TCA** | **1** (`annex3_golden/tca_a2_2.tac`) | Second WMO TCA deferred (F27) |

`vaa_basic` / `tca_basic` product_matrix demos are **hidden** once WMO passers unlock (E21-3 / S02.M2).

Also required (present):

- ≥1 AHL bulletin (`metar_multi_ahl.txt`)
- ≥1 happy-path IWXXM (`annex3_golden/metar_basic.golden.xml` → `collect_iwxxm`)

## Adding a golden

1. Prefer a fixture already under `packages/tac2iwxxm/tests/fixtures/`.
2. Copy the file into `apps/frontend/src/fixtures/examples/bodies/`.
3. Register it in `examplesCatalog.ts` with `provenance` pointing at the package path and `wmoPass` / `wmoSeed` when it is a WMO default golden.
4. If a product reaches ≥2 TAC examples, remove its row from `FIXTURE_GAPS` in the catalog module and this table.
