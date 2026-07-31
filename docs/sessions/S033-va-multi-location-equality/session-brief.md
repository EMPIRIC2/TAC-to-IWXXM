---
session_id: S033-va-multi-location-equality
type: feature
status: in_progress
branch: evolve/EV-026-va-multi-location-equality
started_at: 2026-07-31
intent: "#809 residual — ADR-032 canonicalize_xml equality for sigmet-multi-location-VA under defaults; promote catalog wmoReference→wmoPass; close issue"
orchestrator: 16-evolve
evolve_cycle_id: EV-026
github_issues:
  - 809
context_briefs:
  - docs/context/va-multi-location-809.md
standing_docs_touched:
  - docs/feature-list.md
  - docs/test-plan.md
  - docs/user-journeys.md
  - docs/decisions/evolve-decisions.md
  - docs/adr/ADR-032-wmo-default-golden-glossary.md
feature_ids: [F23, F6, F7]
feature_note: "Deepen F23 (#809 equality) + F6 convert shape + F7.g catalog tier — no new Fn"
ui_preview: n/a
---

# Session S033 — va-multi-location-equality

## Intent

Finish [#809](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/809): soft-compare already shipped in
EV-025 / [#816](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/816). This cycle delivers ADR-032
`canonicalize_xml` equality under annex3 + default pin, then flips catalog
`wmoReference` → `wmoPass` and closes the issue.

## Prior session

| Item | Disposition |
|------|-------------|
| S032 / EV-025 | **Completed** — US REMARKS + #809 soft path; PR #816 `2412312` |
| Residual context | [Context: va-multi-location-809](../../context/va-multi-location-809.md) |
| Soft golden | `packages/tac2iwxxm/tests/fixtures/annex3_golden/sigmet_multi_location_va.*` |
| Catalog | `sigmet_multi_location_va` tier `wmoReference` |

## Scope (locked — D-S033-open=1)

### In

1. Encoder deltas so `canonicalize_xml(convert(vendor_tac)) == canonicalize_xml(vendor_xml)`
2. Flip TC-EV025-008 soft/inequality asserts → strict equality (or successor TC ids)
3. TC-EV025-009 / promote path expects equality + `wmoPass: true`
4. Catalog + FIXTURE_GAPS: `wmoPass` passer; remove equality-pending note
5. Close GitHub #809

### Out

- Reopen dig ❌ US REMARKS (#810–#812) — closed by #816
- Sample-menu removal while still reference (not applicable once passer)
- TC SIGMET A6-2 (#738)

## Known equality blockers (from context)

Calendar year-month stamp, ATS/MWO display metadata, ring vertex order, coordinate
formatting, phenomenonTime density — see Context brief.

## Success

1. ADR-032 equality green under defaults
2. Catalog `wmoPass` for `sigmet_multi_location_va`
3. #809 closed

## PR

[#817](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/817) **merged** to `main` @ `101f555` (`D-S033-817-merge`). Optional 13 / T3.4 when_ships pending user.
