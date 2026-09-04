# Scoped context: Workflows runtime (#1132)

> **Status**: active  
> **Created**: 2026-09-03  
> **Session**: `EV-1132-workflows-runtime`  
> **Tickets**: [#1132](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1132) · parent [#922](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/922) · contract [#931](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/931)  
> **Corpus**: [Corpus: product] F6/F8 · [Corpus: system-spec] §Platform logical layers · [Corpus: adr] ADR-042, ADR-018, ADR-037–041

## Goal

Implement ADR-042 MVP: `packages/workflows` + F8 cutover to `execute(message, workflow)`.

## Locked decisions (from ADR-042 / #1132)

| ID | Decision |
|----|----------|
| D1 | Package name `workflows` under `packages/workflows` (MIT, hatchling) |
| D2 | Public API: `execute(message, workflow: str | WorkflowDefinition) -> WorkflowResult` |
| D3 | Workflow files: repo-root `workflows/*.yaml`; default search path configurable |
| D4 | MVP stages only for F8 path; unknown stage → fail-closed |
| D5 | Store/quarantine via injected callables — package does not import SQLAlchemy/DO |
| D6 | `process_job` becomes thin adapter calling `execute` (preserve signature for callers) |
| D7 | `/convert` unchanged |
| D8 | No live gateway / alert delivery this cycle |
| D9 | Coverage 100%; no FastAPI/Supabase in package |
| D10 | Soft-pass `SCHEMATRON_SKIPPED` parity with current F8 pipeline |

## Current F8 behavior (must preserve)

`apps/worker/.../pipeline.process_job`: tac_lint → tac2iwxxm.convert → iwxxm_validate(xsd+schematron); soft-skip SCHEMATRON_SKIPPED; return PipelineResult.

## Architecture sketch

```text
WorkflowMessage(tac, product, job_id, …)
        │
        ▼
 packages/workflows.execute(msg, "f8-metar-ingest-default")
        │  load YAML → resolve ${ENV:} → stage loop
        ├─ validate-tac  → tac_validate.lint
        ├─ convert-iwxxm → tac2iwxxm.convert
        ├─ validate-xsd / validate-schematron → iwxxm_validate
        └─ onValid/onInvalid → optional StorePort callbacks
        │
        ▼
 WorkflowResult → worker maps to store/quarantine writers
```

## Standing docs to update (draft-docs)

- `[Corpus: system-spec]` — Workflows row Implemented; Component Details for `packages/workflows`
- `[Corpus: product]` F8 deepen note
- `[Corpus: tech-spec]` dependency-inventory + template-conformance
- `[Corpus: decisions]` EV-1132 section
- ADR-042 consequences: mark runtime in progress / done on merge

## Out of scope

UI #934 · DB workflows · async · replace `/convert` · DisseminationPlan runtime #936 · non-MVP stages beyond stubs
