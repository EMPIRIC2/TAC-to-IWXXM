# ADR-054: Severity ladder and Strict operator control

**Status:** Accepted (EV-severity-strict-ui, 2026-11-01)  
**Date:** 2026-11-01  
**Corpus:** [Corpus: product §F7] [Corpus: product §F10] [Corpus: product §F2] [Corpus: api] [Corpus: adr/ADR-022] [Corpus: adr/ADR-023] [Corpus: adr/ADR-028] [Corpus: adr/ADR-045] [Corpus: adr/ADR-046]  
**Session:** `~/.cursor/workflow/EMPIRIC2/TAC-to-IWXXM/sessions/EV-severity-strict-ui`  
**Decisions:** D-SSU-01 … D-SSU-08

## Context

Workbench issue severities and the legacy Strict Validation checkbox did not share a raise policy. Operators need convert failures distinct from IWXXM validation failures they may ignore, plus dialect warnings and informational notes.

## Decision

1. **Severity ladder:** `critical` = convert failure; `error` = IWXXM validation failure (ignorable); `warning` = dialect/station/region non-adherence; `info` = operational awareness.
2. **Strict master (default OFF):** FE raises critical+error only. Server returns all issues. Strict ON raises the full ladder and drives `validate_output` when the validate step is on.
3. **Step toggles (v1):** lint, convert, validate only — no decode step ([Corpus: adr/ADR-045]).
4. **HTTP / download:** Convert success with IWXXM errors → HTTP 200, convert ok, download allowed with awareness. Critical convert failures keep hard-fail semantics.
5. **Operator copy:** plain language only; no internal doc refs.
6. **Wire:** additive `strict`, `strict_lint`, `strict_convert`, `strict_validate`; optional `raised_severities` on the convert response.

## Consequences

- Amends ADR-023 Strict Validation mapping to the unified Strict master.
- Soft-preview (ADR-022) still forces validation off.
- Registry codes (ADR-028) unchanged except optional later remaps.

## Alternatives considered

Dual Strict controls; stripping unraised issues; Decode step in v1; HTTP 422 on IWXXM-only errors — rejected per intake AQ2–AQ5.
