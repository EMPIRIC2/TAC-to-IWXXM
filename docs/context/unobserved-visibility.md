# Context — unobserved visibility

**Session:** `EV-1399-unobserved-visibility`
**Date:** 2026-10-14
**Mode:** micro evolve
**Ticket:** [#1399](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1399)
**Corpus:** [Corpus: product §F6] [Corpus: product §F15] [Corpus: tests] [Corpus: domain]

## Goal

Accept `////` visibility as not observed. Do not count that report as a missing-visibility failure. Do not treat NCD that appears only after `RMK` as a body cloud group.

## Out of scope

- A report that truly omits the visibility group
- The rest of the remarks policy
- Encoding `//////` as a nil cloud layer (documented separately; not in this ticket's acceptance checks)
- Changing the runway-visual-range nil that already accompanies unobserved visibility
- Operator UI
- Other epic children

## Locked decision

Keep the existing nil reason. Change only the lint so `////` and `////SM` count as a visibility group, and so remark-only `NCD` is not a body cloud finding. A word boundary does not match a solidus, so the visibility pattern must use a lookbehind, and it must not treat the first four slashes of `//////` as visibility.

## Why

WMO TAC-to-XML guidance treats a quantity that cannot be reported because of a sensor failure as `xsi:nil="true"` with `http://codes.wmo.int/common/nil/notObservable`. The IWXXM translation suite does that for both forms:

| Fixture | TAC | Visibility encoding |
|---------|-----|---------------------|
| `ENFB-282350Z` | `////` | `nilReason` `notObservable` |
| `CWFD-290000Z` | `////SM` | `nilReason` `notObservable` |

`missing` is the nil reason for a NIL report and for runway visual range when the aerodrome has no sensors and visibility is below 1500 m. It is not the reason for a visibility group that is present as solidi.

`NCD` is a coded cloud group. Guidance maps it to an empty cloud element with `notDetectedByAutoSystem`. That group belongs in the observation body. Free text after `RMK` is not that group.

`//////` is a different token. Guidance maps it to a cloud layer whose amount and base are nil (`notObservable` or `notDetectedByAutoSystem`). The MKJP sample contains it, and convert currently drops it. That encoding is outside the three acceptance checks on #1399.

## Inventory on `stage` at `031e2ef9`

Sample: `METAR MKJP 072300Z 12012KT //// ////// 30/26 Q1013 RMK CLD FROM CEILOMETER RWY 30 NCD=`

| Piece | State |
|-------|--------|
| Convert | Succeeds. Visibility is nil with `notObservable`. |
| Lint | Error `MISSING_VISIBILITY`. Info `NCD_PRESENT` from the remark token. |
| Omitted visibility | Still `MISSING_VISIBILITY`. Keep that. |
| Body `NCD` | Still informational `NCD_PRESENT`, and convert writes `notDetectedByAutoSystem`. Keep that. |
| `////SM` | Convert already uses `notObservable`. Lint does not treat it as a visibility group. |

## Checks still open

- The MKJP sample stays a successful convert with visibility nil and reason `notObservable`
- `MISSING_VISIBILITY` is not raised for `////` or `////SM`
- A report with no visibility group still raises `MISSING_VISIBILITY`
- `NCD` only after `RMK` does not raise `NCD_PRESENT`
- `NCD` in the observation body still raises `NCD_PRESENT`
