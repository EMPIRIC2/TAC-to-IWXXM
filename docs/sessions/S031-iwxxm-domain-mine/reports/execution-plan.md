# Execution plan — S031 / EV-024 (#804 / #807 / #773 IWXXM domain mine + sample menu)

> **Status**: **approved** (2026-07-30) — E24-T1..T5 (1 / 1 / 2 / 2 / 1)  
> **Branch**: `evolve/EV-024-iwxxm-domain-mine`  
> **Evolve cycle**: EV-024  
> **Features**: deepen F6 / F2 / F4 / F12 / F13 / F25 (+ F6.b) — no new Fn  
> **Spec sources**: feature-list §S031; spec §S031/EV-024; UJ-039; TC-EV024-001..008;
> ADR-032 amend; E24-*; S02.M1/M2/L1; #804/#807/#773 (exclude #806)

## Current State

| Field | Value |
|-------|-------|
| **Active phase** | Phase C — Build (07) |
| **Active milestone** | M7 remaining |
| **Active task** | T7.1 |
| **Tasks** | 19 / 22 |
| **Last updated** | 2026-07-30 |

## Tech Stack Summary

| Area | Choice | Source |
|------|--------|--------|
| Runtime SoT | Vendor pin IWXXM **v2025-2** (+ iwxxm-us pin) | E24; #804/#773 |
| Mining | `mine-domain-sources` + `extract-pdf-to-repo` (#773) | skill |
| Working clones / PDFs | `.local/` only — not committed | #804/#773 OOS |
| Catalog tiers | `wmoPass` + `wmoSeed` + **`wmoReference?: boolean`** | S02.M1 |
| Sample menu stems | Product-in-scope + TAC peers; SWX/VONA/WAFS/QVACI deferred | S02.M2 |
| Vitest | WMO demos may be pass **or** reference | S02.L1 |
| Encode gaps | Child issues only (no big-bang encode) | E24-C |
| New deps | Prefer none; AskQuestion per new dep | default |
| Deploy | 13 when catalog/API ships | E24-4 |

## Interview locks

| ID | Decision |
|----|----------|
| E24-T1 | Order **1** — M0→#804→#807→#773→promote→catalog→validate→children/smoke |
| E24-T2 | Badge **1** — “WMO passer” vs “WMO reference” (no new route) |
| E24-T3 | Deps **2** — AskQuestion per new dep (prefer none) |
| E24-T4 | Mine **2** — sequential M1→M2→M3 |
| E24-T5 | Plan **1** — approve; B→C → 07 @ T0.1 |

## Milestones & Tasks (TDD order)

`evolve_cycle_id: EV-024` · `feature_ids: [F6, F2, F4, F12, F13, F25]`

### M0 — Theme map + scaffold

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T0.1 | Docs | Map TC-EV024-001..008 → deliverables/paths; `reports/domain-mine-theme-map.md` | TC-EV024 | — | **completed** |
| T0.2 | Docs | Confirm vendor pin SHA + examples inventory seed vs FIXTURE_GAPS | #804 | T0.1 | **completed** |

### M1 — #804 IWXXM/ tree mine

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T1.1 | Docs | Folder×relevancy table (`wmo-im-iwxxm-IWXXM-tree-mining-notes.md`) | TC-EV024-001 | T0.2 | **completed** |
| T1.2 | Docs | Stem×surface examples matrix (validate/convert/UI/defer) | TC-EV024-001 | T1.1 | **completed** |
| T1.3 | Docs | Index notes in `docs/domain/mining/README.md` | #804 | T1.2 | **completed** |

### M2 — #807 org / sibling refresh

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T2.1 | Docs | Refresh `wmo-im-org-mining-notes.md` vs pin; IWXXM family + lineage | TC-EV024-002 | T1.3 | **completed** |
| T2.2 | Docs | Explicit skip one-liners (incl. WIS2/#806) | E24-x | T2.1 | **completed** |

### M3 — #773 IWXXM-US / MDL

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T3.1 | Docs | Extract PDF(s) to `.local/` via extract-pdf-to-repo | #773 | T2.2 | **completed** |
| T3.2 | Docs | Type×TAC×encode×validate checklist + modelling notes | TC-EV024-003 | T3.1 | **completed** |
| T3.3 | Docs | RULE_SOURCE_URLS rows (PDF + modelling + VLab) | #773 | T3.2 | **completed** |

### M4 — Promote durable findings

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T4.1 | Docs | COVERAGE_MATRIX + canonical deltas (only durable) | TC-EV024-008 | T3.3 | **completed** |
| T4.2 | Docs | Re-scrape Guidance / sch assert ids → gap list for children | #804/#800 | T4.1 | **completed** |

### M5 — Sample menu / UJ-039 (catalog)

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T5.1 | Test | Fail Vitest until `wmoReference` allowed (S02.L1) | TC-EV024-006 | T1.2 | **completed** |
| T5.2 | Code | Add `wmoReference?: boolean`; badge/copy in Examples UI | S02.M1; E24-T2 | T5.1 | **completed** |
| T5.3 | Code | Register in-scope WMO stems (TAC peers); update FIXTURE_GAPS | TC-EV024-004/005 | T5.2 | **completed** |
| T5.4 | Test | Load-path / catalog tests green for UJ-039 | TC-EV024-004..006 | T5.3 | **completed** |

### M6 — Validate/CI wire

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T6.1 | Test | Expand WMOExamplesLoader / validate fixtures for in-scope stems | TC-EV024-007 | T1.2 | **completed** |
| T6.2 | Code | Wire or document deferrals with child-issue links | TC-EV024-007 | T6.1 | **completed** |

### M7 — Child issues + smoke

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T7.1 | Docs | File child issues for ❌/⚠ encode/lint/SCH; comment on #804/#807/#773 | TC-EV024-008 | T4.2; T5.4; T6.2 | pending |
| T7.2 | Test | 08-verify-build + 10-e2e smoke (catalog/validate) | routing | T7.1 | pending |
| T7.3 | Deploy | 13-deploy-smoke **when** catalog ships (E24-4) | connectivity | T7.2 | pending |

## Git Strategy

- Branch: `evolve/EV-024-iwxxm-domain-mine`
- One task per atomic commit: `[T{n}.{m}] …`
- PR to main when M0–M7 complete (or M7.3 deferred if no deploy)

## PR checklist (draft)

- [ ] Mining notes indexed; matrices complete
- [ ] Sample menu loads official WMO stems (strict + reference)
- [ ] Vitest/catalog policy updated
- [ ] Validate/CI wire or deferrals
- [ ] Child issues filed; durable promotions committed
- [ ] #806 not in scope
