---
session_id: S031-iwxxm-domain-mine
type: feature
status: in_progress
branch: evolve/EV-024-iwxxm-domain-mine
started_at: 2026-07-30
intent: "Domain mine strongest bundle — #804 IWXXM/ tree + #807 wmo-im org refresh + #773 IWXXM-US/MDL; discovery-first with full ticket acceptance (notes, matrices, fixture/catalog wiring, durable promotions, child engine issues). Exclude #806 (WIS2)."
orchestrator: 16-evolve
evolve_cycle_id: EV-024
github_issues:
  - 804
  - 807
  - 773
context_briefs:
  - docs/context/iwxxm-domain-mine.md
standing_docs_touched:
  - docs/feature-list.md
  - docs/test-plan.md
  - docs/decisions/evolve-decisions.md
  - docs/domain/mining/**
  - docs/domain/rules/RULE_SOURCE_URLS.md
  - docs/domain/rules/COVERAGE_MATRIX.md
  - docs/domain/IWXXM_CONVERSION.md
  - docs/domain/IWXXM_VALIDATION.md
  - docs/domain/TAC_VALIDATION.md
feature_ids: [F6, F2, F4, F12, F13, F25]
feature_note: "Deepen F6/F2/F4/F12/F13/F25 (+ F6.b US map via #773) — no new Fn; discovery + fixture/catalog wiring; child engine tickets later"
---

# Session S031 — iwxxm-domain-mine

## Intent

Run a **discovery-first** domain-mining cycle (same archetype as #800 prep) covering the
strongest complementary WMO + US bundle:

| Issue | Role |
|-------|------|
| [#804](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/804) | Deep `wmo-im/iwxxm` → `IWXXM/` tree: all official examples + folder-by-folder relevancy |
| [#807](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/807) | Org-level / sibling-repo refresh for encode/validate (does not replace #804 deep walk) |
| [#773](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/773) | IWXXM-US METAR/SPECI PDF + MDL modelling sources |

**Exclude:** [#806](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/806) (F8/F17 WIS2 — different lane).

Runtime SoT remains `vendor/manifest.json` → IWXXM **v2025-2**. No hand-edits to
`vendor/schemas/*`. Engine encode rewrites stay in child issues / quality tickets.

## Prior session

| Item | Disposition |
|------|-------------|
| S030 / EV-023 | **Completed** — #800 encode/validate deltas; PR #801 + closeout #802 |
| Tier A / org mining notes | Prior art — refresh, don't restart from zero |
| #800 | Consumed Guidance / FAQ digs; this cycle re-scrapes package tree + org siblings |

## Scope (locked — E24-1..E24-4)

### In — full ticket acceptance (3a)

1. **Inventory & scrape** via `mine-domain-sources` (+ `extract-pdf-to-repo` for #773 PDFs)
2. **Matrices** — folder×relevancy (#804); org ranking refresh (#807); US type×TAC×encode×validate (#773)
3. **Wire in-scope WMO examples** into catalog / goldens / validate fixtures; update `FIXTURE_GAPS.md`
4. **Promote durable rules** to `RULE_SOURCE_URLS` / `COVERAGE_MATRIX` / canonicals
5. **Child issues** for ❌/⚠ engine gaps (link #800 / product quality tickets; no big-bang encode)

### Out

- #806 WIS2 / wis2box / WMO-org exchange mining
- New product encode engines in this cycle (WAFS/QVACI/full SWX/VONA quality)
- Hand-editing `vendor/schemas/*`; committing full upstream clones / PDF binaries
- Mixing IWXXM-US examples into the WMO official catalog
- USWX (non–Annex 3) product schemas

## Routing

See [routing-plan.md](./routing-plan.md). **Approved** Lean+build (user 1a+Build / 4b).

## Current stage

**01-requirements** delta written (UJ-039 + ADR-032 amend + TC-EV024) — pending close → **02-verify-plan**.

## Links

- [#804](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/804) · [#807](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/807) · [#773](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/773)
