# Execution plan — S015 / EV-011 (F15 + F6/F12 deepen)

> **Status**: approved (2026-07-19) — E11-31 catalog via `GET /api/v1/lint-issue-catalog`
> **Branch**: `evolve/EV-011-metar-lint-quality`
> **Evolve cycle**: EV-011
> **Features**: F15 (new); deepen F6 / F12 (METAR/SPECI)
> **Spec sources**: feature-list §F15; ADR-028; spec §tac-validate; UJ-024; TC-F15-001..005;
> research catalog R1–R8; COVERAGE_MATRIX; api-contract; E11-1..E11-31

## Current State

| Field | Value |
|-------|-------|
| **Active phase** | Phase C — 07-build |
| **Active milestone** | M3 — R1–R8 rules |
| **Active task** | T3.9 — R5 RMK fixtures (next) |
| **Tasks** | 16 / 35 completed (… T3.1–T3.8) |
| **Last updated** | 2026-07-19 |

## Tech Stack Summary

| Area | Choice | Source |
|------|--------|--------|
| Registry | `packages/tac-validate` `issue_registry.py` — frozen `IssueSpec` + `ISSUES` / `by_code()` | E11-20 / ADR-028 |
| Public codes | SCREAMING_SNAKE; optional `product`/`tags` on row, not in `code` | E11-21 |
| Catalog (docs) | `docs/domain/rules/ISSUE_CATALOG.md` (+ JSON); pytest drift | E11-22, E11-27 |
| Catalog (HTTP) | **`GET /api/v1/lint-issue-catalog`** — registry export for FE | E11-31 |
| FE catalog | Fetch catalog endpoint; tooltip + panel on workbench | E11-29, E11-31 |
| Lint fixtures | `packages/tac-validate/tests/fixtures/{accept,negative}/metar\|speci/` | E11-24 |
| Convert goldens | Extend `tac2iwxxm` `annex3_golden` + `iwxxm_us_golden` manifests | E11-24 |
| CI | Existing `ci.yml` / package pytest — no new GHA workflow | E11-27 |
| PyPI | Tag `tac-validate-v0.1.1` after F15 acceptance | E11-25 |
| Deploy | Full Render 12–13; H1–H3; **H4–H5 required** | E11-26, E11-29 |
| New deps | None | E11-30 |
| HTTP `/lint-tac` | Wire shape unchanged | E11-12 |

## Milestones & Tasks (TDD order)

`evolve_cycle_id: EV-011` · `feature_ids: [F15, F6, F12]`

### M1 — Issue registry + unknown-code CI + catalog stub (F15)

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T1.1 | Test | Registry API tests: `IssueSpec`, `by_code`, `issue_from`; reject unknown codes | TC-F15-001; ADR-028 | — | completed |
| T1.2 | Code | Add `issue_registry.py`; seed rows for existing emitted codes (`EMPTY_TAC`, `MISSING_*`, `MISSING_TERMINATOR`, …) | F15; E11-20 | T1.1 | completed |
| T1.3 | Test | CI gate: any `Issue.code` not in registry fails | TC-F15-001; E11-27 | T1.2 | completed |
| T1.4 | Config | Generate stub `ISSUE_CATALOG.md` (+ JSON); Makefile target `catalog-regen`; drift test | E11-22; E11-27 | T1.2 | completed |

### M2 — Migrate rule bodies onto registry (F15 / F12)

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T2.1 | Test | Existing METAR/SPECI/shared lint tests still green after migration (parity) | TC-F12-001; TC-F15-001 | T1.3 | completed |
| T2.2 | Code | `rules.py` + `product_rules.py` emit via registry helpers only (no `severity=` literals) | F15 acc2; ADR-028 | T2.1 | completed |
| T2.2a | Config | Escalate `issue_registry_guard` from warn → **error** on `severity=` in `rules`/`product_rules` | E11-30; E11-32 | T2.2 | completed |
| T2.3 | Test | Negative fixtures assert `expected_codes` ⊆ registry | TC-F15-003 | T2.2a | completed |

### M3 — METAR/SPECI rules R1–R5 + full R8 (F15 / F12)

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T3.1 | Test | Accept/negative fixtures for R1 (station/time/order) | Research R1; TC-F15-003 | T2.3 | completed |
| T3.2 | Code | Encode R1 rules + registry rows | F15; COVERAGE_MATRIX | T3.1 | completed |
| T3.3 | Test | Fixtures R2 (visibility SM/m/fractions/9999) | Research R2 | T3.2 | completed |
| T3.4 | Code | Encode R2 | F15 | T3.3 | completed |
| T3.5 | Test | Fixtures R3 (wx phenomena grammar) | Research R3 | T3.4 | completed |
| T3.6 | Code | Encode R3 | F15 | T3.5 | completed |
| T3.7 | Test | Fixtures R4 (clouds/CAVOK/VV/CB/TCU) | Research R4 | T3.6 | completed |
| T3.8 | Code | Encode R4 | F15 | T3.7 | completed |
| T3.9 | Test | Fixtures R5 (RMK AO1/AO2/SLP/P/T/PK WND) | Research R5 | T3.8 | pending |
| T3.10 | Code | Encode R5 (+ `iwxxm_us` awareness in lint messages) | F15; F6 deepen | T3.9 | pending |
| T3.11 | Test | Fixtures **full R8**: AUTO, COR, NIL, NOSIG, TEMPO, RVR, wind VRB/gust | E11-28; Research R8 | T3.10 | pending |
| T3.12 | Code | Encode full R8 pack (HARD — no deferral) | E11-23; E11-28 | T3.11 | pending |

