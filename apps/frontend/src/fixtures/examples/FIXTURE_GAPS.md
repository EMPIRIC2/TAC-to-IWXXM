# Golden examples — fixture gaps (F7.g / #780 / F25–F28 / EV-024 / EV-029)

Per E16-8 / E16-13 / S02.M2 / **UJ-039** / **UJ-043**: use in-repo WMO official package
goldens only; do **not** invent TAC. Catalog may list **strict passers** (`wmoPass`) and
**WMO reference** samples (`wmoReference`) per ADR-032 amend.

| Product  | TAC examples in catalog                                                         | Gap                                                                                                                                                                                                                                               |
| -------- | ------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| METAR    | 1 (`annex3_golden/metar_a3_1.tac`)                                              | Second WMO METAR — none in vendor pin                                                                                                                                                                                                             |
| SPECI    | 1 (`annex3_golden/speci_a3_2.tac`)                                              | Second WMO SPECI — none in vendor pin                                                                                                                                                                                                             |
| TAF      | 2 (`taf_a5_1` + `taf_a5_2`)                                                     | none                                                                                                                                                                                                                                              |
| SIGMET   | 5 (A6-1a-TS + A6-1b-CNL + VA-EGGX ref + A6-2-TC ref + multi-location-VA passer) | **#829** / EV-030 T2.4: `sigmet-A6-2-TC` unlocked as `wmoReference` (lint→convert→validate green; ADR-032 encode residual → [#835](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/835)); **#809** multi-location-VA `wmoPass` (TC-EV025-008/009) |
| AIRMET   | 1 (`airmet_a6_1a_ts`)                                                           | CNL peer — none in vendor pin                                                                                                                                                                                                                     |
| **VAA**  | **1** (`annex3_golden/vaa_a7_2.tac`)                                            | Second WMO VAA — none in vendor pin                                                                                                                                                                                                               |
| **TCA**  | **1** (`annex3_golden/tca_a2_2.tac`)                                            | Second WMO TCA — none in vendor pin                                                                                                                                                                                                               |
| **SWXA** | **1** (`annex3_golden/swxa_a7_3.tac`, `wmoReference`)                           | A7-4 / A7-5 deferred (single-seed F28 / TC-F28-005)                                                                                                                                                                                               |

### Stem-level deferrals (EV-027 / #815 inventory · EV-029 shape note)

Happy-path sample menu covers all in-scope single-report official peers under pin
`2025-2`. Explicit non-menu stems (package inventory SoT
`packages/tac2iwxxm/tests/fixtures/wmo_official_tac_inventory.py`):

| Stem                                    | Reason                                                                                     |
| --------------------------------------- | ------------------------------------------------------------------------------------------ |
| `sigmet-A6-2-TC`                        | **Unlocked** EV-030 T2.4 as `wmoReference` (`sigmet_a6_2_tc`); equality/`wmoPass` residual |
| `metar-NIL-collect` / `taf-NIL-collect` | COLLECT / validate shape — not sample-menu happy-path (EV-024)                             |
| `*-translation-failed*`                 | quarantine                                                                                 |
| `spacewx-A7-4` / `spacewx-A7-5`         | SWXA second/third peers — deferred (A7-3 unlocked M11 / TC-F28-005)                        |
| `vona-*`                                | OOS converter                                                                              |

**AHL / multi-report shapes (EV-029 / TC-EV029-002):** FE catalogs METAR multi-AHL only
(`ahl_metar_multi`). Non-METAR AHL + multi-report gaps are documented in
[example-inventory.md](../../../../../docs/sessions/S036-eight-family-ahl-rules-823/reports/mining/example-inventory.md)
— fill in M1+ packs; do not invent TAC.

`vaa_basic` / `tca_basic` product_matrix demos are **hidden** once WMO passers unlock (E21-3 / S02.M2).

Also required (present):

- ≥1 AHL bulletin (`metar_multi_ahl.txt`)
- ≥1 happy-path IWXXM (`annex3_golden/metar_basic.golden.xml` → `collect_iwxxm`)

## Adding a golden

1. Prefer a fixture already under `packages/tac2iwxxm/tests/fixtures/`.
2. Copy the file into `apps/frontend/src/fixtures/examples/bodies/`.
3. Register it in `examplesCatalog.ts` with `provenance` pointing at the package path and
   `wmoPass` + `wmoSeed` (strict) or `wmoReference` + `wmoSeed` (official, pre-equality).
4. If a product reaches ≥2 TAC examples, remove its row from `FIXTURE_GAPS` in the catalog
   module and this table (SIGMET already ≥2).
