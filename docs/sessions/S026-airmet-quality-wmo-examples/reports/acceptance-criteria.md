# Acceptance criteria — S026 / EV-020 (F24 / F25 / F9·F7.g deepen)

> Session artifact for **11-verify-impl** sign-off. Standing product AC also lives in
> `docs/feature-list.md`. Policy: **ADR-032**. Golden bar: **`canonicalize_xml` equality under
> default convert settings only** (E20-D3 — “match on default”).

## F24 — AIRMET quality (#731)

| # | Criterion | Evidence |
|---|-----------|----------|
| F24.1 | AIRMET lint codes registered (ADR-028) | TC-F24-001 |
| F24.2 | WMO `airmet-A6-1a-TS` convert == vendor XML (defaults) | TC-F24-002 |
| F24.3 | Golden validates XSD+SCH | TC-F24-003 |
| F24.4 | Negatives emit registry diagnostics | TC-F24-004 |
| F24.5 | Workbench AIRMET smoke (+ H4–H5 if FE) | TC-F24-005 / UJ-035 |

## F25 — WMO METAR/SPECI/TAF parity + UI gate

| # | Criterion | Evidence |
|---|-----------|----------|
| F25.1 | Listed WMO METAR/SPECI/TAF cases == vendor XML (defaults) | TC-F25-001 |
| F25.2 | Those goldens validate | TC-F25-002 |
| F25.3 | Examples catalog = WMO-passers only (in-scope) | TC-F25-003 |
| F25.4 | Load WMO example → convert smoke (+ H4–H5) | TC-F25-004 / UJ-036 |

## F9 deepen — glossary

| # | Criterion | Evidence |
|---|-----------|----------|
| F9.d1 | Seven-product token meanings (not category-only) | TC-F9-003 |
| F9.d2 | Extensible YAML/JSON registry loads | TC-F9-004 |
| F9.d3 | OpenAIP/F3 miss → designator only (no decode fail) | TC-F9-003 |

## F7.g deepen

| # | Criterion | Evidence |
|---|-----------|----------|
| F7.g1 | Catalog policy enforced in Vitest | TC-F25-003 / TC-F7-008 deepen |

## Sign-off (11-verify-impl)

| Fn | Reviewer | Date | Result |
|----|----------|------|--------|
| F24 | | | pending |
| F25 | | | pending |
| F9 deepen | | | pending |
| F7.g deepen | | | pending |
