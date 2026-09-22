# EV-docstring-multilang-bar — tech plan (standing note)

**Session:** EV-docstring-multilang-bar  
**Date:** 2026-09-22  
**Full plan:** `~/.cursor/workflow/EMPIRIC2/TAC-to-IWXXM/sessions/EV-docstring-multilang-bar/reports/tech-plan.md`

## Summary

| Item | Choice |
|------|--------|
| Branch / PR | `feat/EV-docstring-multilang-bar` → `stage` |
| Layout | `scripts/docs/` + Makefile targets below |
| Targets | `check-docs`, `test-doctest`, `check-docs-ts`, `check-docs-rust` |
| Deps | stdlib + existing pytest/vitest/cargo; inventory if new |
| Milestones | M1 checkers → M2 fill → M3 examples → M4 warn-clean; **one PR** |
| Connectivity | N/A |

See [ADR-048](../adr/ADR-048-multilang-inline-documentation-bar.md), D-EVDOC-*, TP-EVDOC-*.
