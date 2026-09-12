# Verification report — M3 (S014 / EV-010)

**Date:** 2026-07-18  
**Branch:** `evolve/EV-010-package-publish-validation`  
**Scope:** M3 — iwxxm-validate Rust + schema subset + xsdata (T3.1–T3.9)

## Checks

| Check | Result |
|-------|--------|
| `make format-check` | PASS |
| `ruff check` (touched areas) | PASS |
| Focused pytest (100 collected) | **99 passed**, 1 skipped |

## M3 task summary

| Task | Commit (short) |
|------|----------------|
| T3.7a codegen regen smoke | `b1e53c9` |
| T3.7 commit pydantic models | `98e909a` |
| T3.8a validate Rust SDK tests | `f95fe7d` |
| T3.8 wire validate_iwxxm + dedupe | `8af040b` |
| T3.9 iwxxm-validate CLI | `b044871` |

(Earlier T3.1–T3.6 on same branch.)

## Next

Minor PR for M3 → then M4.
