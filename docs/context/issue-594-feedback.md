# Context — Issue #594 Testing Feedback

> **Mode**: scoped | **Slug**: issue-594-feedback | **Generated**: 2026-06-22  
> **Feature / workflow**: [GitHub #594](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/594) — COR handling + input traceability | **Status**: active

## Executive Summary

Follow-up tester feedback ([#594](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/594)) reports three items from METAR/SPECI batch testing. **End-of-message `=` handling** appears resolved per the reporter. **COR reports** consistently produce `translationFailedTAC` in IWXXM output while non-COR equivalents succeed — root cause traced to GIFTs `metarDecoder` header regex accepting only `METAR COR STID` (COR before station), not the ICAO-standard `METAR STID ddHHmmZ COR` (COR after time). **Input traceability** is a UX gap: results show generic `manual_input.txt` / `manual_input` labels; original TAC is stored client-side but not displayed, and the API `ConversionResult` schema has no `tac_input` field.

## Resolution Log

| ID | Category | Decision |
|----|----------|----------|
| R1 | Uncertainty | **`=` terminator** — reporter says resolved; no implementation work unless repro reappears |
| R2 | Decision | **COR fix** — GIFTs `metarDecoder` TPG grammar extension (`Type Cor? Ident ITime Cor?`) so ICAO COR-after-time headers decode without a backend preprocessor |
| R3 | Decision | **Traceability** — add `tac_input` to `ConversionResult` API and display original TAC in results UI |
| R4 | Scope | **#594 bundle** — COR (F1/GIFTs) + traceability (F1 UI); exclude unrelated #555 items already deferred in S001 |

## Scope & Constraints

**In scope (#594)**

| Item | Feature | Component | Priority |
|------|---------|-----------|----------|
| COR after time group fails decode | F1 | `packages/gifts/gifts/metarDecoder.py` | High — conversion correctness |
| Show original TAC per result | F1 | `apps/frontend/.../FileConverter.tsx`, optionally `apps/backend` schema | Medium — UX |
| Multi-line manual input per-result TAC mapping | F1 | `FileConverter.tsx` + `split_manual_entries` alignment | Medium — traceability accuracy |

**Out of scope (unless user expands)**

- #555 siblings: auto-clear input, in-app error log preview (deferred in S001 / EV-001).
- REQ-016: no unrelated migration rewrites.
- TAF COR (separate decoder in `tafDecoder.py` — only if reporter samples include TAF).

**Linked issues**

- Parent feedback thread: [#555](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/555) (initial recommendations).
- Recent UI work: [#656](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/656) / S001 (Convert & Convert&Send).

## Environment / Topology

No deploy topology change. Browser → `POST /api/v1/convert` unchanged. COR fix is server-side (GIFTs); traceability is primarily frontend display with optional API schema extension.

## Existing Infrastructure

| Asset | Path | Relevance |
|-------|------|-----------|
| METAR header regex | `packages/gifts/gifts/metarDecoder.py` L156 | `^(METAR\|SPECI)(\s+COR)?\s+[A-Z]{4}.+?=` — COR only before station |
| COR encoder flag | `packages/gifts/gifts/metarEncoder.py` L96–98 | Sets `reportStatus=CORRECTION` when `cor` in decoded TAC |
| Backend convert path | `apps/backend/src/utilities/gifts_adapter.py` `convert_tac_to_iwxxm` | Decoder → encoder; no COR normalization |
| Manual entry split | `apps/backend/src/api.py` `split_manual_entries` | One TAC per non-empty line |
| Conversion result schema | `apps/backend/src/schemas/conversion.py` `ConversionResult` | `name`, `content`, `source`, `size_bytes` — no TAC echo |
| Results UI | `apps/frontend/src/app/components/FileConverter.tsx` L1001–1061 | Shows `originalName` + XML only; `originalContent` not rendered |
| COR E2E (passing) | `apps/e2e/tac-file-conversion.e2e.spec.ts` L28–41 | Uses `METAR COR FAOR ...` (COR **before** station) |
| COR unit test (passing) | `packages/gifts/tests/test_metar_encoding.py` `test_cor` | `SPECI COR BIAR ...` pattern |
| Fail-mode test | `packages/gifts/tests/test_metar_encoding.py` L63–70 | `METAR USTR 311338Z COR=` — intentional fail (wrong order) |

## Cross-Reference Matrix

| Source | `=` terminator | COR before station | COR after time (ICAO) | TAC in results UI | API echoes TAC |
|--------|----------------|--------------------|-----------------------|-------------------|----------------|
| Issue #594 reporter | Resolved | Fails (reports) | Likely primary failure mode | Requested | Implied |
| GIFTs decoder regex | N/A | Supported | **Not supported** | N/A | N/A |
| ICAO Annex 3 | N/A | Valid variant | **Standard position** | N/A | N/A |
| Current E2E | N/A | Tested PASS | Not tested | Shows `manual_input.txt` | No |
| `ConversionResult` schema | N/A | N/A | N/A | N/A | No field |

### Repro evidence (local, 2026-06-22)

Via `convert_tac_to_iwxxm`:

| Input pattern | `translationFailedTAC` | `reportStatus` |
|---------------|------------------------|----------------|
| `METAR COR FAOR 101200Z ...` | absent | CORRECTION |
| `METAR FAOR 101200Z COR ...` | **present** | NORMAL |
| `METAR FAOR 101200Z ...` (no COR) | absent | NORMAL |
| `SPECI COR BIAR 290000Z ...` | absent | CORRECTION |

## Implementation Backlog

1. **COR decoder fix (R2)** — Extend `metarDecoder` header regex and/or TPG grammar so `COR` after `ddHHmmZ` sets `cor` flag and decodes body. Add regression tests mirroring ICAO examples; keep existing `METAR COR STID` path green.
2. **COR fail-mode audit** — Review `test_metar_encoding.py` fail cases; distinguish invalid COR placement from supported ICAO placement.
3. **Traceability — per-line mapping (R3)** — When backend returns `manual_input_1`, `manual_input_2`, map each result to its line TAC (frontend currently assigns full `manualInput` blob to every result when `index >= pendingFiles.length`).
4. **Traceability — display (R3)** — Show original TAC in results card (collapsible or side-by-side with XML); update a11y labels.
5. **Optional API field** — Add `tac_input` (or `source_tac`) to `ConversionResult`; back-add `api-contract.md`; update OpenAPI example in `api.py`.
6. **Tests** — GIFTs unit tests for COR-after-time; frontend unit test for TAC display; E2E with `METAR STID ddHHmmZ COR` pattern.
7. **Docs** — Link fix to #594 in evolve/hotfix artifacts; no feature-list Fn unless traceability becomes a named capability.

## Data & Credentials

No new credentials. Repro uses public METAR patterns; reporter did not attach failing sample strings — request samples if fix validation needs real-world bulletins.

## Unresolved Gaps

- **Reporter samples missing** — exact failing TAC strings not in #594; ⚠️ Assumed: ICAO after-time COR based on local repro matching symptom description.
- **TAF/SPECI with trends + COR** — not exhaustively probed; may surface secondary parser issues after header fix.
- **AMD COR** (`METAR AMD COR ...`) — fails in local probe; out of scope unless reporter confirms.

## Sources

- [GitHub #594](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/594) — issue body (2026-03-13)
- [Repo: packages/gifts/gifts/metarDecoder.py](packages/gifts/gifts/metarDecoder.py) — header regex L156
- [Repo: apps/frontend/src/app/components/FileConverter.tsx](apps/frontend/src/app/components/FileConverter.tsx) — results UI, L254–265 mapping
- [Repo: apps/backend/src/schemas/conversion.py](apps/backend/src/schemas/conversion.py) — `ConversionResult`
- [Repo: apps/backend/src/utilities/gifts_adapter.py](apps/backend/src/utilities/gifts_adapter.py) — `convert_tac_to_iwxxm`
- Local repro: `convert_tac_to_iwxxm` COR variants (2026-06-22)
