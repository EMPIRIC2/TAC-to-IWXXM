# CMO Week 1 evaluation TAC corpus

[Corpus: product §F6] [Corpus: tests] [Corpus: decisions]

**Authoritative source (do not rewrite TAC):**

`/Users/bigme/Desktop/TAC-to-IWXXM Testing/` — CMO / Brown University two-week NMHS
evaluation pack (extracted via macOS `textutil` from the Week 1 `.docx` datasets).

| File | Source document |
|------|-----------------|
| `metar.txt` | `Week 1 METAR Testing Dataset_1.docx` |
| `speci.txt` | `Week 1 – SPECI Testing Dataset-V1.docx` |
| `taf.txt` | `Week 1 – TAF Testing Dataset_2.docx` |
| `sigmet.txt` | `Week 1 – SIGMET Testing Dataset_4.docx` |

**Profile / version for matrix runs:** `annex3` / `2025-2`.

Typos, truncated forecasts, cross-product lines, and missing terminators are **intentional
corpus content** (authoritative). Classify converter outcomes; do not “clean” these files.

**Runner:** `uv run python scripts/cmo_week1_matrix.py`

**Session:** `EV-cmo-week1-test-sets`
