# EV-layout-dx — package DX naming, interfaces, and scenario tests

**Date:** 2026-11-05  
**Session:** `~/.cursor/workflow/EMPIRIC2/TAC-to-IWXXM/sessions/EV-layout-dx`  
**Status:** Spec band in progress (gate closed)

## Context

Opaque module names (example: `iwxxm_validate.c14n`) hide the job from new
contributors. Prior `EV-packages-module-reorg` removed pass-through shims. It
did not set a NumPy-class discoverability bar. The operator asked for interfaces
and tests of the form "I want to do XYZ".

## Decisions

1. Open evolve **EV-layout-dx**. Close **EV-packages-module-reorg** (L1/L2 done).
2. Add standing bar [Corpus: package-dx] (`docs/engineering/package-dx.md`).
3. Public renames: new clear primary names + aliases for **one** CalVer package
   version.
4. Pilot package: `iwxxm-validate`. First rename target: Canonical XML helpers
   (`c14n*` → `canonical_xml` / `to_canonical_xml` / `canonical_xml_equal`).
5. Do not use `canonicalize_xml` as the new primary name (collision with
   ADR-032 `metar_shared.xml_canonical.canonicalize_xml`).
6. DX tests `TC-DX-001`…`TC-DX-004` lock "I want to …" import paths.
7. ADR-037 stands: no top-level `packages/<name>` directory rename in this cycle.
8. Markdown edits in this cycle use ASD-STE100 + avoid-ai-writing. Human STE
   review against Issue 9 remains required.

## Non-goals

- Convert / lint / validate result changes
- Operator UI / H4–H5
- Sticky L3 from the prior reorg

## Follow-ups

- Feasibility + tech-plan + documenting verify
- Build gate AskQuestion before code renames
