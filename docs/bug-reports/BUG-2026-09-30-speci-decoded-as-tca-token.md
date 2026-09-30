# BUG-2026-09-30 — SPECI explained as a wall of TCA tokens

| Field | Value |
| --- | --- |
| **Status** | fixed |
| **Feature** | F9 live decode |
| **Severity** | medium (wrong plain-language decode; conversion itself is unchanged) |
| **Classification** | decode product selection |

## Error description

A SPECI pasted while the form product is TCA is explained as
`TCA (partial decode)` and every group, including `SPECI`, is labeled `TCA token`.

## Error logs

```
TCA (partial decode): TCA token; TCA token; TCA token; ...
SPECI    TCA token
YUDO     TCA token
151115Z  TCA token
```

Report:

```
SPECI YUDO 151115Z 05025G37KT 3000 1200NE +TSRA BKN005CB 25/22 Q1008 TEMPO TL1200 0600 BECMG AT1200 8000 NSW NSC=
```

## Investigation

| When | Finding |
| --- | --- |
| 2026-09-30 | Live decode sends the selected product. Auto-detect would have chosen SPECI. |
| 2026-09-30 | `decode_tac` trusted that product. TCA has no METAR/SPECI grammar, so the glossary fallback was `{product} token`. |
| 2026-09-30 | The summary joined those identical clauses under `TCA (partial decode)`. |

## Repro test

`tests/bugs/test_bug_2026_09_30_speci_decoded_as_tca_token.py` failed on `result.product == "SPECI"` before the fix and passes after it.

## Fix

When the report's first word is a supported product keyword, decode as that product. Unknown groups say `Unrecognized group`, and the summary drops a repeated clause. Decode sentences no longer use label dashes.
