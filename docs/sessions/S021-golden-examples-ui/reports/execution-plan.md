# Execution plan — S021 / EV-016 (F7.g golden examples / #780)

> **Status**: **approved** (2026-07-26) — Batch 2=A / E16-16  
> **Active task after approve**: T1.1 (07-build)

> **Branch**: `evolve/EV-016-golden-examples-ui`  
> **Evolve cycle**: EV-016  
> **Features**: F7 deepen (slice **F7.g** only)  
> **Mode**: delta (frontend-only; no API / env / DB)  
> **Spec sources**: feature-list §F7.g; spec §F7 golden examples; UJ-032; TC-F7-008;
> context/golden-examples-ui.md; E16-1..E16-15; ADR-024 (modes)

## Current State

| Field                | Value                          |
| -------------------- | ------------------------------ |
| **Active phase**     | Phase C — 07-build             |
| **Active milestone** | M2 — FileConverter Examples UX |
| **Active task**      | T2.1 in_progress               |
| **Tasks**            | 3 / 11 completed               |
| **Last updated**     | 2026-07-26                     |

## Tech Stack Summary (S021 delta)

| Area             | Choice                                                                                   | Source          |
| ---------------- | ---------------------------------------------------------------------------------------- | --------------- |
| Template         | `static+api+worker` (unchanged)                                                          | ADR-018         |
| Scope            | Frontend-only static catalog + Examples UX                                               | E16-4 / E16-9   |
| Catalog          | Typed TS under `apps/frontend/src/fixtures/examples/` + copied `.tac`/`.xml` (`?raw` OK) | E16-11          |
| Examples control | Existing Radix `./ui/select` (grouped); place next to product / Manual TAC Input         | E16-12 / E16-15 |
| New npm deps     | **None** — reuse `@radix-ui/react-select` via `ui/select`                                | E16-15          |
| Modes            | Existing ADR-024 `tac` / `ahl_bulletin` / `collect_iwxxm`                                | E16-4 / R3      |
| IWXXM sample     | ≥1 happy-path single-report golden XML → `collect_iwxxm`                                 | E16-14          |
| Fixtures         | annex3 + product_matrix + iwxxm_us; VAA/TCA 1+gap                                        | E16-13 / E16-8  |
| Tests            | Vitest hard (TC-F7-008); H4–H5 when FE deploys                                           | E16-5           |
| CORS / API       | No new routes or CORS tasks — reuse existing H0c / connectivity                          | E16-9           |
| Deploy           | Frontend static redeploy only (13); skip 12                                              | Lean+build      |

## Feature ↔ Milestone Mapping

| Slice / AC                          | Milestone     | Deliverable                               |
| ----------------------------------- | ------------- | ----------------------------------------- |
| Catalog completeness (C1)           | M1            | Copied goldens + typed catalog + gap note |
| Click-to-load TAC/AHL/IWXXM (C2–C4) | M2            | Examples `Select` + FileConverter wiring  |
| Demo labeling + Vitest green        | M2–M3         | Toast + non-operational label; TC-F7-008  |
| H4–H5 when FE ships                 | M3 / stage 13 | Deploy smoke (no API/env)                 |

## Data Dependencies

| Asset                                                                                 | Staging               | Needed By |
| ------------------------------------------------------------------------------------- | --------------------- | --------- |
| `packages/tac2iwxxm/tests/fixtures/annex3_golden/*`                                   | present (copy source) | T1.2      |
| `packages/tac2iwxxm/tests/fixtures/product_matrix/{sigmet,airmet,vaa,tca}_basic.tac`  | present               | T1.2      |
| `packages/tac2iwxxm/tests/fixtures/iwxxm_us_golden/{sigmet,airmet,metar,speci}_*.tac` | present               | T1.2      |
| `packages/tac2iwxxm/tests/fixtures/metar_*ahl*.txt`                                   | present               | T1.2      |
| Backend / DB / env                                                                    | **N/A**               | —         |

**Copy policy**: Copy fixture **content** into `apps/frontend/src/fixtures/examples/`; never import Python packages at runtime. Record package-relative provenance in catalog metadata.

### Planned catalog pairing (E16-13)

| Product / kind | Examples (≥2 or gap)          | Source roots                                    |
| -------------- | ----------------------------- | ----------------------------------------------- |
| METAR          | ≥2 TAC (+ prefer ≥1 iwxxm_us) | annex3 + iwxxm_us                               |
| SPECI          | ≥2 TAC (+ prefer ≥1 iwxxm_us) | annex3 + iwxxm_us                               |
| TAF            | ≥2 TAC                        | annex3 (+ iwxxm_us if useful)                   |
| SIGMET         | 2 TAC                         | product_matrix + iwxxm_us                       |
| AIRMET         | 2 TAC                         | product_matrix + iwxxm_us                       |
| VAA            | **1 + documented gap**        | product_matrix only                             |
| TCA            | **1 + documented gap**        | product_matrix only                             |
| AHL            | ≥1 bulletin                   | `metar_multi_ahl.txt` (or single)               |
| IWXXM          | ≥1 happy-path XML             | e.g. `metar_basic.golden.xml` → `collect_iwxxm` |

