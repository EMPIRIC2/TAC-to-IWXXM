# GitHub Project board — TAC-to-IWXXM

Canonical Project Status and planning policy for agents and humans.

[Corpus: project-board] · Decision log: [decisions/ev-project-board-planning.md](decisions/ev-project-board-planning.md)

| Key | Value |
|-----|--------|
| Owner | `EMPIRIC2` |
| Project | **#7** — [TAC-to-IWXXM](https://github.com/orgs/EMPIRIC2/projects/7) |
| Repo | `EMPIRIC2/TAC-to-IWXXM` |
| Capacity | **20 h/week** solo · ~**15 shipping h/week** · **2-week** iterations (~**30 shipping h**/iteration) |
| I01 start | **2026-09-15** (Mon–Sun × 2; each Ix = 14 days) |

## Status columns (left → right)

`Backlog` → `Ready` → `In progress` → `In review` → `On stage` → `On main` → `Done`

| Status | Meaning |
|--------|---------|
| Backlog | Parked / umbrella / spike / not next |
| Ready | Shippable slice; pull only when a WIP slot is free |
| In progress | Active session / implementation |
| In review | Implementing PR open |
| On stage | On `stage` / staging smoke green |
| On main | On `main` / prod smoke green |
| Done | AC met; session closed |

## Planning fields

| Field | Values | Use |
|-------|--------|-----|
| Priority | P0–P3 | Board rank (keep issue `priority-*` labels aligned) |
| Size | XS / S / M / L / XL | Relative effort (XS≈2h … XL≈32h) |
| Estimate (h) | number | Hours for this issue (or remaining chunk) |
| Iteration | I00-Backlog, I01… | Two-week bucket; epics stay `I00-Backlog` |
| Due date | date | Prefer milestone due; override for hard gates |

Size → hours guide: **XS=2 · S=4 · M=8 · L=16 · XL=32**.

## Velocity / WIP

1. **Done rate:** ≈ **1–2** shippable issues/week at 20 h ≡ **2–4** Done / **2-week** iteration (supersedes older ~12 Done/week swarm assumption).
2. **WIP cap:** ≤ **2** issues in `In progress` (prefer **1**).
3. **Ready queue:** keep **3–5** small shippable issues in `Ready`. Refill from the **active milestone** first.
4. **Epics:** `epic`-labeled issues stay in `Backlog` / `I00-Backlog` until children are Done.
5. **Sizing:** one Done issue ≈ one mergeable PR. Split umbrellas before Ready.
6. **Orphans:** every open issue must be on Project #7 (`item-add` if missing).

## Lifecycle sync (agents)

| Trigger | Status |
|---------|--------|
| Session / evolve / hotfix open (linked issue) | `In progress` |
| Implementing PR opened | `In review` |
| Merged to `stage` / staging smoke green | `On stage` |
| Merged to `main` / prod smoke green | `On main` |
| AC done / session close | `Done` |

## Auto-import new tickets

1. **Preferred:** Project → Workflows → **Auto-add to project** for `EMPIRIC2/TAC-to-IWXXM`, filter `is:issue`, enabled.
2. **Fallback CI:** `.github/workflows/project-auto-add.yml` uses `actions/add-to-project` on `issues: [opened, reopened, transferred]`. Requires repo secret **`PROJECT_TOKEN`**: a **fine-grained PAT** on a dedicated bot account with **Organization → Projects (read & write)** and **Repository → Issues (read-only)** for `EMPIRIC2/TAC-to-IWXXM` only. Do **not** use a classic PAT with blanket `repo` scope.

Sub-issue auto-add may already be enabled; it does **not** replace issue auto-add.

## Milestones (SOW pace)

IWXXM deadlines follow these GitHub milestones (not the EMPIRIC2-planning climate-validation SOW).

| Milestone | Due | Focus |
|-----------|-----|--------|
| [M1](https://github.com/EMPIRIC2/TAC-to-IWXXM/milestone/4) — Profiles | 2026-09-19 | Annex 3 / US / custom closeout |
| [M2](https://github.com/EMPIRIC2/TAC-to-IWXXM/milestone/5) — Dissemination realtime | 2026-10-17 | #843 family; WIS2/EDIS/AMHS/AFTN |
| [M3](https://github.com/EMPIRIC2/TAC-to-IWXXM/milestone/6) — Automation | 2026-11-07 | #876; live harvest / DB |
| [M4](https://github.com/EMPIRIC2/TAC-to-IWXXM/milestone/7) — Nov 11 gate | 2026-11-11 | Hardening, manuals, demo freeze |
| [M5](https://github.com/EMPIRIC2/TAC-to-IWXXM/milestone/8) — Post-workshop / AMS | 2027-01-31 | Platform UI deepen, AMS |

**Nov 11 must-ship (solo):** #1159, thin #911+#806, #1028–1031, #1121–1123, #1025, #949, spike #877.  
**Slip post-gate unless thinned:** #909, #910, #777, #728, #970 remainder, M5 UI.

Live schedule snapshot: session `EV-project-board-planning` → `reports/draft-schedule.md`.

## Views (recommended)

- **Board** — Group by Status
- **Ready** — `status:Ready`
- **WIP** — `status:"In progress","In review"`
- **By iteration** — Group by Iteration (table)
