# Evolve report — S020 Aerodrome quality (F20)

- **Cycle**: EV-015
- **Session**: S020-aerodrome-quality
- **Status**: completed (Phase 4 closed — `D-S020-EV015-phase4-close`)
- **Scope**: TAF + SPECI quality bar (F15 sequel); deepen F6.b SPECI / F6.c TAF convert
  goldens and F12 checklist rules via ADR-028 registry; FE catalog TAF tags; live H1–H5
- **Stages run**: 00, 01, 02, 04, 07, 08, 09, 10, 11, 13, 16 (Lean+build; skip 03/05/06/12)
- **ADRs**: ADR-028 (reused; no new registry ADR)
- **Deploy**: Render API + frontend-v4-web @ merge `eae8bdc` (CI Deploy `29967487455`);
  images `20260722235831-eae8bdc`; deploys `dep-d9gljeupbkes73bspkl0` /
  `dep-d9gljfrbc2fs738q90d0`
- **GitHub issues**: #735 / #734 **closed**
- **Follow-ups** (non-blocking): F7 remains Planned; optional 17-retrospective on TAF theme
  fixture strategy; sibling product-quality tickets (#731, #733, #736–#741) out of scope

## Summary

EV-015 raised TAF and SPECI to the F15 METAR quality bar: registry codes and catalog tags,
accept/negative fixture packs for exceptional-rule themes, convert goldens (Annex-3 +
IWXXM-US) with `iwxxm:TAF` / `iwxxm:SPECI` roots, workbench catalog filters for TAF tags, and
authenticated live catalog + lint/convert smoke. Production H1–H5 passed after merge #778.

## Artifacts changed (high level)

- `packages/tac-validate` — registry + product_rules TAF/SPECI; fixtures; catalog regen
- `packages/tac2iwxxm` — TAF/SPECI Annex-3 + IWXXM-US goldens; mis-class guards
- `apps/backend` — TC-F20-005 integration smoke (catalog + lint/convert)
- `apps/frontend` — WorkbenchConsole catalog TAF tag filters/copy
- Docs: feature-list F20 Done; COVERAGE_MATRIX; api-contract; CHANGELOG
- Session reports under `docs/sessions/S020-aerodrome-quality/`

## Verification

- 08-verify-build: PASS
- 09-qa / 10-e2e: PASS (UJ-031 / TC-F20; live H4–H5 at 13)
- 11-verify-impl: APPROVED (`D-S020-EV015-11-A`)
- 13-deploy-smoke: PASS (`deploy-smoke.md` — H0ci/H1/H0c/H3/H4/H5 + catalog taf/speci)
