# Execution plan — S014 / EV-010 (F11–F14)

> **Status**: approved (2026-07-18)
> **Branch**: `evolve/EV-010-package-publish-validation`
> **Evolve cycle**: EV-010
> **Spec sources**: feature-list §F11–F14; spec package/backend deltas; api-contract ADR-026;
> test-plan TC-F11–F14; config-spec/deploy PyPI OIDC; ADR-016/026/027;
> context `package-publish-validation.md`; E10-1..40

## Current State

| Field | Value |
|-------|-------|
| **Active phase** | Phase B → C (tech plan) |
| **Active milestone** | — (not started) |
| **Active task** | — |
| **Tasks** | 0 / ~39 pending |
| **Last updated** | 2026-07-18 |

## Tech Stack Summary

| Area | Choice | Source |
|------|--------|--------|
| Backend HTTP | FastAPI; msgspec response encode (thin helper); Form/File intake; pydantic OpenAPI aliases | ADR-026, E10-38 |
| Packages IR | msgspec (existing) | ADR-016 |
| XSD codegen | **xsdata** + **xsdata-pydantic** → pydantic models; adapt msgspec/Rust follow-on | ADR-027, E10-40 |
| `iwxxm-validate` native | New `packages/iwxxm-validate/rust` via maturin; lxml parity until cutover | E10-36 |
| Schema wheel | Runtime subset only (XSD+SCH+catalogs for supported versions/profiles) | E10-34 |
| `tac2iwxxm` native | Existing `packages/tac2iwxxm/rust` + maturin (optional) | ADR-017 |
| PyPI publish | One GHA workflow + **package matrix**; OIDC trusted publishing; tags `*-v0.1.0` | E10-37, E10-25 |
| Wheels | manylinux + macOS + Windows for native pkgs; pure Python `tac-validate` | E10-39 |
| CLI | `tac-validate` console script; optional `iwxxm-validate` thin CLI | E10-39 |
| Perf gates | Soft in build; hard at publish: lib p95 ≤**0.85×** lxml baseline; HTTP p95 ≤**1.0×** pydantic map; wheel smokes | E10-35 |
| Deploy | PyPI tags + full Render 12–13 (msgspec HTTP) | E10-15 |
| FE | Update shared/OpenAPI TS types same cycle as breaking responses | E10-18 |

## Milestones & Tasks (TDD order)

### M1 — Layer cost matrix + benches (#703 / F11.1)

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T1.1 | Test | Bench harness stubs: lint, convert IR, XSD, Schematron, HTTP DTO encode (pydantic map vs msgspec) on single METAR, bulletin, golden IWXXM | TC-F11-002 | — | pending |
| T1.2 | Code | Implement harness; write p50/p95 to `docs/sessions/S014-…/reports/layer-cost-matrix.md` | F11 acc1; context R5 | T1.1 | pending |
| T1.3 | Config | Record absolute baselines used for 0.85× / 1.0× hard gates | E10-35 | T1.2 | pending |

### M2 — `tac-validate` domain depth + CLI + publish prep (F12)

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T2.1 | Test | Negative fixtures + diagnostics for METAR/SPECI/TAF full checklist; SIGMET/AIRMET/VAA/TCA template+gate coverage | TC-F12-001; E10-21 | — | pending |
| T2.2 | Code | Encode mined rules from `docs/domain/` (cite-only Annex); coverage matrix gates | F12; COVERAGE_MATRIX | T2.1 | pending |
| T2.3 | Test | CLI smoke tests for `tac-validate` entry point | F12 acc1; E10-39 | — | pending |
| T2.4 | Code | Console script + README install/usage | F12 | T2.3 | pending |
| T2.5 | Test | Clean-venv wheel install smoke (local) | UJ-DEV-005 | T2.4 | pending |

### M3 — `iwxxm-validate` Rust core + schema subset + xsdata codegen (F13 + F11.3)

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T3.1 | Config | Scaffold `packages/iwxxm-validate/rust` + maturin (mirror tac2iwxxm); keep hatch pure path | E10-36; ADR-017 | — | pending |
| T3.2 | Test | Parity suite stubs vs lxml isoschematron + golden IWXXM | TC-F13-001 | — | pending |
| T3.3 | Code | Rust well-formed + XSD + native Schematron/SVRL; Python SDK `validate_iwxxm` | F13; E10-22 | T3.1, T3.2 | pending |
| T3.4 | Config | Bundle **runtime schema subset** into wheel (exclude modelling/translation bulk); document subset in session report | E10-34; E10-6 | T3.1 | pending |
| T3.5 | Test | Soft benches vs lxml; assert path for hard 0.85× at publish | E10-35; TC-F11-002 | T3.3, T1.3 | pending |
| T3.6 | Config | xsdata + xsdata-pydantic codegen pipeline from pinned XSD; CI hook on vendor pin bumps | ADR-027; E10-40 | — | pending |
| T3.7a | Test | Codegen regen smoke — pinned XSD → pydantic models importable / non-empty | ADR-027; F11 acc4 | T3.6 | pending |
| T3.7 | Code | Commit/regenerate pydantic models; optional msgspec/Rust adapt helpers (follow-on) | F11 acc4; ADR-027 | T3.7a | pending |
| T3.8a | Test | Backend `/validate` (and convert+validate path) uses Rust SDK; no double heavy-layer run | F11.4; F13; api-contract | T3.3 | pending |
| T3.8 | Code | Backend F2 wrapper calls Rust SDK (dedupe double-run with convert+validate) | F11.4; F13 | T3.8a | pending |
| T3.9 | Test | Optional `iwxxm-validate` CLI smoke | E10-39 | T3.3 | pending |

