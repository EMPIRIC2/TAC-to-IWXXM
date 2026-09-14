# EV-970 S3 — validate fill + sticky Product hygiene

[Corpus: product §F29] [Corpus: product §F7.q] [Corpus: tests §TC-F29]
[Corpus: tests §TC-EV052] [Corpus: decisions]

| Date | Decision |
|------|----------|
| 2026-09-14 | S3 targets remaining `validate/metar_speci` `needs-fixture` (~859 baseline); convert/lint already cleared (S1/S2) |
| 2026-09-14 | Ambition = **material reduction** + tracked residual / intentional `oos` cites — not near-zero in one PR |
| 2026-09-14 | Sticky vs Quality metrics dashboard: **clarify + normalize** — keep separate pipelines; do **not** drive sticky from `corpus_metrics.json` this cycle |
| 2026-09-14 | Sticky Product column: allowlist canonical products; junk `meta.product` (`XYZ`, `???`, `BOGUS`, `UNKNOWN`, `NOT_A_PRODUCT`, …) rolls to pack parent (`metar_speci` → `METAR`) |
| 2026-09-14 | Sticky markdown must label Match as ready inventory + golden live outcomes (not dashboard `match_pass`) |
| 2026-09-14 | Happy + edge_pass: convert-then-validate smoke; sad/edge_fail initially `oos` (SCH deferred) |
| 2026-09-14 | CI: PR smoke subset; full matrix nightly; no network/Supabase in matrix |
| 2026-09-14 | Session: `EV-970-metar-validate-fixtures`; ticket [#970](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/970) |
| 2026-09-14 | **Amend:** Schematron negatives are **in-scope**. Filling blocked until validate stack can fail-closed on WMO 2025-2 SCH (S3b) |

## Baseline (pre-S3 fill, 2026-09-14)

| Engine pack | needs-fixture | ready | oos |
|-------------|--------------:|------:|----:|
| convert/metar_speci | 0 | 273 | 47 |
| lint/metar_speci | 0 | 720 | 0 |
| validate/metar_speci | ~859 | 1 | 0 |

## Counts after S3 smoke fill

| Status | validate/metar_speci |
|--------|---------------------:|
| ready | 430 |
| needs-fixture | 0 |
| oos | 430 |

Happy + edge_pass: convert-then-validate smoke (`scripts/ci/fill_ev970_s3_validate_matrix.py`).
Sad + edge_fail: initially `oos` until S3b.

## S3b — SCH negatives in-scope (unblocked)

| Date | Decision |
|------|----------|
| 2026-09-14 | Native Schematron: remap WMO `dsdl` → xmloxide `dml` NS; rewrite XPath2 `if/then/else`; soft `SCHEMATRON_XPATH_UNSUPPORTED` for residual XPath2 |
| 2026-09-14 | F29 validate runners use `validate_iwxxm` (native); `sch_ids` match message prefix |
| 2026-09-14 | Loaders: ready validate cases may use `meta.xml` without TAC |
| 2026-09-14 | Filled **110** probed SCH negatives (11 rules × 10); **320** residual oos (codelist/`document()`/`index-of`) |

### Counts after S3b

| Status | validate/metar_speci |
|--------|---------------------:|
| ready | 540 |
| needs-fixture | 0 |
| oos | 320 |

Scripts: `fill_ev970_s3b_sch_negatives.py`. Probe tests: `test_tc_ev970_s3b_schematron_dsdl.py`.

## S3c — residual oos Batch A (hybrid)

| Date | Decision |
|------|----------|
| 2026-09-14 | Continue EV-970 as S3c; hybrid Batch A native mutations → Batch B document()/index-of |
| 2026-09-14 | Native: XPath2 word comparisons rewrite with XML entities (`lt`→`&lt;`) |
| 2026-09-14 | Batch A filled **160** more SCH negatives (16 rules); residual **160** oos (16 rules) for Batch B |

### Counts after S3c Batch A

| Status | validate/metar_speci |
|--------|---------------------:|
| ready | 700 |
| needs-fixture | 0 |
| oos | 160 |
| SCH negatives (sad/edge_fail ready) | 270 |

Script: `scripts/ci/fill_ev970_s3c_sch_oos.py`.

### Batch B residual rules (document / index-of / harder)

Present/recent weather + seaState codelist `document()`; SurfaceWind-1/6/7; Observation-2;
ObservationReport-2/3/4/6/9; TrendForecast.weather; SeaSurfaceState.

## S3c Batch B (2026-09-14)

| Date | Decision |
|------|----------|
| 2026-09-14 | Native: Observation-2 XPath1 stand-in; `number(text())` rewrite; **no** `document()` stand-in (xmloxide does not expose namespaced `xlink:href` safely) |
| 2026-09-14 | Mutations: Wind `kt` (not `[kn_i]`), Wind-1 both extremes, Report-2/3/4/6 structural |
| 2026-09-14 | Batch B filled **80** more SCH negatives (8 rules); residual **80** oos (8 rules: RDF `document()` + Report-9 `index-of`) |
| 2026-09-14 | F29 runners: match codelist assert text to `sch_ids` when pattern id is omitted from WMO message |

### Counts after S3c Batch B

| Status | validate/metar_speci |
|--------|---------------------:|
| ready | 780 |
| needs-fixture | 0 |
| oos | 80 |
| SCH negatives (sad/edge_fail ready) | 350 |

### Batch B leftover oos (document / index-of)

Present/recent weather + seaState + SeaSurfaceState + TrendForecast.weather (`document()`);
ObservationReport-9 (`index-of`).

## S3c Batch B2 (2026-09-14) — clear residual 80 oos

| Date | Decision |
|------|----------|
| 2026-09-14 | Mirror `xlink:href` → unprefixed `href` before Schematron parse so XPath1 can see codelist URIs |
| 2026-09-14 | `document()` stand-in: `starts-with(@href,'http://codes.wmo.int/') or boolean(@nilReason)` |
| 2026-09-14 | Report-9 stand-in: every ARP `gml:pos` must have ancestor with `srsName` + `srsDimension='2'` + `axisLabels` |
| 2026-09-14 | Aggressive METAR_SPECI XPath1 stand-ins apply **only** for IWXXM **2025-2** Schematron paths so CA_ECCC 3.0.0 national uoms / partial translationCentre* remain soft |

### Counts after S3c Batch B2

| Status | validate/metar_speci |
|--------|---------------------:|
| ready | 860 |
| needs-fixture | 0 |
| oos | 0 |
| SCH negatives (sad/edge_fail ready) | 430 |

## Sticky junk Product repro

`UNKNOWN_PRODUCT.yml` sad/edge_fail `meta.product` values appeared as Product rows in the
EV-052 sticky table. Fix: collector allowlist / pack-parent rollup.
