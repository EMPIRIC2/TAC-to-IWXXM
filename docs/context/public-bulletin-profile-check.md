# Context — public-bulletin profile check

**Session:** `EV-1272-public-bulletin-profile-check`  
**Date:** 2026-09-23  
**Mode:** scoped evolve (standard)  
**Ticket:** [#1272](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1272)  
**Corpus:** [Corpus: product §F6] [Corpus: product §F15] [Corpus: tests §TC-LIVE-FEEDS] [Corpus: adr/ADR-009] [Corpus: adr/ADR-036]

## Goal

One local command pulls a fresh public sample for every semantic profile, runs conversion, IWXXM schema validation, lint, and decode, writes a pass/fail summary, and exits non-zero when any sampled report fails. Misses are filed against the lint profile catalog and the convert allowlists.

## Out of scope

- G-AIRMET until a TAC feed exists.
- Promoting `stage` to `main`.
- Browser UI, H4–H5 connectivity, and a deploy this session.
- A new CORPUS member. Standing deltas stay in `docs/feature-list.md` and `docs/test-plan.md`.

## Locked intake

| Topic | Lock |
|-------|------|
| Scale | Standard. Spec→Build gate **closed** until documenting verify |
| Session | Feature, normal urgency, continue `EV-1272-public-bulletin-profile-check` |
| Users | Maintainers running the check |
| Fence | Lint catalog shape, convert allowlists, and Canada IWXXM 3.0.0 `SCHEMA_PARSE_ERROR` vs document `XSD_VALIDATION_ERROR` stay distinct |
| Delivery | Local Make/command first. GitHub schedule only after that command is stable |
| Success | Summary plus non-zero exit on any convert, schema, lint, or decode failure |
| Docs | Delta `docs/test-plan.md` and `docs/feature-list.md`. Waive a new CORPUS row |
| Build intent | `tests/live`, quality-matrix fixtures, Makefile, `tac-validate` catalog, convert allowlists. No UI preview |
| Fold-in | Uncommitted `tests/live/national_feeds.py`, `tests/live/test_national_feeds.py`, `tests/unit/test_national_feed_compare.py`, quality-matrix YAML, and related Makefile / hook edits |
| Memory | Session-open returned no accepted knowledge. Historical retrieve hit only `q-verification-gate` (vecinita RAG). **Waive** — not a Decision, Feature, or FailureMode for this check |

## Problem

`make test-live-feeds` already samples MET Norway and NOAA AWC METAR/TAF, checks lint, convert, and XSD, and compares shared observations ([Corpus: tests §TC-LIVE-FEEDS]). It does not cover the #1272 feed set (AWC international and convective SIGMET, NOAA tgftp VAA/TCA/AIRMET/VONA/space weather, JMA Tokyo VAAC), does not sample one report per semantic profile, does not run decode, and is not a merge gate.

## Inventory

| Piece | State |
|-------|--------|
| `tests/live/national_feeds.py` | Uncommitted helpers for MET Norway, AWC METAR/TAF, optional KNMI. Not the full #1272 feed list |
| `make test-live-feeds` | Runs `tests/live/test_national_feeds.py -m live_api`. Manual tier; CI does not call these hosts |
| Lint profiles | Rows in the lint profile catalog (`docs/domain/profiles/catalog.yaml` and `tac-validate` issue catalog). National differences are rows, not new modules ([#1269](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1269)) |
| Canada 3.0.0 | `iwxxm-validate` emits `SCHEMA_PARSE_ERROR` when the XSD fails to compile and `XSD_VALIDATION_ERROR` when the document fails (`packages/iwxxm-validate/src/iwxxm_validate/xsd.py`) |
| Working tree | Checked out `docs/EV-1252-name-table-landed` with the fold-in files dirty. Evolve branch is cut from that tip so the files travel; rebase onto `origin/stage` before the implementing PR |

## Build intent (not started)

Packages and tests only. No browser wiring. Schedule workflow is deferred until the local command is stable.

## Resolutions

| ID | Decision |
|----|----------|
| R1 | Extend the live-feed check to the #1272 sources and the four checks (convert, schema, lint, decode) |
| R2 | Keep `SCHEMA_PARSE_ERROR` separate from `XSD_VALIDATION_ERROR` in the summary |
| R3 | National lint misses become catalog rows |
| R4 | H4–H5 and UI preview are N/A for this session |