## Milestones & Tasks (TDD order)

`evolve_cycle_id: EV-016` · `feature_ids: [F7]` · slice `F7.g`

### M1 — Static examples catalog

| Task | Type | Description                                                                                                                                   | Spec Source                  | Depends On | Status    |
| ---- | ---- | --------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------- | ---------- | --------- |
| T1.1 | Test | Catalog completeness unit tests (TC-F7-008 C1): ≥2 TAC/product or gap entry; ≥1 AHL; ≥1 IWXXM; VAA/TCA gap asserted                           | test-plan TC-F7-008; UJ-032  | —          | completed |
| T1.2 | Code | Copy selected goldens into `apps/frontend/src/fixtures/examples/`; typed `examplesCatalog.ts` (+ load helpers); `FIXTURE_GAPS.md` for VAA/TCA | feature-list F7.g; E16-11/13 | T1.1       | completed |
| T1.3 | Docs | Provenance fields on each catalog entry (package path + id); demo/`nonOperational: true` flag                                                 | context R2; UJ-032           | T1.2       | completed |

### M2 — FileConverter Examples UX

| Task | Type | Description                                                                                                                     | Spec Source        | Depends On | Status  |
| ---- | ---- | ------------------------------------------------------------------------------------------------------------------------------- | ------------------ | ---------- | ------- |
| T2.1 | Test | Vitest click-to-load: TAC sets body+product+toast+demo label; AHL → `ahl_bulletin`; IWXXM → `collect_iwxxm` (C2–C4)             | TC-F7-008; UJ-032  | T1.2       | pending |
| T2.2 | Code | Wire grouped Examples control via existing `./ui/select` next to product / Manual TAC Input; `data-testid="examples-select"`    | E16-12/15; ADR-024 | T2.1       | pending |
| T2.3 | Code | `loadExample(id)` sets editor body, `product`, `inputMode`; toast (“Loaded … example”); visible demo / non-operational labeling | UJ-032 steps 3–6   | T2.2       | pending |
| T2.4 | Test | Soft-fail / file-queue **not** present in catalog (C5 out of v1)                                                                | E16-7              | T1.2       | pending |

### M3 — Gate docs + handoff

| Task | Type   | Description                                                                       | Spec Source                       | Depends On | Status  |
| ---- | ------ | --------------------------------------------------------------------------------- | --------------------------------- | ---------- | ------- |
| T3.1 | Docs   | Session notes: gap list + how to add a golden; link #780 AC                       | feature-list F7.g AC              | T2.3       | pending |
| T3.2 | Test   | Full frontend Vitest green for touched modules (TC-F7-008 hard gate)              | test-plan F7 golden-examples gate | T2.1–T2.4  | pending |
| T3.3 | Docs   | HANDOFF for 08→13: FE-only deploy; H4–H5 on 13; no API/env checklist items        | routing-plan; connectivity        | T3.2       | pending |
| T3.4 | Config | Confirm no `dependency-inventory` / env-contract deltas (reuse Radix Select only) | E16-15 / E16-9                    | T2.2       | pending |

## Phase Gate Check (B→C)

- [x] Execution plan approved (Batch 2 / E16-16)
- [x] 05/06 skipped per Lean+build (re-open only if deps/ADR conflict)
- [x] No new backend routes or env knobs
- [x] Tasks T1.1–T3.4 scoped to F7.g / #780 only

## Git Strategy

| Item               | Value                                                                   |
| ------------------ | ----------------------------------------------------------------------- |
| Branch             | `evolve/EV-016-golden-examples-ui`                                      |
| Commits            | One logical task (or tight TDD pair) per commit: `[T1.1]`, `[T1.2]`, …  |
| PR                 | Minor PR to `main` after M3 + 08–11; 13 after FE deploy                 |
| Out of scope files | `apps/backend/**`, `packages/**` (read-only copy source), env contracts |

## PR Plan

| PR          | Scope                          | Status  |
| ----------- | ------------------------------ | ------- |
| S021 / F7.g | Catalog + Examples UX + Vitest | pending |

## Phase Gate Log

| Gate   | Result  | Date       | Notes                 |
| ------ | ------- | ---------- | --------------------- |
| A→B    | passed  | 2026-07-26 | E16-10 user approve   |
| B→C    | passed  | 2026-07-26 | E16-16; 05/06 skipped |
| C→D    | pending | —          | after 07+08           |
| Deploy | pending | —          | 13 H4–H5 FE           |
