---
session_id: S024-dissemination-file-select
type: feature
status: in_progress
branch: evolve/EV-018-dissemination-file-select
started_at: 2026-07-28
intent: "Multi-file selection in dissemination portal for export preflight/send (#785)"
orchestrator: 16-evolve
evolve_cycle_id: EV-018
github_issue: 785
context_briefs:
  - docs/context/dissemination-file-select.md
standing_docs_touched:
  - docs/feature-list.md
  - docs/spec.md
  - docs/api-contract.md
  - docs/user-journeys.md
  - docs/test-plan.md
  - docs/decisions/evolve-decisions.md
  - docs/context/dissemination-file-select.md
prior_session: S023-public-app-privacy
scope_lock_decision_id: D-S024-E18-scope-lock
---

# Session S024 — dissemination-file-select

## Intent

Add **multi-file selection** in the dissemination portal (drawer) so operators can choose
which converted / uploaded artifacts to preflight and send, instead of a single implicit
payload ([#785](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/785)).

Extends **F16–F19** dissemination UX; preserves BYOC memory-only credentials
(ADR-021 / ADR-029 / ADR-030). Public-app context from **S023 / F21** applies (no operator JWT).

## Prior session

| Item | Disposition |
|------|-------------|
| S023 / EV-017 / #783 | **Completed** (session closed); PR #790 — public app + privacy |
| S019 / EV-014 / F16–F19 | **Shipped** — dissemination drawer + sinks |
| Issue #785 | **Open** — multi-file export selection |

## Classification

| Field | Value |
|-------|-------|
| Session type | **`feature`** |
| Orchestrator | **16-evolve** (EV-018) |
| Preset | **Lean+build** (E18-3 → E18-7) |
| Branch | `evolve/EV-018-dissemination-file-select` |
| Fn allocation | **Deepen F16** (E18-2); F17–F19 reuse the same selection contract |

## Scope (Phase 0 — Batch 1+2 **locked** 2026-07-28 — awaiting formal scope-lock)

### In (from issue #785 + intake)

1. Export selection panel: eligible payloads (name, product type, size/status, source)
2. Multi-select (checkboxes + select-all / clear); empty selection disables Preflight/Send
3. Preflight + Send apply only to selection; per-file pass/fail/skip feedback
4. Same selection contract for multi-DB (**F16**) and reuse for WIS2/EDIS/AMHS (**F17–F19**)
5. Candidates = **current-session + dropped files only** (E18-4); Finished history deferred
6. **N sequential** `/preflight` + `/send` with UI aggregation (E18-5) — no batch API v1
7. Selection **count cap ≤20** + existing body/size limits (E18-6)
8. Unit + e2e coverage (extend UJ-027–030 / drawer Vitest)

### Out (v1 non-goals)

- Saved dissemination profiles / remembered destinations
- F8 worker auto-push
- Cross-session bulk archive download (browser zip) unless it reuses selection UI later
- IndexedDB / Finished **work-history** as selectable sources (defer)
- Batched multi-payload dissemination API (defer; sequential only)

### Security invariants (non-negotiable)

- BYOC credentials remain one-shot / memory-only
- No new persistence of destination secrets
- `DISSEMINATION_EGRESS_ALLOWLIST` unchanged

## Intake decisions

| ID | Decision |
|----|----------|
| E18-1 | **A** — Open `S024` → 16-evolve / EV-018 |
| E18-2 | **B** — Deepen **F16**; F17–F19 reuse selection contract (no F23) |
| E18-3 | **B** — Lean (amended by E18-7) |
| E18-4 | **A** — Current-session + dropped files only in v1 |
| E18-5 | **A** — N sequential `/preflight`+`/send`; UI aggregates |
| E18-6 | **A** — Count cap ≤20 + existing body/size limits |
| E18-7 | **A** — Amend to **Lean+build** (`00→16→01→02→04→07→08→10→13`) |
| E18-8 | **A** — Open **local / non-deployed** UI preview now |

## AskQuestion

Unavailable in this environment — **written interview** (same pattern as S023).
