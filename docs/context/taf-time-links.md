# Context: TAF forecast time links

**Session:** `EV-1408-taf-time-links`
**Date:** 2026-10-15
**Mode:** standard evolve
**Ticket:** [#1408](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1408)
**Corpus:** [Corpus: product §F6] [Corpus: api] [Corpus: tests §TC-F6-051]

## Goal

Each TAF forecast time points at an id in the same document. The operator issue catalog lists `OUTPUT_VALIDATION_WARNING`. A failed TAF preview uses a nil base forecast.

## Out of scope

- Continuation lines
- `PROB30` / `PROB40` `TEMPO` indicator choice
- Operator UI
- Other epic children

## Locked decision

The base forecast phenomenon time was a fragment for a placeholder id that was not in the document. It now links to `#t.valid`, the valid period already written in the document. Change groups keep an inline time period with its own id.

A failed TAF soft-preview shell used `observation`, the METAR body element. It now uses `baseForecast` with a nil reason.

## Checks

- A one-line `VRB` TAF has no broken internal time link
- A one-line `PROB40 TEMPO` TAF has no broken internal time link
- The catalog row for `OUTPUT_VALIDATION_WARNING` is plain language
- A failed TAF preview does not emit an observation element
