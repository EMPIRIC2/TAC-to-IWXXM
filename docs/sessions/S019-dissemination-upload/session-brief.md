---
session_id: S019-dissemination-upload
type: feature
status: in_progress
branch: cursor/dissemination-upload-e25c
started_at: 2026-07-20
intent: "Dissemination epic — Upload to Database (#729) + WIS2 (#2) + EDIS (#6) + AMHS/SWIM/AFS"
orchestrator: 16-evolve
evolve_cycle_id: EV-014
context_briefs: []
standing_docs_touched:
  - docs/decisions/evolve-decisions.md
  - docs/feature-list.md
  - docs/user-journeys.md
  - docs/test-plan.md
  - docs/spec.md
  - docs/adr/ADR-021-byo-credentials-admin-removal.md
  - docs/adr/ADR-029-dissemination-ssrf-allowlist.md
---

# Session S019 — dissemination-upload

## Intent

One BIG dissemination evolve cycle:

1. **F16** — Dissemination drawer + multi-DB upload (#729)
2. **F17** — WIS2 pathway (#2)
3. **F18** — EDIS → RTH Washington (#6)
4. **F19** — AMHS / SWIM / AFS adapters

## Phase 0 — APPROVED (2026-07-21)

| Gate | Decision |
|------|----------|
| Q23 | Multi-DB: Postgres, MySQL/MariaDB, SQL Server, SQLite (A–D; no other named vendor) |
| Q24=A | Approve F16–F19 + **Full** routing → write feature-list + start 01-requirements |
| Q25=A | Run 02-verify-plan now (PR #753) |
| Q26=A | Fix F8 non-goals → worker-path only |
| Q27=A | Component Overview notes Planned F16–F19 |
| Q28=A (+batch) | Close-gate clarify; H6 UJ-027–030; ADR-029 Accepted; L1 defer 04 |
| AskQuestion | Waived (cloud written interview) |

### Locked intake (summary)

- One-shot BYOC destination creds (memory-only); no saved profiles
- Drawer + sink chooser (DB / WIS2 / EDIS / AMHS|SWIM|AFS)
- URI-only for DB; preflight schema diff; block Send until green
- DDL / create-if-missing; drag-drop + convert-then-send
- Supabase **Auth + F5** stay; destination ≠ Supabase ops DB
- SSRF max guard + required `DISSEMINATION_EGRESS_ALLOWLIST`
- Staging wis2box for test; live WIS2/EDIS/DB = user BYOC
- Merge: staging OK; **cycle close** needs live BYOC green (Postgres + WIS2 + EDIS)

## Feature mapping

| Fn | Status | Issues |
|----|--------|--------|
| F16 | Planned | #729 |
| F17 | Planned | #2 |
| F18 | Planned | #6 |
| F19 | Planned | non-goals overturn |

## Current stage

**01-requirements** (delta) — in progress after Phase 0 approval.

## Links

- PR: https://github.com/joseph-c-mcguire/metar-to-IWXXM/pull/753
- [#729](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/729) [#2](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/2) [#6](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/6)
