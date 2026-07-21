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
AskQuestion UI waived in cloud). **Batch 3 clarifications recorded 2026-07-20/21** — Q10/Q11/Q12/Q13/Q15/Q16
locked; **Q14 [Contradiction] open** blocks Phase 0 approval until next interview turn. No `F16+`
in `feature-list.md` yet.

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

### Batch 3 (Assumed / written) — clarifications 2026-07-20/21 (AskQuestion waived / cloud)

| ID | Status | Decision / note |
|----|--------|-----------------|
| Q10 | **Locked Assumed** | **NOT** dropping Supabase Auth — login stays Supabase-handled. “Dropping Supabase for database” applies **only** to Sending/converting dissemination destination: users provide one-shot BYO Postgres URI for upload/send (not using Supabase as the ops/send DB). **Q10A=D:** deploy-time BYO for **app auth** (operator sets Supabase env once; users don’t paste app auth) — aligned with ADR-021. **Q10B:** N/A / see above. |
| Q11=A+B | **Locked Assumed** | Max-security SSRF package: full recommended baseline (backend-only egress, deny private/metadata ranges, DNS rebinding guard, TLS preferred, timeouts/size limits, secret redaction, rate limit) **PLUS require** deploy allowlist `DISSEMINATION_EGRESS_ALLOWLIST` (host/CIDR) — empty allowlist = no user-URI egress in prod (staging may use explicit list). |
| Q12=B | Locked Assumed | Staging wis2box stood up in **this project's infra** |
| Q13=A | Locked Assumed | Real SMTP/submission to **NWS Telecommunications Gateway (RTH Washington)** |
| Q14=A | Locked Assumed + **[Contradiction]** | User chose **A** = only saved/encrypted profiles out of scope (B-only from the out-of-scope list). **Do not assume** DDL/create-if-missing, drag-drop external IWXXM, AMHS, or multi-DB are in. **Contradiction** with Batch 1 require-existing table (no create-if-missing) and Q1=A convert-then-send — Phase 0 **NOT** approved until resolved in next interview turn. |
| Q15=A | Locked Assumed | Keep Q8=C — **block cycle close** until Postgres + WIS2 + EDIS all green on **real targets** |
| Q16 | **Locked Assumed** | User/operator must bring **own credentials** (EDIS/RTH; by extension WIS2/DB destinations as applicable). Cycle still blocks on live green per Q15=A. Credentials are customer/operator-supplied, **not** provisioned by us (except staging wis2box infra per Q12=B). |

**Advisory (supersedes Batch 2 readiness note):** Q15=A + Q8=C means live Postgres + wis2box + EDIS
(RTH Washington) are hard close gates — not optional smoke later. Credentials are BYO (Q16).

### Open [Contradiction] (blocks Phase 0 full approval)

1. **I-S019-EV014-Q14-batch1** — Q14=A (only profiles OOS) vs Batch 1 require-existing / no create-if-missing + Q1=A convert-then-send. Do not silently expand scope to DDL / drag-drop / AMHS / multi-DB. Resolve in next interview turn.

### Resolved this clarification turn

- **I-S019-EV014-Q10-supabase-byo** — resolved (auth stays Supabase; send-DB BYO only; Q10A=D ↔ ADR-021)
- **I-S019-EV014-Q11-pending-rec** — resolved (Q11=A+B max-security + required allowlist)
- **I-S019-EV014-Q14-multiselect** — superseded by Q14=A lock + **I-S019-EV014-Q14-batch1** Contradiction

### Corpus contradictions (updated)

| Corpus item | Status / tension |
|-------------|------------------|
| **ADR-021** BYO deploy-env Supabase (no in-app paste-keys for app auth) | **Eased by Q10** — app auth stays deploy-time Supabase (Q10A=D); paste BYO is **destination** URI only (Q5/Q6) |
| **F5** work history on Supabase | **Eased by Q10** — Auth+F5 store remain Supabase; only send/ops destination DB is BYO |
| **Non-goals**: push sinks; paste-keys UI | Still open vs Q8=C / Q12–Q13 live WIS2+EDIS + paste destination credentials |
| **Batch 1**: require-existing + Q1=A | **Open Contradiction** with Q14=A reading (see I-S019-EV014-Q14-batch1) |

### Prior session

S018 / EV-013 closed 2026-07-20 (Q0=A waive leftover 08/09/11/12 bookkeeping); #750 remarks live.

## Feature mapping

TBD after Phase 0 fully approved — **do not invent F16+ yet**.

## Links

- [#729](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/729) Upload to Database
- [#2](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/2) WIS2
- [#6](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/6) EDIS
