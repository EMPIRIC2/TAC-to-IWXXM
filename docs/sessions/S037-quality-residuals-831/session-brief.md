---
session_id: S037-quality-residuals-831
type: feature
status: in_progress
branch: evolve/EV-030-quality-residuals-831
started_at: 2026-08-02
intent: "EV-029 residuals — #831 parameterized rule matrices (happy/sad/edge), #829 TC SIGMET deepen (lint pack / STNR / A6-2-TC menu), #820 VAA/TCA decode residual deepen beyond F9 G4."
orchestrator: 16-evolve
evolve_cycle_id: EV-030
github_issues:
  - 831
  - 829
  - 820
prior_session: S036-eight-family-ahl-rules-823
context_briefs:
  - docs/context/quality-residuals-831.md
standing_docs_touched: []  # filled after 01/04
feature_ids: [F29, F23, F12, F2, F13, F9, F26, F27]
feature_note: "D-S037-fn — F29 rule matrices (#831) + deepen F23/F12/F2/F13 (#829) + F9/F26/F27 (#820)"
ask_question: written interview — D-S037-open = 1,1,2,1
ui_preview: declined — docs/repo only (menu unlock catalog-tier; no non-deployed UI this session)
---

# Session S037 — quality-residuals-831

## Intent

Close the three open residuals left by **S036 / EV-029** (#828 merged), in this order:

| Order | Issue | Focus |
|------:|-------|--------|
| 1 | [#831](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/831) | Parameterized happy/sad/edge matrices for lint · convert · validate (design → pilot runner) |
| 2 | [#829](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/829) | TC SIGMET tac-validate pack, STNR/geometry negatives, A6-2-TC sample-menu unlock |
| 3 | [#820](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/820) | Deeper VAA/TCA decode beyond F9 G4 best-effort |

## Prior session

| Item | Disposition |
|------|-------------|
| S036 / EV-029 | **Completed** — #823/#740/#738 closed; PR #828 @ `4e6577a` |
| Residuals at close | #829, #820, #831 — this session |

## Scope (locked — D-S037-open = 1,1,2,1)

### In

1. **#831** — Evaluate harness shape; land runners + pilot matrices; inventory gate for empty slots
2. **#829** — TC-specific lint registry/fixtures; STNR / exceptional geometry (or explicit OOS); catalog/menu tier decision for `sigmet-A6-2-TC`
3. **#820** — Structured decode for major VAA/TCA labels + forecast hours; shrink residual allowlist / matrix updates

### Out

- New deployables / hosting moves (#712, #830 Supabase strip unless required)
- WIS2 mining (#806), SIGWX/VONA/QVACI
- Non-deployed UI preview this session (catalog unlock may still touch FE data — H4–H5 only if FE ships)

## Routing

**Preset:** Standard — `00→16→01→02→04→07→08→09→10→11→12→13`  
**Skip:** `03, 05, 06` unless 04 surfaces new deps/tooling  
See [routing-plan.md](routing-plan.md).

## Progress

- **00-context** completed · **Fn** `D-S037-fn` · open commit `f88e9cb`
- **01-requirements** completed (`D-S037-E30-M` = 2,1 — API/#829 catalog)
- **02-verify-plan** Gate A PASS (`D-S037-02-phase-a`) @ `876ffda`
- **04-tech-plan** Gate B PASS (`D-S037-04-plan`=1) @ `317447a`+ — 27 tasks approved
- **07-build** @ **T0.1** — #831 design note
