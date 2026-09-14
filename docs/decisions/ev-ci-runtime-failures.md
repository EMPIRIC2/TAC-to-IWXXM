# EV-ci-runtime-failures decisions

**Session:** EV-ci-runtime-failures  
**Date:** 2026-09-14  
**Operator:** proceed with recommendations (routing + R choices)

| ID | Decision | Rationale |
|----|----------|-----------|
| D1 | Standard evolve routing incl. tech-plan + verify-tech | CI change touches ADR-043 + TC-F34 |
| D2 | Fix iwxxm-validate mutation baseline **and** dual-cadence matrix | Red is test/code path, not survivors; full daily matrix is ~20m wall |
| D3 | Daily mutation = subset/rotate; weekly + `workflow_dispatch all` = full matrix | Preserves D-S069-e4 coverage without daily cost |
| D4 | Map PEP 440 `.devN` → Cargo `YYYY.M.D-dev.N` for Cargo.toml only | Fixes maturin nightly; PyPI keeps `.devN` |
| D5 | Schemathesis unchanged this cycle | Already path-filtered + budgeted; low failure rate |
| D6 | PR into `stage` | pr-into-stage-first |
| D7 | No coverage / Schemathesis budget weakening | quality bar |

[Corpus: tests] [Corpus: adr/ADR-043] [Corpus: decisions]
