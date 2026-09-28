# Operational TAC the current profiles do and do not cover

Session: EV-1266-operational-tac-delta. Ticket: #1266. Scale: standard. Gate: closed.

[Corpus: product §F6] [Corpus: product §F15] [Corpus: domain-profiles] [Corpus: tests]

UI reference: N/A. No operator screen in this cycle. The note is from the 2026-09-23 public-bulletin pass, the catalog on `stage`, and the #1267 / #1265 landings.

## Goal

Record which operational TAC the current lint and convert profiles accept, and which formats they still do not cover, after refreshing the original issue text against what #1267 and #1265 already shipped.

## What was checked (2026-09-23)

Public text retrieved that day and run through annex3 lint:

| Product | Sources sampled | Result (that pass) |
|---|---|---|
| International SIGMET | Aviation Weather Center feed | 115 of 119 reports linted clean |
| International AIRMET | NWS raw `WA` gateway (Brussels, Tirana, Brasilia, and others) | Accepted by annex3 lint |
| VAA | Darwin Dukono, Washington Fuego, Montreal test, Anchorage Chikurachki | Accepted by annex3 lint |
| TCA | NHC Odalys and Polo (East Pacific), Fay, Reunion Juluka, Darwin Ex-TC Narelle | Accepted by annex3 lint |
| SWXA | `FNXX` from SWPC, PECASUS, and ACFJ (several marked TEST) | Accepted by annex3 lint |
| VONA | New Zealand Whakaari/White Island, Tuhua/Mayor Island, NZ test bulletin | Accepted by annex3 lint |

Lint, convert, and validate matrices for TAF, SIGMET, AIRMET, VAA, TCA, SWXA, and VONA are filled under `tests/quality_matrices/` and are on `stage` (#1265). The issue text that said those lint matrices were “not committed yet” is stale.

## Profiles that accept the sampled forms

The four legacy Convert aliases stay. They cover the Annex 3 / national paths that matched the 2026-09-23 samples:

| Legacy name | Semantic id | Pin | Products that matched the pass |
|---|---|---|---|
| annex3 | ICAO_2025 | IWXXM 2025-2 | METAR, SPECI, TAF, SIGMET, AIRMET, VAA, TCA, VONA |
| iwxxm_us | US_FAA_NWS | IWXXM 2025-2 and IWXXM-US 3.0 | METAR, SPECI, TAF, SIGMET, AIRMET, TCA, SWXA, VONA, VAA |
| ca_eccc | CA_ECCC | IWXXM-CA 3.0.0 | METAR, SPECI, TAF, AIRMET, SIGMET (TAC path), VAA |
| in_imd | IN_IMD | core IWXXM | METAR, SPECI, TAF, SIGMET, TCA |

HTTP `product=sigmet` stays one wire value. F6 stays Implemented. No new feature id.

## Formats that stayed outside those four (refresh after #1267)

#1267 added selectable profiles for the four formats the 2026-09-23 pass could not route through annex3 / iwxxm_us / ca_eccc / in_imd. The original issue said “no convert profile.” That is no longer true for the catalog ids below. What remains is source and grammar limits, not a missing dropdown row.

| Format | Catalog id | Convert | Lint | Validate | Remaining gap |
|---|---|---|---|---|---|
| US convective SIGMET | `US_NWS_CONVECTIVE_SIGMET` | Yes — existing convective emitter | Yes | Yes (iwxxm_us pin path) | International Annex 3 SIGMET stays on ICAO_2025 when this profile is not selected |
| G-AIRMET | `US_NWS_G_AIRMET` | Refuses until a text bulletin is on file | Refuses | Listed | Public feed is hazard polygons, not TAC |
| US volcano-observatory VONA (Alaska, Hawaii, Cascades) | `US_NWS_VONA` | Refuses until a clean TAC fixture is accepted | Refuses | Listed | NWS raw `WM` samples had spaces replaced with `?` and a truncated body; not fixtures. Annex 3 VONA and the current `iwxxm_us` VONA path stay unchanged |
| Canadian SIGMET (MSC datamart) | `CA_MSC_SIGMET` | Refuses text convert until a TAC source exists | — | Validates published IWXXM 3.0.0 | MSC file has no TAC in the XML. `ca_eccc` keeps its SIGMET TAC path |

Refusal copy lives in `packages/tac2iwxxm` (`_SOURCE_UNAVAILABLE` for `us_nws_g_airmet`, `us_nws_vona`, `ca_msc_sigmet`). Catalog gaps match [docs/domain/profiles/catalog.yaml](../domain/profiles/catalog.yaml).

## Still not covered (no selectable profile today)

- Canadian AIRMET as a separate MSC-only profile beyond `ca_eccc` AIRMET. MSC AIRMET remains on the CA_ECCC path where TAC exists; this delta does not invent a second AIRMET profile.
- Inventing national TAC for G-AIRMET polygons or for MSC SIGMET when only IWXXM is published.
- Alaska/Hawaii VONA until a clean TAC source replaces the corrupted `WM` gateway samples.
- Live operator feeds (#1262–#1264). Those are a later milestone.

## Out of scope

- Building new converter profiles or grammar (done under #1267 where intended; further emitters need their own tickets).
- The live-feed operator tab (#1262, #1263, #1264).
- Reopening METAR/SPECI convert residuals already accepted on #970.
- Claiming full Annex 3 coverage.
- Promoting `stage` to `main`.
- Operator UI, browser end-to-end, and a deploy for this ticket.

## Sources

- https://aviationweather.gov/data/api/
- https://tgftp.nws.noaa.gov/data/raw/
- https://ds.data.jma.go.jp/svd/vaac/data/
- https://dd.weather.gc.ca/

## Success

- This brief is the standing record of the 2026-09-23 pass and the post-#1267 refresh.
- Stale “no convert profile” / “lint matrices not committed” claims are corrected here and in the selectable-profiles brief.
- No product code in this ticket. PR target later: `stage`.
