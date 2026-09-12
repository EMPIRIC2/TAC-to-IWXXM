---
slug: metar-remarks-667
topic: "Handle Remark Portion of METARs (#667)"
status: active
created: 2026-07-20
session_id: S018-metar-remarks-667
evolve_cycle_id: EV-013
linked_features: [F6]
---

# Context — metar-remarks-667

## Baseline (2026-07-20)

| Profile | RMK behavior before EV-013 |
|---------|----------------------------|
| `iwxxm_us` | AO2 / SLP / PK WND → Addendum / peak-wind; malformed → `MALFORMED_REMARKS` |
| `annex3` | **Silent drop** — no issue, no XML |
| Unparsed (plain language, T…, P…) | Dropped from XML even on `iwxxm_us` |

## Target (E13-1)

1. `annex3` + `RMK` → `ConvertIssue(code=REMARKS_EXCLUDED, severity=info)` (convert still `ok`)
2. `iwxxm_us` → keep structured emit; leftover RMK tokens → `iwxxm-us:humanReadableText`
3. Parse `T########` / `P####` into IR; retain in free-text until structured codec lands (no invented NWS URIs)

## Refs

- Issue #667
- `[Corpus: product]` F6; domain `IWXXM_CONVERSION.md` US REMARKS keep-list
- Schema: Addendum.humanReadableText / Remarks.freeText
