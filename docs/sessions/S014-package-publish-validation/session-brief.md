---
session_id: S014-package-publish-validation
type: feature
status: closing  # Phase 4 prep done; awaiting user close checkpoint
branch: evolve/EV-010-package-publish-validation
started_at: 2026-07-18
intent: "Validation stack perf review (#703); publishable tac-validate (#698), iwxxm-validate Rust+SDK (#699), tac2iwxxm with validate extras (#693); domain rule encoding; PyPI + release-tag CI/CD"
orchestrator: 16-evolve
evolve_cycle_id: EV-010
context_briefs:
  - docs/context/package-publish-validation.md
standing_docs_touched: []
---

# Session S014 — package-publish-validation

## Intent

One evolve cycle covering GitHub issues:

| Issue | Role |
|-------|------|
| [#703](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/703) | Measure/design first — layer cost matrix, msgspec expansion, codegen spike |
| [#698](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/698) | Design + publish full TAC product validation package |
| [#699](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/699) | Design + publish fast IWXXM validation (Rust core + Python SDK), Schematron in-cycle |
| [#693](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/693) | Publish `tac2iwxxm` with optional validate extras |

Plus: incorporate `docs/domain/` mined rules aggressively into packages; PyPI trusted
publishing + release-tag CI/CD ([Real Python PyPI guide](https://realpython.com/pypi-publish-python-package/)).

## Intake decisions (Phase 0 — recorded 2026-07-18)

| ID | Decision |
|----|----------|
| E10-1 | Open feature session S014 → 16-evolve |
| E10-2 | One cycle EV-010: #703 measure/design first, then #698 → #699 → #693 |
| E10-3 | PyPI + release-tag CI; **Render 12–13 included** after E10-15 (msgspec HTTP) |
| E10-4 | PyPI names: `tac-validate`, `iwxxm-validate`, `tac2iwxxm` |
| E10-5 | Converter: convert + optional `tac2iwxxm[validate]` extras |
| E10-6 | Bundle pinned `vendor/schemas/*` in `iwxxm-validate` wheel |
| E10-7 | Design **and implement** full Rust Schematron this cycle (must-ship 11B) |
| E10-8 / E10-15 | Expand msgspec into backend; **prefer msgspec over pydantic for validation** on high-churn paths (breaking HTTP OK + Render redeploy) |
| E10-9 | Aggressively encode mined `docs/domain/` rules into `tac-validate` / convert (all products) |
| E10-10 / 11B | **Production** IWXXM data-model codegen from XSD / `iwxxm-modelling` |
| E10-11 | Must-ship everything (no stretch deferrals as default) |
| E10-12 | Fn F11–F14 |
| E10-13→15 | Routing includes 13-deploy-smoke |

## Proposed Fn allocation (pending approval)

| Fn | Title | Primary issues |
|----|-------|----------------|
| F11 | Validation stack performance review + msgspec deepen + codegen spike | #703, #10B, #8C |
| F12 | Publishable TAC product validation (`tac-validate`) + domain rules | #698, #9C |
| F13 | Fast IWXXM validate Rust core + Python SDK (+ Schematron design/impl) | #699, #6A, #7B |
| F14 | Publish `tac2iwxxm` (+ validate extras) + shared PyPI/release CI | #693, #5B, #3A |

## Scope notes

**In (approved direction):** measure-first #703 deliverables; three PyPI packages; schema
bundling; Rust Schematron design (impl stretch); msgspec in backend internals; domain rule
encoding; XSD/modelling codegen prototype; PyPI + tag workflow.

**Out (default):** inventing a TAC UML parallel; changing vendor pins without sync PR;
dropping pydantic from OpenAPI without a plan; full Render redeploy unless backend HTTP
contract changes require it.

## Routing plan

See [routing-plan.md](./routing-plan.md) — pending user approval.

## Links

- Issues: #703, #699, #698, #693
- Domain: [docs/domain/](../../domain/README.md)
- ADRs: ADR-016 (msgspec), ADR-017 (PyO3)
- Context: [package-publish-validation.md](../../context/package-publish-validation.md)
