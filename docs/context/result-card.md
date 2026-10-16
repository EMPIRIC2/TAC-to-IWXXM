# Context: convert result card

**Session:** `EV-1411-result-card`
**Date:** 2026-10-16
**Mode:** micro evolve
**Ticket:** [#1411](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1411)
**Corpus:** [Corpus: product §F7] [Corpus: tests]

## Goal

Show one clear convert result. The page title is TAC to IWXXM. The newest result is first. Status is valid, valid with notes, or needs attention. An invalid result says do not publish. Errors and notes stay in separate lists.

## Out of scope

- Converter libraries and backend response changes
- A redesign of session filters, the colour legend, or try-an-example
- Rules catalog work that already shipped
- Defects that already pass on staging: correction indicator, METAR variable wind in knots, wind-direction variation, a clean abbreviated heading, and simple SIGMET tops, movement, and intensity

## Locked decision

Keep the existing convert response. The page reads `errors`, `issues`, `ok`, and the XML text it already receives. Error severity, a failed convert, or XML that is not well-formed is needs attention and must not be published. Info and warnings are notes. A clean result is valid.

## Why

Staging still titles the page METAR-2-IWXXM. Results stack oldest first. Lint codes lead the log, and XML can look publishable when validation failed. Operators need the status first, then the sentences, with the code underneath.

## Checks

- The heading and browser title are TAC to IWXXM
- After two converts, the newest result is first
- An invalid result says do not publish and does not read as Passed
- Errors and notes are separate lists
