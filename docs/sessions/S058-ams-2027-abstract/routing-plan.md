# Routing plan — S058 / EV-049

**Preset:** Lean (`auto_lean: true` — docs/narrative; no API/arch)  
**Route:** `00 → 16 → 01 → 02`  
**Skip:** `03`, `04`, `05`, `06`, `07`, `08`, `09`, `10`, `11`, `12`, `13`  
**Branch:** `evolve/EV-049-ams-2027-abstract` (base `stage@b57f2a87`)  
**Features:** narrative deepen only (no new Fn)  
**Issues:** [#958](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/958)  
**Constraint:** abstract prose **handwritten** — agent must not draft title/body  
**Status:** **PARKED** `D-S058-park=1a` (2026-08-09) — resume later; `#958` → Ready

| Stage | Required | Mode | Status | Notes |
|-------|----------|------|--------|-------|
| 00-context | yes | session | **completed** | D-S058-route=1a; scaffold=2a; then parked |
| 16-evolve | yes | orchestrator | **parked** | not started past plan card |
| 01-requirements | yes | delta | **parked** | not executed |
| 02-verify-plan | yes | delta | **parked** | not executed |
| 03-plan-tooling | no | — | skipped | no new Cursor rules |
| 04-tech-plan | no | — | skipped | no execution plan / code |
| 05-verify-tech | no | — | skipped | no tech plan |
| 06-tech-tooling | no | — | skipped | no new deps |
| 07-build | no | — | skipped | no product code; optional human paste scaffold only |
| 08-verify-build | no | — | skipped | no build |
| 09-qa | no | — | skipped | Lean docs |
| 10-e2e | no | — | skipped | no UI (stock Lean 10 N/A) |
| 11-verify-impl | no | — | skipped | close after Gate A + human abstract path clear |
| 12-verify-deploy | no | — | skipped | no deploy |
| 13-deploy-smoke | no | — | skipped | no deploy; no stage→main |

## Skip rationale

| Skipped | Why |
|---------|-----|
| 03 | No new agent rules for narrative support |
| 04–08 | Lean: no code/architecture; evidence + checklist only |
| 09 / 11 | No implementation verify beyond Gate A |
| 10 / 12 / 13 | No UI / deploy; `D-S058-promote=3a` |

## Approved

- `D-S058-route=1a` — Lean Auto-Lean `00→16→01→02`; handoff 16-evolve (2026-08-09)
- `D-S058-scaffold=2a` — evidence + deadline tracker + AC checklist + empty paste scaffold
- Plan-mode SwitchMode skipped — user already approved complete routing + scaffold this turn

## Corpus cites

[Corpus: product §F7] [Corpus: product §F16] [Corpus: product §F17] [Corpus: decisions]
