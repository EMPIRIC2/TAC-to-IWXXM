# ADR-054: Severity ladder and Strict operator control

**Status:** Accepted (EV-severity-strict-ui, 2026-11-01); amended 2026-11-04 for partial decode  
**Date:** 2026-11-01  
**Corpus:** [Corpus: product §F7] [Corpus: product §F10] [Corpus: product §F2] [Corpus: api] [Corpus: adr/ADR-022] [Corpus: adr/ADR-023] [Corpus: adr/ADR-028] [Corpus: adr/ADR-045] [Corpus: adr/ADR-046]  
**Session:** `~/.cursor/workflow/EMPIRIC2/TAC-to-IWXXM/sessions/EV-severity-strict-ui`  
**Decisions:** D-SSU-01 … D-SSU-08

## Context

The workbench issue severity scale and the legacy Strict Validation checkbox did not share one raise policy. Operators need convert failures to stay distinct from IWXXM validation failures that they may ignore. Operators also need dialect warnings and informational notes.

## Decision

1. **Severity ladder:**
   - `critical` — convert failure (Traditional Alphanumeric Code (TAC) did not become IWXXM)
   - `error` — IWXXM validation failure (operator may ignore for download awareness)
   - `warning` — dialect, station, or region non-adherence, **and** partial decode when unread TAC tokens stay after decode (`PARTIAL_DECODE`)
   - `info` — operational awareness
2. **Strict master (default OFF):** The frontend raises `critical` and `error` only. The server returns all issues. When Strict is ON, the frontend raises the full ladder and sets `validate_output` when the validate step is on.
3. **Step toggles (v1):** lint, convert, and validate only — no decode step ([Corpus: adr/ADR-045]).
4. **HTTP / download:** Convert success with IWXXM errors → HTTP 200, convert ok, download allowed with awareness. Critical convert failures keep hard-fail semantics.
5. **Operator copy:** plain language only; no internal doc refs.
6. **Wire:** additive `strict`, `strict_lint`, `strict_convert`, `strict_validate`; optional `raised_severities` on the convert response.
7. **Partial decode wiring (2026-11-04):** When decode leaves residual TAC tokens, the convert path and the TAC lint path give registry code `PARTIAL_DECODE` at severity `warning`. The pack engine does not give this lint code. Convert failure and IWXXM validation failure keep the critical and error maps above.

## Consequences

- Amends ADR-023 Strict Validation mapping to the unified Strict master.
- Soft-preview (ADR-022) still forces validation off.
- Registry codes (ADR-028) gain `PARTIAL_DECODE` as a warning row.
- Live thirty-day eval pipeline stages map as: partial decode → warning; convert hard fail → critical; IWXXM native fail → error.

## Alternatives considered

Dual Strict controls; stripping unraised issues; Decode step in v1; HTTP 422 on IWXXM-only errors — rejected per intake AQ2–AQ5.
