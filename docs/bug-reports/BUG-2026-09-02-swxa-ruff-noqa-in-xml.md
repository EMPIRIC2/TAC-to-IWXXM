# BUG-2026-09-02-swxa-ruff-noqa-in-xml

## Error description

SWXA annex3 convert for `swxa_a7_3` failed the quality PR sticky comment
(Fail=1): emitted XML contained the literal text `# ruff: noqa: F403, F405`
inside `aixm:horizontalProjection` for circle geometries (NIGHTSIDE / DAYSIDE).

## Error logs

```
FAIL mismatch SWXA swxa_a7_3
got horizontalProjection text: '# ruff: noqa: F403, F405'
```

## Investigation

A `# ruff: noqa: F403, F405` line was accidentally placed **inside** an f-string
XML template in `profiles/annex3_emit/swxa.py` `_swxa_region_xml` (circle branch).
Module-level noqa already exists at top of file.

## Repro test

`tests/bugs/test_bug_2026_09_02_swxa_ruff_noqa_in_xml.py`

## Fix

Remove the inline noqa from the f-string template.
