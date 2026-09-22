# Context — profile-builder-workbench-edit

**Session:** `EV-profile-builder-workbench-edit`  
**Ticket:** [#1203](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1203)  
**Date:** 2026-09-16  
**Mode:** scoped evolve (full)  
**Corpus:** [Corpus: product §F7.w] (+ F7.v / F9 / F15–F19); [Corpus: system-spec]; [Corpus: api]; [Corpus: tests]; [Corpus: adr/ADR-038]

## Goal

IDE-style Profile Builder workbench with full create/edit across five libraries, Overview compare + product enablement, YAML↔UI round-trip — fixing staging gaps after #1197 Phase A.

## Locked intake

See session `routing-plan.md` (D1–D28). Highlights: remove DnD; full authoring; foundation fork-only; operator decides all design choices.

## Inventory (current code)

### Frontend (`apps/frontend`)

| Area | Paths |
|------|--------|
| Profiles page | `ConversionProfilePage.tsx` (+ tooltips, inspector/compare hooks) |
| Five library tabs | `ProfileBuilderLibraries.tsx` |
| Library draft/YAML shell | `LibraryDraftShell.tsx`, `libraryYamlDiagnostics.ts` |
| Assets list | `LibraryAssetsListPanel.tsx` |
| Conversion templates / DnD | `ConversionTemplatesPanel.tsx` (DnD target for removal) |
| Dissemination / Decoding panels | `DisseminationLibraryPanel.tsx`, `DecodingLibraryPanel.tsx` |
| Pickers / IDs / API | `LibraryPickersBar.tsx`, `libraryIds.ts`, `conversionProfilesApi.ts`, `wmoLibraryDefaultsSync.ts` |

### Backend (`apps/backend`)

| Area | Paths |
|------|--------|
| Library CRUD + `validate-yaml` | `routers/conversion_profiles.py`, `services/conversion_profiles_service.py` |
| Schemas / kinds | `schemas/conversion_profiles.py` (`LibraryKindLiteral` × 5) |
| Migrations | `alembic/.../library_assets.py`, `library_asset_yaml.py` |
| Convert hard-cut | `metar_iwxxm_api/convert_library_hard_cut.py` |

### Prior cycle

- #1196 / PR #1197 Phase A merged to `stage` (shell + tooltips + YAML validate). This cycle **supersedes DnD** as a goal and deepens editability.

## Must-not-break

- Convert hard-cut / semantic profile binding
- F5 sessions; F8 worker (no auto-push)
- Dissemination egress allowlist / memory-only BYOC creds (F16–F19)
- No Corpus/ADR/EV ids on operator surfaces (EV-048)
- Foundation profile integrity (read-only; fork to customize)

## Spec docs to delta (next: requirements)

- `docs/feature-list.md` §F7.w
- `docs/user-journeys.md` (new UJ-072i-* or similar)
- `docs/test-plan.md` (TC-EVWB-* / H4–H5)
- `docs/api-contract.md` (library YAML schema / validate endpoints as needed)
- `docs/spec.md` component notes
- `docs/adr/ADR-038-*.md` amend if contract changes
- `docs/decisions/evolve-decisions.md`

## F107 / memory

Sparse retrieve — **waive** cross-project hits; keep-local prior #1196 lineage only.

## Out of scope

F8 auto-push; new sink protocols; Convert chrome rewrite; PyPI breaks.
