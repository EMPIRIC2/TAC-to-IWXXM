# Context — EV-970 METAR validate fixtures + sticky hygiene

**Session:** EV-970-metar-validate-fixtures  
**Mode:** scoped evolve  
**Ticket:** [#970](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/970)  
**Date:** 2026-09-14  

[Corpus: product §F29] [Corpus: product §F7.q] [Corpus: tests] [Corpus: decisions]

## Goal

1. **S3 validate fill** — material reduction of `validate/metar_speci` `needs-fixture` (~859), with tracked residual / intentional `oos`.
2. **Sticky hygiene** — Product allowlist + pack-parent rollup so opaque codes never appear as Product rows; clarify sticky vs dashboard so PR comment is not misread as F7.q scores.

## Prior art

| Slice | Decision doc | Outcome |
|-------|--------------|---------|
| S1 convert | `docs/decisions/ev-970-s1-convert-fill.md` | convert NF → 0 (273 ready / 47 oos) |
| S2 lint | `docs/decisions/ev-970-s2-lint-fill.md` | lint NF → 0 (720 ready) |
| Sticky Skip | HF-quality-pr-comment-skips | NF/`oos` omitted from Skip column |

## Sticky vs dashboard (must not conflate)

| | Sticky (EV-052) | Dashboard (F7.q) |
|--|-----------------|------------------|
| Scripts / API | `collect_quality_pr_stats.py`, `format_quality_pr_comment.py` | `generate_quality_metrics.py` → `corpus_metrics.json` → `/api/v1/quality-metrics*` |
| Inputs | annex3 / iwxxm_us **goldens** (live C14N) + F29 YAML **inventory** | Official WMO corpus live convert/lint/validate |
| Match meaning | Golden equal **or** `status: ready` inventory slot | `match_pass` vs official XML |
| Audience | PR reviewers | Operators (`/quality`) |

**Operator decision (2026-09-14):** clarify + normalize — keep pipelines separate; normalize Product keys; label inventory vs live; document relationship. Do **not** unify sticky onto `corpus_metrics.json` this cycle.

## Opaque Product codes (repro)

Live sticky (2026-09-14 local collect) shows Match:2 rows for:

`???`, `BOGUS`, `NOT_A_PRODUCT`, `UNKNOWN`, `XYZ` under `annex3`.

**Root cause:** `tests/quality_matrices/testdata/lint/metar_speci/UNKNOWN_PRODUCT.yml` sad/edge_fail cases set `meta.product` to those strings so lint emits `UNKNOWN_PRODUCT`. Collector treats them as Product keys; only `METAR_SPECI`→`METAR` is normalized today.

**Fix direction:** allowlist known products; unknown → roll under pack parent (`metar_speci` → `METAR`) or omit from Product column; keep fixture TAC/meta intent for the lint rule; sticky footnote that matrix Match = ready inventory, not F7.q match_pass.

## Validate inventory

Baseline ~859 `needs-fixture` under `validate/metar_speci`. After S3/S3b/S3c Batch A+B+B2:

| Status | Count |
|--------|------:|
| ready | **860** |
| oos | **0** |
| needs-fixture | **0** |
| SCH negatives ready | **430** |

Ambition met: NF cleared; residual `document()`/`index-of` unblocked via native stand-ins + href mirror.

## Must-not-break

- F29 runners / inventory gate (TC-F29-*)
- EV-052 sticky job soft-fail behavior
- F7.q dashboard artifact generation / public API
- Convert/lint S1/S2 ready counts (no regress NF)

## Downstream docs delta (draft-docs)

- `docs/decisions/ev-970-s3-validate-fill.md` (new)
- F29 / EV-052 deepen notes: sticky Product allowlist + sticky≠dashboard
- Optional test-plan TC for product normalization
- #970 issue body refresh (stale ~1880 figure)

## Out

Non–METAR/SPECI matrix campaigns; sticky↔corpus metrics unification; 100% Annex-3 claim.
