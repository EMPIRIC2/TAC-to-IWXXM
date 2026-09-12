# PR remediation — PRM-005 / PR #685

**Cycle**: PRM-005 · **Review**: PRR-005 · **Branch**: `fix/S002-issue-594-feedback`  
**Date**: 2026-06-23 · **Session**: S002-issue-594-feedback

## Summary

| Metric | Count |
|--------|------:|
| Fixed | 5 |
| Deferred | 0 |
| Won't fix | 0 |

## Commits

| SHA | Finding(s) | Description |
|-----|------------|-------------|
| `5dc31e5` | F-002, F-005 | TAC typo; R2 docs — grammar-only COR fix |
| `010eb12` | F-003, F-006 | FileConverter manual-first result mapping + unit test |
| `9cdec46` | F-004 | E2E pre count scoped to results region (4 blocks) |

## Findings

- **F-002** — Bug report spec table: `tac echo` → `TAC echo`
- **F-003** — FileConverter assumed file results before manual; flipped to match API
- **F-004** — `tac-file-upload-database.e2e.spec.ts` expects 4 `<pre>` with Source TAC panels
- **F-005** — Context doc R2 no longer references nonexistent backend preprocessor
- **F-006** — `split(/\r?\n/)` + manual-first index logic aligned with `split_manual_entries`

## CI

Pending after push — watch `ci-cd.yml` on `fix/S002-issue-594-feedback`.

## Follow-up

- Re-review (18-pr-review) offered after CI green
