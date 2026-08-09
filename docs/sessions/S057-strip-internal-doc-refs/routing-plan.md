# Routing plan — S057 / EV-048

**Preset:** Standard (**approved** `D-S057-preset-reconfirm=1`)  
**Route:** `00 → 16 → 01 → 02 → 04 → 05 → 07 → 08 → 09 → 10 → 11`  
**Skip:** `03`, `06`, `12`, `13`  
**Branch:** `evolve/EV-048-strip-internal-doc-refs` (base `stage@d7652d5d`)  
**Features:** deepen **F7**, **F21** (no new Fn)  
**Issues:** [#951](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/951)  
**Status:** **in_progress** — 16-evolve → 08-verify-build

| Stage | Required | Mode | Status | Notes |
|-------|----------|------|--------|-------|
| 00-context | yes | session | **completed** | S057 open; Standard amend |
| 16-evolve | yes | orchestrator | **in_progress** | Orchestrating; child 08 |
| 01-requirements | yes | delta | **completed** | D-S057-01-ac=1; guard-s0=1 |
| 02-verify-plan | yes | delta | **completed** | Gate A PASS D-S057-gateA=1 |
| 03-plan-tooling | no | — | skipped | unless new Cursor rules for guard |
| 04-tech-plan | yes | delta | **completed** | D-S057-04-plan=1; guard-ext=1 |
| 05-verify-tech | yes | delta | **completed** | Gate B PASS D-S057-gateB=1 |
| 06-tech-tooling | no | — | skipped | no new runtime deps |
| 07-build | yes | full | **completed** | M1–M3; T3.3 skipped |
| 08-verify-build | yes | delta | pending | |
| 09-qa | yes | delta | pending | |
| 10-e2e | yes | delta | pending | operator-visible copy if UI hits |
| 11-verify-impl | yes | delta | pending | |
| 12-verify-deploy | no | — | skipped | waive unless deploy |
| 13-deploy-smoke | no | — | skipped | waive unless deploy |

## Skip rationale

| Skipped | Why |
|---------|-----|
| 03 | No new Cursor rules expected beyond optional CI test for guard |
| 06 | No new runtime dependency inventory change |
| 12 / 13 | Merge gate is tip CI green → `stage`; no live deploy required for copy hygiene |

## Corpus cites

[Corpus: api] [Corpus: product §F7] [Corpus: product §F21] [Corpus: tests]
