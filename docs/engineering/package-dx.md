# Package developer experience

[Corpus: package-dx]

This document sets the naming and interface bar for Python packages under
`packages/`. The goal is that a new contributor can find the right import for a
job without ticket history or standards jargon in the path name.

Session: EV-layout-dx. Related: [Corpus: product] §M1, [Corpus: product] §F2,
[Corpus: adr/ADR-037], [Corpus: tests] `TC-DX-*`.

No tool guarantees ASD-STE100 compliance for this file. Human review against
Issue 9 remains required.

## Terms

| Term | Meaning |
|------|---------|
| TAC | Traditional Alphanumeric Code (aviation text products such as METAR) |
| IWXXM | WMO XML format for the same aviation products |
| Canonical XML | W3C Canonical XML 1.0 (also called C14N). A normal form used to compare XML when formatting differs |
| Façade | Small public surface a package exports for common jobs |
| DX test | Automated test that locks an "I want to …" import path |

## Rules for names

1. Prefer full English words in **new** public module and symbol names.
2. You may keep a short domain noun after you define it once in the package
   README or module docstring (examples: XSD, GML, TAC, IWXXM).
3. Do not put ticket ids, evolve ids, or session ids in public paths.
4. Opaque standards codes (example: `c14n`) are not enough as the only public
   name. Expand them in the primary path. You may keep the short form as an
   alias.
5. When you rename a public symbol, keep the old name as an alias for at least
   one CalVer package version. State the alias in the module docstring.

## Interfaces

Each publishable package must:

1. Export primary job symbols in `__all__`.
2. Point to those symbols from a short README table titled "Start here".
3. Label advanced helpers as advanced (pin-specific tools, internal engines).

Do not grow a second unofficial public surface in a nested module without a
README link.

## DX scenario tests

For each listed journey, a unit test must prove that the preferred import works
and that the symbol appears in `__all__` when the journey is public.

Draft journeys for `iwxxm-validate` (see [Corpus: tests]):

| ID | Journey |
|----|---------|
| TC-DX-001 | I want to validate IWXXM XML against pinned schemas |
| TC-DX-002 | I want to compare two IWXXM documents for Quality Metrics and ignore formatting noise |
| TC-DX-003 | I want to know whether the Rust native engine is available |
| TC-DX-004 | I want validation tuned for Quality Metrics reporting |

Pilot rename for TC-DX-002: primary module `canonical_xml` with
`to_canonical_xml` and `canonical_xml_equal`. Keep `c14n_xml` and `c14n_equal`
as aliases during the CalVer window. Do not use `canonicalize_xml` as the new
primary name. That name already belongs to a different helper under
`metar_shared.xml_canonical` (ADR-032).

## Phases

| Phase | Work |
|-------|------|
| L1 | This bar + DX tests + `iwxxm-validate` Canonical XML pilot |
| L2 | Other opaque names in `iwxxm-validate` + package README pass |
| L3 | Other packages by inventory priority |
| L4 | `apps/` layout clarity (docs first; low-risk moves only) |
| L5 | Root README and removal or relocation of confusing root items |

ADR-037 still forbids a big-bang rename of top-level `packages/<name>`
directories unless a later evolve amends that ADR.

## Must not

- Change convert, lint, or validate **results** in the name of a rename.
- Drop a public PyPI symbol without an alias period or an explicit breaking
  decision in [Corpus: decisions].
- Put planning ids in operator-facing UI copy.
