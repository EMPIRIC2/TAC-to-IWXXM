---
session_id: S027-vaa-quality
type: feature
status: completed
branch: evolve/EV-021-vaa-quality
started_at: 2026-07-29
intent: "VAA + TCA quality bars (#736/#737) — lint, convert, validate, workbench"
orchestrator: 16-evolve
evolve_cycle_id: EV-021
github_issues:
  - 736
  - 737
context_briefs: []
standing_docs_touched: []
feature_ids:
  - F26
  - F27
feature_note: "F26 VAA #736; F27 TCA #737; deepen F6.f / F12 / F7.g"
---

# Session S027 — vaa-quality (+ TCA)

## Intent

Raise **VAA** (`iwxxm:VolcanicAshAdvisory`) and **TCA** (`iwxxm:TropicalCycloneAdvisory`)
to the F15/F20/F23/F24 quality bar per [#736](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/736)
and [#737](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/737): registry-backed lint,
WMO vendor convert fidelity (`canonicalize_xml` under defaults), XSD+Schematron round-trip,
exceptional-rule fixtures, and F7 workbench product paths.

## Prior session

| Item | Disposition |
|------|-------------|
| S026 / EV-020 | **Completed** — F24 AIRMET + F25 WMO METAR/SPECI/TAF; PR #793 (`0f77194`); #731 closed |
| S025 / EV-019 | **Completed** — F23 SIGMET general + VA SIGMET; PR #792; #733/#739 closed |

## Scope (locked — E21-1..E21-4)

### In

- [#736](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/736) VAA → `va-advisory-A7-2` TAC→IWXXM
  **`canonicalize_xml`-equal** under default convert settings
- [#737](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/737) TCA → `tc-advisory-A2-2` same bar
- Exceptional rules from issues + `TAC-to-XML-Guidance.txt` (VAA + TCA sections)
- Mine WMO examples: 2025-2 vendor goldens + `iwxxm-translation` Amd79-80-2023 advisory cases
  (see [reports/wmo-vaa-tca-examples-inventory.md](./reports/wmo-vaa-tca-examples-inventory.md))
- ADR-028 registry deepen for VAA/TCA lint codes; accept + negative fixtures
- Catalog / workbench: **only** list examples that pass the golden bar (E21-3)
- Keep F23–F25 passers green; do not conflate with VA/TC SIGMET

### Out (unless added)

- TC SIGMET #738, SWX #740, VONA #741
- Treating `*-translation-failed` as happy-path golden
- Non-default profile/version golden equality
- PyPI release bumps

## Routing

See [routing-plan.md](./routing-plan.md). **Approved** Lean+build+11 (E21-4).

## Current stage

**COMPLETE** — D-S027-E21-13-merge; PR #794 merged `df56d1f`; H1–H5 + VAA/TCA live smoke **PASS**.
F26/F27 **Done**. Report: [reports/deploy-smoke.md](./reports/deploy-smoke.md).

## Links

- Issues: [#736](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/736), [#737](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/737)
- Siblings (do not conflate): [#739](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/739) VA SIGMET;
  [#738](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/738) TC SIGMET
- Vendor goldens: `va-advisory-A7-2.{tac,xml}`, `tc-advisory-A2-2.{tac,xml}` (2025-2)
- Guidance: `TAC-to-XML-Guidance.txt` §Volcanic Ash Advisory / §Tropical Cyclone Advisory
