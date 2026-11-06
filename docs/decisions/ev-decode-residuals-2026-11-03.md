# Decision — Staging decode residuals: dual-write + per-typo warnings

**Date:** 2026-11-03  
**Session:** `EV-decode-residuals-2026-11-03`  
**Features:** F9, F15

## Decisions

1. **Inventory:** The operator residual meaning tables (TAF, METAR, SPECI, SIGMET) for the
   staging window ending 2026-11-03 are the acceptance list for this cycle, implemented in
   that product order.
2. **Decode surfaces:** Dual-write legacy `decode.py` explainers **and** pack YAML rules
   (ADR-045). Packs do not emit lint.
3. **Typos:** Explain as malformed in decode; register **one `tac-validate` warning code per
   typo pattern**; do not auto-rewrite TAC or change convert.
4. **No-source national practices:** Decode with plain-language meaning; do not invent
   document citations or put planning ids in operator attribution.
5. **Regression placement:** Tests live in `packages/tac-decoding/tests` and
   `packages/tac-validate/tests` so they run on PRs to `stage` via existing CI.
6. **E2E:** Required for Decoding library / lint catalog operator-visible surfacing.

## Alternatives rejected

| Option | Why not |
|--------|---------|
| Pack-only or legacy-only | Leaves live residuals or pack drift |
| Single shared typo code | Harder remediations and catalog clarity (operator chose per-pattern) |
| Auto-fix typos in convert | Out of scope; risk silent wrong IWXXM |
| Invented sources for no-source rows | Violates provenance honesty |

## Cite

[Corpus: product §F9] [Corpus: product §F15] [Corpus: tests] [Corpus: decisions]
[Corpus: adr/ADR-044] [Corpus: adr/ADR-045]
