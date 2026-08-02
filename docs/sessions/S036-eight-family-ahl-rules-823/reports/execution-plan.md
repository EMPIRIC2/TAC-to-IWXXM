# Execution plan — S036 / EV-029 (#823 eight-family AHL / rules)

> **Status**: **approved** (2026-08-01) — `D-S036-04-plan` = 1; Gate B PASS → 07 @ T0.1  

> **Branch**: `evolve/EV-029-eight-family-ahl-rules`  
> **Evolve cycle**: EV-029  
> **Features**: F28 (new); deepen F6 / F6.bulletin / F12 / F2 / F13 / F15 / F20 / F23 / F24 / F26 / F27  
> **Spec sources**: feature-list §F28 + EV-029 deepen; spec §S036/EV-029; UJ-043;
> TC-EV029-001..008; TC-F28-001..006; api-contract `product=swxa`; E29-*; S02.M1–L1;
> #823 / #738 / #820 / #740

## Current State

| Field | Value |
|-------|-------|
| **Active phase** | Phase C — 07-build |
| **Active milestone** | M1 — AHL / COM / shared bulletin model |
| **Active task** | T1.1 |
| **Tasks** | 6 / 48 completed |
| **Last updated** | 2026-08-01 |

## Tech Stack Summary

| Area | Choice | Source |
|------|--------|--------|
| Template | `static+api+worker` | template |
| AHL / filename | Extend `packages/tac2iwxxm` bulletin/AHL; dissemination imports | E29-T2=1 |
| Registry | ADR-028 `tac-validate`; add/extend family + SWXA rows | F12/F15/F28 |
| Golden compare | ADR-032; SWXA may use `wmoReference` v1 | S02.L1 |
| Runtime SoT | Vendor IWXXM **2025-2** | context |
| API | Additive `product=swxa` enum in 07 (docs already) | S02.M1; E29-M=2 |
| Mining | **Full re-mine all eight families in M0 before any Phase B code** | E29-T3=2 |
| CI | **Separate workflow per family** + root `ci.yml` | E29-T4=2 |
| New deps | Prefer none; AskQuestion per new dep | E29-T5=1 |
| Deploy | API redeploy when behavior/`swxa` ships; H1–H3; **H4–H5 waived** unless FE Examples unlock | E29-T6=1 |
| Kill-switch | HARD themes; mid-build block → AskQuestion (no silent defer) | E29-T8=1 |
| SIGMET Ms | Three milestones: gen / VA / TC | E29-T7=1 |
| ADR | New ADR only if AHL shared API needs it; else amend existing | E29-T2 |

## Interview locks

| ID | Decision |
|----|----------|
| E29-T1 | **3** — one milestone per product (METAR/SPECI/TAF separate) |
| E29-T2 | **1** — AHL in `tac2iwxxm` |
| E29-T3 | **2** — full re-mine before Phase B |
| E29-T4 | **2** — separate CI workflow per family |
| E29-T5 | **1** — no new deps without AskQuestion |
| E29-T6 | **1** — redeploy API; H1–H3; H4–H5 waive unless FE |
| E29-T7 | **1** — SIGMET gen / VA / TC = three milestones |
| E29-T8 | **1** — HARD kill-switch + AskQuestion |
| E29-T9 | **1** — Approve M0–M12 (48 tasks); Gate B → 07 @ T0.1 |

## Milestones & Tasks (TDD order)

`evolve_cycle_id: EV-029` · `feature_ids: [F28, F6, F12, F2, F13, F15, F20, F23, F24, F26, F27]`

**Gate:** No M1+ code/tests until **M0 complete** (E29-T3=2).

