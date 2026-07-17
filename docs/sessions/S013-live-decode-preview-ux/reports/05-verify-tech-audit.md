# 05-verify-tech audit — S013 / EV-009 (delta)

> **Scope**: execution-plan.md (M1–M4, 21 tasks) claims vs repo reality + spec corpus
> **Date**: 2026-07-16

## Statement audit (repo-verified)

| ID | Claim (execution plan) | Evidence | Verdict |
|----|------------------------|----------|---------|
| A1 | F9 engine target `packages/tac2iwxxm/src/tac2iwxxm/decode.py` exists with per-product explainers + msgspec `DecodeResult` | [Repo: decode.py — `_explain_metar_speci`/`_explain_taf`/`_explain_sigmet_airmet`/`_explain_advisory`; `DecodeResult` msgspec.Struct] | approved |
| A2 | `DecodeTacResponse` in `apps/backend/src/schemas/validation.py` lacks `summary` → additive field is the whole backend HTTP delta | [Repo: validation.py:295–300] | approved |
| A3 | `MISSING_TERMINATOR` currently `severity="error"` in `rules.py`; `ok` keyed to error-severity in `api.py` — downgrade to `info` flips `ok` for clean single reports with no other change | [Repo: rules.py:88–96; api.py:28–31] | approved |
| A4 | `fixes[]` plumbing exists end-to-end: `tac_validate.models.Fix` (code/message/replacement) → `LintFixModel` → frontend `LintFix` — quick fix needs no new API surface | [Repo: models.py:36; validation.py:261–274; api.ts:453–462] | approved |
| A5 | Severity vocabulary `error|warning|info` already typed in frontend (`api.ts:45`) and documented in `models.py` docstring — no type changes needed for info rendering | [Repo: api.ts:45; models.py:15] | approved |
| A6 | Frontend anchor points exist: `DecodePanel` (summary block target), `useLiveWorkbenchAssist` (live path), `SoftPreviewControl`/`LiveIwxxmToggle`/`FailedTacCue`/`WorkbenchConsole` (F10 wiring), `tacEditorSpans` (span hover affordance) | [Repo: apps/frontend/src/app/components/*, hooks/useLiveWorkbenchAssist.ts, utils/tacEditorSpans.ts] | approved |
| A7 | Test infra in place: package pytest suites (`packages/*/tests`), backend API tests, Vitest component tests, Playwright `apps/e2e` — no new harness needed | [Repo: packages/tac2iwxxm/tests/test_decode_tac.py; apps/frontend/src/app/components/DecodePanel.test.tsx; apps/e2e/f7-ui-api-connections.e2e.spec.ts] | approved |
| A8 | No new dependencies: XML pretty-print as local util; summary = template strings | dependency-inventory unchanged; user approved 04 Phase 4 | approved |
| A9 | Deploy path unchanged (backend image + static frontend; no env/CORS delta) → 12/13 reuse existing H4–H5 harness | [Corpus: tech-spec/deploy]; api-contract additive only | approved |
| A10 | `useLiveWorkbenchAssist` does **not** currently surface `fixes` from lint results — T3.6 must thread `fixes` through the hook (noted so build doesn't miss it) | [Repo: hooks/useLiveWorkbenchAssist.ts — destructures issues only] | approved (task note) |

## Consistency checklist (reference.md §Consistency)

- [x] F9/F10 in feature-list have spec sections + TC coverage (TC-F9/TC-F10)
- [x] No config-spec deltas claimed anywhere (no new params)
- [x] api-contract matches planned backend deltas (additive `summary`; severity enum)
- [x] test-plan and user-journeys reference same IDs (UJ-020/021 ↔ TC-F9/F10)
- [x] dependency-inventory — no new packages (A8)
- [x] No data-management deltas (fixtures in repo)
- [x] Execution-plan tasks trace to F9/F10 + spec sections (Spec Source column)
- [x] ADR-025 referenced inline in spec/feature-list/api-contract deltas
- [x] Template `static+api+worker` not contradicted (no new deployables)
- [x] No denied audit statements outstanding (02 audit: 0 denied)

## Verdict

**PASS** — plan is buildable as written; one build-time note (A10) attached to T3.6.
