# 01-requirements — S019 / EV-014 (delta)

**Date**: 2026-07-21  
**Mode**: delta / evolve  
**Status**: completed (corpus delta for Phase A)

## Inputs

- Phase 0 approved (Q23=A–D, Q24=A Full routing)
- Issues #729, #2, #6
- Intake Batches 1–5 locked (see evolve-decisions EV-014)

## Artifacts updated

| Document | Delta |
|----------|-------|
| `docs/feature-list.md` | F16–F19 Planned; non-goals amended |
| `docs/user-journeys.md` | UJ-027–030 |
| `docs/test-plan.md` | TC-F16..F19 + scope |
| `docs/spec.md` | F16–F19 section; BYO amend |
| `docs/adr/ADR-021-…` | Destination paste amendment |
| `docs/adr/ADR-029-…` | SSRF + allowlist (Proposed) |
| `docs/decisions/evolve-decisions.md` | Phase 0 approved |
| `docs/decisions/requirements-decisions.md` | EV-014 decision table |

## Deferred to 04-tech-plan

- API sketch (`/upload/preflight`, sink handles)
- Writer-contract column DDL per engine
- wis2box Render service shape
- EDIS SMTP library choice
- AMHS/SWIM/AFS protocol details

## Next

02-verify-plan (delta consistency pass).
