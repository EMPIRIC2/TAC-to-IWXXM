# Scoped context — Manual TAC Input modes (#730)

**Status**: active  
**Session**: S016-manual-tac-input-modes / EV-012  
**Created**: 2026-07-20  
**Linked**: F7, ADR-024, UJ-011, [#730](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/730)

## Topic

Validate the operator workbench **Manual TAC Input** surface (TAC report / AHL bulletin /
IWXXM COLLECT) shipped under ADR-024 — operator-visible mode switching, hints, and
end-to-end success/placeholder behavior.

## Code anchors

| Area | Path |
|------|------|
| Mode UI | `apps/frontend/src/app/components/FileConverter.tsx` (`input-mode-*` test ids) |
| Client APIs | `apps/frontend/src/utils/api.ts` — `convertBulletin`, `ingestCollect` |
| Kind detect | `apps/frontend/src/utils/inputKind.ts` (and Vitest) |
| Unit coverage | `FileConverter.test.tsx`, `api.test.ts` (501 path) |
| Playwright gap | No `apps/e2e/` matches for input-mode / convert-bulletin / ingest-collect (as of intake) |

## Corpus

- [ADR-024](../adr/ADR-024-operator-input-modes.md) — modes + COLLECT 501 honesty
- `[Corpus: api]` — `/convert-bulletin`, `/ingest-collect` 501
- `[Corpus: tests]` — UJ-011 (API/H7); F7 H6′ journeys lack mode-group cases
- F7 remains **Planned** (E11-11); this cycle does **not** flip status

## Resolutions (local)

| ID | Resolution |
|----|------------|
| R1 | Validation-only under F7; no new Fn |
| R2 | Auto-switch on paste/upload is acceptance-critical |
| R3 | Playwright authored in stage **10** (lean; no 07) |
| R4 | Staging smoke required (H4–H5 + AHL + COLLECT 501) |
| R5 | COLLECT member extract remains deferred |

## Connectivity

Browser workbench → single API origin (`/api/v1/convert`, `/convert-bulletin`,
`/ingest-collect`). H4–H5 live connectivity + authenticated workbench pass in **13**.
