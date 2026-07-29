# Execution plan — S026 / EV-020 (F24 / F25 + F9·F7.g deepen)

> **Status**: **approved** (2026-07-29) — E20-F1..F8 (1 / 1 / 3 / 1 / 2 / 1 / 1 / 1)  
> **Branch**: `evolve/EV-020-airmet-quality`  
> **Evolve cycle**: EV-020  
> **Features**: F24 (new); F25 (new); deepen F9 / F7.g / F6 / F3  
> **Spec sources**: feature-list §F24/F25; ADR-028; ADR-032; UJ-035/036; TC-F24/TC-F25;
> COVERAGE_MATRIX A1–A4 / W1–W4; api-contract S026; config-spec glossary; E20-*

## Current State

| Field | Value |
|-------|-------|
| **Active phase** | Phase C — 07-build (M6 remaining: T6.3–T6.5) |
| **Active milestone** | M6 — Smoke / verify / AC / deploy |
| **Active task** | T6.3 (next) |
| **Tasks** | 24 / ~28 completed (M0–M6 partial) |
| **Last updated** | 2026-07-29 |

## Tech Stack Summary

| Area | Choice | Source |
|------|--------|--------|
| Registry | Reuse ADR-028 `tac-validate`; add AIRMET rows | F24 |
| Golden compare | `canonicalize_xml` under default convert settings | ADR-032; E20-D3 |
| Products | AIRMET + METAR + SPECI + TAF (`taf-A5-1` **and** `taf-A5-2`) | E20-E1; S02.M1 |
| Catalog (FE) | Incremental unlock — SIGMET-first until each golden greens | E20-F4; S02.L2 |
| Glossary | Official/near-official + `decode_glossary.yaml` overrides; env `TAC2IWXXM_DECODE_GLOSSARY_PATH` | E20-E2; S02.L1 |
| Glossary YAML | Prefer workspace PyYAML if usable; else add **`pyyaml`** as sole new direct dep on `tac2iwxxm` | E20-F5=2 |
| Research | Full mining → `reports/wmo-quality-research-catalog.md` | E20-F2 |
| CI | Combined **`wmo-quality.yml`** (SIGMET+AIRMET+METAR/SPECI/TAF); migrate/replace `sigmet-quality.yml` | E20-F3=3 |
| New deps | Prefer none; PyYAML allowed per E20-F5=2 | E20-F5 |
| HTTP wire | Unchanged convert/decode shapes; richer decode strings only | ADR-032 |
| Deploy | API+FE redeploy if changed; H1–H3 if API; **H4–H5 required** | E20-F6 |
| Kill-switch | HARD themes; mid-build block → AskQuestion (no silent defer) | E20-F7 |

## Interview locks

| ID | Decision |
|----|----------|
| E20-F1 | Milestone order **1** — Research → AIRMET lint → AIRMET golden → METAR/SPECI → TAF → glossary+catalog → smoke |
| E20-F2 | Research **1** — full mining catalog |
| E20-F3 | CI **3** — `wmo-quality.yml` combined pack |
| E20-F4 | FE unlock **1** — incremental SIGMET-first |
| E20-F5 | Deps **2** — PyYAML only if not already usable transitively (else declare on tac2iwxxm) |
| E20-F6 | Deploy **1** — redeploy; H1–H3 if API; H4–H5 required |
| E20-F7 | Kill-switch **1** — AskQuestion; no silent defer |
| E20-F8 | Plan **1** — approve M0–M6; skip 05/06; B→C → 07 @ T0.1 |

## Milestones & Tasks (TDD order)

`evolve_cycle_id: EV-020` · `feature_ids: [F24, F25, F9, F7, F6, F3]`

### M0 — Research + combined WMO quality CI

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T0.1 | Docs | Mine WMO guidance + EUR Doc 014 + Annex/codes for AIRMET + METAR/SPECI/TAF; write `reports/wmo-quality-research-catalog.md` mapping → A1–A4 / W1–W4; cite SIGMET keep-green | E20-F2; #731 | — | **completed** |
| T0.2 | Docs | Link catalog from COVERAGE_MATRIX F24/F25 sections; cite-only paywall | F24/F25 acc | T0.1 | **completed** |
| T0.3 | Config | Add `.github/workflows/wmo-quality.yml` + `scripts/ci/run_wmo_quality.sh` + `make test-wmo-quality`; migrate SIGMET pack from `sigmet-quality.yml` (deprecate/remove old workflow + Makefile target or thin alias) | E20-F3=3 | T0.2 | **completed** |

### M1 — F24 AIRMET lint (themes A1–A2)

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T1.1 | Test | Accept/negative fixtures A1 (header / sequence / validity / FIR) | TC-F24-001/004; A1 | T0.2 | **completed** |
| T1.2 | Code | Registry rows + AIRMET rules for A1 | F24; ADR-028 | T1.1 | **completed** |
| T1.3 | Test | Fixtures A2 (phenomenon + intensity / STNR / WKN …) | A2 | T1.2 | **completed** |
| T1.4 | Code | Encode A2 checklist rules | F24 | T1.3 | **completed** |

### M2 — F24 AIRMET golden (theme A3)

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T2.1 | Test | Annex3 golden `airmet-A6-1a-TS`; M-xsd/M-sch stubs; root `iwxxm:AIRMET` | TC-F24-002/003; A3 | T1.4 | **completed** |
| T2.2 | Code | Convert fidelity — AirspaceVolume / posList / FL (close nil-geometry gap) | F6; #731 | T2.1 | **completed** |
| T2.3 | Docs | Mark A1–A3 closed or AskQuestion-deferred (E20-F7) | E20-F7 | T2.2 | **completed** |
| T2.4 | Test | A4 negatives + translation-failed adjacency | TC-F24-004; A4 | T2.3 | **completed** |

