# verify-qa (Spec) — S071 / EV-061

**Mode:** Spec-development  
**Corpus:** [Corpus: tests] [Corpus: journeys] [Corpus: api] [Corpus: decisions §EV-061]

## Required cases (must appear in 07/09/10)

| Area | TC | Notes |
|------|-----|-------|
| Live bulletin harness | TC-LIVE-F6-030 / TC-EV061-1011 | Multipart field **`files`** |
| AHL decode + convert | TC-EV061-1012-001..004 | Golden rows; convert-bulletin; UI parity; `INVALID_AHL` |
| Validate IWXXM decode | TC-EV061-1010-001..003 | Item-by-item rows; additive fields; F7.s/F7.t |
| Product/Profile bars | TC-EV061-1013-001..003 | No-wrap ≥1024px; mode row; param bar + stack |
| Catalog tab | TC-EV061-1014-001..004 | Nav; lint+IWXXM rows; verified hrefs; EV-048 |
| stage→main gate | TC-EV061-1015-001..002 | Required-check inventory; merge blocked if red |
| CORS | H0c | Existing `test_cors_policy.py` — no new origins |
| Live UI | H4–H5 | UJ-064..068 after UI ships (12/13) |
| Live bulletin | H7 | After M1 harness fix |

Vitest alone is not T3. No product code in Spec mode. TC stubs live in [Corpus: tests] EV-061 section.

## Gaps vs 04 plan

None blocking. `INVALID_AHL` vs `bulletin_split_failed` alias/replace is a 07 decision, not a missing TC.
