# EV-970 S1 — convert quality-matrix fill

[Corpus: product §F29] [Corpus: tests §TC-F29] [Corpus: product §F36]

| Date | Decision |
|------|----------|
| 2026-09-09 | Fill order convert → lint → validate |
| 2026-09-09 | S1 clears `convert/metar_speci` `needs-fixture` via ready variants + PARSE_ERROR negatives; residual → `oos` cite `#970 EV-970-S1 convert residual` |
| 2026-09-09 | Lint (718) + validate (859) deferred to S2/S3 under same ticket |

## Counts after S1

| Status | convert/metar_speci |
|--------|--------------------:|
| ready | 273 |
| oos | 47 |
| needs-fixture | 0 |
