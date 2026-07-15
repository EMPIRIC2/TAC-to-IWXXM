# Scoped context — Issue #655 TAC traceability UX

**Status**: superseded (shipped PR #715; session closed 2026-07-13)  
**Created**: 2026-07-12  
**Session**: S010-issue-655-tac-traceability / EV-007  
**GitHub**: [#655](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/655) (parent [#594](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/594))  
**Feature**: F6 (operator UI delta)

## Problem

Operators convert METAR/SPECI TAC and see result cards titled `manual_input.txt` without a clear
view of the **source TAC** that produced each IWXXM output. Traceability matters for multi-line
manual input and file+manual mixes.

## Prior work

- **EV-003 / #594**: `ConversionResult.tac_input` on API; **Source TAC** `<pre>` panel in
  `FileConverter` when `originalContent` is non-empty (TC-001b).
- **EV-005 / #664**: Custom output filename for manual downloads (card title may still be custom
  basename).

## Live check (2026-07-12)

| Surface | Finding |
|---------|---------|
| Prod API `/api/v1/convert` | Returns `tac_input` with manual METAR |
| Prod UI (user report) | Source TAC panel **missing** after Convert |
| Repo `FileConverter.tsx` | Panel gated on `file.originalContent` truthy |

**Hypothesis**: Client mapping gap and/or weak prominence — not missing API field. UI must
always populate `originalContent` from `tac_input` **or** pre-clear manual/file queue lines, and
must not hide the panel when traceability is the product goal.

## Approved UX (Phase 0 decisions)

| ID | Decision |
|----|----------|
| R1 | **F6 delta**, UI-only — no API/schema change |
| R2 | **All reasonable UX**: header TAC snippet, TAC-derived card label where helpful, prominent Source TAC, multi-line index mapping |
| R3 | **Frontend redeploy** required (12/13) |
| R4 | Out of scope: ZIP sidecar, bulletin UI, API changes |

## Implementation notes

- Harden `originalContent` assignment in convert handler (never leave empty when TAC known).
- Consider `deriveResultTitle(tac)` — e.g. `METAR KJFK 121251Z` — while keeping download names
  per #664 rules.
- Multi-line: show `Line N of M` chip when `manualResultCount > 1`.
- Always render Source TAC region (aria); use em dash + helper text only if TAC truly unknown.
- Extend Vitest (`FileConverter.test.tsx`) and Playwright (`tac-file-conversion.e2e.spec.ts`).

## References

- [Context: issue-594-feedback](issue-594-feedback.md)
- [Corpus: test-plan](../test-plan.md) TC-001b
- `apps/frontend/src/app/components/FileConverter.tsx`
