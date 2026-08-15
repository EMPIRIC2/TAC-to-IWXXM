---
session_id: S067-m0-ready-apex-accumulate-validate
type: feature
status: in_progress
branch: evolve/EV-057-m0-ready-apex-accumulate-validate
orchestrator: 16-evolve
evolve_cycle_id: EV-057
github_issues: [948, 903, 838]
prior_session: S066-quality-metrics-diff-page
opened: 2026-08-15
---

# Session brief — S067-m0-ready-apex-accumulate-validate

> **Cycle**: EV-057 · **Type**: feature · **Opened**: 2026-08-15  
> **Branch**: `evolve/EV-057-m0-ready-apex-accumulate-validate` (base `stage@b796882e`)  
> **Orchestrator**: **16-evolve** · **Preset**: **Standard**  
> **Issues**: [#948](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/948), [#903](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/903), [#838](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/838)  
> **Corpus**: [Corpus: product §F7] [Corpus: product §F1] [Corpus: product §F6] [Corpus: product §F2] [Corpus: product §F4] [Corpus: tech-spec] [Corpus: deploy] [Corpus: journeys]

## Goal

Ship M0 Ready issues **#948** (apex → `app.` redirect), **#903** (accumulate conversions → one ZIP), and **#838** (validate existing IWXXM paste/upload) onto **`stage`** under Standard routing; **promote to `main` only after a separate user re-approve**.

## Intent

Close the three shippable M0 Ready items in one evolve cycle (epic [#841](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/841) stays Backlog). Order: **#948 → #903 → #838**.

| Decision | Choice |
|----------|--------|
| D-S067-first | **1a** — #948 first |
| D-S067-pack | **2c** — one cycle, all three Ready |
| D-S067-success | **3c** — stage + promote path |
| D-S067-oos | **1a** — exclude #841/#727/#874; S056 ruleset-admin leftover; drive-bys |
| D-S067-promote | **2b** — land all three on `stage` first; promote only after re-approve |
| D-S067-blockers | **3a** — none known; surface as found |
| D-S067-preset | **4a** — Standard |
| D-S067-type | **1a** — `feature` → 16-evolve |
| D-S067-order | **2a** — #948 → #903 → #838 |
| D-S067-ui-preview | **3a** — remind at 11-verify-impl |
| D-S067-proceed | **4a** — open S067 + EV-057 |
| D-S067-board | **1** — #948 → In progress (WIP 1); #903/#838 stay Ready until started |

## In scope

1. **#948** — Permanent redirect `tac-to-iwxxm.com` (+ `www` if covered) → `https://app.tac-to-iwxxm.com`; TLS; document in deploy docs. [Corpus: tech-spec] [Corpus: deploy]
2. **#903** — Accumulate sequential successful conversions; Download all ZIP; content-derived default archive name; clear/reset. [Corpus: product §F1/F6/F7]
3. **#838** — Paste/upload existing IWXXM → F2 validate without TAC convert; F4 version/profile consistency. [Corpus: product §F2/F4/F7]

## Out of scope

- [#841](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/841) epic and children [#727](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/727) / [#874](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/874)
- S056 converter-perf **ruleset apply** (repo-admin leftover; not a ticket)
- Batch disseminate of accumulated set; F33 mass-ingest path as substitute for #903
- Reverse-engineering TAC from IWXXM (#838)
- Promote to `main` until explicit re-approve after all three are on `stage`

## Success criteria (session)

- All three issues meet their GitHub AC on **`stage`** with Standard verify/smoke as routed
- Board: issues move Ready → In progress → In review / On stage → Done as milestones land
- Promote AskQuestion only after stage smoke for the full pack

## UI preview

**Remind at 11-verify-impl** (`D-S067-ui-preview=3a`) — non-deployed / local only when offered; not staging/prod.

## Board

- Project [#7 TAC-to-IWXXM](https://github.com/orgs/EMPIRIC2/projects/7)
- WIP: **#948 In progress** (1 ≤ 2); #903/#838 remain Ready until their milestones start
