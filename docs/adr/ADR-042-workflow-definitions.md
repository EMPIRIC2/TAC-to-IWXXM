# ADR-042: Workflow definitions — execute(message, workflow) (spike #931)

> **Status**: Accepted (EV-931 / #931)  
> **Date**: 2026-09-03  
> **Related**: [ADR-037](ADR-037-platform-logical-layers.md), [ADR-038](ADR-038-conversion-profile-contract.md), [ADR-039](ADR-039-staged-validation-pipeline.md), [ADR-040](ADR-040-sql-adapters-mapping-config.md), [ADR-041](ADR-041-dissemination-gateway.md), [ADR-018](ADR-018-f8-worker-template.md)  
> **Issues**: [#931](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/931), [#922](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/922)  
> **Absorbed:** F8 hard-coded pipeline contract · operator batch path sketch · #934 UI prerequisite

## Context

Spike [#931](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/931) asks for a small **workflow engine** over ingest → profile → pipeline stages → `onValid` disseminate / `onInvalid` quarantine+alert. Goal: **`execute(message, workflow)`** as the primary operational entrypoint; **`convert`** remains a library primitive.

Upstream contracts are now standing (ADR-037–041):

- **Profiles** — ConversionProfile id + resolution (ADR-038)
- **Pipeline stages** — PipelineResult stage ids (ADR-039)
- **Input adapters** — MappingConfig / source adapter refs (ADR-040)
- **Output gateways** — DisseminationGateway kinds + DisseminationPlan hooks (ADR-041)

Today operational paths are **hard-coded**:

| Caller | Current | Gap |
|--------|---------|-----|
| F8 worker | `metar_worker.pipeline.process_job` — lint → convert → validate → store/quarantine | Fixed env profile; no named workflow |
| HTTP `/convert` | Direct `tac2iwxxm.convert` | Not workflow-aware |
| Dissemination drawer | One-shot preflight/send | Operator-triggered; not pipeline-integrated |
| Mass ingest | Bulletin split → per-row convert | Partial batch; no workflow id |

ADR-039 deferred unified PipelineResult **runtime** to #931. ADR-041 deferred DisseminationPlan **runtime** to #931/#936.

Constraints:

- ADR-037 Option C — no big-bang package renames; new package requires ADR (this ADR)
- ADR-021/029 — no BYOC credentials in workflow definitions
- Template purity — executor must not import FastAPI/Supabase
- #931 spike = contract + documentation; runtime in follow-on build

## Decision

1. **Accept a declarative YAML WorkflowDefinition DSL** — not BPMN, Temporal, Celery, or Argo. Stage vocabulary is **fixed MET operations** (parse, validate-tac, convert-iwxxm, validate-xsd, …), not general-purpose orchestration.

2. **Accept normative execute contract:**

   ```yaml
   execute(message: WorkflowMessage, workflow: WorkflowDefinition | str) -> WorkflowResult
   ```

   - `workflow` as `str` resolves a registered workflow id (e.g. `f8-metar-ingest-default`)
   - `WorkflowResult` aggregates ADR-039 `PipelineResult` + `onValid` / `onInvalid` action outcomes
   - **Sync** execute for MVP runtime; async job queue / worker fan-out deferred

3. **New package `packages/workflows`** — thin MET-lib executor (stage registry + action dispatch). Rationale: cross-cuts `tac-validate`, `tac2iwxxm`, `iwxxm-validate`, `dissemination` without pulling orchestration into `apps/worker` or `tac2iwxxm`. Apps remain **thin callers**.

4. **Workflow file location (v1):** git-managed `workflows/*.yaml` at repo root (reviewed, versioned). DB-managed / operator-uploaded workflows deferred to #933/#934.

5. **WorkflowDefinition minimum fields:**

   | Field | Purpose |
   |-------|---------|
   | `id` | Stable workflow id (e.g. `us-metar-production`) |
   | `version` | Semver pin for breaking DSL changes |
   | `input.adapter` | Optional source adapter ref (ADR-040) — F8 may omit (poller supplies message) |
   | `profile` | ConversionProfile id and/or `strategy` + `fallback` (ADR-038) |
   | `pipeline` | Ordered stage ids (ADR-039 mapping) |
   | `onValid` | Actions: `disseminate`, `store` |
   | `onInvalid` | Actions: `store` (quarantine), `alert` |

6. **Stage registry (normative ids → owners):**

   | Stage id | Owner package | Notes |
   |----------|---------------|-------|
   | `parse` | `tac2iwxxm` | Product parse → IR dict |
   | `validate-tac` | `tac-validate` | LintReport |
   | `normalize` | implicit in parsers | **Planned** explicit stage |
   | `validate-semantic` | `tac-validate` + profile overlays | **Planned** |
   | `convert-iwxxm` | `tac2iwxxm` | ConvertResult |
   | `validate-xsd` | `iwxxm-validate` | StageResult pattern |
   | `validate-schematron` | `iwxxm-validate` | |
   | `validate-codelists` | `iwxxm-validate` | **Planned** |
   | `exchange-packaging` | `dissemination` | Pre-dissemination |

   Fail-closed on unknown stage id. First failing stage halts pipeline (no skip-by-default).

7. **Action dispatch:**

   - `onValid.disseminate: [gateway-ref, …]` — resolves ADR-041 gateway kind + plan ref; **DisseminationPlan runtime deferred to #936**
   - `onValid.store` / `onInvalid.store` — ADR-040 sink / quarantine tables
   - `onInvalid.alert` — operator notification channel refs (no secrets in YAML)

8. **Secrets policy:** workflow files **must not** embed credentials. Use `${ENV:VAR_NAME}` or opaque `secretRef:` keys resolved at runtime from deploy env / secret store (ADR-021). Preflight rejects literal URLs with embedded auth.

9. **Caller matrix:**

   | Caller | Role | MVP |
   |--------|------|-----|
   | `apps/worker` | Poll → `execute(message, workflow_id)` | **Primary** — replaces hard-coded `process_job` in follow-on build |
   | `apps/backend` | Optional batch/replay endpoint | **Planned** (#934) |
   | HTTP `/convert` | Library primitive | **Unchanged** — not replaced by execute |
   | Operator UI #934 | Workflow picker + run history | Blocked until this ADR |

10. **MVP runtime scope (Planned build — not #931):**

    - Stages: `validate-tac` → `convert-iwxxm` → `validate-xsd` + `validate-schematron`
    - `onInvalid` → quarantine store only
    - `onValid` → archive store only (no live gateway send)
    - Gateway disseminate + alert channels in follow-on after #936

11. **Implementation deferred:** #931 delivers contract + ADR only. Unified `PipelineResult` population, executor, and F8 cutover are separate build cycles.

## Normative sketch

```yaml
id: us-metar-production
version: "1.0.0"
input:
  adapter: postgres-prod          # ADR-040 MappingConfig ref (Planned)
profile:
  strategy: station-country
  fallback: ICAO_2025             # ADR-038 ConversionProfile id
pipeline:
  - parse
  - validate-tac
  - normalize
  - validate-semantic
  - convert-iwxxm
  - validate-xsd
  - validate-schematron
  - validate-codelists
onValid:
  disseminate:
    - gateway: postgres-archive
    - gateway: wis2-production
      planRef: wis2-default         # DisseminationPlan id (runtime #936)
  store:
    - sink: iwxxm_reports
onInvalid:
  store:
    - sink: quarantine-db
  alert:
    - channel: operations           # secretRef at runtime
```

## Alternatives considered

| # | Alternative | Why rejected |
|---|-------------|--------------|
| A | Temporal / Celery / Argo | Overkill for fixed MET stage set; ops burden |
| B | Code-only workflows (Python dicts) | Not operator-reviewable; blocks #934 UI |
| C | Executor in `apps/worker` only | Backend batch cannot share; import smell |
| D | Executor in `packages/tac2iwxxm` | Violates separation — spans validate/disseminate |
| E | YAML DSL + `packages/workflows` | **Accepted** |
| F | DB-only workflow storage v1 | Deferred — git YAML sufficient for first milestone |

## Consequences

### Positive

- Epic #922 Workflows layer has standing contract
- F8 `process_job` has migration target (`f8-metar-ingest-default` workflow)
- #934 workflow UI and #938 pipeline inspector unblocked at contract level
- Clear boundary: workflow owns stage halt; DisseminationPlan owns per-destination retry (#936)

### Negative / follow-ups

- New `packages/workflows` workspace member — update template registry + uv workspace on implementation
- F8 cutover requires regression against existing ingest tests
- `normalize` / `validate-semantic` / `validate-codelists` stages need explicit implementations before full sketch is runnable
- Async batch execute API not defined in v1

## References

- [Context: workflow-definitions-931](../context/workflow-definitions-931.md)
- EV-931 session `reports/931-workflow-definitions.md`
- F8 reference: `apps/worker/src/metar_worker/pipeline.py`
