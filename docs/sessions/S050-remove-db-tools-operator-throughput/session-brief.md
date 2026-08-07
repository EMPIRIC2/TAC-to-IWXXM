---
session_id: S050-remove-db-tools-operator-throughput
type: feature
status: in_progress
branch: evolve/EV-042-remove-db-tools-operator-throughput
started_at: 2026-08-07
intent: "Remove Dissemination drawer DB sinks; operator churn UX; secure mass file/folder ingest (#897). Restore DB tools deferred to #898."
orchestrator: 16-evolve
evolve_cycle_id: EV-042
prior_session: S049-operator-sources-briefing
prior_evolve_cycle_id: EV-041
github_issues:
  - 897
  - 898
context_briefs:
  - docs/context/remove-db-tools-operator-throughput.md
feature_ids: []  # TBD Phase 1 — deepen F7/F16; possible new Fn for mass ingest
deepen_feature_ids:
  - F7
  - F16
route_status: in_progress
current_stage: 00-context
ui_preview: accepted — non-deployed local http://localhost:18000
preset: Standard
decisions:
  D-S050-ev041: "merge #895 then close S049 (user 2)"
  D-S050-db-scope: "drawer DB sinks only; keep F17–F19; leave DatabaseUploadDialog (user 1)"
  D-S050-cycle-scope: "ship all three: remove DB + churn UX + mass ingest (user 1)"
  D-S050-churn: "queue+keyboard AND batch actions (user 3)"
  D-S050-mass-shape: "multi-file + folder/zip + progress + per-file errors (user 1)"
  D-S050-mass-sec: "auth + caps + sniff/zip-bomb guards (user 2)"
  D-S050-db-api: "UI hide only (user 1)"
  D-S050-preset: "Standard (user 1)"
  D-S050-improvements: "accept recommended pack (user 1)"
  D-S050-ui-preview: "yes local non-deployed (user 1)"
---

# Session S050 — remove-db-tools-operator-throughput

## Intent

Ship [#897](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/897): temporarily remove
operator **multi-DB BYOC** sinks from the Dissemination drawer, improve operator
**throughput** (churn reports quickly), and add **secure mass ingest** via file/folder
upload. DB restore/redesign is [#898](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/898)
(not this cycle).

[Corpus: product §F16] [Corpus: product §F7] [Corpus: system-spec] [Corpus: adr/ADR-029]
[Corpus: adr/ADR-030]

## Goal (one sentence)

Operators can batch-ingest TAC securely and move reports through convert → validate →
non-DB disseminate without DB-destination UI, with restore tracked separately on #898.

## Scope

### In (Phase 0 locked)

1. **Remove drawer DB sinks** — Postgres / MySQL / SQL Server / SQLite from Dissemination
   drawer; keep WIS2 / EDIS / AMHS / SWIM / AFS.
2. **Operator churn / workflow pass** — UX so operators process reports quickly (details TBD).
3. **Secure mass file/folder ingest** — bulk intake with security limits (details TBD).

### Out of scope

- Restore/redesign of DB tools (#898 / #896 spike)
- Changing F17–F19 pathway design beyond shared-drawer impact of removing DB sinks
- Legacy `DatabaseUploadDialog` (primary/archive) — left alone this cycle
- F8 auto-push sinks
- Persisting destination secrets / weakening SSRF allowlist

## Routing

**Proposed:** Standard — `00 → 16 → 01 → 02 → 04 → 05 → 07 → 08 → 09 → 10 → 11 → 12 → 13`  
Skip `03`, `06` unless new rules/deps appear. Pending approval AskQuestion.

## Status

Opened 2026-08-07 after EV-041 close (PR #895 merged @ `fa5b2140`).
