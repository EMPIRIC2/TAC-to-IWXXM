# EV-adr048-doc-linters — tech plan (standing note)

**Session:** EV-adr048-doc-linters  
**Date:** 2026-09-22  
**Full plan:** `~/.cursor/workflow/EMPIRIC2/TAC-to-IWXXM/sessions/EV-adr048-doc-linters/reports/tech-plan.md`

## Summary

| Item | Choice |
|------|--------|
| Branch / PR | `feat/EV-adr048-doc-linters` → `stage` |
| Native | ruff D (numpy) · eslint-plugin-jsdoc · Rust `missing_docs` |
| Checkers | Harden private PY Parameters/Returns; TS methods/members |
| Targets | Existing `check-docs*` + `make lint` |
| Deps | `eslint-plugin-jsdoc` (inventoried); ruff D built-in |
| Milestones | M1 ruff D → M2 eslint+TS checker → M3 private PY → M4 CI/PR |
| Connectivity | N/A |

See [ADR-048](../adr/ADR-048-multilang-inline-documentation-bar.md), D-EVDOC-LINT-*, TP-EVDOC-LINT-*.
