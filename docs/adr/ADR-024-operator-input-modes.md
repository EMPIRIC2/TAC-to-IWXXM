# ADR-024: Operator input modes — AHL bulletin, COLLECT placeholder, log_level, nil reasons

> **Status**: Accepted  
> **Date**: 2026-07-15  
> **Deciders**: User (build deferred surfaces with placeholders where endpoints missing)  
> **Stage**: 07-build / evolve EV-008  
> **Related**: ADR-023; feature-list F6/F7; api-contract; UJ-011  
> **Session**: S011-f7-operator-ui / EV-008  
> **Decision id**: D-S011-ADR024-input-modes

## Context

ADR-023 wired dormant Convert params but deferred AHL bulletin UI, COLLECT/`.gz`, convert
`log_level`, and nil-reasons. Operators need those journeys in the UI now; some backends exist
(`/convert-bulletin`), some do not (COLLECT ingest).

## Decision

1. **Input mode control** on FileConverter: `TAC report` | `AHL bulletin` | `IWXXM COLLECT`.
2. **AHL bulletin** → real `POST /api/v1/convert-bulletin`; show `bulletin_meta` summary and
   per-report results/issues.
3. **COLLECT / `.gz`**: accept `.xml` / `.gz` uploads; inflate gzip client-side (and server-side
   in `read_uploaded_text`); call `POST /api/v1/ingest-collect` which returns **501** placeholder
   until member extract + validate ships. UI shows placeholder notice, not a silent failure.
4. **Log Level** = minimum severity for **conversion / validation / lint process messages** on
   input and output (Conversion log + workbench console). Also sent as multipart `log_level`
   (accepted/logged by API). Not server env `LOG_LEVEL`.
5. **Include Nil Reasons** → multipart `include_nil_reasons` (accepted; engine may still emit
   NIL shells until tac2iwxxm honors the flag — logged as placeholder behavior).

## Alternatives Considered

| # | Alternative | Why rejected |
|---|-------------|--------------|
| 1 | Wait for full COLLECT backend before UI | Blocks operator discovery of the path |
| 2 | Fake COLLECT success in UI | Misleading vs 501 honesty |

## Consequences

- Feature matrix: AHL bulletin UI becomes Yes; COLLECT UI = placeholder.
- Corpus updated (api-contract, feature-list, spec, evolve-decisions).
- Follow-up: implement `ingest-collect` member extract + honor `include_nil_reasons` in emit.
