# Context — validation policy remainders

**Session:** EV-validation-policy-remainders
**Issue:** [#1216](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1216)
**Date:** 2026-09-21
**Corpus:** [Corpus: product §F15] [Corpus: product §F2] [Corpus: adr/ADR-046] [Corpus: adr/ADR-045] [Corpus: tests] [Corpus: decisions]

## Problem

The merged policy-layers work loads an IWXXM output policy and resolves its id from the conversion profile. `POST /api/v1/validate` logs that id and calls `validate_iwxxm` without it, so select/ignore does not change the issue list operators already see. MatchPort is specified (ADR-046, TC-EV-VPL-003) and was not in milestones M1–M6. Detectors still scan TAC text themselves.

## Locked solution shape

Keep the D-VPL lock.

- IWXXM vendor `.sch` stays the source of asserts. The bound output policy enables or disables assert ids. XSD and well-formed stay outside select.
- Public HTTP stays a conversion profile id. No new policy field. The backend passes the resolved id into validation so the existing validate page shows the filtered issue list.
- MatchPort is a protocol on `tac-validate`. Callers may inject `tac-decoding` matches. Strict mode runs only when the caller passes a port. An empty port emits `MISSING_DECODE_MATCH` for every annex3 METAR theme detector. Omitting the port, including `/lint-tac`, keeps today's TAC scan. Other products scan TAC. When a match is present, the lint issue reuses the decode span. Decode packs do not emit lint.

## Touched components

| Component | Change |
|---|---|
| `packages/iwxxm-validate` | Apply the output policy inside validation |
| `apps/backend` | Pass the resolved policy id into the validator; no new HTTP field |
| `apps/frontend` | No new control; the existing issue list renders the report |
| `packages/tac-validate` | MatchPort plus the TC-EV-VPL-003 strict/fallback behavior |

## Must not break

- `/lint-tac` and `/validate` issue wire shape
- ADR-028 code stability
- Pack-engine boundary (decode does not emit lint)
- Vendor schemas read-only
- Default annex3 policy with an empty select still means the full non-preview assert set

## Memory

Session-open retrieve returned no accepted matches. Keep this cycle local to ADR-046 and the D-VPL lock.

## Docs to delta (draft-docs)

ADR-046 amend · lock note if a decision is tightened · feature-list F2/F15 · test-plan TC-EV-VPL-003 and TC-EV-VPL-005 pass criteria
