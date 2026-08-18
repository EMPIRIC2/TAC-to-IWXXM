# 01-requirements — S071 / EV-061 (delta)

> **Status**: in_progress — non-catalog deltas drafted; **catalog (#1014) blocked** on source URL research  
> **Date**: 2026-08-18  
> **Corpus**: [Corpus: product §F2] [Corpus: product §F6] [Corpus: product §F7] [Corpus: product §F9] [Corpus: product §F10] [Corpus: product §F15] [Corpus: product §F34] [Corpus: api] [Corpus: journeys] [Corpus: tests] [Corpus: tech-spec] [Corpus: deploy]

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
| D-S071-links | **11 URL failures** — user searching replacements; Build blocked |

## Artifacts touched

- `docs/feature-list.md` — F7.u / F7.v; F2/F6/F9/F34 deepen; summary rows
- `docs/user-journeys.md` — UJ-064..068, UJ-DEV-009
- `docs/test-plan.md` — UJ ↔ TC-EV061-* mapping
- `docs/deploy.md` — §Promote stricter gate (#1015)
- `docs/sessions/S071-…/reports/catalog-link-crawl-2026-08-18.md` — crawl results
- Catalog AC / UJ-068 **not finalized** until URLs fixed

## AHL context (for #1012)

- Heading: `T1T2A1A2ii CCCC YYGGgg [BBB]`
- Body: TAC reports, often `=`-terminated
- Golden: `SAUS31 KZNY 121200` + two METARs (live fixture)
- EV-060 fixed lint heading noise; #1011 is harness `file`→`files`; product decode/convert is #1012

## Next

1. User supplies replacement URLs for crawl failures
2. Finish catalog (#1014) Spec AC + any api-contract delta
3. 02-verify-plan Gate A
4. Spec→Build remains **closed**
