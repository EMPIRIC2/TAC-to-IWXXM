# EV-retire-profile-dissem-ui-catalogs — requirements decisions

**Session:** `EV-retire-profile-dissem-ui-catalogs`  
**Date:** 2026-09-17  
**Corpus:** [Corpus: product] [Corpus: adr/ADR-044]

## Locked requirements (operator: recommended)

| ID | Topic | Choice |
|----|-------|--------|
| D-EVRPC-01 | UI preview | Docs/repo only (no local preview) |
| D-EVRPC-02 | Feature mapping | Deepen F7.v (five catalogs); **retire F7.w authoring UI**; deepen F9 → `tac-decoding`; F16–F19 send retained with simpler pickers |
| D-EVRPC-03 | HTTP | Family-aware `GET /api/v1/rule-catalogs?family=…` + selection-options; packages export; `lint-issue-catalog` compatibility |
| D-EVRPC-04 | Decode + CRUD | Extract `tac-decoding`; one-release `tac2iwxxm` re-export; **delete** library authoring UI + operator library YAML CRUD; dissem drawer send + dropdowns only |
| D-EVRPC-05 | Cutover | **Hard** — no dual UX / no YAML escape hatch |

## Acceptance criteria (requirements lock)

1. Hard-cutover FE: Profile Builder / five-library authoring / Dissemination Bench authoring removed
2. Workbench (+ dissem drawer) uses dropdowns backed by deployed selection APIs
3. Catalog shell with five tabs; each row has plain-language what/why (EV-048 clean)
4. Each owning package exposes a stable Python catalog export used by the backend aggregator
5. `packages/tac-decoding` published on monorepo PyPI path; decode API parity
6. UJ-072f–UJ-072i authoring journeys **Retired**; new UJ-076* for catalogs + dropdowns
7. Must-not-break: convert, lint, soft-preview, decode-tac, dissem preflight/send + allowlist

## ADR

[ADR-044](../adr/ADR-044-package-owned-catalogs-tac-decoding.md)
