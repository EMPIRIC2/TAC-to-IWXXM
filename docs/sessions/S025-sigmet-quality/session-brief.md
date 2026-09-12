---
session_id: S025-sigmet-quality
type: feature
status: active
branch: evolve/EV-019-sigmet-quality
started_at: 2026-07-29
intent: "SIGMET family quality bars (#733 general + #739 VA); F23 + deepen F6.d/F12; EV-011/EV-015 stack"
orchestrator: 16-evolve
evolve_cycle_id: EV-019
github_issues:
  - 733
  - 739
context_briefs:
  - docs/context/sigmet-quality.md
standing_docs_touched:
  - docs/feature-list.md
---

# Session S025 — sigmet-quality

## Intent

Raise **General SIGMET** and **Volcanic-ash SIGMET** TAC lint, validation, and TAC→IWXXM
conversion quality to the same bar F15/F20 set for aerodrome products:

1. **[#733](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/733)** — General SIGMET
   (`iwxxm:SIGMET`): phenomena other than VA/TC; sequence, validity, FIR/CTA, geometry,
   altitude, movement/intensity; AIRMET/SIGMET family exceptional rules (CNL, STNR, point→circle, …).
2. **[#739](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/739)** — VA SIGMET
   (`iwxxm:VolcanicAshSIGMET`): general SIGMET mapping + volcano identity + ash geometry /
   forecast position; `NO VA EXP`; cancel FIR-moved-ash; **not** VAA advisory path.

Same stack as EV-011 / EV-015: `tac-validate` / `tac2iwxxm` / `iwxxm-validate` / goldens /
coverage matrix / ADR-028 registry (reuse, amend codes only).

## Prior session

| Item | Disposition |
|------|-------------|
| S024 / EV-018 | **Completed** — F16 multi-file select; PR #791 |
| S020 / EV-015 | **Completed** — F20 Done; #735/#734; PR #778 (quality-bar peer) |
| S015 / EV-011 | **Completed** — F15 Done; ADR-028 registry |

## Intake decisions (Phase 0 — locked 2026-07-29)

| ID | Decision |
|----|----------|
| E19-1 | Open `S025-sigmet-quality`, type `feature` → 16-evolve (EV-019); scoped context |
| E19-2 | Full quality bars for **both** #733 and #739; **#738 TC SIGMET out of scope** |
| E19-3 | New **F23** (SIGMET family quality: general + VA) + deepen **F6.d** / **F12**; reuse ADR-028 |
| E19-4 | Routing **Lean+build**: `00→16→01→02→04→07→08→10→13` (skip 03/05/06/09/11/12 unless needed) |
| E19-5 | Full #733/#739 AC — guidance + fixtures + goldens + matrix (general **and** VA) |
| E19-6 | Siblings OOS; no PyPI; no F16–F19; F7 Planned (smoke only) |
| E19-7 | Redeploy if API/FE changes; H1–H3 if API; H4–H5 workbench `sigmet` + VA smoke |
| E19-8 | Lock Phase 0; write F23; **pause before 01-requirements** |
| E19-ui | **⚠️ Assumed B** — no non-deployed UI preview; docs/repo only (Q9 omitted) |
| AskQuestion | Waived (written interview; tool unavailable) |

## Fn allocation

| Fn | Title | Role |
|----|-------|------|
| **F23** | SIGMET family quality bar (general + VA) | New — product quality metrics, journeys, tests; registry codes |
| **F6** (deepen) | Convert/golden fidelity | F6.d SIGMET (+ VA SIGMET root) |
| **F12** (deepen) | `tac-validate` rule packs + fixtures | Coverage-matrix SIGMET + VA SIGMET rows |

## Scope (Phase 0 **approved** 2026-07-29)

### In

- #733 exceptional-rule table → accept + negative fixtures (or explicit deferrals)
- #739 exceptional-rule table → accept + negative fixtures; distinguish from VAA (#736)
- Encode audit vs WMO `TAC-to-XML-Guidance.txt` + 2025-2 corrections
- Common rules: `reportStatus` / `permissibleUsage`, `translationFailedTAC`, geometry CRS, nilReasons, one-IWXXM-per-TAC-report
- Round-trip convert → `iwxxm-validate` XSD+Schematron on goldens
- Coverage-matrix SIGMET + VA SIGMET row updates
- API/UI smoke: `product=sigmet` / VA path + workbench (F7 Planned; smoke only)

### Out

- [#738](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/738) Tropical-cyclone SIGMET
- [#731](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/731) AIRMET, [#736](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/736) VAA, [#737](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/737) TCA, #740 SWX, #741 VONA
- PyPI release bumps; F16–F19; COLLECT

## Routing plan

See [routing-plan.md](./routing-plan.md) — **approved** Lean+build (E19-4).

## Current stage

**07-build** — M0 complete (T0.1–T0.3); next **T1.1** F23 theme G1 accept/negative fixtures.

## Links

- Issues: [#733](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/733), [#739](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/739)
- Predecessor peer: F20 / EV-015 — `docs/sessions/S020-aerodrome-quality/`
- Corpus: F23 + deepen F6/F12 — `docs/feature-list.md`
- Domain: `docs/domain/rules/COVERAGE_MATRIX.md`, ADR-028
- Encode: `vendor/schemas/iwxxm/2025-2/IWXXM/examples/TAC-to-XML-Guidance.txt`
- 01 report: [reports/01-requirements.md](./reports/01-requirements.md)
