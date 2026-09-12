# 02-verify-plan audit — S047 / EV-039

**Date:** 2026-08-06  
**Mode:** delta · consistency on EV-039 F16 live SQL + teardown  
**AC gate:** `D-S047-ac` = 1 (AC1–AC7 / feature-list items 12–18)  
**Corpus:** `[Corpus: product §F16]` · `[Corpus: journeys §UJ-027]` · `[Corpus: tests]` ·
`[Corpus: tech-spec]` · `[Corpus: decisions]` · `[Corpus: adr/ADR-029]` · `[Corpus: adr/ADR-030]`

## Inventory (delta)

| # | Document | Scope | Status |
|---|----------|-------|--------|
| 1 | feature-list.md | F16 EV-039 deepen + AC12–18 | audited |
| 2 | user-journeys.md | UJ-027 live local Compose path | audited |
| 3 | test-plan.md | TC-F16-LIVE-001..004 + F16 gate | audited |
| 4 | tech-spec.md | Local mock BYOC pointer | audited |
| 5 | env-contract.md | Allowlist note for live e2e | audited |
| 6 | requirements-decisions.md | EV-039 / F16-R1..R9 | audited |
| 7 | evolve-decisions.md §EV-039 | Scope + ACs | audited |
| 8 | 01-requirements-summary.md | Manifest + AC table | audited |

Skipped (per D-S047-ac manifest): api-contract.md, new ADR.  
**spec.md**: EV-039 deepen bullet added in 02 (`D-S047-02-gate-a`=2) — S02.M3 resolved.

## Consistency checklist

| Check | Result |
|-------|--------|
| AC1–AC7 ↔ feature-list 12–18 ↔ evolve-decisions ↔ 01 summary | ✅ |
| AC2 ↔ TC-F16-LIVE-001..004 (PG/MySQL/SQL Server/SQLite) | ✅ |
| UJ-027 live path ↔ TC-F16-LIVE-* ↔ test-plan UJ map | ✅ |
| AC3 mocked suite separate from live | ✅ journeys + test-plan |
| AC4–AC6 teardown ↔ LIVE-004 + F16 gate checklist | ✅ |
| AC7 make/CI docs ↔ tech-spec make targets (exist today) | ✅ `compose-mock-byoc-up/down` |
| No new Fn | ✅ deepen F16 only |
| Harness reuses existing Compose overlay | ✅ `docker-compose.mock-byoc.yml` |
| SSRF/allowlist cites ADR-029 | ✅ |
| Connectivity H4–H5 for local live UI↔API | ⚠ expected 04/07 wiring — S02.M2 |
| Feature ↔ Spec component map | ✅ F16 → `packages/dissemination` + drawer (pre-existing) |

## High confidence (auto-approved)

| ID | Statement | Source |
|----|-----------|--------|
| S1.1 | Deepen F16 only; no new Fn | D-S047-open Q1; EV-039/F16-R1 |
| S1.2 | All four dialects: PG + MySQL + SQL Server + SQLite | Q2=1; F16-R2 |
| S1.3 | Compose mock-byoc + Playwright live (no route mocks) | Q4=1; F16-R3 |
| S1.4 | Teardown across integration + e2e + local | Q3=1; F16-R4 |
| S1.5 | UI preview declined | Q5=2; F16-R5 |
| S1.6 | AC1–AC7 approved as written | D-S047-ac=1 |
| S1.7 | Standard routing; skip 03/06 | Phase 0 preset |
| S1.8 | Live suite may be CI opt-in if SQL Server heavy | F16-R8; TC-F16-LIVE-003 |

**Auto-approved:** 8 high-confidence statements.

## Medium confidence (recommend accept as 04/07 work)

| ID | Statement | Issue | Recommend |
|----|-----------|-------|-----------|
| S02.M1 | `compose-mock-byoc-down` today is `stop`+`rm -f`, not `down -v` | Volumes / `restart: unless-stopped` may linger vs AC4 “volumes where safe” | **04/07:** harden teardown (down -v or explicit volume rm; assert no orphans) |
| S02.M2 | Live Playwright needs local API+FE + CORS + allowlist wiring | Not specified beyond env-contract pointer | **04:** execution-plan tasks for harness env, make target, H4–H5 local |
| S02.M3 | `spec.md` §F16 lacks EV-039 one-liner | **RESOLVED** in 02 — deepen bullet added (`D-S047-02-gate-a`=2) | — |
| S02.M4 | “Write assertion” mechanism unspecified | Query DB from test vs trust send response | **04:** pick approach (prefer verify row via async driver or SQL CLI) |
| S02.M5 | T3 naming for local Compose vs deployed T3 | Journeys already say “local Compose — not production” | **Accept** wording; keep LIVE suite out of prod `make test-live` unless opted in |

## Low confidence

| ID | Statement | Note |
|----|-----------|------|
| S02.L1 | SQL Server always required in CI | AC7/R8 allow opt-in; local close still requires all four | **Accept** — local evidence OK if CI skips LIVE-003 |

## Contradictions

None blocking. S02.M3 resolved by `spec.md` §F16 EV-039 deepen bullet.

## Connectivity (stage 02)

- Mocked H6′ remains Vitest/Playwright with route mocks — **not** sole proof for EV-039 live ACs.
- Live suite is local Compose T2/(local)T3 — must wire CORS + allowlist in 04/07 (S02.M2).
- No claim that Vitest alone satisfies TC-F16-LIVE-*.

## Gate A recommendation

**PASS** with S02.M1–M2, M4–M5 + S02.L1 accepted as **04/07** work; S02.M3 fixed in 02.
Close 02 → start **04-tech-plan** (Standard; 03 skipped).

## Gate A result (locked)

| ID | Decision |
|----|----------|
| D-S047-02-gate-a | **2** — PASS; add `spec.md` EV-039 note in 02 first, then close → 04 |

**Status:** Gate A **PASS** 2026-08-06 — close 02 → **04-tech-plan**.

