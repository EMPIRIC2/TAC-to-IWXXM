# ADR-022: Soft-preview via `preview=true` on `/api/v1/convert`

> **Status**: Accepted  
> **Date**: 2026-07-13  
> **Deciders**: User (S011 API contract Batch 1 option A)  
> **Stage**: 01-requirements  
> **Related**: feature-list F6/F7; api-contract; issues #665/#666  
> **Session**: S011-f7-operator-ui / EV-008  
> **Decision id**: D-S011-01-api-A

## Context

Operators need best-effort IWXXM and failed-span markers for editor highlighting when TAC is
partially invalid (#666), without inventing a second convert stack. Alternatives were a
dedicated `/preview-convert` route vs a flag on the existing convert endpoint.

## Decision

1. Soft-preview is **`preview=true`** (multipart/form field) on `POST /api/v1/convert`.
2. Preview may return **HTTP 200** with `ok: false`, best-effort IWXXM, and `failed_spans`
   (`start`/`end`/+message).
3. Default (`preview` omitted/false) keeps hard-fail HTTP semantics for non-quarantine
   failures. **EV-023 amend:** product-shaped unreliable TAC returns HTTP 200 with a
   `@translationFailedTAC` quarantine shell (successful convert of the quarantine
   document) — distinct from soft-preview `ok:false` + `failed_spans`.
4. Preview does **not** mean Schematron-passed publish.

## Alternatives Considered

| # | Alternative | Why rejected |
|---|-------------|--------------|
| 1 | Dedicated `POST /api/v1/preview-convert` | Extra route/client; user preferred flag on convert |
| 2 | Only client-side fake preview | Insufficient for real span/XML markers |

## Consequences

- Backend convert path grows a preview branch in tac2iwxxm / adapters (04/07).
- Frontend workbench and TC-F7-003 rely on this contract.
- OpenAPI/shared types updated when P1 codegen lands; until then api-contract is SoT.
