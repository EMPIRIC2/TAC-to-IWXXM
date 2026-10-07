# BUG-2026-10-07 empty bulletin when SIGMET omits =

[Corpus: product §F6] [Corpus: api]

## Error description

Convert fails with "No TAC reports found after the abbreviated heading." when the
operator converts a SIGMET (or AIRMET) bulletin from the live map. Those reports
often begin with a WMO abbreviated heading and omit the trailing `=` terminator.

## Error logs

```
Conversion Error
No TAC reports found after the abbreviated heading.
```

HTTP mapping: `empty_bulletin` → 400 with that message (`apps/backend/src/api_wire.py`).

## Investigation

- Convert auto-switches TAC input to AHL bulletin mode when `looksLikeAhlBulletin` is true.
- `split_bulletin(..., product="SIGMET")` uses `_TAC_SIGMET`, which required `.+?=`.
- VAA/TCA/SWXA/VONA already allow `(?:=\s*$|\Z)`.
- Sample without `=` → `empty_bulletin`; same sample with `=` → one report.

## Repro test

`tests/bugs/test_bug_2026_10_07_empty_bulletin_sigmet_no_equals.py`

## Fix

`packages/tac2iwxxm/src/tac2iwxxm/bulletin.py`: `_TAC_SIGMET` and `_TAC_AIRMET` end
with `(?:=\s*$|\Z)` so a single report may omit `=`, matching VAA/TCA/SWXA/VONA.

## Interview record

AskQuestion unavailable. Operator reported Convert failing with the empty-bulletin
message after map-loaded SIGMET work. Proceeded with repro and fix on that basis.

## Prevention & countermeasures

Keep a regression test on AWC-style SIGMET without `=`. Prefer fixture coverage over
manual Convert clicks when map feeds change.
