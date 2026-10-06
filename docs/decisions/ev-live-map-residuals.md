# EV-live-map-residuals

[Corpus: product §F9] [Corpus: product §F15] [Corpus: decisions]

## Decision

Explain the ten residual families still left on the live map. Keep the work inside the
existing METAR, SPECI, and SIGMET/AIRMET decoder. Do not add a product id, change the map,
or change IWXXM.

## Why

A sample of the staging map cache (2026-10-05) still left coded groups undecoded after the
southern SIGMET pass and the convective-SIGMET pass. Operators opening those reports see
the leftovers as errors.

## Families

| Family | Live example |
| --- | --- |
| Pressure tendency | `53002` on `METAR CWNH` |
| Precipitation amount / not available | `P0000`, `PNO` |
| Distant weather and remark cumulonimbus | `DSNT`, `CB` |
| Canadian remark clouds | `SF8`, `AC1CI1`, `ST3CU1CI1` |
| Density altitude | `DENSITY ALT 2700FT` |
| Correction group | `SPECI … CCA` |
| Observed and forecast | `OBS/FCST` |
| Short FIR name | `LA PAZ` |
| Convective state list and reference | `LA TX`, `REF INTL SIGMET FOXTROT SERIES` |
| Navaid segment without a distance | `TRV-PBI` |
| Peak wind | `28019/2200` |
| Canadian remark prose | `PCPN VRY LGT`, `DIST SH ALQDS` |
| Longitude glued to a hyphen | `E08046-` |
| Surface to a height in feet | `SFC/6000FT` |
| Radius | `200NM` |
| Tropical cyclone name | `CHOI-WAN`, `NOLO` |
| Delayed report | `RRA` |
| Lake codes on a convective area line | `LO`, `LH`, `LS` |
| Whole miles before a fraction | `1 3/4SM`, `2 1/2` |
| Runway visual range | `R08/////`, `R35R/2600V3000FT` |
| Vertical visibility | `VV002` |
| Weather began or ended | `RAB19`, `TSB33` |
| Remark prose still coded on the sample | `PRESRR`, `PWINO`, `VIRGA`, `LTNG`, `0.8MM` |

## Feasibility

Every family is a token explanation in the existing decoder. No new dependency.
State abbreviations are explained only on the convective area line, before `FROM`, so a
compass point such as `NE` stays a direction everywhere else.

## Out of scope

- New map layers or popup layout.
- IWXXM element changes for these groups.
- Browser connectivity tasks. The decode text is the only operator-visible change.

## Acceptance

Each family has a regression test and a plain-language explanation. A fresh sample of the
same cache no longer lists those tokens as undecoded. Groups that already decode stay decoded.
