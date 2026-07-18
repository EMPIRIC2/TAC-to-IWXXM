# 01-requirements interview log — S014 / EV-010

## Locked (msgspec / OpenAPI)

| ID | Decision |
|----|----------|
| E10-16 | Document manifest: mandatory + all recommended |
| E10-17 | msgspec on `/convert`, `/validate`, `/lint-tac`, `/decode-tac` (+ bulletin/zip siblings as high-churn); auth/admin/work-sessions stay pydantic |
| E10-18 | Pydantic retained for OpenAPI schema integrations (thin aliases / export); FE types updated same cycle |

## High-churn route set (proposed for ADR-026)

| Route | Engine |
|-------|--------|
| `POST /api/v1/convert` | msgspec |
| `POST /api/v1/convert-zip` | msgspec |
| `POST /api/v1/convert-bulletin` | msgspec |
| `POST /api/v1/validate` | msgspec |
| `POST /api/v1/lint-tac` | msgspec |
| `POST /api/v1/decode-tac` | msgspec |
| Auth, admin, work-sessions, airports, ICAO OPMET stats | pydantic |

OpenAPI: generate/keep schemas via pydantic mirror models or explicit JSON Schema export from Structs where needed.

## Locked (packages / PyPI / domain / Rust / codegen)

| ID | Decision |
|----|----------|
| E10-19 | PyPI `0.1.0` + per-package version tags |
| E10-20 | `tac2iwxxm[validate]` → tac-validate + iwxxm-validate |
| E10-21 | All 7 products; METAR/SPECI/TAF full depth; others templates+gates |
| E10-22 | Native Rust Schematron/SVRL + parity suite |
| E10-23 | Codegen from XSD; UML provenance; CI on vendor pin bumps |
| E10-24 | Soft benches; hard-fail at publish |
| E10-25 | OIDC trusted publishing per package tag |
| E10-26 | UJ-022 / UJ-023 / UJ-DEV-005 |
| E10-27 | Write standing docs now |

## Locked (02 audit + 03 + 04 batch 1)

| ID | Decision |
|----|----------|
| E10-28 | msgspec = responses + post-Form Structs; multipart Form unchanged |
| E10-29 | config-spec + deploy PyPI OIDC notes |
| E10-30 | must-ship kept; 04 kill-switch via AskQuestion only |
| E10-31 | 03 tooling option D |
| E10-32 | Phase A: commit then 04 |
| E10-33 | Milestones M1 benches → M2 tac-validate → M3 iwxxm-validate → M4 tac2iwxxm+OIDC → M5 msgspec HTTP → M6 08–13 |
| E10-34 | Schema wheel bundle = runtime XSD+SCH+catalogs subset |
| E10-35 | Hard benches: lib p95 ≤0.85× lxml; HTTP p95 ≤1.0× pydantic map; wheel smokes |
| E10-36 | New `packages/iwxxm-validate/rust` maturin; lxml parity until cutover |
| E10-37 | One publish workflow + package matrix |
| E10-38 | Thin msgspec→Response helper; pydantic OpenAPI-only |
| E10-39 | manylinux/macOS/win wheels; tac-validate CLI; optional iwxxm-validate CLI |
| E10-40 | xsdata (+ xsdata-pydantic) full Python models; adapt msgspec/Rust follow-on |
