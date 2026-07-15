# ADR-023: Wire dormant FileConverter convert parameters (OPMET operator parity)

> **Status**: Accepted  
> **Date**: 2026-07-15  
> **Deciders**: User (apply dormant-param + reference-gap suggestions for F7 UI)  
> **Stage**: 07-build / evolve EV-008  
> **Related**: feature-list F6/F7; api-contract `/convert`; ADR-022; OPMET IWXXM exchange guidelines; PPT-02  
> **Session**: S011-f7-operator-ui / EV-008  
> **Decision id**: D-S011-ADR023-convert-params

## Context

The operator Conversion Parameters panel exposed Bulletin ID, Issuing Center, On Error,
Log Level, Strict Validation, and Include Nil Reasons, but Convert only sent
`product` / `profile` / `iwxxm_version` / `preview` (and hardcoded `validate_output=false`).
That drifted from `.local/reference` OPMET / PPT-02 translation workflows and from the
existing multipart contract on `POST /api/v1/convert`.

## Decision

1. **Wire to Convert (multipart)** when the hard-convert path runs:
   - `bulletin_id` ← Bulletin ID
   - `issuing_center` ← Issuing Center
   - `stop_on_error` ← On Error **fail** (Skip/Warn → false)
   - `validate_output` + `validation_level` ← Strict Validation
     (`true` → `comprehensive`; `false` → `basic`)
2. **Soft-preview (`preview=true`)** keeps `validate_output=false` /
   `validation_level=basic` even when Strict Validation is checked (does not imply
   publish Schematron — ADR-022).
3. **Log Level** filters the workbench console **client-side** only. Convert has no
   `log_level` Form field; process `LOG_LEVEL` remains server observability env.
4. **Include Nil Reasons** stays a preference UI control only until the API exposes a
   matching field — not sent; labeled as such in UI.
5. **Upload accept** includes `.txt`, `.metar`, and `.tac`. AHL bulletin / COLLECT XML /
   `.gz` remain **Later** (bulletin UI → `/convert-bulletin`).

## Alternatives Considered

| # | Alternative | Why rejected |
|---|-------------|--------------|
| 1 | Remove unused Conversion Parameters | Loses operator controls that already match API |
| 2 | Add `log_level` Form field on convert | No backend consumer; scope creep vs console filter |
| 3 | Always validate on Convert | Soft-preview must stay non-publish; operators need an off switch |

## Consequences

- Hard Convert with Strict Validation on exercises UJ-002-style IWXXM validation in-band.
- Corpus: api-contract, feature-list F7 matrix, spec frontend F7 delta, evolve + product decisions.
- Still deferred: bulletin split UI, COLLECT/FTBP ingest, `include_nil_reasons`, server-side
  log_level on convert.
