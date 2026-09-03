# Scoped context: Workflow definitions (#931)

> **Status**: active  
> **Created**: 2026-09-03  
> **Session**: `EV-931-spike-workflow-definitions-execute-message-workf`  
> **Tickets**: [#931](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/931) · [#922](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/922)  
> **Corpus**: [Corpus: product] F6/F8 · [Corpus: system-spec] · [Corpus: adr] ADR-037–042

## Goal

Spike **workflow engine** contract: `execute(message, workflow)` over ingest → profile → pipeline → `onValid` / `onInvalid`. Spike only — runtime deferred.

## Recommendation

1. **Declarative YAML DSL** + thin Python executor in **`packages/workflows`** (ADR-042)
2. **Git-managed** `workflows/*.yaml` v1 — DB/operator upload deferred (#934)
3. **Stage ids** map to ADR-039 PipelineResult; **profile** block references ADR-038
4. **F8 worker** becomes thin caller — `process_job` migrates to `f8-metar-ingest-default`
5. **HTTP `/convert` unchanged** — library primitive, not replaced
6. **No secrets** in workflow files (ADR-021 env/secretRef indirection)
7. **DisseminationPlan runtime** still #936 — workflow documents `onValid.disseminate` hooks only

## Caller matrix

| Caller | Today | Target |
|--------|-------|--------|
| F8 worker | Hard-coded lint→convert→validate | `execute(msg, "f8-metar-ingest-default")` |
| Backend batch | N/A | Planned (#934) |
| `/api/v1/convert` | Direct convert | Unchanged |
| Dissemination drawer | One-shot BYOC | Stays operator-triggered (not auto on ingest) |

## MVP runtime (Planned — post-ADR build)

- Stages: validate-tac → convert-iwxxm → validate-xsd/schematron
- onInvalid → quarantine; onValid → archive store only
- No live gateway send in MVP

## Out of scope

BPMN · Temporal/Celery · runtime in #931 · UI #934 · inspector #938 · DisseminationPlan runtime #936
