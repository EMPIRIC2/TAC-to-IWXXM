# T3.9 — Optional `iwxxm-validate` CLI smoke (E10-39)

**Session:** S014 / EV-010  
**Task:** T3.9  
**Date:** 2026-07-18  
**Status:** completed  

## Delivered

| Item | Detail |
|------|--------|
| CLI | `iwxxm_validate.cli:main` → console script `iwxxm-validate` |
| Flags | `path`, `--version`, `--profile`, `--json` |
| Engine | `validate_iwxxm` (Rust prefer / lxml fallback) |
| Tests | `packages/iwxxm-validate/tests/test_tc_f13_cli_smoke.py` (6 passed) |

## Next

M3 complete → 08-verify-build / minor PR; then M4 (`tac2iwxxm[+validate]` + PyPI OIDC).
