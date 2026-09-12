# T3.1 — Gate C dig (E26-T4)

**Date**: 2026-07-31  
**Cycle**: EV-026 / S033  
**Gate C rule**: equality + `wmoPass` + #809 closed — **no soft escape**

| Criterion | Evidence | Status |
|-----------|----------|--------|
| ADR-032 `canonicalize_xml` equality | TC-EV025-008 green (`0022fb1`) | ✅ |
| Catalog `wmoPass` | `sigmet_multi_location_va` passer; TC-EV025-009 + Vitest (`5fb6bc4`) | ✅ |
| FIXTURE_GAPS | equality-pending note cleared (`008c9b2`) | ✅ |
| Soft path not re-litigated | Soft structural checks retained as diagnostics inside 008 | ✅ |
| #809 closed | T3.3 | ⏳ |

**Verdict**: encode/catalog Gate C **PASS** — proceed T3.2 verify + T3.3 issue close.
