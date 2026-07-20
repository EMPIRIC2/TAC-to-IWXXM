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

**Phase 0 — NOT fully approved.** Batch 1 + Batch 2 locked Assumed (written interview;
AskQuestion UI waived in cloud). **Batch 3 recorded PARTIAL** 2026-07-20 — clarifications
still needed (Q10 Ambiguity, Q11 pending recommendation, Q14 Ambiguity) before routing lock
and any `F16+` in `feature-list.md`.

### Batch 1 (Assumed / written) — still locked 2026-07-20

| ID | Decision |
|----|----------|
| Creds | One-shot session credentials — paste in UI; **never persist** / never saved profiles |
| UI | Drawer for send/upload destination + preflight |
| Schema | Require **existing** table matching versioned writer contract (no create-if-missing) |
| Q1=A | Convert-in-app then send IWXXM to user's Postgres |
| Q2=A | Any authenticated user |
| Q3=A | Schema preflight clarity is the success metric |
| Q4=D | Include WIS2 + EDIS scaffolding in this ONE cycle |

### Batch 2 (Assumed / written) — locked 2026-07-20

| ID | Decision |
|----|----------|
| Q5=A | Paste in drawer → backend memory-only for preflight+upload (**never persist**) |
| Q6=B | URI-only + preflight + send (no discrete field form in v1) |
| Q7=A | Structured schema diff in drawer; **block Send** until preflight green |
| Q8=C | Ship all three to usable MVP — live wis2box + live EDIS path (**highest risk**) |
| Q9=A | Same drawer: destination type Postgres (now) / WIS2 / EDIS |

### Batch 3 (Assumed / written) — PARTIAL 2026-07-20 (AskQuestion waived / cloud)

| ID | Status | Decision / note |
|----|--------|-----------------|
| Q10 | **Recorded as stated; [Ambiguity] unresolved** | User: *"we're dropping supabase support just user has to provide byo credentials"*. **Do not invent resolution.** Open interpretations: **(1)** drop Supabase Auth+DB entirely and replace with user-pasted credentials for auth AND data; **(2)** drop hosted Supabase dependency for app auth in favor of another IdP; **(3)** only dissemination destinations are BYO-paste while app auth changes separately. |
| Q11 | **Not locked** | User asked for recommendation — pending agent recommendation + user confirm. Do **not** lock yet. |
| Q12=B | Locked Assumed | Staging wis2box stood up in **this project's infra** |
| Q13=A | Locked Assumed | Real SMTP/submission to **NWS Telecommunications Gateway (RTH Washington)** |
| Q14=B | Locked Assumed + **[Ambiguity]** | User selected **only B** (saved/encrypted connection profiles **out of scope**). Ambiguity: options A/C/D/E were **not** selected — confirm whether only B is out of scope or user misunderstood multi-select. |
| Q15=A | Locked Assumed | Keep Q8=C — **block cycle close** until Postgres + WIS2 + EDIS all green on **real targets** |

**Advisory (supersedes Batch 2 readiness note):** Q15=A + Q8=C means live Postgres + wis2box + EDIS
(RTH Washington) are hard close gates — not optional smoke later.

### Unresolved [Ambiguity] / clarifications still needed

1. **I-S019-EV014-Q10-supabase-byo** — Q10 meaning (1)/(2)/(3) above; do not invent.
2. **I-S019-EV014-Q11-pending-rec** — agent recommendation + user confirm before lock.
3. **I-S019-EV014-Q14-multiselect** — confirm only B out-of-scope vs multi-select misunderstanding.

### Corpus contradictions noted (not resolved this batch)

Recorded for Phase 0 / 01-requirements — **do not silently override corpus**:

| Corpus item | Tension with Batch 1–3 |
|-------------|------------------------|
| **ADR-021** BYO deploy-env Supabase (no in-app paste-keys) | Q5/Q10 paste BYO + “dropping supabase support” collide with deploy-env BYO model |
| **F5** work history on Supabase | Q10 “drop supabase” may imply F5 store/auth redesign |
| **Non-goals**: push sinks; paste-keys UI | Q8=C / Q12–Q13 live WIS2+EDIS + paste credentials are push-sink / paste-keys adjacent |
| **Batch 1**: require-existing table | Implies DDL/create-if-missing out (consistent unless later reversed) |
| **Batch 1**: convert-then-send (Q1=A) | Implies drag-drop-of-external-IWXXM maybe out |

### Prior session

S018 / EV-013 closed 2026-07-20 (Q0=A waive leftover 08/09/11/12 bookkeeping); #750 remarks live.

## Feature mapping

TBD after Phase 0 fully approved — **do not invent F16+ yet**.

## Links

- [#729](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/729) Upload to Database
- [#2](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/2) WIS2
- [#6](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/6) EDIS
