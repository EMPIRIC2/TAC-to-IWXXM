# Evolve summary — S020 / EV-015

> Completed: 2026-07-22 (Phase 4 closed — `D-S020-EV015-phase4-close`)  
> Features: **F20** (TAF + SPECI quality bar); deepen **F6.b** / **F6.c** / **F12**  
> Branch: `evolve/EV-015-aerodrome-quality` → PR [#778](https://github.com/joseph-c-mcguire/metar-to-IWXXM/pull/778) → `main` @ `eae8bdc`  
> Issues [#735](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/735) / [#734](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/734) closed on cycle close  
> Orchestrator: 16-evolve (Lean+build `D-S020-EV015-route-1`)

## Outcome

F20 delivered: TAF + SPECI registry deepen (ADR-028 reuse), accept/negative fixtures for themes
T1–T4 / S1–S3 / C1, Annex-3 + IWXXM-US goldens, FE catalog TAF tag filters, and live
`product=taf|speci` catalog + lint/convert smoke. Render H0ci–H5 + catalog smoke PASS on image
`…-eae8bdc`.

## Stage trail

| Stage | Result |
|-------|--------|
| 00–02 | Session + F20 product deltas; Phase A PASS |
| 04 | Execution plan M0–M5; Phase B PASS (05/06 skipped) |
| 07–08 | M0–M5 build (28/28); 08 PASS |
| 09–10 | QA + E2E UJ-031 / TC-F20 (T0); H4–H5 deferred then green at 13 |
| 11 | F20 + F6/F12 deepen sign-off (`D-S020-EV015-11-A`) |
| 12 | Skipped (Lean+build) |
| 13 | Merge #778; Render H0ci–H5 + catalog taf/speci PASS |

## Key decisions

- `D-S020-EV015-route-1` — Lean+build (skip 03/05/06/12)
- ADR-028 reuse — no new registry architecture
- `D-S020-EV015-merge-778` — merge + live smoke + close M5/Phase D
- `D-S020-EV015-phase4-close` — close cycle; close #735/#734

## Artifacts

Session reports under `docs/sessions/S020-aerodrome-quality/reports/`.  
Standing: `docs/evolve-report-EV-015.md`, `docs/CHANGELOG.md`, ADR-028.
