# Acceptance criteria — S027 / EV-021 (F26 / F27 + F6.f / F12 / F7.g deepen)

> Session artifact for **11-verify-impl** sign-off. Standing product AC also lives in
> `docs/feature-list.md`. Policy: **ADR-032** (golden) + **ADR-028** (registry). Golden bar:
> **`canonicalize_xml` equality under default convert settings only** (E21-2).

## F26 — VAA quality (#736)

| # | Criterion | Evidence |
|---|-----------|----------|
| F26.1 | VAA lint codes registered (ADR-028) | TC-F26-001 |
| F26.2 | Exceptional-rule fixtures (**F26 theme V1**) + adjacency (**F26 theme V2**) | TC-F26-004 / TC-F26-006 |
| F26.3 | WMO `va-advisory-A7-2` convert == vendor XML (defaults) | TC-F26-002 |
| F26.4 | Golden validates XSD+SCH | TC-F26-003 |
| F26.5 | Common rules **F26 theme C1** (incl. translation-failed not happy-path) | coverage matrix / goldens |
| F26.6 | Workbench VAA smoke + catalog passers only; unlock when F26 golden greens (**S02.M2**) (+ H4–H5 if FE) | TC-F26-005 / UJ-037 |

## F27 — TCA quality (#737)

| # | Criterion | Evidence |
|---|-----------|----------|
| F27.1 | TCA lint codes registered (ADR-028) | TC-F27-001 |
| F27.2 | Exceptional-rule fixtures (**F27 theme T1**) + adjacency (**F27 theme T2**) | TC-F27-004 / TC-F27-006 |
| F27.3 | WMO `tc-advisory-A2-2` convert == vendor XML (defaults) | TC-F27-002 |
| F27.4 | Golden validates XSD+SCH | TC-F27-003 |
| F27.5 | Common rules **F27 theme C1** | coverage matrix / goldens |
| F27.6 | Workbench TCA smoke + catalog passers only; unlock when F27 golden greens (**S02.M2**) (+ H4–H5 if FE) | TC-F27-005 / UJ-038 |

## F6.f / F12 / F7.g deepen

| # | Criterion | Evidence |
|---|-----------|----------|
| F6.f1 | VAA/TCA encode fidelity to vendor shapes | TC-F26-002 / TC-F27-002 |
| F12.d1 | Registry codes for VAA/TCA rules | TC-F26-001 / TC-F27-001 |
| F7.g1 | Catalog hides non-passers; **incremental per-product unlock** (S02.M2) | TC-F26-005 / TC-F27-005 / TC-F7-008 |

## Sign-off (11-verify-impl)

| Fn | Reviewer | Date | Result |
|----|----------|------|--------|
| F26 | — | — | pending |
| F27 | — | — | pending |
| F6.f / F12 / F7.g deepen | — | — | pending |