### M0 — Full eight-family re-mine + promote (Phase A)

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T0.1 | Docs | Theme map: TC-EV029 / TC-F28 → families × lint/convert/validate × report states × TAC shapes (`reports/eight-family-theme-map.md`) | TC-EV029-001/006; UJ-043 | — | **completed** |
| T0.2 | Docs | Full re-mine eight families (AHL/COM + METAR…SWXA) via `mine-domain-sources`; session mining notes under `reports/mining/` | E29-T3; #823 | T0.1 | **completed** |
| T0.3 | Docs | Example inventory: TAC shapes + IWXXM peers (or `wmoReference` / child) | TC-EV029-002 | T0.2 | **completed** |
| T0.4 | Docs | Promote durable rules → COVERAGE_MATRIX + canonicals; child-issue residuals (S02.M3) | TC-EV029-001; #823 | T0.3 | **completed** |
| T0.5 | Docs | AHL/`T1T2`/BBB/`bulletinIdentifier` design note (tac2iwxxm surface for dissemination) | TC-EV029-003; E29-T2 | T0.4 | **completed** |
| T0.6 | Docs | M0 exit checklist — AskQuestion only if HARD gap blocks Phase B | E29-T8 | T0.5 | **completed** |

### M1 — AHL / COM / shared bulletin model (F6.bulletin)

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T1.1 | Test | AHL/`T1T2`/BBB/filename fixtures (accept + negative) | TC-EV029-003 | T0.6 | pending |
| T1.2 | Code | Extend `tac2iwxxm` bulletin/AHL API; dissemination-importable | E29-T2; F6.bulletin | T1.1 | pending |
| T1.3 | Config | Add `ahl-com-quality.yml` (path-filtered) | E29-T4 | T1.2 | pending |
| T1.4 | Docs | Matrix/COM rows closed or child-issued | #823 B1 | T1.3 | pending |

### M2 — METAR (F15 deepen)

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T2.1 | Test | METAR gap fixtures (lint + convert + validate) from M0 | TC-EV029-007; F15 | T1.4 | pending |
| T2.2 | Code | Registry/encode/validate deltas for METAR gaps | F15; F6 | T2.1 | pending |
| T2.3 | Config | `metar-quality.yml` (or extend existing METAR pack) | E29-T4 | T2.2 | pending |

### M3 — SPECI (F20 deepen)

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T3.1 | Test | SPECI gap fixtures | TC-EV029-007; F20 | T2.3 | pending |
| T3.2 | Code | SPECI lint/convert/validate deltas | F20; F6 | T3.1 | pending |
| T3.3 | Config | `speci-quality.yml` | E29-T4 | T3.2 | pending |

### M4 — TAF (F20 deepen)

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T4.1 | Test | TAF gap fixtures | TC-EV029-007; F20 | T3.3 | pending |
| T4.2 | Code | TAF lint/convert/validate deltas | F20; F6 | T4.1 | pending |
| T4.3 | Config | `taf-quality.yml` | E29-T4 | T4.2 | pending |

### M5 — General SIGMET (F23 deepen)

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T5.1 | Test | Gen SIGMET gap fixtures + CNL as needed | TC-EV029-007; F23 | T4.3 | pending |
| T5.2 | Code | Gen SIGMET deltas; root `iwxxm:SIGMET` | F23; F6.d | T5.1 | pending |
| T5.3 | Config | Extend `sigmet-quality.yml` for gen pack | E29-T4 | T5.2 | pending |

### M6 — VA SIGMET (F23 deepen)

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T6.1 | Test | VA SIGMET gap fixtures | F23; TC-EV029-007 | T5.3 | pending |
| T6.2 | Code | VA SIGMET deltas; root `VolcanicAshSIGMET` | F23; F6.d | T6.1 | pending |
| T6.3 | Config | VA paths in `sigmet-quality.yml` (or `va-sigmet-quality.yml`) | E29-T4 | T6.2 | pending |

### M7 — TC SIGMET (F23 deepen / #738)

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T7.1 | Test | TC SIGMET → `TropicalCycloneSIGMET` fixtures | TC-EV029-004; #738 | T6.3 | pending |
| T7.2 | Code | TC SIGMET quality path (lint/convert/validate) | F23; S02.M2 | T7.1 | pending |
| T7.3 | Config | TC pack workflow (`tc-sigmet-quality.yml` or extend sigmet) | E29-T4 | T7.2 | pending |
| T7.4 | Docs | Close or child-issue #738 residuals | #738 | T7.3 | pending |

### M8 — AIRMET (F24 deepen)

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T8.1 | Test | AIRMET gap fixtures | F24; TC-EV029-007 | T7.4 | pending |
| T8.2 | Code | AIRMET deltas | F24; F6 | T8.1 | pending |
| T8.3 | Config | `airmet-quality.yml` | E29-T4 | T8.2 | pending |

