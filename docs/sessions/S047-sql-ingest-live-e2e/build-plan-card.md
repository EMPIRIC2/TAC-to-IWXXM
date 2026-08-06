# Build Plan Card

> Session: S047-sql-ingest-live-e2e | Updated: 2026-08-06 | Active: Phase 1 / M1 / T1.3

## Goal (one sentence)

Wire local make targets + CORS/allowlist so M2 can run live F16 SQL Playwright.

## Constraints

- Deepen F16 only — [Corpus: product §F16]; no new Fn; no prod SQL — [Corpus: decisions] EV-039
- Allowlist fail-closed — [Corpus: adr/ADR-029] [Corpus: adr/ADR-030]
- Branch: `evolve/EV-039-sql-ingest-live-e2e`
- Q1–Q4 locked; Gate B PASS; T1.1–T1.2 done (`down -v` + project `-p metar-iwxxm-mock-byoc`)

## In scope (this batch — M1 remaining)

- [ ] T1.3 — Config — `test-e2e-f16-live-sql` + `F16_LIVE_SQL` on `test-live-e2e`; local `test-live` includes LIVE — Spec: AC7; Q3/Q4
- [ ] T1.4 — Config — local CORS + egress allowlist recipe — Spec: ADR-030; H4–H5 local
- [ ] T1.5 — Docs — tech-spec make/CI opt-in notes — Spec: tech-spec §mock-byoc

## Out of scope (explicit)

- Live Playwright specs / write helpers (M2 T2.*)
- WIS2/EDIS/F19 live; prod SQL; UI preview
- Default CI requiring LIVE or all four dialects

## Dependencies / blockers

- Data: Docker images for mock-byoc (pull on up)
- Prior: T1.1–T1.2 **completed**; Gate B PASS
- Tooling: 06 skipped (OK)

## Acceptance for this batch

- [ ] Make targets exist; `F16_LIVE_SQL` off when `CI=true` (S05.M2)
- [ ] Local harness env recipe documented (CORS + allowlist)
- [ ] tech-spec updated (incl. project `-p metar-iwxxm-mock-byoc`)

## Next Plan prompt

```
You are refining the next build batch for S047 / EV-039.

Read:
1. docs/sessions/S047-sql-ingest-live-e2e/build-plan-card.md
2. docs/sessions/S047-sql-ingest-live-e2e/reports/execution-plan.md — Current State + active milestone
3. Spec sources for T1.* only (AC4/AC7, tech-spec mock-byoc, ADR-030)

Produce ordered M1 task list, risks, updated card. Do not implement. On approve → 07-build T1.1.
```
