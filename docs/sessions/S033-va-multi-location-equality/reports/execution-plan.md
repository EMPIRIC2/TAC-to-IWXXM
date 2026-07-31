# Execution plan — S033 / EV-026 (#809 VA multi-location ADR-032 equality)

> **Status**: **approved** — Gate B `D-S033-04-plan-approve` (option **1**)  
> **Branch**: `evolve/EV-026-va-multi-location-equality`  
> **Evolve cycle**: EV-026  
> **Features**: deepen F23 / F6 / F7.g — no new Fn  
> **Spec sources**: feature-list §S033/EV-026; UJ-041; TC-EV025-008..009 (strict);
> E26-*; S02.M1/M2/L1; #809; [Context: va-multi-location-809](../../../context/va-multi-location-809.md)

## Current State

| Field | Value |
|-------|-------|
| Soft path | Shipped #816 — soft golden + multi-location encode |
| Catalog | `sigmet_multi_location_va` = `wmoReference` |
| Strict equality | In progress — 07-build |
| Issue | #809 open |
| Active task | T1.2 |

## Locked policy

| Topic | Decision | Source |
|-------|----------|--------|
| Stamps | Example-specific calendar / ATS–MWO OK; no default convert API change | S02.M1 |
| Geometry | Ring order + coord format toward vendor for this stem only | S02.M2 |
| Journeys | Deepen UJ-041 only | S02.L1 |
| TC ids | Reuse TC-EV025-008..009 | E26-TC |
| Deploy | 13 when ships | E26-3 |
| UI | N/A | E26-ui |

## Interview locks (Batch T — approved `1,1,2,1,1`)

| ID | Decision |
|----|----------|
| E26-T1 | Order **1** — dig → red strict → encoder themes → green → catalog → verify/close |
| E26-T2 | Grain **1** — one commit per blocker theme, then equality green |
| E26-T3 | Deps **2** — AskQuestion per new dep (prefer none) |
| E26-T4 | Gate C **1** — equality + `wmoPass` + #809 closed required (no soft escape) |
| E26-T5 | Draft **1** — plan as written; Gate B approved |

## Milestones & Tasks (TDD order)

`evolve_cycle_id: EV-026` · `feature_ids: [F23, F6, F7]`

### M0 — Baseline dig

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T0.1 | Docs | Capture canonicalize diff themes vs vendor (confirm blockers) — [t0-1-canonicalize-diff-themes.md](t0-1-canonicalize-diff-themes.md) | Context 809 | — | completed |

### M1 — Red strict gate + encoder fidelity

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T1.1 | Test | Flip TC-EV025-008 to strict equality (expect red) | TC-EV025-008; E26-TC | T0.1 | completed |
| T1.2 | Code | Calendar year-month + ATS/MWO display stamps for this stem | S02.M1; #809 | T1.1 | completed |
| T1.3 | Code | Ring vertex order + coordinate formatting toward vendor | S02.M2; #809 | T1.2 | pending |
| T1.4 | Code | phenomenonTime / TimeInstant density alignment | Context blocker 5 | T1.3 | pending |
| T1.5 | Test | TC-EV025-008 green under `canonicalize_xml` equality | TC-EV025-008 | T1.4 | pending |

### M2 — Catalog promote

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T2.1 | Code | Catalog `wmoReference` → `wmoPass`; label passer | TC-EV025-009; UJ-041 | T1.5 | pending |
| T2.2 | Docs | FIXTURE_GAPS clear equality-pending / #809 note | TC-EV025-009 | T2.1 | pending |
| T2.3 | Test | TC-EV025-009 Vitest/catalog `wmoPass: true` | TC-EV025-009 | T2.2 | pending |

### M3 — Verify / close

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T3.1 | Docs | Gate C dig — equality + promote checklist | E26-T4 | T2.3 | pending |
| T3.2 | Test | 08-verify-build + 10-e2e smoke (VA stem + catalog) | routing | T3.1 | pending |
| T3.3 | Docs | Close GitHub #809 | #809 AC | T3.2 | pending |
| T3.4 | Deploy | 13-deploy-smoke **when** API/catalog ships | E26-3 | T3.2 | pending |

## Data Dependencies

| Asset | Used by | Notes |
|-------|---------|-------|
| Vendor `sigmet-multi-location-VA.{tac,xml}` | M1–M2 | Under IWXXM 2025-2 pin |
| Package soft golden (pre-flip) | M1 | Drop `soft_compare` in T1.1/T1.5 |

## Git Strategy

- Branch: `evolve/EV-026-va-multi-location-equality`
- One task per atomic commit: `[T{n}.{m}] …`
- PR to `main` when M3 verify green

## Success criteria

- [ ] `canonicalize_xml` equality under annex3 + default pin
- [ ] Catalog `wmoPass` for `sigmet_multi_location_va`
- [ ] TC-EV025-008..009 strict green
- [ ] #809 closed
- [ ] No new deps without AskQuestion
- [ ] 13 when behavior ships (T3.4)

## Gate B → C

| Gate | Result | Date |
|------|--------|------|
| B→C | **PASSED** — Batch T `1,1,2,1,1`; M0–M3 / 12 tasks approved → **07-build** @ T0.1 (`D-S033-04-plan-approve`) | 2026-07-31 |
| C (encode) | Pending — equality + `wmoPass` + #809 closed (`E26-T4`) | — |
