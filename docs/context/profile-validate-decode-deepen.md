# Context — profile-validate-decode-deepen

**Session:** `EV-profile-validate-decode-deepen`  
**Date:** 2026-09-21  
**Mode:** scoped evolve (standard) · resume after intake  
**Ticket:** [#1221](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1221)  
**Corpus:** [Corpus: product §F2] [Corpus: product §F6] [Corpus: product §F7]
[Corpus: product §F9] [Corpus: product §F15] [Corpus: product §F35]
[Corpus: product §F36] [Corpus: domain-profiles] [Corpus: system-spec]
[Corpus: tech-spec] [Corpus: api] [Corpus: tests] [Corpus: journeys]
[Corpus: adr/ADR-036] [Corpus: adr/ADR-044] [Corpus: adr/ADR-045]
[Corpus: adr/ADR-046]

## Goal

Close remaining national-profile / TAC-validate / IWXXM-validate / decode /
operator-catalog spine so operators pick **deployed** profiles and see
**profile-scoped** catalogs — without reopening retired Profile Builder authoring.

## Locked intake

| Topic | Lock |
|-------|------|
| Scale | Standard; Spec→Build gate **closed** until documenting verify |
| UI preview | Docs/repo only (aligns D-EVRPC-01 / ADR-044) |
| F36 | Finish `AU_BOM` / `NZ_CAA_MET` → catalog `implemented`; CA mining P0 as capacity |
| Catalogs | #1120–#1123 profile-scoped lint/IWXXM catalog filters + seed rows |
| ADR-044 | Hard cutover residual: remove Profile Builder authoring; five package catalogs + dropdowns |
| Decode | #724 ICAO station → airport name (glossary soft-fail path exists) |
| OUT | #1222 exchange packaging; #1210/#970/#837/#938/#996/#1159/#1025/#1198; marketplace/dissem |

## Problem / users

Operators converting/validating under national semantic profiles (`US_FAA_NWS`,
`CA_ECCC`, thin packs, AU/NZ) need the Issues Catalog and workbench filters to
show **profile-applicable** rules, and a simpler trust UI (catalogs + pickers)
instead of five-library authoring. Decode still shows bare ICAO codes (#724).

## Must not break

- Convert / lint / soft-preview / `POST /api/v1/decode-tac`
- Dissemination send/preflight + egress allowlist (F16–F19)
- Existing product/family catalog filters
- Operator copy free of corpus/ADR/EV tokens (EV-048)
- No invented national XSDs; US Schematron remains N/A (#870)

## Inventory (2026-09-21)

### Profiles (catalog.yaml)

| Id | Status | Notes |
|----|--------|-------|
| ICAO_2025 / US_FAA_NWS / CA_ECCC | implemented | CA deepen mining issues still open |
| AU_BOM / NZ_CAA_MET | **implemented** | Registry + convert product allowlist; METAR/SPECI/TAF goldens (TC-EV087 / TC-EVPVD-002..003) |
| Thin packs (UK/BR/KR/JP/IN/HK) | implemented | Thin path |
| GLOBAL_AFS | implemented | |
| APAC_ROBEX / EUR_RODEX / AFI / CAR_SAM | **stub** | OUT → #1222 |

### ADR-044 residual

| Piece | State |
|-------|--------|
| `packages/tac-decoding` | Present (packs + glossary + catalog) |
| `GET /api/v1/rule-catalogs` + selection-options | Backend + FE client present |
| Profile Builder authoring UI | **Unmounted** (ADR-044 residual M1) — `WorkbenchMappingBridge` removed from Convert; `ProfileBuilderLibraries` not mounted; Conversion profiles shell nav already gone (EV-RPC); orphan components remain for M6 delete |
| Hard-cut convert Form fields | `convert_library_hard_cut.py` rejects legacy library Form fields |

### #1120 family

| Child | Signal |
|-------|--------|
| #1121 API filters | **Green** — `lint_catalog_profile_filter.py` + TC-EV1120-001..005 |
| #1122 mining | **Green** — US/CA TAC + IWXXM national rows with provenance (TC-EV1120-006..008) |
| #1123 FE filters | **Green** — `useLintIssueCatalog` binds Profile + Exchange (TC-EV1120-009) |
| #1145 glanceable | **Workbench twin green**; Profiles-page hero superseded by ADR-044 unmount (TC-EV1120-010 waived) |

### #724 decode station names

`tac_decoding.glossary` documents optional OpenAIP/F3-style ICAO→name soft-fail;
backend airport schemas exist. Issue still OPEN — wire into decode explanations/summary.

### Prior related context

`docs/context/retire-profile-dissem-ui-catalogs.md`,
`docs/context/profile-builder-workbench-edit.md`,
EV-063/064/087/089/094, EV-1120 Phase A notes.

## CORPUS coverage

Standing rows cover this cycle (product Fn + ADRs + domain-profiles + api + tests).
**No new CORPUS member required.** Doc deltas expected: feature-list F36/F7.v status,
test-plan TC rows, api-contract for catalog filters if not already documented,
domain-profiles catalog status flips.

## Build intent (deferred — gate closed)

| Area | Packages / apps |
|------|-----------------|
| Profiles | `tac2iwxxm`, `docs/domain/profiles` |
| Catalogs | `tac-validate`, `iwxxm-validate`, `apps/backend` lint catalog + rule-catalogs |
| FE | Retire Profile Builder; catalog filters; decode station display |
| Decode | `tac-decoding` + backend `/decode-tac` |
| Deploy | PRs → `stage` first; H4–H5 when FE catalog/dropdown calls change |

## Spec → Build gate

**closed** until Spec band + `bin/verify --phase documenting` pass and operator opens gate.
