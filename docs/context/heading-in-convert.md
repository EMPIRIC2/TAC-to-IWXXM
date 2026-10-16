# Context: abbreviated heading in the main convert path

**Session:** `EV-1409-heading-convert`
**Date:** 2026-10-16
**Mode:** micro evolve
**Ticket:** [#1409](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1409)
**Corpus:** [Corpus: product §F6] [Corpus: api] [Corpus: tests]

## Goal

Pasting a WMO abbreviated heading in front of a report converts that report from the main convert path.

## Out of scope

- Rebuilding abbreviated-heading parsing
- The bulletin endpoint success path
- Visibility, QNH, remarks, the SIGMET body, and TAF time links

## Locked decision

The bulletin endpoint already splits a clean abbreviated heading. The main convert path was treating the heading line as its own report, so the operator saw a missing keyword. That paste now uses the same bulletin split, and the main convert path encodes the reports under the heading. A heading with no report still fails with "No TAC reports found after the abbreviated heading." A malformed heading still fails with a message that the abbreviated heading is not valid.