### M9 — VAA (F26 deepen / #820)

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T9.1 | Test | VAA bulletin/encode residual fixtures | TC-EV029-005; #820 | T8.3 | pending |
| T9.2 | Code | VAA deltas | F26; F6.f | T9.1 | pending |
| T9.3 | Config | `vaa-quality.yml` (extend existing if present) | E29-T4 | T9.2 | pending |

### M10 — TCA (F27 deepen / #820)

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T10.1 | Test | TCA residual fixtures | TC-EV029-005; #820 | T9.3 | pending |
| T10.2 | Code | TCA deltas | F27; F6.f | T10.1 | pending |
| T10.3 | Config | `tca-quality.yml` | E29-T4 | T10.2 | pending |

### M11 — SWXA / F28 + `product=swxa` runtime

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T11.1 | Test | SWXA registry + accept/negative fixtures | TC-F28-001/004 | T10.3 | pending |
| T11.2 | Code | SWXA lint registry + rules | F28; F12 | T11.1 | pending |
| T11.3 | Test | SWXA convert → XSD+SCH (+ golden / `wmoReference`) | TC-F28-002/003; S02.L1 | T11.2 | pending |
| T11.4 | Code | SWXA encode path + AHL FN→LN adjacency | TC-F28-006; F6 | T11.3 | pending |
| T11.5 | Code | Backend/runtime enum `product=swxa` (docs already) | S02.M1; api-contract | T11.4 | pending |
| T11.6 | Config | `swxa-quality.yml` | E29-T4 | T11.5 | pending |
| T11.7 | Test | SWXA product-path smoke | TC-F28-005 | T11.6 | pending |

### M12 — Smoke / verify / deploy

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T12.1 | Test | Product-order regression smoke TC-EV029-007 | TC-EV029-007 | T11.7 | pending |
| T12.2 | Test | Report-state matrix TC-EV029-006 (or child-issue gaps) | TC-EV029-006 | T12.1 | pending |
| T12.3 | Config | 08-verify-build — lint/typecheck/format/full suites | 08 | T12.2 | pending |
| T12.4 | Test | 09-qa delta + 10-e2e smoke (UJ-043) | 09; 10 | T12.3 | pending |
| T12.5 | Docs | 11-verify-impl per–AC; 12-verify-deploy | 11; 12 | T12.4 | pending |
| T12.6 | Test | 13-deploy-smoke — API redeploy; H1–H3; **H4–H5 waive** unless FE Examples unlock (TC-EV029-008) | E29-T6; 13 | T12.5 | pending |
| T12.7 | Docs | Close #823 / link children; evolve summary | #823; S02.M3 | T12.6 | pending |

## Data Dependencies

| Asset | Needed by | Notes |
|-------|-----------|-------|
| Vendor IWXXM 2025-2 + Guidance | M0–M11 | Read-only `vendor/` |
| Existing mining notes (`docs/domain/mining/*`) | M0 | Re-mine, don't discard |
| #823 COM inventory / issue body | M0–M1 | Promote |
| Annex3 / WMO goldens | M2–M11 | Extend |
| No external weights/datasets | — | DMP N/A |

## Git Strategy

| Item | Value |
|------|-------|
| Branch | `evolve/EV-029-eight-family-ahl-rules` |
| Commits | Atomic per task `[T{m}.{n}] …` / `[EV-029] …` |
| PR | Evolve PR to `main` after Phase C/D (or earlier if user requests) |
| Checklist | Lint · typecheck · tests · no secrets · TC mapping |

## Phase Gate Log

| Gate | Criteria | Status |
|------|----------|--------|
| B→C | Plan approved; 05/06 skipped | **passed** (`D-S036-04-plan` = 1) |
| C→D | All M0–M12 tasks done; 08 pass | pending |
| Deploy | 09+10 pass; 11+12 approved; 13 per E29-T6 | pending |

## Task count

| Milestone | Tasks |
|-----------|------:|
| M0 | 6 |
| M1 | 4 |
| M2–M4 | 3×3 = 9 |
| M5–M6 | 3×2 = 6 |
| M7 | 4 |
| M8–M10 | 3×3 = 9 |
| M11 | 7 |
| M12 | 7 |
| **Total** | **48** |
