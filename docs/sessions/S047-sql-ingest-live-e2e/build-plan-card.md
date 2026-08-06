# Build Plan Card

> Session: S047-sql-ingest-live-e2e | Updated: 2026-08-06 | Active: Phase 1 / M1 / T1.4

## Goal (one sentence)

Document local CORS + allowlist recipe and tech-spec make/CI notes for F16 LIVE.

## Constraints

- Deepen F16 only — [Corpus: product §F16]; no new Fn; no prod SQL — [Corpus: decisions] EV-039
- Allowlist fail-closed — [Corpus: adr/ADR-029] [Corpus: adr/ADR-030]
- Branch: `evolve/EV-039-sql-ingest-live-e2e`
- T1.1–T1.3 done; `F16_LIVE_SQL` defaults off in CI

## In scope (this batch — M1 remaining)

- [ ] T1.4 — Config — local CORS + egress allowlist recipe — Spec: ADR-030; H4–H5 local
- [ ] T1.5 — Docs — tech-spec make/CI opt-in notes — Spec: tech-spec §mock-byoc

## Out of scope (explicit)

- Live Playwright specs / write helpers (M2 T2.*)
- WIS2/EDIS/F19 live; prod SQL; UI preview

## Dependencies / blockers

- Prior: T1.1–T1.3 **completed**
- Tooling: 06 skipped (OK)

## Acceptance for this batch

- [ ] Local harness env recipe documented (CORS + allowlist)
- [ ] tech-spec updated (targets + `-p metar-iwxxm-mock-byoc` + CI opt-in)

## Next Plan prompt

```
You are refining the next build batch for S047 / EV-039.

Read:
1. docs/sessions/S047-sql-ingest-live-e2e/build-plan-card.md
2. docs/sessions/S047-sql-ingest-live-e2e/reports/execution-plan.md — Current State + active milestone
3. Spec sources for T1.* only (AC4/AC7, tech-spec mock-byoc, ADR-030)

Produce ordered M1 task list, risks, updated card. Do not implement. On approve → 07-build T1.1.
```
