# EV-bridge-ux-canvas-align — requirements lock

**Date:** 2026-09-14  
**Decision id:** `D-EVBRIDGE-req=1`  
**Session:** `EV-bridge-ux-canvas-align`

## Summary

Lock AC1–AC10 for F7.w deepen: five Libraries (Conversion, TAC validation, IWXXM validation,
Dissemination, Decoding), Profile builder sub-tabs, Mapping bridge on Convert+Profile,
fork-on-edit defaults, hard cut of `semantic_profile`, drop Signed overlays / Dissemination
templates / Semantic preset / Rule pack primary chrome.

## Corpus updates

- [Corpus: product §F7.w] EV-bridge block
- [Corpus: journeys] UJ-072g
- [Corpus: tests] TC-EVBRIDGE-001..010
- [Corpus: api] hard-cut note on `semantic_profile`
- [Corpus: adr/ADR-038] amend EV-bridge

## Operator decisions

See session `reports/intake-decisions.md` and `reports/requirements.md`.

## AC11 (2026-09-14)
Every TAC to IWXXM block mapping requires an associated Conversion library rule; unmatched fail closed. TC-EVBRIDGE-011.
