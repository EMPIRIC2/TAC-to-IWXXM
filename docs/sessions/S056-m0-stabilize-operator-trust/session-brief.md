---
session_id: S056-m0-stabilize-operator-trust
type: feature
status: in_progress
branch: evolve/EV-047-m0-stabilize-operator-trust
started_at: 2026-08-08
intent: "M0 slice: slim husky (#833) + converter perf harness (#834) + operator one-pager (#956) + minimal handbook (#957)"
orchestrator: 16-evolve
evolve_cycle_id: EV-047
prior_session: S055-wmo-aviation-registers
github_issues:
  - 833
  - 834
  - 956
  - 957
milestone: "M0 — Stabilize + operator trust + narrative"
feature_ids: []
deepen_feature_ids:
  - M5
  - F6
  - F7
feature_note: "Deepen M5 (husky reverse EV-036) + F6 (converter perf PR gate) + F7 help/docs; no new product Fn"
preset: Standard
ui_preview: N/A unless help-link UI
decisions:
  D-S056-open: "1 — open S056/EV-047 all four issues"
  D-S056-bundle: "1 — one cycle all four"
  D-S056-husky: "1 — husky lint+fast units; reverse EV-036 day-to-day path"
  D-S056-preset: "1 — Standard; waive 12/13 unless help-link deploy"
---

# Session S056 — M0 stabilize + operator trust

## Goal

Ship the M0 “stabilize + operator trust + narrative” slice: fast local husky
(lint + unit only), a converter perf regression gate that blocks PR merge, and
operator-facing one-pager + minimal handbook for workshop / new users.

[Corpus: product §M5] [Corpus: product §F6] [Corpus: product §F7]
[Corpus: tests] [Corpus: tech-spec] · ops `docs/ops/DEVELOPMENT.md`

## Issues

| # | Title | Map |
|---|--------|-----|
| [#833](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/833) | Slim husky → lint + unit tests | Deepen **M5** (explicit reverse of EV-036 day-to-day hooks) |
| [#834](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/834) | Converter perf regression harness | Deepen **F6** + `[Corpus: tests]` hard PR gate |
| [#956](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/956) | Operator one-pager | Operator narrative / F7 help link |
| [#957](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/957) | Minimal operational handbook | Companion to #956 |

## In scope (Phase 0 — partially locked)

1. **Husky slim-down (#833)** — developer commit/push path = lint/format + agreed
   fast unit subset; typecheck, catalog/registry, actionlint/yamllint, full
   `validate-ci` / coverage matrices stay CI / opt-in `make` (`D-S056-husky=1`).
2. **Converter perf harness (#834)** — hard-fail PR/CI gate when `tac2iwxxm.convert`
   regresses vs committed baselines (thresholds / product scope TBD Phase 0 batch).
3. **Operator one-pager (#956)** + **minimal handbook (#957)** — user-facing docs
   without internal corpus/ADR citations; paths + help-link shape TBD.

## Out of scope

- AMS 2027 abstract (#958)
- Weakening merge gates on `stage` / `main`
- Micro-optimizing the converter (detection + block only for #834)
- Full reverse of all S044 remote-CI slimming decisions beyond the husky/developer path
- Staging/prod deploy unless a help-link UI change requires it (`D-S056-preset=1`)

## Routing

**Standard:** `00 → 16 → 01 → 02 → 04 → 05 → 07 → 08 → 09 → 11`  
Skip `03`, `06`, `10`, `12`, `13` (re-enable `10`/`12`/`13` if help-link needs E2E/deploy).

## Branch

`evolve/EV-047-m0-stabilize-operator-trust` from `stage@adcf3b1f` (PR #960 / EV-046 merged).
PR target: **`stage`** (not `main`).

## Status

Opened 2026-08-08 after `D-S056-open=1,1,1,1`. Next: finish Phase 0 intake
(#834 evaluation + docs paths) → lock evolve-plan-card → **01-requirements**.
