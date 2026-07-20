---
session_id: S019-dissemination-upload
type: feature
status: in_progress
branch: cursor/dissemination-upload-e25c
started_at: 2026-07-20
intent: "Dissemination epic — Upload to Database (#729) + WIS2 (#2) + EDIS (#6)"
orchestrator: 16-evolve
evolve_cycle_id: EV-014
context_briefs: []
standing_docs_touched:
  - docs/decisions/evolve-decisions.md
---

# Session S019 — dissemination-upload

## Intent

One BIG dissemination evolve cycle covering:

1. **Upload to Database** ([#729](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/729)) —
   user-supplied one-shot Postgres credentials + schema preflight + send drawer UI
2. **WIS2 pathway scaffolding** ([#2](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/2))
3. **EDIS-compliant dissemination scaffolding** ([#6](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/6))

## Intake status

**Phase 0 — NOT fully approved.** Batch 1 locked Assumed (written interview; AskQuestion UI
waived in cloud). **Batch 2 pending** before routing lock and any `F16+` in `feature-list.md`.

### Batch 1 (Assumed / written)

| ID | Decision |
|----|----------|
| Creds | One-shot session credentials — paste in UI; **never persist** / never saved profiles |
| UI | Drawer for send/upload destination + preflight |
| Schema | Require **existing** table matching versioned writer contract (no create-if-missing) |
| Q1=A | Convert-in-app then send IWXXM to user's Postgres |
| Q2=A | Any authenticated user |
| Q3=A | Schema preflight clarity is the success metric |
| Q4=D | Include WIS2 + EDIS scaffolding in this ONE cycle |

### Prior session

S018 / EV-013 closed 2026-07-20 (Q0=A waive leftover 08/09/11/12 bookkeeping); #750 remarks live.

## Feature mapping

TBD after Phase 0 fully approved — **do not invent F16+ yet**.

## Links

- [#729](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/729) Upload to Database
- [#2](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/2) WIS2
- [#6](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/6) EDIS
