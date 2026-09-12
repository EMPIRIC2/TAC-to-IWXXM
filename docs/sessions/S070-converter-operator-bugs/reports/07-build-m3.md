# 07-build M3 — Profile + bulletin fields + log_level (#1002/#1005/#1004)

**Status:** implementation complete; 08-verify-build **PASS** (2026-08-18)  
**Corpus:** [Corpus: product §F7] [Corpus: product §F6] [Corpus: product §F29] [Corpus: api] [Corpus: tests §TC-EV060-1002] [Corpus: tests §TC-EV060-1005] [Corpus: tests §TC-EV060-1004]

## Tasks

| ID | Result |
|----|--------|
| T3.1 | Profile a11y + `profile=` tests in `tc-ev060-1002-profile-picker.workflow.test.tsx` |
| T3.2 | Labeled Profile next to Product (`data-testid="profile-type-select"`, `#param-profile`) |
| T3.3 | Bulletin ID / Issuing Center round-trip + invalid CCCC tests |
| T3.4 | Always-visible labeled fields; `parse_optional_bulletin_id` / `parse_optional_issuing_center`; IcaoAutocomplete `formatOnly` for WMO CCCC |
| T3.5 | `test_tc_ev060_1004_log_level.py` — DEBUG vs ERROR verbosity; JWT/Authorization not in logs |
| T3.6 | `set_request_log_level` ContextVar + logger filters; `SecretRedactFilter`; middleware restores logger levels |

## Notes

- No new npm/PyPI deps. Operator copy has no planning ids (`bulletinFieldsCopy`).
- `log_level` still filters client process issues; EV-060 also applies backend logger verbosity (`D-S070-log`).
- Starlette BaseHTTPMiddleware runs the route in a different Context than dispatch — token reset is best-effort; logger `setLevel` restore is the process-global cleanup.
- Fallback import stub includes `set_request_log_level` (`test_api_import_fallback_unit.py`).
- PR #1007 remains open; M3 commits stack on the same evolve branch. Promote held.

## Commits

- `926a0835` `[T3.2] feat: place labeled Profile next to Product at converter top`
- `2b3ca57f` `[T3.4] feat: expose Bulletin ID and Issuing Center with CCCC validation`
- `27882a7f` `[T3.6] feat: apply convert log_level to loggers`
- `35d56960` `[T3.6] fix: stub set_request_log_level in fallback import test`