### M3 — F25 METAR / SPECI (themes W1–W2)

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T3.1 | Test | Golden manifests `metar-A3-1`, `speci-A3-2`; canonicalize vs vendor | TC-F25-001; W1–W2 | T2.4 | **completed** |
| T3.2 | Code | Convert fidelity METAR/SPECI toward vendor shapes | F6; F25 | T3.1 | **completed** |
| T3.3 | Test | XSD+SCH on those goldens | TC-F25-002 | T3.2 | **completed** |

### M4 — F25 TAF (theme W3)

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T4.1 | Test | Golden `taf-A5-1` + `taf-A5-2` (AMD/CNL peer) | TC-F25-001; E20-E1; S02.M1 | T3.3 | **completed** |
| T4.2 | Code | Convert fidelity TAF (incl. cancel/AMD) | F6; F25 | T4.1 | **completed** |
| T4.3 | Test | XSD+SCH on TAF goldens | TC-F25-002 | T4.2 | **completed** |
| T4.4 | Docs | Mark W1–W3 closed or AskQuestion-deferred | E20-F7 | T4.3 | **completed** |

### M5 — F9 glossary + F7.g / W4 catalog

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T5.1 | Test | TC-F9-003/004 — token meanings + registry load + OpenAIP miss | F9 deepen | T4.4 | **completed** |
| T5.2 | Code | Package `decode_glossary.yaml` + loader; env override; PyYAML per E20-F5 | ADR-032; S02.L1 | T5.1 | **completed** |
| T5.3 | Test | Vitest: Examples catalog = WMO-passers only; incremental unlock | TC-F25-003; E20-F4 | T5.2 | **completed** |
| T5.4 | Code | FE catalog gate + provenance; unlock products as goldens green | F7.g; W4; UJ-036 | T5.3 | **completed** |

### M6 — Smoke / verify / AC / deploy

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T6.1 | Test | API/workbench smoke AIRMET + WMO examples (lint/convert/decode) | TC-F24-005; TC-F25-004 | T5.4 | **completed** |
| T6.2 | Config | 08-verify-build — lint/typecheck/format/full suites | 08 | M0–M5 | **completed** |
| T6.3 | Test | 10-e2e — UJ-035 / UJ-036 (+ UJ-020/032 deepen) | 10 | T6.2 | pending |
| T6.4 | Docs | 11-verify-impl — per-Fn AC sign-off F24/F25/F9/F7.g | 11; C=1 | T6.3 | pending |
| T6.5 | Test | 13-deploy-smoke — redeploy if API/FE; H1–H3 if API; **H4–H5 required** | 13; E20-F6 | T6.4 | pending |

## Data Dependencies

| Asset | Needed by | Notes |
|-------|-----------|-------|
| Vendor `TAC-to-XML-Guidance.txt` + 2025-2 examples/XSD/SCH | M0–M4 | Read-only vendor |
| #731 AIRMET exceptional rules | M1–M2 | Issue body |
| EUR Doc 014 mining notes (existing) | M0–M1 | Public TAC shape |
| WMO examples: `airmet-A6-1a-TS`, `metar-A3-1`, `speci-A3-2`, `taf-A5-1`, `taf-A5-2` | M2–M4 | Vendor |
| F23 SIGMET goldens (keep green) | M0 CI | Regression |
| F3 / OpenAIP lookup paths | M5 | Soft-fail on miss |

## Git Strategy

- Branch: `evolve/EV-020-airmet-quality`
- Atomic commits per task: `[T1.1] test: …`
- Evolve PR to `main` after M6 / Phase D
- After push: `bash scripts/ci/watch_github_ci.sh`
- **HARD themes (E20-F7)**: if blocked mid-build → AskQuestion; do **not** silently defer
- Theme ids: “F24 theme An” / “F25 theme Wn” vs pipeline gates
- Combined workflow: `wmo-quality.yml` (E20-F3) — still run full `ci-cd.yml` on PRs

## Connectivity (H0c / H4–H5)

- No new CORS / `VITE_*` knobs expected
- FE catalog / decode copy → **H4–H5 required** after FE deploy (E20-F6)
- Re-run H0c if API image changes
- Staging secrets matrix: reuse existing rows

## Phase Gate Check (B→C)

- [x] Execution plan approved by user (E20-F8=1)
- [x] 05-verify-tech — **skipped** (Lean+build+11); 04-exit consistency PASS (below)
- [x] 06-tech-tooling — **skipped** (Lean+build+11; no new hooks in plan)

## 04-exit consistency (05 substitute)

| Check | Result |
|-------|--------|
| F24/F25 ↔ milestones M0–M6 | **PASS** |
| ADR-032 ↔ glossary + golden tasks | **PASS** |
| UJ-035/036 ↔ T6.1/T6.3 | **PASS** |
| TC-F24/F25 ↔ M1–M5 | **PASS** |
| E20-F3 `wmo-quality.yml` ↔ T0.3 | **PASS** |
| E20-F4 incremental catalog ↔ T5.3/T5.4 | **PASS** |
| E20-F5 PyYAML ↔ T5.2 | **PASS** |
| E20-F6 H4–H5 ↔ T6.5 | **PASS** |
| E20-F7 kill-switch ↔ T2.3/T4.4 | **PASS** |
| Template (static+api+worker) | **PASS** — no new deployable |
| New deps inventory | **PASS** — pyyaml only if T5.2 needs direct declare; back-add inventory then |
