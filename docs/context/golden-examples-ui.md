# Scoped context — Workbench golden examples (#780)

**Status**: active  
**Session**: S021-golden-examples-ui / EV-016  
**Created**: 2026-07-22  
**Linked**: F7, [#780](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/780), #714

## Topic

Add **frontend-only** pre-loaded golden examples so operators can one-click load curated
TAC / AHL / IWXXM samples into the convert + validate workbench without pasting.

## Code anchors

| Area | Path |
|------|------|
| Workbench UI | `apps/frontend/src/app/components/FileConverter.tsx` (`inputMode`, product pickers) |
| Input modes | `apps/frontend/src/utils/inputKind.ts` — `tac` / `ahl_bulletin` / `collect_iwxxm` (ADR-024) |
| Proposed fixtures | `apps/frontend/src/fixtures/examples/` (typed catalog — to add) |
| Package goldens (copy source) | `packages/tac2iwxxm/tests/fixtures/annex3_golden/`, `iwxxm_us_golden/` |
| Optional cases | `test-data/golden/cases/` |
| Existing FE tests | `FileConverter.test.tsx`, workflow Vitest under `apps/frontend/src/test/` |

## Corpus

- `[Corpus: product]` **F7** — Planned; sample loaders from #714 isolated in #780
- Complements F6 convert + F2/F12 validate UX; **no** engine or API contract change
- Prior modes cycle: [manual-tac-input-modes.md](manual-tac-input-modes.md) / EV-012
- Connectivity: H4–H5 when FE ships (static assets only — no new API origins)

## Resolutions (intake)

| ID | Resolution |
|----|------------|
| R1 | Deepen F7 only — no new Fn (E16-2) |
| R2 | Frontend static catalog; copy from package fixtures — never import Python at runtime |
| R3 | Wire into existing FileConverter input modes — no new modes |
| R4 | Lean+build routing; skip 03/05/06/12 unless forced |
| R5 | UJ-032 + TC-F7-008; F7.g slice; F7 stays Planned (E16-5..E16-6) |
| R6 | Happy-path IWXXM only; no soft-fail / file-queue v1 (E16-7) |
| R7 | Thin hazard fixtures: allow 1 + document gap; no invented TAC (E16-8) |
| R8 | Typed FE catalog + Radix `ui/select` Examples control (E16-11..E16-15) |
| R9 | IWXXM: happy-path single-report XML via `collect_iwxxm` (E16-14) |

## Non-goals (cycle)

Backend fixture API, DB seeds, session persistence of examples, dissemination of demos,
engine quality bars, inventing non-round-trippable TAC.
