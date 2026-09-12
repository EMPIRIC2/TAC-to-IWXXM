---
session_id: S070-converter-operator-bugs
type: feature
status: closed
branch: evolve/EV-060-converter-operator-bugs
orchestrator: 16-evolve
evolve_cycle_id: EV-060
github_issues: [1000, 1001, 1002, 1003, 1004, 1005, 1006]
prior_session: S069-ci-schemathesis-mutation
opened: 2026-08-17
closed: 2026-08-18
merge_sha: 6ef540bc
pr: 1007
---

# Session brief — S070-converter-operator-bugs

> **Cycle**: EV-060 · **Type**: feature · **Opened**: 2026-08-17 · **Closed**: 2026-08-18  
> **Branch**: `evolve/EV-060-converter-operator-bugs` → PR [#1007](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/1007) **MERGED** @ `6ef540bc`  
> **Orchestrator**: **16-evolve** · **Preset**: **Standard** · **Promote**: held  
> **Issues**: epic [#1000](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1000) + children #1001–#1006 **CLOSED**  
> **13**: [deploy-smoke.md](reports/deploy-smoke.md) · **Summary**: [evolve-summary.md](reports/evolve-summary.md)  
> **Corpus**: [Corpus: product §F7] [Corpus: product §F6] [Corpus: product §F2] [Corpus: product §F10] [Corpus: product §F29] [Corpus: product §F31] [Corpus: product §F21] [Corpus: api] [Corpus: journeys] [Corpus: tests] [Corpus: decisions §EV-060]

## Goal

Fix operator-visible converter bugs and UX (AHL bulletin lint noise, clearer profile picker, IWXXM as product pass-through, wired log levels, Bulletin ID / Issuing Center) plus Auth/Register UAT, tracked by one M0 epic; Spec first, Build after gate.

## Intent

One feature cycle deepening **F7.t** (IWXXM product) plus F6/F2/F10/F29/F31. No new top-level Fn. GitHub milestone **M0**. Four Build PRs after gate (AHL → IWXXM product → UI params → Auth UAT).

| Decision | Choice |
|----------|--------|
| D-S070-e0 | **1a / 2a / 3a / 4a** — tickets + Spec first; M0 pack; in/out as written; continue intake |
| D-S070-e1 | **1a / 2a / 3a / 4a** — operator bugs/UX now; deepen F7.t (no F35); file tickets at EV9; success = six observables |
| D-S070-e2 | **1b / 2b / 3a / 4a** — operator + API/CLI; include FileConverter/accumulate/QM honor; fence as written; UI preview at 11 |
| D-S070-e3a | **1a / 2a / 3a / 4a** — AHL split then lint reports; product=IWXXM pass-through; F7.s stays; error/empty as drafted |
| D-S070-e3b | **1a / 2a / 3a / 4b** — labeled Profile at converter top; editable Bulletin ID + Issuing Center; wire log_level; a11y must-have |
| D-S070-e3c | **1a / 2c / 3a / 4a** — Auth UAT + Playwright; FileConverter/QM/accumulate honor profile+IWXXM; API same fields |
| D-S070-e4 | **1a / 2a / 3a / 4a** — standing docs delta; existing CORPUS; uat+verify-qa Spec; Standard Spec 01→02→04 |
| D-S070-e5 | **1a / 2a / 3a / 4a** — FE/BE/packages/e2e; four PRs; 09+10+11+uat; staging smoke, promote held |
| D-S070-e6 | **1a / 2a / 3a / 4a** — OOS fence; additive API; privacy fence; no new paid deps |
| D-S070-e7 | **recommended** — no new secrets; existing CORS; H0c + H4–H5; wire log_level only (no new obs contract) |
| D-S070-e8 | **recommended** — Spec 00→16→01→02→04 + uat/verify-qa Spec; Build 07→13 blocked; skip 03/05/06 |
| D-S070-e9 | **recommended** — allocate F7.t; Spec-development only; Spec→Build **closed** |
| D-S070-board | Epic #1000 **Backlog**; children #1001–#1006 **Ready**; WIP 0 until Build |

## In scope

1. **#1001** — AHL bulletin lint/validate: heading as COM, then each contained TAC report. [Corpus: product §F6] [Corpus: product §F7]
2. **#1002** — Labeled Profile (Annex 3 / IWXXM-US) at converter top; applied to convert/lint/validate; keyboard accessible. [Corpus: product §F6] [Corpus: product §F7]
3. **#1003** — **F7.t** product=IWXXM pass-through (lint XML + F2 validate; no TAC convert). F7.s stays. [Corpus: product §F7] [Corpus: product §F2] [Corpus: api]
4. **#1004** — Conversion `log_level` sets backend/package logger verbosity. [Corpus: product §F29] [Corpus: api]
5. **#1005** — Labeled, editable, functional Bulletin ID + Issuing Center. [Corpus: product §F6] [Corpus: product §F7]
6. **#1006** — Auth register/login/logout/persist UAT + Playwright; guest convert still works. [Corpus: product §F31] [Corpus: journeys]
7. FileConverter / accumulate ZIP / Quality metrics **honor** profile + IWXXM product (no QM chrome redesign).
8. API (and existing CLI flags) accept `product=iwxxm`, `profile`, `log_level`, bulletin id / issuing center.

## Out of scope

- Custom ConversionProfile editor [#933](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/933) / spike [#924](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/924) — later, already ticketed
- National/regional packs [#912](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/912) / #916–#921
- Dissemination F16–F19 / [#898](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/898)
- F8 worker auto-push
- Promote `stage` → `main` unless re-approved
- New auth providers / CAPTCHA
- Live in-app log panel; new observability vendors
- New CLI product

## Features

- **F7.t** — IWXXM as product pass-through (#1003) — [Corpus: product §F7]
- Deepen F6 / F2 / F10 / F29 / F31 / F21 — [Corpus: product]

## Success criteria (session)

After Build gate (not now): (1) golden AHL bulletin lint/validate usable; (2) Profile obvious at top and applied; (3) product=IWXXM lints/validates XML only; (4) log-level params change logs; (5) Bulletin ID + Issuing Center visible and used; (6) Auth register+login UAT signed (UJ-003/UJ-046).

## UI preview

**Remind at 11-verify-impl** (`D-S070-e2`) — non-deployed / local only when offered; not staging/prod.

## Board

- Project [#7 TAC-to-IWXXM](https://github.com/orgs/EMPIRIC2/projects/7)
- Milestone: **M0 — Stabilize + operator trust + narrative**
- Epic #1000 **Backlog**; children **Ready** (WIP 0 until 07)
