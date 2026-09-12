# Domain-mine theme → deliverable map — S031 / EV-024

**Date**: 2026-07-30  
**Pin**: `vendor/manifest.json` → `bundles.iwxxm` tag **v2025-2**  
`commit_sha`: `35180cbe3bec0bc536a78714dd78d2e7ba60931f`  
**Local**: `vendor/schemas/iwxxm/2025-2/IWXXM/`

## TC → deliverable

| TC | Theme | Primary deliverable | Milestone |
|----|-------|---------------------|-----------|
| TC-EV024-001 | #804 folder + examples matrix | `docs/domain/mining/wmo-im-iwxxm-IWXXM-tree-mining-notes.md` | M1 |
| TC-EV024-002 | #807 org refresh | `docs/domain/mining/wmo-im-org-mining-notes.md` (refresh) | M2 |
| TC-EV024-003 | #773 US/MDL | `docs/domain/mining/iwxxm-us-metar-speci-pdf-mining-notes.md` (+ optional modelling notes) | M3 |
| TC-EV024-004 | Sample menu lists stems | `apps/frontend/.../examplesCatalog.ts` + `FIXTURE_GAPS.md` | M5 |
| TC-EV024-005 | Load into editor | Catalog load path + Vitest | M5 |
| TC-EV024-006 | Strict vs reference badge | `wmoReference?: boolean` + UI copy | M5 |
| TC-EV024-007 | Validate/CI wire | `WMOExamplesLoader` / `test_wmo_canonical_examples` (+ package goldens) | M6 |
| TC-EV024-008 | Promote + child issues | RULE_SOURCE_URLS / COVERAGE_MATRIX / canonicals + GH children | M4 / M7 |

## UJ / policy

| Item | Binding |
|------|---------|
| UJ-039 | Official WMO stems with TAC peers load from sample menu |
| ADR-032 amend | `wmoPass` (strict) vs `wmoReference` (loadable, may not equal) |
| S02.M2 | Product-in-scope + TAC peers; SWX/VONA/WAFS/QVACI deferred |
| Exclude | #806 WIS2; translation-failed happy-path; US-in-WMO catalog |

## Product-in-scope (sample menu / wire)

METAR · SPECI · TAF · SIGMET (incl. VA) · AIRMET · VAA · TCA

**Deferred from sample menu (S02.M2)**: SWX · VONA · WAFS · QVACI (roadmap / quality tickets)

## Seed inventory — vendor `IWXXM/examples/` (30 stems)

| Stem | TAC | XML | Seed surface (pre-M1 matrix) |
|------|-----|-----|------------------------------|
| metar-A3-1 | ✓ | ✓ | Catalog `wmoPass` ✅ |
| speci-A3-2 | ✓ | ✓ | Catalog `wmoPass` ✅ |
| taf-A5-1 | ✓ | ✓ | Catalog `wmoPass` ✅ |
| taf-A5-2 | ✓ | ✓ | Catalog `wmoPass` ✅ |
| sigmet-A6-1a-TS | ✓ | ✓ | Catalog `wmoPass` ✅ |
| sigmet-A6-1b-CNL | ✓ | ✓ | Catalog `wmoPass` ✅ |
| sigmet-A6-2-TC | ✓ | ✓ | Quality #738 / wire decision M1 |
| sigmet-VA-EGGX | ✓ | ✓ | Package golden; catalog? M1/M5 |
| sigmet-multi-location-VA | ✓ | ✓ | Wire decision M1 |
| airmet-A6-1a-TS | ✓ | ✓ | Catalog `wmoPass` ✅ |
| va-advisory-A7-2 | ✓ | ✓ | Catalog `wmoPass` ✅ |
| tc-advisory-A2-2 | ✓ | ✓ | Catalog `wmoPass` ✅ |
| metar-NIL-collect | ✓ | ✓ | Validate / COLLECT — not happy-path encode |
| taf-NIL-collect | ✓ | ✓ | Validate / COLLECT |
| *-translation-failed* | ✓ | ✓ | Quarantine — **not** sample menu |
| spacewx-A7-3/4/5 (+ alt) | ✓ | ✓ | Deferred sample menu (#740) |
| vona-A7-1 | ✓ | ✓ | Deferred (#741) |
| WAFS-Example | — | ✓ | Deferred (IWXXM-only) |
| qvaci-Example | — | ✓ | Deferred (IWXXM-only) |
| TAC-to-XML-Guidance.txt | — | — | Guidance re-scrape M4 |

## `IWXXM/` top-level (pin tree)

| Path | Kind | Likely relevancy |
|------|------|------------------|
| `examples/` | dir | P0 — corpus |
| `rule/` | dir | P0 — Schematron + RDF |
| `*.xsd` | files | P0 in-scope products; P2 WAFS/QVACI |
| `ReleaseNotes-IWXXM.txt` | file | Catalog / drift |
| `html/` | dir | Informative |
| `XMI/` | (may be absent on pin) | Informative if present |

## Code touchpoints (M5–M6)

| Surface | Path |
|---------|------|
| Examples catalog | `apps/frontend/src/fixtures/examples/examplesCatalog.ts` |
| Gaps table | `apps/frontend/src/fixtures/examples/FIXTURE_GAPS.md` |
| Catalog tests | `apps/frontend/src/fixtures/examples/examplesCatalog.test.ts` |
| WMO loader | `apps/backend/src/utilities/wmo_examples_loader.py` |
| Canonical examples tests | `apps/backend/tests/iwxxm/test_wmo_canonical_examples.py` |
| Package goldens | `packages/tac2iwxxm/tests/fixtures/annex3_golden/` |

## Prior art (refresh, don’t restart)

- `wmo-im-tier-a-mining-notes.md`, `wmo-im-org-mining-notes.md`
- `iwxxm-2025-2-reference-set-mining-notes.md`
- EV-023 / #800 (Guidance / SCH deltas already shipped)
