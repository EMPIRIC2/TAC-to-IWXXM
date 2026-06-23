# BUG-2026-06-22-issue-594-cor-traceability

| Field | Value |
|-------|-------|
| **Status** | resolved |
| **Feature** | F1 (METAR → IWXXM conversion) |
| **Severity** | high |
| **Classification** | code bug (GIFTs grammar) + UX gap (traceability) |
| **Remediation path** | local-first — deploy after user approval |
| **GitHub** | [#594](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/594) |

## Error description

Tester feedback ([#594](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/594)):

1. **COR handling** — METAR/SPECI reports with the correction indicator (COR) consistently produce `translationFailedTAC` in IWXXM output while the same reports without COR translate successfully.
2. **Input traceability** — Results show generic `manual_input` labels; original TAC input is not displayed alongside each converted result.
3. **`=` terminator** — Reporter notes resolved; no work unless repro reappears.

## Error logs

Local repro via `convert_tac_to_iwxxm` (2026-06-22):

| Input | `translationFailedTAC` |
|-------|------------------------|
| `METAR COR FAOR 101200Z 33003KT CAVOK 04/M00 Q1023=` | absent |
| `METAR FAOR 101200Z COR 33003KT CAVOK 04/M00 Q1023=` | **present** |
| `METAR FAOR 101200Z 33003KT CAVOK 04/M00 Q1023=` | absent |

## Symptoms & reproduction

| Field | User answer |
|-------|-------------|
| Symptom | Multiple — COR failure + traceability UX gap |
| Where | Production and local |
| When | Always (COR-after-time pattern) |
| Frequency | Every time |
| Repro env | Both |
| Severity | High |
| Evidence | Context doc + local repro |
| Tried | 00-context research — decoder grammar gap identified |

## Investigation

### Root cause (preliminary)

GIFTs `metarDecoder` TPG grammar: `METAR -> Type Cor? Ident ITime (NIL|Report)` — COR only allowed **before** station ID. ICAO-standard `METAR STID ddHHmmZ COR ...` places COR **after** the time group; parser fails → encoder emits `translationFailedTAC`.

Traceability: `ConversionResult` has no `tac_input` field; `FileConverter` stores `originalContent` client-side but only renders `originalName` and IWXXM XML in the results card.

### Spec conformance

| Spec | Section | Result |
|------|---------|--------|
| docs/feature-list.md | F1 conversion | in scope |
| ICAO Annex 3 COR placement | after time group | **implementation drift** in GIFTs grammar |
| docs/api-contract.md | ConversionResult | **gap** — no TAC echo field |
| REQ-016 | migration | no unrelated rewrites |

## Verification plan

| Field | User answer |
|-------|-------------|
| Success criterion | COR-after-time converts with CORRECTION status; each result shows source TAC |
| Checks | Full main CI parity (local) + gh on main after merge |
| Monitoring | User watches production after deploy |

## Repro test

| Test | Path | Status |
|------|------|--------|
| COR after time | `tests/bugs/test_bug_2026_06_22_issue_594_cor_after_time.py` | GREEN (3/3) |

## Fix

1. **GIFTs** — `METAR -> Type Cor? Ident ITime Cor? (NIL|Report)` in `metarDecoder.py`
2. **API** — optional `tac_input` on `ConversionResult`; populated for JSON, manual, and file conversions
3. **Frontend** — Source TAC panel in results; per-line manual mapping via `tac_input` / split lines

## Verification → Layer 1

- [x] Repro test RED → GREEN
- [x] GIFTs `test_cor`, `test_cor_after_time`, `test_failModes`
- [x] Frontend `FileConverter.test.tsx` (71 tests)
- [x] Full CI unit parity (local) — format, lint, typecheck, unit matrix pass
- [ ] Integration tests — blocked by port 18001 conflict (vecinita-embedding-dev)
- [ ] PR branch CI — pending
