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
