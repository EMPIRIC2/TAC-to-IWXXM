# UAT script (Spec) — S070 / EV-060

**Mode:** Spec-development (`D-S070-e4`)  
**Sign-off:** product owner (Build `uat` after Spec→Build)  
**Environment for Build:** local non-deployed preview `http://localhost:18000` (API `http://localhost:18001`); staging after 13  
**Corpus:** [Corpus: journeys] [Corpus: product §F7] [Corpus: product §F31]

Test accounts only. No production PII.

| ID | Actor | Journey | Steps | Expected | Sign-off |
|----|-------|---------|-------|----------|----------|
| UAT-059 | Operator | UJ-059 | Paste well-formed AHL METAR bulletin; lint/validate | No heading syntax flood; METARs checked | |
| UAT-060 | Operator | UJ-060 | Select product IWXXM; paste valid XML; then paste TAC | F2 result / no convert; TAC → not-XML | |
| UAT-061 | Operator | UJ-061 | Find Profile at converter top; change it; convert | Labeled; keyboard usable; profile applied | |
| UAT-062 | Operator | UJ-062 | Fill Bulletin ID + Issuing Center; convert | Values in output | |
| UAT-063 | Operator / logs | UJ-063 | Same convert DEBUG vs ERROR | Log verbosity differs; no JWT in DEBUG | |
| UAT-003 | Operator | UJ-003 / 046 | Register, login, logout, reload | Session persist; guest convert still works | **PASS** 2026-08-18 local :18000 (product owner) |

Build mode records pass/fail in `reports/uat-report.md`.
