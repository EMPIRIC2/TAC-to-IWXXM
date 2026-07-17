# Execution plan — S013 / EV-009 (F9 + F10)

> **Status**: approved (2026-07-16)
> **Branch**: `evolve/S013-live-decode-preview-ux`
> **Spec sources**: feature-list §F9/§F10; spec §packages/tac2iwxxm S013 delta,
> §packages/tac-validate S013 delta, §apps/frontend F9/F10 delta; api-contract §lint-tac/§decode-tac;
> test-plan TC-F9-001/002 + TC-F10-001/002; ADR-025; UJ-020/021

## Current State

- Phase: 1 (EV-009 build)
- Active milestone: M2
- Active task: T2.1 (in_progress)

## Tech Stack Summary (all existing — no new dependencies)

| Area | Choice |
|------|--------|
| Backend | Python 3.12, FastAPI, msgspec structs in packages |
| F9 engine | `packages/tac2iwxxm/src/tac2iwxxm/decode.py` — regex parsing + template strings (no LLM) |
| F10 lint | `packages/tac-validate/src/tac_validate/rules.py` — severity + fixes[] |
| Frontend | React 18 + Vite + Tailwind; CodeMirror 6; Vitest; Playwright (`apps/e2e`) |
| XML pretty-print | Small local formatter util (no new package) |
| Deploy | Unchanged — Render API image (`ghcr.io/...backend:main-latest`) + static frontend; no new env/CORS |

## Milestones & Tasks (TDD order)

### M1 — F9 backend: value-aware decode + summary (packages/tac2iwxxm + apps/backend)

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T1.1 | Test | Unit tests: value-aware explanations — METAR/SPECI/TAF fixtures (TC-F9-001 tokens: `18004KT`, gusts, VRB, `10SM`, `4000`, `M05/M12`, `A3011`, `Q1013`, `121251Z`, clouds, wx, FM/TEMPO/BECMG/PROB); offsets unchanged | test-plan TC-F9-001 | — | completed |
| T1.2 | Code | Implement value-aware explainers in `decode.py` (all 7 products; sparse best-effort) | spec §tac2iwxxm S013; F9 acc 1 | T1.1 | completed |
| T1.3 | Test | Unit tests: `summary` paragraph — flowing prose, "Not decoded: …" residual clause, "partial decode" wording, all 7 products | test-plan TC-F9-002 §1–3 | — | completed |
| T1.4 | Code | Summary builder; `DecodeResult.summary` (msgspec, additive) | spec §tac2iwxxm S013; ADR-025 §1 | T1.2, T1.3 | completed |
| T1.5 | Test | Backend API test: `POST /api/v1/decode-tac` returns `summary`; existing fields unchanged | api-contract §decode-tac | — | completed |
| T1.6 | Code | `DecodeTacResponse.summary` in `apps/backend/src/schemas/validation.py` + endpoint passthrough | api-contract §decode-tac | T1.4, T1.5 | completed |

### M2 — F10 backend: terminator lint UX (packages/tac-validate + apps/backend)

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T2.1 | Test | Unit tests: `MISSING_TERMINATOR` severity `info`, reworded copy, `ok: true` when otherwise clean, paired `add_terminator` fix with `replacement` = text + `=` | test-plan TC-F10-002 §1–2; ADR-025 §2 | — | in_progress |
| T2.2 | Code | `rules.py`: severity + copy + fix entry; verify `api.py` `ok` semantics untouched | spec §tac-validate S013 | T2.1 | pending |
| T2.3 | Test | Backend lint-tac contract test: severity + fixes passthrough to HTTP response | api-contract §lint-tac | T2.2 | pending |

### M3 — F9/F10 frontend (apps/frontend + apps/e2e)

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T3.1 | Test | Vitest: "Plain language" block at top of DecodePanel renders `summary` and updates on prop change | test-plan TC-F9-002 §4 | — | pending |
| T3.2 | Code | DecodePanel plain-language block; `api.ts` decode types gain `summary` | spec §frontend F9/F10 delta | T1.6, T3.1 | pending |
| T3.3 | Test | Vitest: `IwxxmPreviewPane` — pretty XML, badge ("Soft preview — not for publish" / "Passed"), failed-span count links, most-recent-only, responsive stacking | test-plan TC-F10-001 | — | pending |
| T3.4 | Code | `IwxxmPreviewPane` component; wire Soft-preview + Live IWXXM output into pane; plain-language soft-fail copy (code secondary) | spec §frontend F9/F10 delta; ADR-025 §3 | T3.3 | pending |
| T3.5 | Test | Vitest: console `info` styling distinct; "Add `=`" action appends terminator; editor affordance on hint span | test-plan TC-F10-002 §3–4 | — | pending |
| T3.6 | Code | Quick-fix action (console line + editor affordance) using lint `fixes[]`; info-level console rendering | spec §frontend F9/F10 delta | T2.3, T3.5 | pending |
| T3.7 | Test | Playwright T2: UJ-020 live-typing summary; UJ-021 preview pane + quick fix | test-plan TC-F9-002 §4, TC-F10-001/002 | T3.2, T3.4, T3.6 | pending |

### M4 — Verify & deploy (stages 08–13)

| Task | Type | Description | Stage | Depends On | Status |
|------|------|-------------|-------|------------|--------|
| T4.1 | Config | 08-verify-build — lint/typecheck/format/full suites | 08 | M1–M3 | pending |
| T4.2 | Test | 09-qa + 10-e2e (parallel) — full QA + UJ-020/021 E2E | 09/10 | T4.1 | pending |
| T4.3 | Docs | 11-verify-impl — per-Fn acceptance sign-off (F9 acc 1–4; F10 acc 1–4) | 11 | T4.2 | pending |
| T4.4 | Config | 12-verify-deploy — checklist; PR EV-009 → main | 12 | T4.3 | pending |
| T4.5 | Test | 13-deploy-smoke — deploy; H4–H5 + H6′ UJ-020/021 live smokes | 13 | T4.4 | pending |

## Data Dependencies

None — golden TAC fixtures already in repo test suites.

## Git Strategy

- Branch: `evolve/S013-live-decode-preview-ux` (open)
- Atomic commits per task: `[T1.1] test: …` etc.
- Minor PR checkpoints optional; single evolve PR `[EV-009] F9/F10 — live decode translations + preview UX` → `main` at M4 (T4.4)
- CI watch after every push (`scripts/ci/watch_github_ci.sh`)

## Phase Gate Check (C→D)

- [ ] All M1–M3 tasks completed; full pytest + Vitest + lint/typecheck green
- [ ] TC-F9-001/002 + TC-F10-001/002 green at T0/T2
- [ ] Decode contract backward-compatible (no removed fields/offsets)

## Phase Gate Log

| Gate | Date | Result | Notes |
|------|------|--------|-------|
| A→B | 2026-07-16 | passed | Phase A checkpoint approved ("Proceed") |
| B→C | 2026-07-16 | passed | Phase B checkpoint approved (D-S013-EV009-b-to-c-pass); 04 approved + 05 PASS |
