# verify-qa (Spec) — S070 / EV-060

**Mode:** Spec-development  
**Corpus:** [Corpus: tests] [Corpus: journeys]

## Required cases (must appear in 07/09/10)

| Area | TC | Notes |
|------|-----|-------|
| AHL | TC-EV060-1001-001..003 | Heading COM; malformed; FileConverter parity |
| IWXXM product | TC-EV060-1003-001..004 | Pass-through; not-XML; convert no-op; honor surfaces |
| Profile | TC-EV060-1002-001..003 | Top control; a11y; honor |
| Bulletin fields | TC-EV060-1005-001..003 | Round-trip; empty; invalid |
| log_level | TC-EV060-1004-001..002 | Verbosity; no secrets |
| Auth | TC-EV060-1006-001..004 | Playwright + facilitated UAT |
| CORS | H0c | Existing `test_cors_policy.py` |
| Live | H4–H5 | After UI ships (12/13) |

Vitest alone is not T3. No product code in Spec mode.
