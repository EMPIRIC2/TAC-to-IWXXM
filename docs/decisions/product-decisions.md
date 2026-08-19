# Product Decisions Log (Audit)

> Stage: 02-verify-plan | Chronological verdict log

| Timestamp | Stmt ID | Verdict | Notes |
|-----------|---------|---------|-------|
| 2026-06-14 | C1 | approved | Vendor sync from wmo-im directly; forks not needed for schemas |
| 2026-06-14 | C2 | approved | packages/auth library imported by apps/backend |
| 2026-06-14 | S-migration | approved | Big-bang — one PR, feature freeze |
| 2026-06-14 | S-gifts | modified | Manual GIFTs merges only — no scheduled auto-sync (overrides REQ-014) |
| 2026-06-14 | S-js | approved | pnpm workspaces at root |
| 2026-06-14 | S-auth-routes | approved | Auth routes at `/auth/*` on API root |
| 2026-06-14 | S-golden | approved | TC-M003 uses normalized canonical XML diff |
| 2026-06-14 | S-legacy | approved | Archive legacy repos after stable production deploy |
| 2026-06-14 | C5 | modified | migration-plan Out of scope → REQ-016 (was REQ-013) |
| 2026-06-14 | C6 | modified | Archive legacy repos removed from migration In scope; REQ-019 post-deploy |
| 2026-06-14 | S1.6 | approved | Batch ZIP verified in code (`/api/v1/convert-zip`); GH issues checked — no dispute |
| 2026-06-14 | S1.16 | approved | F3 Partial Web UI coverage correct |
| 2026-06-14 | S2.9 | approved | Feature freeze or coordinated downtime during big-bang |
| 2026-06-14 | S1.8 | approved | F3 limited by external API availability and cache TTL |
| 2026-06-14 | S2.7 | approved | Single METAR conversion < 2s typical |
| 2026-06-14 | S2.8 | approved | Batch 10 files < 10s |
| 2026-06-14 | S5.3 | approved | Local dev ports 18000 frontend, 18001 API |
| 2026-06-14 | S3.7 | modified | UJ-001 acceptance: conversion + schema validation pass (not iwxxm:METAR root) |
| 2026-06-14 | S3.1 | approved | UJ-001–003 at E2E tier T2 |
| 2026-06-14 | S3.4 | modified | E2E command → `make tests:e2e` (user-journeys, test-plan, migration-plan, config-spec) |
| 2026-06-14 | S4.6 | approved | H5 via scripts/deploy/verify_connectivity.sh |
| 2026-06-14 | S4.7 | approved | Vendor sync PR human review required |
| 2026-06-14 | S5.5 | approved | CORS preflight on /api/v1/* and /auth/* |
| 2026-06-14 | S6.1 | approved | Migration effort 2–5 dev-days |
| 2026-06-23 | S2.1 | modified | F5 purpose: "work history / session state" not "audit trail" (spec.md) |
| 2026-06-23 | S2.2 | approved | Guest login auto-creates Draft from in-browser converter state (F5-R33) |
| 2026-06-23 | S2.3 | approved | WIP stays WIP when input edited before re-convert (F5-R34) |
| 2026-06-23 | S2.4 | approved | Finished read-only disables Convert/Convert&Send; New METAR required (F5-R35) |
| 2026-06-23 | C1 | modified | S005 → S004 delivery labels in feature-list, test-plan, api-contract |
| 2026-06-23 | C2 | modified | H6 tier description includes UJ-004 (test-plan) |
| 2026-06-14 | S6.2 | approved | Risk level Medium |
| 2026-06-14 | S6.5 | approved | Branch feat/monorepo-big-bang |
| 2026-07-15 | D-S011-ADR023 | approved | Wire dormant Convert params (bulletin/issuing/stop_on_error/validate); console log filter; .tac accept; nil reasons deferred (ADR-023) |
| 2026-07-15 | D-S011-ADR024 | approved | AHL bulletin UI + COLLECT 501 placeholder + log_level/include_nil_reasons (ADR-024) |
| 2026-07-16 | EV009-S3.1 | approved | Unit renderings: inHg altimeter, "day DD at HH:MM UTC", statute miles, wind "from DDD° at N kt" |
| 2026-07-16 | EV009-S3.2 | approved | Quick fix via existing lint fixes[] — code add_terminator, replacement = text + '=' |
| 2026-07-16 | EV009-S3.3 | approved | Preview pane shows most recent preview only (no history v1) |
| 2026-07-16 | EV009-S3.4 | approved | Passing preview badge copy: "Passed" |
| 2026-07-21 | EV014-S1.H1–S6.H3 | auto-approved | 28 high-confidence F16–F19 claims from Q5–Q24 / requirements-decisions EV-014 (see S019 02-verify-plan-audit) |
| 2026-07-21 | C-EV014-1 | approved (modified) | Q26=A — F8 bullet narrowed to worker path; AMHS/push sinks → F16–F19 |
| 2026-07-21 | S-EV014-M1 | approved (modified) | Q27=A — Component Overview + backend/frontend purpose note Planned F16–F19 |
| 2026-07-21 | S-EV014-M2 | approved (modified) | Q28=A — hard close PG+WIS2+EDIS; F19 live optional with waive |
| 2026-07-21 | S-EV014-M3 | approved (modified) | Q28 batch — H6 / live harness list UJ-027–030 when F16–F19 ships |
| 2026-07-21 | S-EV014-M4 | approved (modified) | Q28 batch — ADR-029 → Accepted |
| 2026-07-21 | S-EV014-L1 | approved | Q28 batch — allowlist config/env-contract deferred to 04 |
| 2026-07-27 | S-EV017.1–10 | auto-approved | 10 high-confidence F21/F22 locks from E17-4A…E17-11 (S023 02-verify-plan) |
| 2026-07-27 | C-EV017.1 | modified | api-contract Auth → None (F21 public) for lint/decode/catalog/dissemination |
| 2026-07-27 | C-EV017.2 | modified | test-plan TC-003 retired; TC-004 + live E2E → IndexedDB / no JWT |
| 2026-07-27 | C-EV017.3 | modified | spec backend/frontend overview + Security → public + abuse + IndexedDB |
| 2026-07-27 | C-EV017.4 | modified | UJ-013/015 (+ related) → public + IndexedDB |
| 2026-07-27 | C-EV017.5 | deferred | env-contract stale-until-F21 banner; full rewrite 04/12 |
| 2026-07-27 | C-EV017.6 | modified | Added TC-F21-auth-gone + TC-F22-001..003 stubs |
| 2026-07-27 | D-S023-02-C-EV017-A | approved | Contradiction batch option A |
| 2026-07-29 | EV019-S1.1–S6.1 | auto-approved | 14 high-confidence F23 locks from E19-2..E19-14 (S025 02-verify-plan-audit) |
| 2026-07-29 | C-EV019-F21F22 | modified | feature-list summary F21/F22 Planned → Implemented (S023 sync) |
| 2026-07-29 | S1.M1 | approved | D-S025-EV019-s1m1-1 — full HARD themes; 04 kill-switch |
| 2026-07-29 | S6.M1 | approved | D-S025-EV019-s6m1-1 — keep G1–G3; prefix F23 theme vs gate |
| 2026-07-29 | S9.M1 | approved | D-S025-EV019-s9m1-1 — keep skip 05; light pass at 04 exit |
| 2026-07-29 | D-S025-02-phase-a | approved | Phase A PASS → 04-tech-plan (user A) |
| 2026-07-29 | EV020-S02.H1–18 | auto-approved | 18 high-confidence F24/F25/F9 locks from E20-* (S026 02-verify-plan-audit) |
| 2026-07-29 | S02.M1 | approved | D-S026-EV020-s02m1-1 — taf-A5-2 remains F25 golden (AMD/CNL peer) |
| 2026-07-29 | S02.M2 | approved | D-S026-EV020-s02m2-1 — ADR-032 → Accepted |
| 2026-07-29 | S02.L1 | approved | D-S026-EV020-s02l1-1 — lock TAC2IWXXM_DECODE_GLOSSARY_PATH |
| 2026-07-29 | S02.L2 | approved | D-S026-EV020-s02l2-1 — incremental Examples catalog unlock OK |
| 2026-07-29 | D-S026-02-phase-a | approved | Gate A PASS (Lean skip AskQuestion) → 04-tech-plan |
| 2026-07-29 | EV021-S02.H1–12 | auto-approved | 12 high-confidence F26/F27 locks from E21-* (S027 02-verify-plan-audit) |
| 2026-07-29 | S02.M1 | approved | D-S027-EV021-s02m1-1 — keep F26 V1–V3 / F27 T1–T3 + “F26/F27 theme” prefix |
| 2026-07-29 | S02.M2 | approved | D-S027-EV021-s02m2-1 — incremental catalog unlock per product (peer E20-F4) |
| 2026-07-29 | S02.L1 | approved | D-S027-EV021-s02l1-1 — extend combined wmo-quality.yml; finalize in 04 |
| 2026-07-29 | D-S027-02-phase-a | approved | Gate A PASS (Lean skip AskQuestion) → 04-tech-plan |
| 2026-07-31 | EV025-S02.H1–12 | auto-approved | 12 high-confidence F6.b/F12/F2/F13/F23 locks from E25-* (S032 02-verify-plan-audit) |
| 2026-07-31 | S02.M1 | approved | D-S032-EV025-s02m1-1 — #809 soft-compare first; wmoPass only when ADR-032 equality holds |
| 2026-07-31 | S02.M2 | approved | D-S032-EV025-s02m2-1 — aim close all dig ❌ in-cycle; residuals → child issues (don’t block Gate C) |
| 2026-07-31 | S02.L1 | approved | D-S032-EV025-s02l1-1 — TC-EV025-010 may document SCH deferrals without blocking Lane A goldens |
| 2026-07-31 | D-S032-02-phase-a | approved | Gate A PASS (Lean skip AskQuestion) → 04-tech-plan |
| 2026-07-31 | E25-T1 | approved | D-S032-EV025-t1-1 — M0→#810→#811→#812→adjacent→#809→validate→Gate C |
| 2026-07-31 | E25-T2 | approved | D-S032-EV025-t2-1 — per dig type/row encode (+lint) goldens |
| 2026-07-31 | E25-T3 | approved | D-S032-EV025-t3-2 — AskQuestion per new dep |
| 2026-07-31 | E25-T4 | approved | D-S032-EV025-t4-1 — Lane A then Lane B |
| 2026-07-31 | E25-T5 | approved | D-S032-EV025-t5-3 — dig ❌ encode residual blocks Gate C (supersedes S02.M2) |
| 2026-07-31 | E25-T6 | approved | D-S032-EV025-t6-1 — draft execution plan; Gate B pending |
| 2026-07-31 | D-S032-04-plan-approve | approved | Gate B=1 — M0–M7 approved; Lean → 07-build @ T0.1 |
| 2026-08-03 | EV031-H1–10 | auto-approved | 10 high-confidence F30/F31 locks (S038 verify-plan-audit) |
| 2026-08-03 | C1–C5 | modified | D-S038-02-batch-c=1 — fix stale F21 leftovers (config/spec/feature-list/api/UJ/TC-LIVE) |
| 2026-08-03 | M1–M3 | approved | D-S038-02-batch-c=1 — ADR-033 Proposed; Alembic+JWT draft until 04 |
| 2026-08-03 | D-S038-02-phase-a | approved | Gate A PASS → 04-tech-plan (03 skipped Standard) |
| 2026-08-18 | EV061-H1–10 | auto-approved | 10 high-confidence EV-061 deepen locks (S071 02-verify-plan) |
| 2026-08-18 | C1 | modified | D-S071-02-c1 — journeys header: UJ-068 links resolved / #1014 unblocked |
| 2026-08-18 | M1 | modified | D-S071-02-m1 — UJ-067 includes H4–H5 |
| 2026-08-18 | M2–M4 | approved | D-S071-02-m2/m3/m4 — TC detail + api-contract + catalog schema → 04 |
| 2026-08-18 | D-S071-gateA | approved | Gate A PASS → 04-tech-plan; Spec→Build closed |
