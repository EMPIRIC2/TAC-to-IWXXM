# Context: SIGMET body

**Session:** `EV-1410-sigmet-body`
**Date:** 2026-10-15
**Mode:** micro evolve
**Ticket:** [#1410](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1410)
**Corpus:** [Corpus: product §F6] [Corpus: tests §TC-F6-052]

## Goal

A SIGMET body normalizer sits in front of the encoder that already keeps tops, movement, intensity, and a bare cancellation. It unwraps coordinates, keeps the flight information region name, accepts a compound direction, and ignores a remark on a cancellation.

## Out of scope

- Operator pages
- The 2012 year bug
- Tops, speed, and intensity on the simple one-line sample
- A bare cancellation with no remark

## Locked decision

`W-NW` is 292.5 degrees, the shorter arc between west and northwest. The region name is the words in front of `FIR`, not the aerodrome indicator of the meteorological watch office. A `RMK` token on a cancellation is not phenomenon text. Volcanic-ash location lists stay limited to ash, so an ordinary thunderstorm still uses the existing tops and movement encoder.
