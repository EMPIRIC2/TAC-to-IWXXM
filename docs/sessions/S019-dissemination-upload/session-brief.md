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

**Phase 0 — NOT fully approved.** Batch 1–3 locked Assumed (written interview;
AskQuestion UI waived in cloud). **Batch 4 locked 2026-07-21** — Q14r/Q17/Q18/Q19 recorded;
**Q14r extras enum [Ambiguity] open** blocks Phase 0 approval until next interview enumerates
which of {DDL, drag-drop, multi-DB, AMHS} are IN for v1. No `F16+` in `feature-list.md` yet.

### Batch 1 (Assumed / written) — still locked 2026-07-20

| ID | Decision |
|----|----------|
| Creds | One-shot session credentials — paste in UI; **never persist** / never saved profiles |
| UI | Drawer for send/upload destination + preflight |
| Schema | Require **existing** table matching versioned writer contract (no create-if-missing) — *may be amended if DDL selected in Q14r enum* |
| Q1=A | Convert-in-app then send IWXXM to user's Postgres — *may be amended if drag-drop selected in Q14r enum* |
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
| Q12=B | **Locked Assumed** (amended Batch 4) | Staging wis2box in **this project's infra** = **test harness only** (see Q17). Production / live WIS2 acceptance uses **user-supplied** WIS2 endpoint credentials (BYOC). |
| Q13=A | Locked Assumed | Real SMTP/submission to **NWS Telecommunications Gateway (RTH Washington)** |
| Q14=A | **Locked Assumed** (literal kept) | Only saved/encrypted connection profiles out of scope (B-only from the original OOS list). Literal Q14=A **kept**; see Q14r for intentional scope expansion. |
| Q15=A | Locked Assumed | Keep Q8=C — **block cycle close** until Postgres + WIS2 + EDIS all green on **real targets** |
| Q16 | **Locked Assumed** | User/operator must bring **own credentials** (EDIS/RTH; by extension WIS2/DB destinations as applicable). Cycle still blocks on live green per Q15=A. Credentials are customer/operator-supplied, **not** provisioned by us (except staging wis2box **test harness** per Q12=B/Q17). |

### Batch 4 (Assumed / written) — locked 2026-07-21 (AskQuestion waived / cloud)

| ID | Status | Decision / note |
|----|--------|-----------------|
| Q14r=B | **Locked Assumed** + **[Ambiguity] pending enum** | Keep **Q14=A literally** (profiles still OOS). Epic **also designs** DDL, drag-drop external IWXXM, multi-DB, **and/or** AMHS — user chose **expand scope (B)** rather than recommended pack (A). **Still-[Ambiguity]:** which of {DDL, drag-drop, multi-DB, AMHS} are **IN for v1** of this cycle — “and/or” not enumerated. Phase 0 **blocked** on that enumeration (next interview). Prior Contradiction **I-S019-EV014-Q14-batch1** resolved as **scope expanded intentionally**; sub-issue **I-S019-EV014-Q14r-extras-enum** open for which extras. |
| Q17=A | **Locked Assumed** (**testing only**) | Stand up staging wis2box on Render/Docker **for test**. For **live** WIS2 the user brings own credentials/node (**BYOC**). Amends Q12=B: project staging wis2box = test harness; production acceptance = user-supplied WIS2 endpoint creds. |
| Q18≈A (BYOC) | **Locked Assumed** | User brings own credentials for EDIS (and live paths). Interpret as **Q18≈A**: backend uses **one-shot user-pasted SMTP/gateway settings in drawer** (memory-only), **not** deploy-only operator SMTP. Testing also BYOC. |
| Q19=A | **Locked Assumed** | Work history stays in Supabase `tac_work_sessions` / `kv_upload_key`; **never** store destination secrets. |

**Advisory (supersedes Batch 2 readiness note):** Q15=A + Q8=C means live Postgres + WIS2 + EDIS
(RTH Washington) are hard close gates — not optional smoke later. Staging wis2box is in-project
**test harness** only (Q17); live WIS2 + EDIS + DB destinations are BYOC (Q16/Q17/Q18).

### Open [Ambiguity] (blocks Phase 0 full approval)

1. **I-S019-EV014-Q14r-extras-enum** — Q14r=B expands epic design to DDL / drag-drop / multi-DB / AMHS (“and/or”), but **v1 IN-set not enumerated**. Next interview must pick which of {DDL, drag-drop, multi-DB, AMHS} are in for this cycle’s v1.

### Resolved this Batch 4 turn

- **I-S019-EV014-Q14-batch1** — resolved: user chose expand scope (Q14r=B) rather than recommended pack (A); contradiction closed as **scope expanded intentionally**; extras enum tracked as I-S019-EV014-Q14r-extras-enum
- **F5 / destination secrets** — locked by Q19=A (work history stays Supabase; never store destination secrets)

### Corpus contradictions (updated)

| Corpus item | Status / tension |
|-------------|------------------|
| **ADR-021** BYO deploy-env Supabase (no in-app paste-keys for app auth) | **Eased by Q10** — app auth stays deploy-time Supabase (Q10A=D); paste BYO is **destination** URI/SMTP only (Q5/Q6/Q18) |
| **F5** work history on Supabase | **Locked by Q19=A** — Auth+F5 store remain Supabase; never store destination secrets |
| **Non-goals**: push sinks; paste-keys UI | Partially eased — paste is intentional for **destination** creds (Q5/Q18≈A memory-only); push-sinks non-goal vs Q8=C live WIS2+EDIS still needs non-goal inventory after Q14r enum |
| **Batch 1**: require-existing + Q1=A | **Contradiction resolved** as intentional expand (Q14r=B); **v1 extras enum still open** |

### Prior session

S018 / EV-013 closed 2026-07-20 (Q0=A waive leftover 08/09/11/12 bookkeeping); #750 remarks live.

## Feature mapping

TBD after Phase 0 fully approved — **do not invent F16+ yet**.

## Links

- [#729](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/729) Upload to Database
- [#2](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/2) WIS2
- [#6](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/6) EDIS
