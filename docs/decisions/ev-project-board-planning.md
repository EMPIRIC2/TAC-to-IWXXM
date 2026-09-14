# EV-project-board-planning — board velocity & schedule

**Session:** `EV-project-board-planning` (2026-09-13)  
**Orchestrator:** evolve  
**Standing doc:** [docs/project-board.md](../project-board.md) · [Corpus: project-board]

## Problem

Open work lacked maintainable Priority / Size / Estimate / Iteration / dates on the
GitHub board. Historical close rates (~12–20 Done/week) reflected swarm/agent pace,
not solo **20 h/week**.

## Decisions

| ID | Decision |
|----|----------|
| D-EV-PBP-01 | Reuse org Project **#7**; do not create a duplicate board |
| D-EV-PBP-02 | Capacity **20 h/week**, ~**15 shipping h**, ~~**1-week** iterations~~ → superseded cadence by **D-EV-TWI-01**, **I01 = 2026-09-15** |
| D-EV-PBP-03 | Target **1–2 Done issues/week** (supersede ~12 Done/week assumption in older board README); with 2-week iterations ≡ **2–4 Done / iteration** (**D-EV-TWI-01**) |
| D-EV-PBP-04 | Deadlines = GitHub milestones M1–M5 + Nov 11 Directors gate (not EMPIRIC2-planning climate SOW) |
| D-EV-PBP-05 | Board fields: Priority, Size, Estimate (h), Iteration, Due date |
| D-EV-PBP-06 | Auto-import via Project Auto-add + Actions fallback (secret `PROJECT_TOKEN`) |
| D-EV-PBP-07 | CORPUS opt-in row **project-board** |
| D-EV-PBP-09 | Nov 11 must-ship set + explicit slips (#909/#910/#777/#728/#970 remainder) |
| D-EV-TWI-01 | **EV-two-week-iterations (2026-09-14):** Iteration cadence **2 weeks** (14 days Mon–Sun×2); I01 start unchanged **2026-09-15**; capacity still 20 h/week; remapping of existing Iteration values via **pair-merge** (old I(2n−1)+I(2n) → new In); option labels stay `I01`…`I30` (no date-in-name rename this cycle) |

## Non-goals

- Implementing product tickets in this cycle
- Changing milestone due dates without a separate AskQuestion
- Switching Iteration from single-select to native GitHub Iteration field (deferred)
