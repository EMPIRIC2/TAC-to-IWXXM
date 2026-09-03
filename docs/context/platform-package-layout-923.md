# Scoped context: Platform package layout (#923)

> **Status**: active  
> **Created**: 2026-09-03  
> **Session**: `EV-922-epic-modular-conversion-validation-integration-d` (slice #923)  
> **Tickets**: [#922](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/922) (epic) · [#923](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/923) (slice)  
> **Corpus**: [Corpus: system-spec] §Component Overview · [Corpus: adr] ADR-013, ADR-030, ADR-036 · [Corpus: product] F6 / F7 / F16–F19 · [Corpus: tech-spec]

## Goal

Investigate and validate the proposed platform layering (**Core → Profiles → Validation → Adapters → Dissemination**) against the current monorepo. Deliver a **gap matrix**, migration options A/B/C, and a **milestone sequence** — no production ship.

## Interview (E0–E8) — recorded

| Batch | Decision |
|-------|----------|
| E0 | Goal / in-out / success locked at evolve intake (slice A = #923 only) |
| E1 | Type: feature/evolve · tickets #922/#923 · urgency: M5 / normal |
| E2 | Users: maintainers + architects · no operator journeys · must-not-break: F21 public convert, package purity, vendor read-only |
| E3 | Docs: system-spec delta · ADR draft/amend · this scoped brief · optional feature-list note · no new CORPUS member unless gap |
| E4 | Build intent: docs/ADR only; deploy none; e2e skipped |
| E5 | No rename this slice · no API break · no PII · envs untouched |
| E6 | UI N/A |
| E7–E8 | Routing approved; Spec band only; gate closed |

## Current tree (seed for gap matrix)

| Current path | Role today | Likely target layer(s) |
|--------------|------------|------------------------|
| `packages/tac2iwxxm` | TAC→IWXXM convert + decode + IR (F6) | conversion (+ bits of core / profiles) |
| `packages/tac-validate` | TAC lint / rule registry (F12/F15+) | validation (TAC stage) |
| `packages/iwxxm-validate` | XSD + Schematron (F2/F13) | validation (IWXXM stage) |
| `packages/dissemination` | Sinks, writer-contract, SSRF, AFS helpers (F16–F19, ADR-030) | dissemination (+ gateways/afs) |
| `packages/shared` | Cross-cutting types/utils | core / shared |
| `packages/auth` | JWT middleware (not convert path) | stay deployable-adjacent (not platform MET layers) |
| `docs/domain/profiles/` | Semantic/exchange profile content (ADR-036 / #912) | profiles (content home — not a Python package yet) |
| `apps/backend` | Thin HTTP wiring | stays apps; calls packages |
| `apps/frontend` / `apps/worker` / `apps/e2e` | UI / F8 / Playwright | out of #923 migrate scope |
| `vendor/schemas/*` | Read-only schema snapshots | unchanged |

**uv workspace members today:** `shared`, `auth`, `tac2iwxxm`, `iwxxm-validate`, `tac-validate`, `dissemination`, `apps/backend`, `apps/worker`.

## Hard boundaries (must not break)

1. No FastAPI / Supabase product-DB imports inside MET packages ([Corpus: system-spec]).
2. Vendor schemas read-only ([Corpus: adr] ADR-001).
3. F21 public convert/validate/lint/decode/preview/dissemination paths remain.
4. ADR-036 split: semantic profiles ≠ exchange profiles ≠ BYOC “profiles”.
5. ADR-030: dissemination stays a library; backend thin routers only.

## Options (from #923 — to decide in Spec/Build)

| Option | Meaning |
|--------|---------|
| **A** | Big-bang restructure into `core` / `conversion` / `validation` / `adapters` / `gateways` / `dissemination` / `profiles` packages |
| **B** | Incremental rename/split behind stable APIs |
| **C** | Keep current packages; document logical layers only |

**Recommendation (locked): Option C** — logical layers only; defer Option B until #924–#927 ([ADR-037](../adr/ADR-037-platform-logical-layers.md)).

## Milestone sequence (draft — revise after #924–#927)

```text
Core → Profiles → Validation → Adapters → Dissemination
```

Sibling spikes may revise: #924 ConversionProfile · #925 canonical MET · #926 SQL adapters · #927 DisseminationGateway · #931 workflows ✅ ADR-042 · Platform UIs #933–#938.

## Resolutions (local)

| ID | Statement |
|----|-----------|
| **R1** | This session delivers investigation artifacts only; migrate-now requires explicit approval after write-up. |
| **R2** | Profiles *content* stays under #912 / `docs/domain/profiles/`; #923 owns package/layout contract only. |
| **R3** | Supporting UIs (#933–#938) remain blocked until architecture spikes close. |
| **R4** | KG session-open: no accepted knowledge matches — proceed fail-open ([Corpus: skill-integration]). |

## Out of scope

#924–#931 · platform UIs · #843 feature deepen · national rule-pack content · behavior changes · package renames without ADR + approval.

## Next

Spec band complete → Build band commits standing docs only (no package moves).
