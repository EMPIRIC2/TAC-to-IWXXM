# Context — retire-profile-dissem-ui-catalogs

**Session:** `EV-retire-profile-dissem-ui-catalogs`  
**Date:** 2026-09-17  
**Mode:** scoped evolve (standard)  
**Corpus:** [Corpus: product §F7.v] [Corpus: product §F7.w] [Corpus: product §F9]
[Corpus: product §F15–F19] [Corpus: system-spec] [Corpus: tech-spec] [Corpus: api]
[Corpus: tests] [Corpus: journeys] [Corpus: adr/ADR-028] [Corpus: adr/ADR-032]
[Corpus: adr/ADR-038]

## Goal

Hard-cutover retire Profile Builder + Dissemination Bench complex UI/UX. Replace selection
with **backend/code-deployed dropdowns**. Ship **five package-driven trust catalogs**
(TAC Validation, IWXXM Validation, Conversion, Dissemination, Decoding). Extract
**`tac-decoding`** as a publishable PyPI package that owns TAC→natural-language decode and
the Decoding catalog extension surface.

## Locked intake (operator)

| Topic | Lock |
|-------|------|
| UI strategy | **Hard cutover** — drop Profile Builder / Dissemination Bench authoring UX |
| Selection UX | Simple **dropdowns** only; options from **deployed backend** registries |
| Catalogs | Five read-only trust tabs (patterned on Validation Issues Catalog) |
| Extension | Python packages are the open-source extendable SoT; code + deploy to add |
| Decode | New package `tac-decoding` (PyPI); move decode/glossary ownership from `tac2iwxxm` |
| Scale | Standard; Spec→Build gate closed until documenting verify |

## Problem / users

Operators need to **trust** which rules run for lint, IWXXM validate, convert, disseminate,
and decode — without maintaining a complex in-browser profile/dissemination authoring IDE.
Prior cycles (EV-conversion-profile-ux-libraries → EV-profile-builder-workbench-edit / #1203)
expanded five-library authoring; this cycle **reverses that UI investment** in favor of
inspectable catalogs + pickers.

## Must not break

- Workbench convert / lint / soft-preview / `POST /api/v1/decode-tac`
- `GET /api/v1/lint-issue-catalog` (F7.v / F15) behavior for TAC (+ existing IWXXM merge)
- Dissemination **send/preflight** + egress allowlist (F16–F19 / ADR-021/029/030)
- Conversion runtime profiles (`annex3` / `iwxxm_us` / national) — selection may simplify;
  encode path stays
- Public unauthenticated operator app (F21) — no new auth requirement for catalogs

## Inventory (current code)

### Frontend — retire / simplify

| Area | Paths |
|------|--------|
| Profile Builder shell | `ProfileBuilderLibraries.tsx`, `LibraryDraftShell.tsx`, `LibraryWorkbenchShell.tsx` |
| Library panels | `ConversionTemplatesPanel.tsx`, `TacValidationRulesPanel.*`, `DisseminationLibraryPanel.tsx`, `DecodingLibraryPanel.tsx`, `LibraryAssetsListPanel.tsx` |
| Overview / mapping | `ProfileOverviewPanel.tsx`, `WorkbenchMappingBridge.*` |
| Profiles page | `ConversionProfilePage.tsx` |
| Dissemination bench/drawer | `DisseminationDrawer.tsx`, `DisseminationOpsPage.tsx` |
| Existing trust catalog | `LintValidationCatalogPage.tsx` (+ `useLintIssueCatalog.ts`) |
| Pickers | `LibraryPickersBar.tsx`, `ConversionCatalogPicker.tsx` |

### Backend / packages — extend

| Area | Paths |
|------|--------|
| TAC issue registry | `packages/tac-validate` → `issue_registry` + `docs/domain/rules/ISSUE_CATALOG.*` |
| IWXXM catalog rows | `apps/backend/src/services/iwxxm_validation_catalog.py` |
| Conversion profiles API | `routers/conversion_profiles.py`, `services/profile_catalog.py` |
| Decode today | `packages/tac2iwxxm/decode.py`, `glossary.py`, `data/decode_glossary.yaml` |
| Dissemination | `packages/dissemination` (`gateway`, `exchange_registry`, sinks) |
| Library CRUD (likely retire/narrow) | `conversion_profiles` library_assets YAML paths |

### Prior related sessions

`EV-062-validation-issues-catalog`, `EV-conversion-profile-ux-libraries`,
`EV-bridge-ux-canvas-align`, `EV-profile-builder-*`, `EV-1120-phase-a-profile-ux`,
`EV-091-dissemination-drawer-restore`, `EV-profile-builder-workbench-edit` (#1203).

## Build intent (deferred — gate closed)

| Intent | Notes |
|--------|-------|
| Apps | `apps/frontend` hard cutover; `apps/backend` catalog/dropdown APIs |
| Packages | New `packages/tac-decoding`; catalog export APIs in owning packages |
| Deploy | Backend image must ship new package + registries; FE static redeploy |
| QA/E2E | Journey updates for retired builders; catalog tab smoke; decode parity |
| Observability | No new PII; catalog endpoints public-read like lint-issue-catalog |

## CORPUS gaps to close in draft-docs

1. Product: supersede F7.w Profile Builder authoring AC; deepen F7.v → five catalogs; F9 package owner
2. System-spec: add `tac-decoding` component; catalog-extension architecture
3. Tech-spec / dependency-inventory: new PyPI package
4. API: dropdown registries + multi-family catalogs
5. Tests / journeys: hard-cutover + trust catalog UJs
6. ADR: UI retirement + package-owned catalogs + decode extract

## Open for requirements

- Fn id strategy (deepen F7.v/F7.w/F9 vs new Fn)
- HTTP shape (one catalog API with `family=` vs per-package routes)
- Shim window for `tac2iwxxm.decode_tac` re-exports
- Whether library_assets CRUD APIs are deleted or backend-only retained

## UI preview

Recommended default for this cycle: **docs/repo only** (inventory above). Confirm in
requirements startup if operator wants a local non-deployed preview instead.

## Next

`spec-development/requirements` (delta) → draft-docs → feasibility → tech-plan → verify-tech.
