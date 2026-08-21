# 01-requirements — S071 / EV-061 (delta)

> **Status**: ready for Gate A / digest — catalog link policy resolved (`D-S071-links-resolve`)  
> **Date**: 2026-08-18  
> **Corpus**: [Corpus: product §F2] [Corpus: product §F6] [Corpus: product §F7] [Corpus: product §F9] [Corpus: product §F10] [Corpus: product §F15] [Corpus: product §F34] [Corpus: api] [Corpus: journeys] [Corpus: tests] [Corpus: tech-spec] [Corpus: deploy] [Corpus: decisions §EV-061]

## Locked decisions (01)

| ID | Outcome |
|----|---------|
| D-S071-01-goal | Deepen F7/F2/F6/F9/F10/F15/F34 for #1010–#1015 |
| D-S071-01-docs | Delta standing: feature-list, journeys, test-plan, deploy; decisions |
| D-S071-01-preview | No local UI preview during 01 |
| D-S071-01-uj | New UJ-064..068 + UJ-DEV-009 |
| D-S071-01-validate | Decode panel parity with TAC item-by-item rows |
| D-S071-01-catalog-nav | Top-level nav tab/page |
| D-S071-01-catalog-scope | Lint **and** IWXXM validation catalog |
| D-S071-01-bars | No-wrap ≥1024px; stack OK below |
| D-S071-01-ahl | Golden multi-METAR + malformed clear errors |
| D-S071-01-ci | Required checks on stage→main: full CI + lint + typecheck + full E2E |
| D-S071-01-cors | No new origins |
| D-S071-links | Initial crawl 11 failures — user research |
| D-S071-links-resolve | 3-tier model; semantic IDs OK; verified operator hrefs; #1014 unblocked |

## Artifacts touched

- Standing: `feature-list.md`, `user-journeys.md`, `test-plan.md`, `deploy.md`
- Domain: `mining/ev061-catalog-source-replacements-2026-08-18.md`, `RULE_SOURCE_URLS.md` policy note, `TAC_VALIDATION.md` note
- Provenance retarget: `catalog_attribution.json`, `PROVENANCE_MAP.json`, `ISSUE_CATALOG.json` (operator `source_url` → verified landings; no planning ids in attribution)
- Session: this report + `catalog-link-crawl-2026-08-18.md`

## AHL context (for #1012)

- Heading: `T1T2A1A2ii CCCC YYGGgg [BBB]`
- Body: TAC reports, often `=`-terminated
- Golden: `SAUS31 KZNY 121200` + two METARs (live fixture)
- EV-060 fixed lint heading noise; #1011 harness `file`→`files`; product decode/convert is #1012

## Next

1. Approve 01 digest → **02-verify-plan** Gate A
2. Spec→Build remains **closed** until Spec band complete
