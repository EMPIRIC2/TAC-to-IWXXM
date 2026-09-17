# ADR-044: Package-owned rule catalogs, UI hard cutover, `tac-decoding`

**Status:** Accepted (requirements lock — EV-retire-profile-dissem-ui-catalogs, 2026-09-17)  
**Date:** 2026-09-17  
**Corpus:** [Corpus: product §F7.v] [Corpus: product §F7.w] [Corpus: product §F9]
[Corpus: product §F16–F19] [Corpus: system-spec] [Corpus: api] [Corpus: adr/ADR-028]
[Corpus: adr/ADR-032] [Corpus: adr/ADR-038]

## Context

Profile Builder / five-library authoring UX (F7.w deepens through #1203) became too complex
for operators. Trust is better served by **read-only catalogs** of the rules that already
ship in Python packages (as with F7.v Validation Issues Catalog), plus **simple dropdowns**
whose options come only from **backend-deployed** registries. TAC→natural-language decode
(F9 / ADR-032 glossary) should be an independent open-source PyPI package so third parties
can extend decoding without carrying the full converter.

## Decision

1. **Hard cutover UI** — Remove Profile Builder / library authoring / Dissemination Bench
   authoring surfaces from the operator app. Do not keep a dual path or in-browser YAML
   escape hatch.
2. **Dropdowns only for selection** — Conversion / validation / dissemination / decoding
   selection uses dropdowns (or equivalent simple pickers) fed by deployed backend lists.
   Adding options requires package code + backend deploy — not browser-only add-ons.
3. **Five trust catalogs** — Operator UI exposes five tabs (or a tabbed catalog shell):
   TAC Validation, IWXXM Validation, Conversion, Dissemination, Decoding. Catalogs are
   **read-only** inspect surfaces for trust/transparency.
4. **Package-owned SoT** — Each catalog is exported from the owning package:
   - TAC Validation → `tac-validate` (ADR-028 registry)
   - IWXXM Validation → `iwxxm-validate` (+ backend merge helpers as today)
   - Conversion → `tac2iwxxm` (profiles / conversion catalog export)
   - Dissemination → `dissemination` (gateway/sink/exchange registry export)
   - Decoding → **`tac-decoding`** (glossary + decode rules catalog)
5. **HTTP** — Prefer one family-aware catalog API, e.g.
   `GET /api/v1/rule-catalogs?family=tac|iwxxm|conversion|dissemination|decoding`,
   aggregating package exports. Keep `GET /api/v1/lint-issue-catalog` as a compatibility
   alias or thin wrapper for TAC (+ existing IWXXM merge) during transition.
   Separate lightweight selection-options endpoints (or narrowed existing list routes)
   feed dropdowns.
6. **`tac-decoding` package** — New `packages/tac-decoding` (PyPI name `tac-decoding`)
   owns `decode_tac`, glossary, and Decoding catalog export. `tac2iwxxm` re-exports for
   **one release** then deprecates those entry points (ADR-032 amend: glossary home moves).
7. **Library YAML CRUD** — Operator-facing and browser-driven library-assets authoring
   APIs/UI are **removed**. Runtime continues to use code-shipped registries only.
8. **Dissemination send retained** — F16–F19 drawer **send/preflight** remains; destination
   / exchange selection simplifies to dropdowns. Egress allowlist / memory-only credentials
   unchanged (ADR-021/029/030).

## Consequences

### Positive

- Lower operator cognitive load; clearer trust story
- Open-source extension path aligned with packages already published (tac-validate, etc.)
- Clear ownership for decode as a standalone library

### Negative / risks

- Loss of in-app profile authoring (operators who relied on F7.w must wait for code deploys)
- Migration cost: FE deletions, API removals, journey/test rewrites
- Temporary dual import path during `tac2iwxxm` re-export window

### Must not

- Persist BYOC secrets in catalogs or dropdown metadata
- Put internal doc refs in operator catalog copy (EV-048)
- Auto-push F8 ingest into dissemination

## Supersedes / amends

- **Supersedes (UI):** F7.w Profile Builder authoring AC and UJ-072f–UJ-072i authoring journeys
  for operator surfaces (historical Implemented status retained; new deepen marks **Retired UI**)
- **Amends:** ADR-032 (glossary package home → `tac-decoding`); ADR-038 (operator overlay/library
  authoring UI no longer primary; runtime contract of packaged profiles remains)
- **Does not supersede:** ADR-028 registry model; F16–F19 send semantics; F7.v catalog quality bar

## Acceptance (this evolve)

1. Profile Builder / library authoring / Dissemination Bench authoring UI gone
2. Five catalog tabs usable against package exports via family-aware API
3. Dropdowns list only backend-deployed options
4. `tac-decoding` importable; `/decode-tac` parity; one-release re-export from `tac2iwxxm`
5. Docs + tests/journeys updated; H4–H5 for new FE→API catalog/dropdown calls
