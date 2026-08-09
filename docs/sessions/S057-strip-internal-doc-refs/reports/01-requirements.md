# 01-requirements — S057 / EV-048

**Status**: completed — `D-S057-01-ac=1` (`D-S057-guard-s0=1`; UI preview `D-S057-ui-preview=1`)  
**Date**: 2026-08-08  
**Mode**: delta (deepen F7 + F21)  
**Issues**: [#951](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/951)

## Corpus

[Corpus: product §F7] [Corpus: product §F21] [Corpus: api] [Corpus: journeys]
[Corpus: tests] [Corpus: decisions]

## Standing doc deltas

| Doc | Change |
|-----|--------|
| `docs/feature-list.md` | F7 + F21 EV-048 deepen + AC tables |
| `docs/api-contract.md` | Operator-facing OpenAPI/error copy policy |
| `docs/user-journeys.md` | UJ-055 |
| `docs/test-plan.md` | TC-EV048-001..005 + UJ map |
| `docs/decisions/evolve-decisions.md` | Cycle EV-048 scope + AC table |
| `docs/decisions/requirements-decisions.md` | EV-048 section |

## Skipped (N/A this cycle)

- New ADR (hygiene deepen; no architecture change)
- `deploy.md` / dependency inventory — no new env or runtime deps
- H4–H5 live deploy — waived with 12/13 unless 11 requires

## Acceptance criteria (confirmed)

| AC | Criterion | TC |
|----|-----------|-----|
| AC1 | Audit findings listed in PR | TC-EV048-001 |
| AC2 | OpenAPI descriptions pass guard | TC-EV048-002 |
| AC3 | Operator UI string catalogs pass guard | TC-EV048-003 |
| AC4 | Client-facing API errors pass guard | TC-EV048-004 |
| AC5 | Automated guard fails on synthetic regression | TC-EV048-005 |
| AC6 | Soft-preview etc. operator-friendly; tests updated | TC-EV048-002/003 |

## Guard patterns (locked)

`\[Corpus:`, `docs/sessions/`, `docs/feature-list`, `\bADR-\d+\b`, `\bEV-\d+\b`, `\bS0\d+\b`

## UI preview

Non-deployed local: http://localhost:5173/

## Next

**02-verify-plan** (Gate A).
