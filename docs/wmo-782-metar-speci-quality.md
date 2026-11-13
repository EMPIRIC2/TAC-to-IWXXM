# WMO handbook METAR and SPECI quality

> Related: [product-requirements.md](product-requirements.md),
> [domain-contract.md](domain-contract.md), [api-contract.md](api-contract.md),
> [test-plan.md](test-plan.md)
>
> Documentation note: No tool proves ASD-STE100 compliance. A human must review
> this file against Issue 9.

## Purpose

This page states durable product behavior for METAR and SPECI quality checks
drawn from WMO-No. 782 (*Aerodrome Reports and Forecasts*). It does not quote
paywalled handbook prose.

## Operator paths

1. Paste or type TAC on Convert, or use structured METAR/SPECI entry.
2. Live lint and decode run on the workbench text.
3. Convert uses the existing conversion path. Optional control: include national
   remarks in IWXXM (default on).

## Lint families

| Family | What operators should expect |
|--------|------------------------------|
| Identification | Code name, station, time, COR / NIL / AUTO placement |
| Group order | Handbook section order; wrong order is an error |
| Wind | Format, VRB rules, calm, gust threshold, high-speed P forms, variation span |
| Visibility | Reporting steps, directional minimum, AUTO `////`, missing solidus |
| RVR | At most four groups, solidus missingness, steps, tendency U/D/N |
| Weather | Legal combinations, FG/BR bands, SHPL ban, vicinity limits |
| Cloud | Ascending heights, CB/TCU rules, VV exclusivity, NCD with AUTO |
| Temperature / QNH | Dew-point not above air temperature; Q////; Q vs A digit ranges |
| TREND | No PROB; four-digit FM; no V-group; unit match; NOSIG exclusivity |
| Remarks | RMK is national; convert may omit it from IWXXM |

Registry codes and default severities live in `config/rules/ISSUE_CATALOG.json`.

## Tests

Unit tests under `packages/tac-validate/tests/test_wmo_782_*.py` cover emitters.
Optional permutation shards for handbook dimensions may exist on a developer
machine. Those shards are not required for a fresh clone.