### M4 — Goldens R6 + SPECI adjacency R7 (F15 / F6)

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T4.1 | Test | Expand annex3 + iwxxm_us golden manifests (METAR+SPECI); M-parse/M-xsd/M-sch stubs | TC-F15-002; TC-F6-020 | T3.12 | pending |
| T4.2 | Code | Convert fidelity fixes for new goldens (COR/NIL/RMK/US) — HARD themes must green; “scoped” = fixture depth within theme, not theme drop | F6 deepen; #732; E11-23 | T4.1 | pending |
| T4.3 | Test | R7 adjacency: METAR↔SPECI shared pack; no silent cross-product pass | TC-F15-005; UJ-024 | T4.2 | pending |
| T4.4 | Docs | Update COVERAGE_MATRIX METAR/SPECI rows; link research catalog | F15 acc3 | T4.3 | pending |

### Stage 06 deliverables (before 07-build; not a build milestone)

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T6.0 | Config | Stage 06: Makefile catalog regen; fixture README; optional pre-commit; keep `issue_registry_guard` at **warn** until T2.2 — then escalate to **error** (see T2.2a). **No new deps** | E11-30; E11-32 | Plan approval | completed |

### M5 — Catalog API + FE tooltips + smoke + verify/deploy (F15)

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T5.1 | Test | API tests for `GET /api/v1/lint-issue-catalog` (auth, shape, codes ⊆ registry) | api-contract; E11-31 | T1.4 | pending |
| T5.2 | Code | Backend route exporting registry (msgspec); OpenAPI alias | api-contract; E11-31 | T5.1 | pending |
| T5.3 | Test | Vitest: lint issue code tooltip resolves via catalog API client | TC-F15-004; E11-29 | T5.2 | pending |
| T5.4 | Code | FE: fetch catalog; tooltip + lightweight catalog panel on workbench | E11-29; UJ-024 | T5.3 | pending |
| T5.5 | Test | API smoke `product=metar` + `product=speci` lint+convert + catalog GET (H3) | TC-F15-004 | T4.3, T5.2 | pending |
| T5.6 | Config | 08-verify-build — lint/typecheck/format/full suites | 08 | M1–M4, T5.4, T6.0 | pending |
| T5.7 | Test | 09-qa + 10-e2e — UJ-024 / TC-F15-001..005 | 09/10 | T5.6 | pending |
| T5.8 | Docs | 11-verify-impl — per-Fn F15 + F6/F12 deepen sign-off | 11 | T5.7 | pending |
| T5.9 | Config | 12-verify-deploy — Render checklist + `tac-validate-v0.1.1` tag plan | 12; E11-25 | T5.8 | pending |
| T5.10 | Test | 13-deploy-smoke — API+FE redeploy; H1–H5 (H4–H5 required); re-run **H0c** CORS unit tests when API image changes | 13; E11-26; connectivity-gates | T5.9 | pending |

## Data Dependencies

| Asset | Needed by | Notes |
|-------|-----------|-------|
| `docs/domain/` cite tables | M3 rules | Cite-only; no Annex prose in wheel |
| `vendor/schemas/*` pins | M4 M-xsd/M-sch | Read-only |
| Existing annex3 / iwxxm_us goldens | M4 | Extend, don't replace |
| Research catalog R1–R8 | M3–M4 | Session report |

## Git Strategy

- Branch: `evolve/EV-011-metar-lint-quality`
- Atomic commits per task: `[T1.1] test: …`
- Minor PRs optional per milestone; evolve PR to `main` after M5 / Phase D
- After push: `bash scripts/ci/watch_github_ci.sh`
- **HARD R1–R8 (E11-23/28)**: if a theme blocks mid-build → AskQuestion; do **not** silently defer

## Connectivity (H0c / H4–H5)

- No new CORS / `VITE_*` knobs (E11-12 / E11-26)
- New GET is same API origin — covered by existing `METAR_CORS_ORIGINS`
- Re-run H0c if backend image changes; **H4–H5 mandatory** after FE catalog/tooltip deploy (E11-29)
- Staging secrets matrix: reuse existing rows

## Phase Gate Check (B→C)

- [x] Execution plan approved by user (E11-31)
- [x] 05-verify-tech PASS (E11-32)
- [x] 06-tech-tooling delta complete (T6.0 / stage 06)

## Phase Gate Log

| Gate | Date | Result | Notes |
|------|------|--------|-------|
| A→B | 2026-07-19 | passed | 01–03 complete; D-S015-EV011-phase-a-pass |
| B plan | 2026-07-19 | approved | User option 2 — GET lint-issue-catalog (E11-31) |
| B tech audit | 2026-07-19 | passed | 05 PASS — S1–S4 all option 1 (E11-32); 35 tasks; HARD docs aligned |
| B→C | 2026-07-19 | passed | D-S015-EV011-b-to-c=A — start 07-build @ T1.1 |
