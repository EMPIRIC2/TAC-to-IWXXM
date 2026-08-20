# UAT script (Spec) — S071 / EV-061

**Mode:** Spec-development (`D-S071-e4`)  
**Sign-off:** product owner (Build `uat` after Spec→Build; UI preview at 11 per `D-S071-e2`)  
**Environment for Build:** local non-deployed preview `http://localhost:18000` (API `http://localhost:18001`); staging after 13  
**Corpus:** [Corpus: journeys] [Corpus: product §F7] [Corpus: product §F2] [Corpus: product §F6] [Corpus: product §F15]

Guest/public operator. Test accounts only if Auth is touched (not this cycle). No production PII.

| ID | Actor | Journey | Steps | Expected | Sign-off |
|----|-------|---------|-------|----------|----------|
| UAT-064 | Operator | UJ-064 | Open Validate IWXXM with sample IWXXM; observe decode panel | Item-by-item readable rows (parity with TAC); F7.s/F7.t still work | pending Build |
| UAT-065 | Operator | UJ-065 | Paste golden `SAUS31 KZNY` multi-METAR AHL; decode; convert; then malformed AHL | Per-report rows + convert-bulletin success; malformed → clear error | pending Build |
| UAT-066 | Operator | UJ-066 | Converter at ≥1024px; then resize below | Product Type + Profile no wrap; stack OK below 1024px | pending Build |
| UAT-067 | Operator | UJ-067 | Conversion parameters visible at ≥1024px | Parameters on one aligned bar with mode chrome | pending Build |
| UAT-068 | Operator | UJ-068 | Open **Lint & validation catalog** tab; click a source link | Code / description / level / working href; no planning ids in copy | pending Build |
| UAT-DEV-009 | Maintainer | UJ-DEV-009 | Open a `stage`→`main` PR (or docs dry-run of required checks) | Required: full unit + lint + typecheck + full E2E + Staging gate | pending Build |

Build mode records pass/fail in `reports/uat-report.md`. Do not run these steps in Spec mode.
