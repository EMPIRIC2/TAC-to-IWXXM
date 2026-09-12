# Context — Dissemination multi-file export selection (#785)

> **Mode**: scoped | **Slug**: dissemination-file-select | **Generated**: 2026-07-28  
> **Feature / workflow**: Multi-select export candidates in dissemination drawer  
> **Status**: active | **Session**: S024 / EV-018  
> **Issue**: [#785](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/785)

## Executive Summary

Operators need to **choose a subset** of ready IWXXM/TAC artifacts in the dissemination
portal before Preflight/Send. Today the drawer is effectively single-payload (current
conversion or one drop). v1 adds a selectable candidate list, multi-select, selection-scoped
preflight/send, and per-file results — without changing BYOC memory-only or egress allowlist
rules.

| Pillar | Choice (Batch 1+2 locked) |
|--------|---------------------------|
| Feature id | **Deepen F16**; F17–F19 reuse selection contract (no F23) |
| Surfaces | Dissemination drawer (`apps/frontend`) + existing preflight/send APIs |
| API shape | **N sequential** calls; UI aggregates (E18-5) |
| Caps | Selection count **≤20** + existing body/size limits (E18-6) |
| Security | ADR-021/029/030 — memory-only BYOC; allowlist unchanged |
| Auth context | Public operator app (**F21** / S023) — no JWT for drawer |
| History sources | **Current-session + drops only** (E18-4); Finished IndexedDB deferred |
| Routing | **Lean+build** (E18-7) |

## Problem (from #785)

1. No list of eligible export candidates
2. No subset selection (select all / none / individual)
3. Preflight/send not limited to chosen files with per-file feedback

## Related corpus

| Corpus | Touch |
|--------|-------|
| product | `feature-list.md` F16–F19 (+ F23) |
| system-spec | `spec.md` dissemination drawer |
| api | `api-contract.md` `/dissemination/preflight` + `/send` |
| tests | `test-plan.md` UJ-027–030 / H4–H5 / H6′ |
| adr | ADR-021, ADR-029, ADR-030 |

## Prior art

- **S019 / EV-014** — F16–F19 shipped (drawer, sinks, BYOC)
- **S023 / EV-017** — F21 public app; F5/F7 → IndexedDB (affects “history as source” Q)

## Resolution Log

| ID | Category | Decision |
|----|----------|----------|
| E18-1 | Decision | Open S024 / EV-018 for #785 |
| E18-2 | Decision | Deepen F16; F17–F19 reuse selection UI (no F23) |
| E18-3 | Decision | Lean (amended E18-7 → Lean+build) |
| E18-4 | Ambiguity | Current-session + dropped files only in v1 |
| E18-5 | Decision | N sequential `/preflight`+`/send`; UI aggregates |
| E18-6 | Decision | Count cap ≤20 + existing body/size limits |
| E18-7 | Ambiguity | Lean+build routing |
| E18-8 | Decision | Open local / non-deployed UI preview now |
| E18-9 | Decision | Single candidate: auto-select; panel collapsed/optional |
| E18-10 | Decision | Interleaved preflight→send per file + interactive mail→dest progress; red fail mark |
| E18-11 | Decision | Continue on failure; aggregate statuses |
| E18-12 | Decision | Four milestones M1–M4 (selection → aggregator → UI/progress → tests) |
| E18-13 | Decision | Progress graphic: CSS + `motion` + lucide; no new deps |
| E18-14 | Decision | `prefers-reduced-motion` → hide graphic; text-only progress |
| E18-15 | Decision | Primary Disseminate (preflight→send); optional Preflight-only |
| E18-16 | Decision | Vitest + Playwright + progress-row screenshot; H6′ @ 13 |
