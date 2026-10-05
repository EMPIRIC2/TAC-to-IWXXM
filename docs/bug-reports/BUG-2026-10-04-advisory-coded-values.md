# BUG-2026-10-04 — Advisory decode leaves coded values

## Error description

On a tropical cyclone advisory, the decode names each line and then repeats the code. `22MPS`, `NW 20KMH`, and `WI 250NM OF TC CENTRE TOP FL500` stay as written. Selecting a line highlights from the label through the padding, and the title `TC` is a second chip beside the cyclone name.

## Error logs

```text
Maximum wind: 22MPS
Movement: NW 20KMH
Cumulonimbus extent: WI 250NM OF TC CENTRE TOP FL500
```

| Field | Value |
|-------|--------|
| Surface | Convert, live decode |
| Product | TCA, and the same pattern on VAA, SWXA, and VONA |
| Observed | 2026-10-04 |

## Investigation

1. Field explanations were `"{label}: {raw value}"`.
2. The highlight span started at the label, so it covered the label and the blank columns.
3. Title tokens `TC` and `ADVISORY` were extra chips because they sit before the first field.

## Repro test

`packages/tac-decoding/tests/test_hf_advisory_plain.py`

`tests/bugs/test_bug_2026_10_04_advisory_coded_values.py`

## Fix

Advisory values are read in plain language, the highlight sits on the value, and the title chips are not repeated once fields are present. [Corpus: product §F9]
