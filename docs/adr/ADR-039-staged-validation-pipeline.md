# ADR-039: Staged validation pipeline + canonical IR boundary (spike #925)

> **Status**: Accepted (EV-925 / #925)  
> **Date**: 2026-09-03  
> **Related**: [ADR-036](ADR-036-semantic-vs-exchange-profiles.md), [ADR-037](ADR-037-platform-logical-layers.md), [ADR-038](ADR-038-conversion-profile-contract.md)  
> **Issues**: [#925](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/925), [#922](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/922)

## Context

Spike [#925](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/925) investigates a canonical aviation MET model between TAC parse and IWXXM generation, with staged validation and structured multi-result output aligned with ADR-036 §4 and architecture [#914](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/914).

Today:

- **IR:** `tac2iwxxm.ConvertResult.ir` — product-specific `dict[str, Any]` from `parse_*` functions
- **TAC validation:** `tac-validate` → flat `LintReport`
- **Conversion:** `tac2iwxxm.convert` → `ConvertResult` with issues
- **IWXXM validation:** `iwxxm-validate` → `ValidationReport`; **`stages`** populated for `ca_eccc` layered path (EV-068)
- **HTTP:** `/api/v1/validate` — separate 7-layer operator stack (airport + XML layers)

ADR-037 Option C keeps package names — extracting `packages/core/canonical-model` is out of scope for this spike.

## Decision

1. **Canonical IR boundary — keep-in-place.** The versioned IR remains **`tac2iwxxm` product parse output** (`ConvertResult.ir`). Document per-product dict shapes as the canonical boundary. Typed msgspec canonical structs are **deferred** until METAR-family schemas stabilize under #912.

2. **Reject** new `packages/core/canonical-model` package for M5 / #925 window (same rationale as ADR-037 Option C).

3. **Accept PipelineResult contract** — normative multi-stage aggregate for library/platform use:

   | Stage id (examples) | Owner | Current artifact |
   |---------------------|-------|------------------|
   | `profile_resolution` | backend `profile_wire` | wire metrics only |
   | `tac_lint` | `tac-validate` | `LintReport.issues` |
   | `convert` | `tac2iwxxm` | `ConvertResult.issues` |
   | `wmo_wellformed` / `wmo_xsd` / `wmo_sch` / `code_ca` | `iwxxm-validate` | `StageResult` (ca_eccc) |
   | `exchange_packaging` | `dissemination` / `ca_exchange_validate` | post-convert |

   Reuse `iwxxm_validate.StageResult` shape for cross-package stages when implemented.

4. **Confirm architecture:** **one ICAO baseline parse/convert path + national overlays** at lint, emit, and validate attach points (ADR-036) — not N independent converters.

5. **Implementation deferred:** unified `PipelineResult` runtime and #938 inspector require workflow orchestrator [#931](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/931). #925 delivers contract + mapping only.

6. **Fixtures:** profile-driven layouts under `profiles/<id>/<product>/{valid,invalid,expected-*}` remain F36 / #912 — reference `CA_ECCC` staged validate as pattern.

## Consequences

### Positive

- #925 acceptance without risky IR package extract
- Clear stage map for #931 workflows and #938 inspector
- `ca_eccc` staged validate is the reference implementation

### Negative / follow-ups

- IR remains untyped dict — tooling/inspector must stay product-aware until typed IR ADR
- Platform-wide `stages[]` not yet on lint/convert HTTP responses
- `/validate` 7-layer model remains separate — document dual paths in api corpus

## References

- [Context: canonical-met-staged-validation-925](../context/canonical-met-staged-validation-925.md)
- EV-925 session report `925-canonical-met-staged-validation.md`
