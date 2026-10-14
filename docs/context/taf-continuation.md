# Context — multi-line TAF as one forecast

**Session:** `EV-1401-taf-continuation`
**Date:** 2026-10-14
**Mode:** micro evolve
**Ticket:** [#1401](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1401)
**Corpus:** [Corpus: product §F6] [Corpus: product §F20] [Corpus: tests]

## Goal

A pasted multi-line TAF converts as one forecast. `AMD NOT SKED` is a trailer, so it does not mark the report as an amendment.

## Out of scope

- Probability groups
- Operator result stacking
- Other epic children

## Locked decision

The converter already joins lines inside one TAF string. The HTTP paste path was splitting every non-empty line into its own entry, so each continuation failed as a TAF header. That split now joins a line that does not open a station onto the previous TAF. A real `TAF AMD` marker still sets amendment status. The trailer `AMD NOT SKED` does not.
