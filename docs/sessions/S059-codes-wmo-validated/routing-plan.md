# Routing plan — S059 / EV-050

**Preset:** Standard (**proposed** — code + CI membership checks; not Auto-Lean)  
**Route:** `00 → 16 → 01 → 02 → 04 → 05 → 07 → 08 → 09 → 11`  
**Skip:** `03`, `06`, `10`, `12`, `13`  
**Branch:** `evolve/EV-050-codes-wmo-validated` (base `stage`)  
**Features:** deepen **F12**, **F15**, **F20**, **F23** (no new Fn)  
**Issues:** [#959](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/959) (parent [#889](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/889))  
**Status:** proposed — awaiting `D-S059-route`

| Stage | Required | Mode | Status | Notes |
|-------|----------|------|--------|-------|
| 00-context | yes | session | **in_progress** | Open after S058 park |
| 16-evolve | yes | orchestrator | pending | EV-050 |
| 01-requirements | yes | delta | pending | ACs for harvest + membership |
| 02-verify-plan | yes | delta | pending | Gate A |
| 03-plan-tooling | no | — | skipped | unless new Cursor rules |
| 04-tech-plan | yes | delta | pending | execution plan |
| 05-verify-tech | yes | delta | pending | Gate B |
| 06-tech-tooling | no | — | skipped | no new runtime deps expected |
| 07-build | yes | full | pending | harvest + tac-validate wire |
| 08-verify-build | yes | delta | pending | |
| 09-qa | yes | delta | pending | |
| 10-e2e | no | — | skipped | no browser UI |
| 11-verify-impl | yes | delta | pending | |
| 12-verify-deploy | no | — | skipped | waive unless deploy |
| 13-deploy-smoke | no | — | skipped | waive unless deploy; no stage→main |

## Skip rationale

| Skipped | Why |
|---------|-----|
| 03 | No new agent rules expected |
| 06 | Harvest uses existing vendor tree; no new publishable dep expected |
| 10 | No operator UI change |
| 12 / 13 | Merge gate tip CI → `stage`; no live deploy / promote |

## Approved

Pending `D-S059-route`.

## Corpus cites

[Corpus: product §F12] [Corpus: product §F15] [Corpus: product §F20]
[Corpus: product §F23] [Corpus: tests] [Corpus: tech-spec]
