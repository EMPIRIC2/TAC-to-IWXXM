# EV-yaml-engine-configurability — requirements lock (#1224)

**Locked:** 2026-09-21  
**Session:** `~/.cursor/workflow/EMPIRIC2/TAC-to-IWXXM/sessions/EV-yaml-engine-configurability`  
**Issue:** [#1224](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1224)  
**Documenting→Implementing gate:** closed  
**Context:** [yaml-engine-configurability.md](../context/yaml-engine-configurability.md)

[Corpus: product §F2/F6/F9/F12/F15] [Corpus: adr/ADR-044] [Corpus: adr/ADR-045] [Corpus: adr/ADR-046] [Corpus: tests] [Corpus: tech-spec] [Corpus: decisions]

## Intake (recommended options locked)

| ID | Choice |
|----|--------|
| R1 | Deepen F2/F6/F9/F12/F15 — no new Fn |
| R2 | Matrix + cookbook + `examples/overlays/` + preflight + README/config-spec |
| R3 | Matrix products: METAR, SPECI, TAF, SIGMET, AIRMET, VAA, TCA |
| R4 | Monorepo script + thin per-package CLI hooks |
| R5 | UI preview N/A — no UI features |
| R6 | Write requirements deltas now |

## Decisions

| ID | Decision |
|----|----------|
| D-EVYEC-01 | Honesty first: do not claim full YAML execute coverage; publish matrix |
| D-EVYEC-02 | Convert emit remains Python this cycle; pack IR + profile binding documented |
| D-EVYEC-03 | Detector YAML deepen deferred (honesty matrix only) |
| D-EVYEC-04 | Preflight: monorepo entrypoint + thin package hooks |
| D-EVYEC-05 | No HTTP client policy/pack YAML; no ADR-044 authoring; no Schematron-as-YAML; #1222 out |
| D-EVYEC-06 | Glossary SoT = `tac-decoding`; legacy env alias documented |
| D-EVYEC-07 | H4–H5 N/A; UJ-DEV-010 + TC-EVYEC-001..005 |
| D-EVYEC-08 | Scale standard; Spec gate stays closed until documenting verify |

## Tech plan

See [ev-yaml-engine-configurability-tech-plan.md](ev-yaml-engine-configurability-tech-plan.md) (TP-EVYEC-01..06).  
Verify-tech: [ev-yaml-engine-configurability-verify-tech.md](ev-yaml-engine-configurability-verify-tech.md) — **Pass**.

## Acceptance (mirror feature-list)

1. Matrix published + schema/presence lock (TC-EVYEC-001)
2. Four package READMEs link cookbook + env vars (TC-EVYEC-002)
3. Preflight fail-closed / accept fixtures (TC-EVYEC-003)
4. No OpenAPI policy-injection fields (TC-EVYEC-004)
5. Glossary SoT docs (TC-EVYEC-005)

## Verify angles (session extras)

`product-engine-matrix` · `overlay-fail-closed` · `pypi-readme-overlay-smoke` · `api-no-policy-injection` · `glossary-single-home`
