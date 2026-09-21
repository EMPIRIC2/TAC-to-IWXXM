# Verify-tech — EV-yaml-engine-configurability (#1224)

**Date:** 2026-09-21  
**Against:** [ev-yaml-engine-configurability-tech-plan.md](ev-yaml-engine-configurability-tech-plan.md)  
**Product lock:** [ev-yaml-engine-configurability.md](ev-yaml-engine-configurability.md)

[Corpus: decisions] [Corpus: tests] [Corpus: product §F2/F6/F9/F12/F15]

## Consistency vs product plan

| Product AC | Tech coverage | Status |
|------------|---------------|--------|
| Matrix published + lock | T1 / M1 | Aligned |
| READMEs + cookbook | T5 / M4 | Aligned |
| Preflight fail-closed | T3–T4 / M3 | Aligned |
| No HTTP injection | T7 | Aligned |
| Glossary SoT | T6 | Aligned |
| No FE / H4–H5 | TP-EVYEC-05 | Aligned |
| No emit-YAML / detector deepen / ADR-044 | Out of scope lists match | Aligned |

## Provable statements

| # | Statement | Risk | Confidence | Disposition |
|---|-----------|------|------------|-------------|
| S1 | Overlay loaders already exist in four packages | Low | High | Accept — cite packs.py / policy.py / profile_resolve.py |
| S2 | Shared preflight can validate `extends` without new deps | Low | High | Accept — PyYAML present |
| S3 | `--check-overlay` on four CLIs is thin | Low | Med | Accept — optional if Makefile entrypoint covers TC-EVYEC-003 |
| S4 | Examples in package trees are enough for CI without wheel packaging | Low | High | Accept — monorepo tests |
| S5 | OpenAPI already has no policy YAML body fields | Low | High | Accept — regression lock only |
| S6 | Draft matrix cells are honest enough for presence lock | Low | Med | Accept — evidence upgrades optional in Build |
| S7 | Connectivity tasks required by generic tech-plan template | Med | High | **Waive** — product plan H4–H5 N/A (D-EVYEC-07 / TP-EVYEC-05) |
| S8 | New ADR required | Low | High | Reject — TP-EVYEC-04 |

## Build Plan Card parity

All In-scope task IDs T1–T8 appear in tech-plan; Spec sources cited; TDD-friendly order; card is not a second tracker.

## Verdict

**Pass** — proceed to documenting verify (`bin/verify --phase documenting`), then AskQuestion to open Build gate.

## Waivers recorded

- Connectivity / H4–H5 execution-plan tasks: **waived** (no UI)
