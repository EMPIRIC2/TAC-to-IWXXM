# BUG-2026-10-05-sigmet-highlights

## Error description

A valid southern oceanic SIGMET highlighted unrelated preview lines and showed
`9000FT/FL290` as a TAC error. The polygon was dropped, both vertical limits
became FL290, and a heading such as `WSPSZ1` failed to parse.

## Error logs

```
PARSE_ERROR unable to parse SIGMET header
residual: 9000FT/FL290
lowerLimit/upperLimit both FL 290
geometry: None
```

## Investigation

1. The point pattern accepted only north latitudes, so `S7520 W14200` never
   became a polygon.
2. `FL290` inside `9000FT/FL290` was read as a single flight level.
3. A polygon separator `-` was paired as another meteorological watch office,
   then the preview searched the whole XML for `-`.
4. `WSPSZ1` uses a letter in the bulletin number, so the heading was left on
   the report and the header parse failed.

## Repro test

`tests/bugs/test_bug_2026_10_05_sigmet_highlights.py`

Red before the parser, emitter, decode, lint, and preview-pairing changes.
Green after those changes.
