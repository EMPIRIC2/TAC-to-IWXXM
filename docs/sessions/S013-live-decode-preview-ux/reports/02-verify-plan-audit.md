# 02-verify-plan audit — S013 / EV-009 (delta)

> **Scope**: F9/F10 delta sections written in 01-requirements (2026-07-16)
> **Documents audited**: feature-list.md (F9/F10), spec.md (S013 deltas), user-journeys.md
> (UJ-020/021), test-plan.md (TC-F9/F10), api-contract.md (lint/decode deltas), ADR-025

## Consistency pass (full cross-doc)

| # | Check | Result |
|---|-------|--------|
| 1 | Feature ↔ Spec — F9/F10 map to spec components | PASS (tac2iwxxm, tac-validate, frontend deltas + §F9/F10 section) |
| 2 | Feature ↔ Journey — F9→UJ-020, F10→UJ-021 | PASS |
| 3 | Journey ↔ Test — UJ-020/021 in test-plan UJ table → TC-F9-001/002, TC-F10-001/002 | PASS |
| 4 | Feature ↔ Test — acceptance bullets ↔ TC pass criteria | PASS |
| 5 | Spec ↔ Config — no new config/env keys claimed anywhere | PASS |
| 6 | Test ↔ Acceptance — F9 acc 1–4 / F10 acc 1–4 covered by TC criteria | PASS |
| 7 | Cross-doc naming | **FIXED** — severity enum said `warn` in api-contract/spec/ADR-025; frontend `LintIssue` type and `tac_validate.models` docstring use `warning`. All docs corrected to `error \| warning \| info`. |
| 8 | Scope boundaries — LLM excluded consistently (feature-list, spec, ADR-025) | PASS |
| 9 | Template conformance — static+api+worker; no new deployables; packages keep SoC (no FastAPI/Supabase imports implied) | PASS |
| 10 | Connectivity — UJ-020/021 reuse existing lint/decode/convert origins; H4–H5 unchanged; H6′ rows added | PASS |

## Statement audit

High-confidence statements (traceable to explicit user selections in intake E9-1…E9-8 and
Batches 1–2 "all recommended") — **auto-approved**:

| ID | Statement | Source |
|----|-----------|--------|
| S1.1 | Summary is one flowing paragraph, deterministic, backend-built | E9-6 + Batch1-Q1a |
| S1.2 | Residuals named via "Not decoded: …" clause | Batch1-Q2a |
| S1.3 | Sparse products: best-effort summary + "partial decode" wording | Batch1-Q3a |
| S1.4 | Value-aware decode for all seven products | E9-3 |
| S1.5 | "Plain language" block at top of decode panel, live | E9-4 |
| S2.1 | Dedicated side-by-side IWXXM preview pane anchors Soft-preview + Live IWXXM | E9-5 |
| S2.2 | Pane = pretty-printed XML + status badge + failed-span count linked to editor | Batch2-Q4a |
| S2.3 | Stacked below editor under `lg` | Batch2-Q5a |
| S2.4 | Quick fix on console line + editor affordance | Batch2-Q6a |
| S2.5 | MISSING_TERMINATOR → `info`; `ok` keyed to `error` only | Batch2-Q7 (confirmed) |
| S2.6 | Deploy this cycle (12–13) | E9-8 |
| S2.7 | `ok` computed from error-severity only is existing `tac_validate.api` behavior | [Repo: packages/tac-validate/src/tac_validate/api.py:28-31] |

Medium/low-confidence statements (agent-invented details) — presented to user:

| ID | Conf | Statement | Verdict |
|----|------|-----------|---------|
| S3.1 | Medium | Exact unit renderings: `A3011` → "Altimeter 30.11 inHg"; `121251Z` → "day 12 at 12:51 UTC"; `10SM` → "Visibility 10 statute miles"; wind "from 180° at 4 kt" | pending |
| S3.2 | Medium | Quick fix rides the existing lint `fixes[]` array as `code: add_terminator` with `replacement` = full text + `=` | pending |
| S3.3 | Medium | Preview pane shows only the **most recent** preview (no preview history) | pending |
| S3.4 | Low | Passing preview badge copy is "Passed" (vs e.g. "Valid IWXXM") | pending |

## Verdict

PASS pending S3.1–S3.4 review. One naming inconsistency found and fixed in place (severity
enum). No contradictions with existing Fn scope; REQ-016 not applicable (post-migration).
