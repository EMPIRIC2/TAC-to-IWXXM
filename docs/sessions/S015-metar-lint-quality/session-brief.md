---
session_id: S015-metar-lint-quality
type: feature
status: in_progress
branch: evolve/EV-011-metar-lint-quality
started_at: 2026-07-19
intent: "METAR lint issue registry (INFO/WARNING/ERROR) + #732 METAR TAC lint/validate/convert quality; research + validation/conversion expansion from external METAR/IWXXM resources"
orchestrator: 16-evolve
evolve_cycle_id: EV-011
context_briefs:
  - docs/context/metar-lint-quality.md
standing_docs_touched: []
---

# Session S015 — metar-lint-quality

## Intent

Raise **METAR** TAC lint, validation, and TAC→IWXXM conversion quality ([#732](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/732)):

1. **Maintainable issue registry** — machine-readable codes with severities `info` / `warning` / `error`, extensible without ad-hoc string literals.
2. **Golden convert → validate** — representative METAR TAC → IWXXM → XSD + Schematron (pinned versions) where goldens exist or are added.
3. **Research & expansion** — mine ideas from external METAR decode / IWXXM convert references to deepen lint rules, diagnostics, and conversion fidelity (Annex-3 + IWXXM-US where applicable).

## Prior session close

| Item | Disposition |
|------|-------------|
| S011 / EV-008 | **Completed** 2026-07-19 (user close) |
| PR [#716](https://github.com/joseph-c-mcguire/metar-to-IWXXM/pull/716) | Merged `22a6199` (2026-07-15) |
| 13-deploy-smoke on EV-008 | Waived — merge landed; later deploys via S013/S014 |

## Intake decisions (Phase 0 — recorded 2026-07-19)

| ID | Decision |
|----|----------|
| E11-1 | Close S011/EV-008; open new session (not resume EV-008) |
| E11-2 | Open `S015-metar-lint-quality`, type `feature`, scoped context → 16-evolve |
| E11-3 | Full #732 quality bar + issue registry + goldens **plus** research / validation / conversion expansion |
| E11-4 | New **F15** (issue registry + METAR quality metrics) + deepen **F6/F12** for METAR goldens/rules |
| E11-5 | Routing **00–13** incl. 03/06 + Render 12–13 (approved) |
| E11-6 | Research depth = **all**: aggressive R1–R6 encode + 01 research catalog + registry/goldens + opportunistic METAR quality improvements |

## Proposed Fn allocation

| Fn | Title | Role |
|----|-------|------|
| **F15** | Maintainable TAC lint issue registry + METAR quality bar | New — codes, severities, docs, CI registry checks |
| **F6** (deepen) | METAR convert fidelity + product_matrix goldens | Annex-3 / IWXXM-US edge cases (COR/NIL/RMK as scoped) |
| **F12** (deepen) | METAR `tac-validate` rule pack + negative fixtures | Coverage-matrix gaps; structured diagnostics |

## Scope

### In

- Issue registry (maintainable, additive) for METAR (design for reuse by other products later)
- Severities: `info`, `warning`, `error` (aligned with existing `Issue.severity`)
- Accept + negative METAR fixtures; golden IWXXM + round-trip `iwxxm-validate`
- Coverage-matrix METAR row review; gaps closed or deferred with rationale
- Research notes from: [MetarCentral how-to-read](https://metarcentral.com/learn/how-to-read-metar), [AviationRef decoder](https://www.aviationref.com/metar-decoder), [moryakovdv/iwxxmConverter](https://github.com/moryakovdv/iwxxmConverter)
- API/UI path smoke: `product=metar` convert / lint-tac / decode-tac + workbench

### Out (default)

- New products beyond F6 seven-product set
- Full COLLECT extract / dissemination
- Treating [FlightPlanDatabase FMS spec](https://flightplandatabase.com/dev/specification) as METAR authority (not METAR — skip as domain source)
- Closing sibling product tickets (#730 etc.) unless a shared registry change requires it

## Routing plan

See [routing-plan.md](./routing-plan.md) — **pending user approval**.

## Links

- Issue: [#732](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/732)
- Corpus: F6 / F12 / proposed F15 — `docs/feature-list.md`
- Domain: `docs/domain/rules/COVERAGE_MATRIX.md`
- Packages: `tac-validate`, `tac2iwxxm`, `iwxxm-validate`
- Context: [metar-lint-quality.md](../../context/metar-lint-quality.md)
