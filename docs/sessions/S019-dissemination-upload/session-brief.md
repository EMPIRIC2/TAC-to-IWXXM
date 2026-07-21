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
---

# Session S019 — dissemination-upload

## Intent

One BIG dissemination evolve cycle covering:

1. **Upload to Database** ([#729](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/729)) —
   user-supplied one-shot DB credentials + schema preflight + send drawer UI
   (DDL create-if-missing, drag-drop IWXXM/TAC, multi-DB beyond Postgres)
2. **WIS2 pathway** ([#2](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/2)) —
   staging wis2box test harness + live BYOC
3. **EDIS-compliant dissemination** ([#6](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/6)) —
   RTH Washington via BYOC SMTP/gateway
4. **AMHS / SWIM / AFS adapters** (Q20=D — overturn prior non-goals for this cycle)

## Intake status

**Phase 0 — NOT fully approved.** Batch 1–5 locked Assumed (written interview;
AskQuestion UI waived in cloud). **Batch 5 locked 2026-07-21** — Q20/Q21/Q22 recorded;
**I-S019-EV014-Q14r-extras-enum resolved** (all four extras IN). **Still open:**
**I-S019-EV014-Q20C-vendors** (multi-DB vendor list) + **user approval gate** on draft
Fn allocation + scope + Full routing (Q22=A). No `F16+` rows in `feature-list.md` yet
(draft Fn table below only — awaiting approval).

### Batch 1 (Assumed / written) — still locked 2026-07-20 (**amended Batch 5**)

| ID | Decision |
|----|----------|
| Creds | One-shot session credentials — paste in UI; **never persist** / never saved profiles |
| UI | Drawer for send/upload destination + preflight |
| Schema | **Superseded by Q20=A:** DDL / create-if-missing allowed (overrides earlier require-existing-only) |
| Q1 | **Amended by Q20=B:** Convert-in-app then send **plus** drag-drop upload of external IWXXM/TAC |
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
| Q14r=B | **Locked Assumed** (enum resolved Batch 5) | Keep **Q14=A literally** (profiles still OOS). Epic **also designs** DDL, drag-drop external IWXXM, multi-DB, **and** AMHS — user chose **expand scope (B)**. v1 IN-set enumerated in Batch 5 Q20 (all four). |
| Q17=A | **Locked Assumed** (**testing only**) | Stand up staging wis2box on Render/Docker **for test**. For **live** WIS2 the user brings own credentials/node (**BYOC**). Amends Q12=B: project staging wis2box = test harness; production acceptance = user-supplied WIS2 endpoint creds. |
| Q18≈A (BYOC) | **Locked Assumed** | User brings own credentials for EDIS (and live paths). Interpret as **Q18≈A**: backend uses **one-shot user-pasted SMTP/gateway settings in drawer** (memory-only), **not** deploy-only operator SMTP. Testing also BYOC. |
| Q19=A | **Locked Assumed** | Work history stays in Supabase `tac_work_sessions` / `kv_upload_key`; **never** store destination secrets. |

### Batch 5 (Assumed / written) — locked 2026-07-21 (AskQuestion waived / cloud)

| ID | Status | Decision / note |
|----|--------|-----------------|
| Q20=B,C,A,D | **Locked Assumed** | **All four extras IN** for this cycle: **A)** DDL / create-if-missing (**supersedes** Batch 1 require-existing-only); **B)** drag-drop upload of IWXXM/TAC **in addition to** convert-then-send; **C)** multi-DB beyond Postgres — **vendor list still needed** (open **I-S019-EV014-Q20C-vendors**); **D)** AMHS / SWIM / AFS adapters **IN** this cycle. Resolves **I-S019-EV014-Q14r-extras-enum**. |
| Q21=A | **Locked Assumed** | Staging/test OK for merge; **live BYOC demos required before cycle close** (with Q15=A). |
| Q22=A | **Locked Assumed** (proposed) | **Full routing preset** (stages 00–13). Awaiting user approval gate with Fn+scope. |

**Advisory (supersedes Batch 2 readiness note):** Q15=A + Q8=C + Q21=A means live Postgres + WIS2 + EDIS
(RTH Washington) (+ AMHS/SWIM/AFS per Q20=D) are hard close gates — staging/test can merge;
live BYOC demos required before cycle close. Staging wis2box is in-project **test harness**
only (Q17); live WIS2 + EDIS + DB destinations are BYOC (Q16/Q17/Q18).

### Open [Ambiguity] (blocks Phase 0 full approval)

1. **I-S019-EV014-Q20C-vendors** — Q20=C multi-DB beyond Postgres is IN, but **vendor/engine list
   not yet specified** (e.g. MySQL, SQL Server, Oracle, SQLite, …). Next interview must lock vendors.

### Awaiting Phase 0 approval gate

1. Multi-DB vendor list (I-S019-EV014-Q20C-vendors)
2. User approval of draft Fn allocation + scope + Full routing (Q22=A)

### Resolved this Batch 5 turn

- **I-S019-EV014-Q14r-extras-enum** — resolved: all four extras IN (Q20=A,B,C,D)
- Batch 1 Schema require-existing-only — **superseded** by Q20=A (DDL / create-if-missing)
- Batch 1 Q1=A convert-then-send-only — **amended** by Q20=B (plus drag-drop)

### Draft Fn allocation (PROPOSED — do NOT write `feature-list.md` rows until user approves)

| Fn | Title | Issues |
|----|-------|--------|
| F16 | Dissemination drawer + DB upload (URI one-shot, preflight, DDL, drag-drop, multi-DB) | #729 |
| F17 | WIS2 live pathway (staging wis2box test + live BYOC) | #2 |
| F18 | EDIS → RTH Washington (BYOC SMTP/gateway) | #6 |
| F19 | AMHS / SWIM / AFS adapters | (new / expand non-goals overturn) |

### Corpus amendments required (after Phase 0 approval → 01-requirements)

| Corpus item | Required change |
|-------------|-----------------|
| **Non-Goals** push sinks | Overturn / narrow — push sinks IN this cycle (WIS2/EDIS/AMHS/SWIM/AFS) |
| **Non-Goals** paste-keys | Clarify: paste allowed for **upload/destination creds only** (not app auth) |
| **Non-Goals** AMHS/SWIM/AFS | Overturn — adapters IN this cycle (Q20=D → F19) |
| **ADR-021** | Amend for destination paste (URI/SMTP memory-only; app auth stays deploy-time) |
| **ADR new** | Dissemination security / SSRF (Q11=A+B allowlist + baseline) |

### Corpus contradictions (updated)

| Corpus item | Status / tension |
|-------------|------------------|
| **ADR-021** BYO deploy-env Supabase (no in-app paste-keys for app auth) | **Eased by Q10** — app auth stays deploy-time Supabase (Q10A=D); paste BYO is **destination** URI/SMTP only (Q5/Q6/Q18) — **ADR-021 amend required** |
| **F5** work history on Supabase | **Locked by Q19=A** — Auth+F5 store remain Supabase; never store destination secrets |
| **Non-goals**: push sinks; paste-keys; AMHS/SWIM/AFS | **Inventory pending** after Phase 0 approval — Q8=C + Q20=D overturn push sinks / AMHS; paste = dest only |
| **Batch 1**: require-existing + Q1=A | **Superseded/amended** by Q20=A (DDL) + Q20=B (drag-drop) |

### Prior session

S018 / EV-013 closed 2026-07-20 (Q0=A waive leftover 08/09/11/12 bookkeeping); #750 remarks live.

## Feature mapping

**Draft only** (see table above) — write `feature-list.md` rows **only after** user approves
Phase 0 scope (vendors + Fn + Full routing).

## Links

- [#729](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/729) Upload to Database
- [#2](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/2) WIS2
- [#6](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/6) EDIS
