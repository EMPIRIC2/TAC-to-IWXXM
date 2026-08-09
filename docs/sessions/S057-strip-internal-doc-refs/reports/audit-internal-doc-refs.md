# Audit — internal doc refs in operator / public surfaces (EV-048 / #951)

**Date**: 2026-08-08  
**Session**: S057-strip-internal-doc-refs  
**TC**: TC-EV048-001  
**Corpus**: [Corpus: api] [Corpus: product §F7] [Corpus: product §F21] [Corpus: tests]

## Scope scanned

| Surface | Method |
|---------|--------|
| OpenAPI | `app.openapi()` — all string values |
| FE catalogs | Soft-preview label/help, guest loss notice, Help URLs, privacy `STORAGE_INVENTORY` purposes, example `label`s |
| Client `detail` | Spot-check (T2.3); no common `HTTPException(detail=…ADR…)` found pre-build |

## OpenAPI hits (pre-M2 strip; **cleared in M2**) — 19 pattern matches / ~16 string surfaces

| Pattern | Location (summary) |
|---------|-------------------|
| ADR-031 | `/translation/statistics*` + `/validate` route descriptions |
| EV-040 / E11-31 | `/lint-issue-catalog` + `LintIssueCatalogEntryModel` |
| S011 / #702 / TC-F7-002 | `/decode-tac` + `DecodeSegmentModel` |
| TC-F6-030 | `/convert-bulletin` |
| ADR-024 | `/ingest-collect` + `include_nil_reasons` Form |
| ADR-022 | convert `preview` Form; `ConversionResponse.ok` / `failed_spans`; `FailedSpan` |
| ADR-025 | `DecodeTacResponse.summary` |

Comments-only ADR cites in `api.py` / utilities remain **out of scope**.

## Frontend

Operator-visible catalog strings are **clean** under the locked guard (Soft-preview already
plain language; exported `SOFT_PREVIEW_*` for scanning). ADRs/EV/S0/UJ remain in **comments**
and **tests** (allowed). **T3.3 Playwright skipped** (D-S057-04-t3 — no visible hits).

Note: privacy inventory purposes still mention product Fn IDs (`F5` / `F31`) — **not** in
the locked regex set; left as-is unless a follow-on cycle expands the guard.

## Client-facing errors

No hits in `detail=` paths containing ADR/EV/S0/TC/E##/#/Corpus (T2.3 spot-check).
Developer-path `NotImplementedError` ADR cites remain (not HTTP `detail`).

## Guard

Automated: `apps/backend/tests/unit/test_tc_ev048_openapi_internal_doc_refs.py` +
`apps/frontend/src/utils/internalDocRefGuard.test.ts` + `operatorVisibleCopy.ts`
(synthetic inject + catalog/OpenAPI scan). Post-M2 OpenAPI scan **green**.
