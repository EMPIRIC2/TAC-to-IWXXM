# ADR-025: Deterministic plain-language decode summary + terminator lint UX

> **Status**: Accepted  
> **Date**: 2026-07-16  
> **Deciders**: User (S013 intake E9-3/E9-6/E9-7; Batch 1–2 all-recommended)  
> **Stage**: 01-requirements  
> **Related**: feature-list F9/F10; api-contract §lint-tac/§decode-tac; test-plan TC-F9/TC-F10  
> **Session**: S013-live-decode-preview-ux / EV-009  
> **Decision id**: E9-6 / E9-7 (evolve-decisions §EV-009)

## Context

The F7 decode panel shows generic group labels ("Temperature / dewpoint (°C)") without parsed
values, and users asked for a natural-language description of the report. Separately, two
messages confused users on single pasted reports: `MISSING_TERMINATOR` (error-severity lint
for a missing `=`, common when pasting from feeds that omit it) and `LAYER12_SOFT_FAIL`
(soft-preview status presented as an error code). Alternatives included frontend-composed
summaries, LLM-generated text, and keeping terminator severity as-is.

## Decision

1. **Backend deterministic summary (F9)**: `packages/tac2iwxxm` `decode_tac` builds a
   plain-language `summary` paragraph from parsed token values — no LLM, fully unit-testable.
   `POST /api/v1/decode-tac` returns it additively. Explanations become value-aware for all
   seven products (sparse products best-effort with "partial decode" wording); residuals are
   named in a trailing "Not decoded: …" clause.
2. **Terminator lint is advisory (F10)**: `packages/tac-validate` severity vocabulary is
   `error | warning | info` (already documented in `models.py`; rules emit only `error` today);
   `MISSING_TERMINATOR` moves `error` → `info` with copy "Reports in bulletins end with '='
   — add it before publishing". `ok` stays keyed off `error` issues, so an otherwise-clean
   single report lints `ok: true`. A paired `add_terminator` fix entry powers a one-click
   "Add `=`" quick fix (console line + editor affordance).
3. **Soft-fail is a status, not an error (F10)**: `LAYER12_SOFT_FAIL` remains the API code,
   but UI presents plain-language status copy ("Soft preview — not for publish", cause, next
   step) in the new IWXXM preview pane badge and console.

## Alternatives Considered

| # | Alternative | Why rejected |
|---|-------------|--------------|
| 1 | Frontend-composed summary from segments | Duplicates parsing logic in TS; not reusable by API/worker consumers; harder to test |
| 2 | LLM-generated summary | Non-deterministic, latency/cost, unacceptable for an ops tool |
| 3 | Keep MISSING_TERMINATOR as error | Blocks `ok` and alarms users pasting single reports from feeds that omit `=` |
| 4 | Drop the terminator rule entirely | Bulletin publishing still requires `=`; hint retains guidance |

## Consequences

- Decode response contract grows `summary` (additive; TC-F9-002 guards back-compat).
- `tac-validate` severity enum documented as `error | warning | info`; downstream consumers
  (worker, CI gates) unaffected because `ok` semantics keyed to `error` are unchanged.
- Frontend needs info-level console styling, quick-fix action, and the preview pane (F10).
- Summary wording becomes part of golden-fixture tests; copy changes are test changes.