### M4 — `tac2iwxxm[+validate]` + PyPI OIDC matrix (F14)

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T4.1 | Test | Convert sample METAR in clean venv; `[validate]` extra resolves both validators | TC-F14-002 | T2.5, T3.3 | pending |
| T4.2 | Code | `tac2iwxxm[validate]` extra deps; README | F14; E10-20 | T4.1 | pending |
| T4.3 | Config | Single GHA publish workflow + **matrix** (3 packages); OIDC `id-token: write`; tag filters | TC-F14-001; E10-37 | — | pending |
| T4.4 | Test | Workflow dry-run / act or CI on tag push to TestPyPI if configured; else checklist gate | pypi-release-checklist | T4.3 | pending |
| T4.5 | Config | manylinux + macOS + Windows maturin wheel jobs for native packages | E10-39 | T4.3, T3.1 | pending |

### M5 — msgspec high-churn HTTP + FE types (F11.2)

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T5.1 | Test | API tests: convert/validate/lint/decode (+ zip/bulletin) responses via msgspec path; auth unchanged | TC-F11-001; ADR-026 | — | pending |
| T5.2 | Code | Thin helper Struct→`msgspec.json.encode`→`Response`; pydantic OpenAPI aliases only; Form intake unchanged | E10-28, E10-38 | T5.1 | pending |
| T5.3 | Test | Soft HTTP bench ≤1.0× pydantic map baseline | E10-35 | T1.3, T5.2 | pending |
| T5.4 | Test | Vitest / OpenAPI-derived FE type updates for breaking shapes | E10-18; F11 | T5.2 | pending |
| T5.5 | Code | Frontend client types + workbench call sites | api-contract; UJ-022 | T5.4 | pending |
| T5.6 | Test | Re-run H0c CORS policy suite + confirm `METAR_CORS_ORIGINS` / staging secrets matrix still cover FE↔API after msgspec HTTP (no new CORS knobs) | connectivity-gates; TC-F11-001 | T5.2 | pending |

### M6 — Verify & deploy (stages 08–13)

| Task | Type | Description | Stage | Depends On | Status |
|------|------|-------------|-------|------------|--------|
| T6.1 | Config | 08-verify-build — lint/typecheck/format/full suites | 08 | M1–M5 | pending |
| T6.2 | Test | 09-qa + 10-e2e — QA + UJ-022/023 / DEV-005 | 09/10 | T6.1 | pending |
| T6.3 | Docs | 11-verify-impl — per-Fn F11–F14 acceptance | 11 | T6.2 | pending |
| T6.4 | Config | 12-verify-deploy — PyPI OIDC + Render checklist; evolve PR | 12 | T6.3 | pending |
| T6.5 | Test | 13-deploy-smoke — Render redeploy; H4–H5 + H6′ UJ-022; tag publish smokes (includes live CORS after T5.6) | 13 | T6.4, T5.6 | pending |
| T6.6 | Test | Hard publish gates: 0.85× lib, 1.0× HTTP, wheel smokes | E10-35 | T6.5 | pending |

## Data Dependencies

| Asset | Needed by | Notes |
|-------|-----------|-------|
| `vendor/schemas/*` pins | M3 bundle + xsdata | Read-only; subset for wheel |
| `docs/domain/` rules | M2 | Cite-only; no Annex prose in wheel |
| Golden IWXXM / TAC fixtures | M1–M3 benches/parity | Existing test-data |

## Git Strategy

- Branch: `evolve/EV-010-package-publish-validation`
- Atomic commits per task: `[T1.1] test: …`
- Single evolve PR `[EV-010] F11–F14 — package publish + validation stack` → `main` at M6
- After push: `bash scripts/ci/watch_github_ci.sh`
- Kill-switch (E10-30): AskQuestion only if must-ship item blocks; do not silently drop

## Phase Gate Check (B→C)

- [x] Execution plan approved by user
- [x] 05-verify-tech PASS
- [x] 06-tech-tooling for Rust/maturin/xsdata/PyPI workflow deps

## Phase Gate Log

| Gate | Date | Result | Notes |
|------|------|--------|-------|
| A→B | 2026-07-18 | passed | 02 PASS + 03 tooling; 34B commits |
| B plan | 2026-07-18 | approved | User 43A — M1–M6 execution plan |
| B tech audit | 2026-07-18 | passed | 05 PASS — 44A–47A applied |
| B→C | 2026-07-18 | pending | 06 done — await user checkpoint |
