# M1 Canonical Closeout Audit

**Date:** 2026-09-07  
**Scope:** Audit whether milestone `M1` can be canonically marked complete without product-behavior changes.

[Corpus: product §M1] [Corpus: system-spec §Repository] [Corpus: tests §TC-M001] [Corpus: tests §TC-M004] [Corpus: adr/ADR-003] [Corpus: decisions]

## Conclusion

`M1` is now canonically closed as **Implemented**.

The repository was already functionally in the monorepo shape described by `M1`; this follow-up pass reconciled the remaining canonical blockers by updating the milestone status in `docs/feature-list.md`, amending stale `REQ-003` / `REQ-007` language in `docs/decisions/requirements-decisions.md`, and removing active runtime/test/doc assumptions that still described the schema tree as git submodules. [Corpus: product §M1] [Corpus: system-spec §Repository] [Corpus: tests §TC-M001] [Corpus: tests §TC-M004]

## Authority Check

### Canonical status signal

- `docs/feature-list.md` now lists `M1 | Monorepo layout (...) | Implemented`, which is the authoritative product-status answer. [Corpus: product §M1]
- `docs/spec.md` already describes the repository as a single-git monorepo with `apps/`, `packages/`, and `vendor/`. [Corpus: system-spec §Repository]
- `docs/test-plan.md` defines migration acceptance evidence through `TC-M001` and `TC-M004`. [Corpus: tests §TC-M001] [Corpus: tests §TC-M004]
- `docs/adr/ADR-003-big-bang-monorepo-migration.md` records the intended end state: remove submodules, move to the target tree, and update docs/CI accordingly. [Corpus: adr/ADR-003]

### Resolved contradictions

- The ambiguous `M1 closed 2026-08-04` wording in an unrelated `EV-032` feature note was rewritten to `EV-032 milestone 1 closed 2026-08-04`, preventing confusion with platform milestone `M1`. [Corpus: product §F23] [Corpus: product §M1]
- `REQ-003` and `REQ-007` in `docs/decisions/requirements-decisions.md` were amended so the decisions log no longer preserves `packages/gifts` as part of the current target layout. [Corpus: decisions] [Corpus: system-spec §Repository] [Corpus: adr/ADR-014]

## Evidence That M1 Is Functionally Delivered

- `.gitmodules` is absent in the repo root. [Corpus: tests §TC-M001] [Corpus: tests §TC-M004]
- The repository contains the monorepo layout required by `M1`: `apps/`, `packages/`, and `vendor/`. [Corpus: system-spec §Repository]
- `tests/migration/test_tc_m001_monorepo_clone_smoke.py` checks no `.gitmodules`, required monorepo paths, and `make install` / `make test-unit`. [Corpus: tests §TC-M001]
- `tests/migration/test_tc_m004_no_submodule_refs.py` checks that `.gitmodules` is absent and that selected standing docs, workflows, and scripts do not instruct `git submodule`. [Corpus: tests §TC-M004]
- `tests/migration/test_m10_ci_monorepo_paths.py` verifies CI targets monorepo paths instead of legacy repo layout. [Corpus: tests §TC-M001] [Corpus: adr/ADR-003]

## Closeout Changes Applied

These changes were applied to remove the final closeout blockers and align current guidance with the monorepo end state.

1. `docs/feature-list.md`
   - Updated the top-level `M1` row to `Implemented`.
   - Added an explicit `M1` status line in the platform feature detail section.
   - Disambiguated the `EV-032` milestone wording that previously read `M1 closed 2026-08-04`. [Corpus: product §M1] [Corpus: product §F23]

2. `docs/decisions/requirements-decisions.md`
   - Amended `REQ-003` and `REQ-007` to reflect the post-cutover package layout and `packages/gifts` removal. [Corpus: decisions] [Corpus: adr/ADR-014] [Corpus: system-spec §Repository]

3. `apps/backend/src/utilities/version_detector.py`
   - Updated docstrings and default schema-root resolution to prefer `vendor/schemas` while preserving legacy compatibility fallback. [Corpus: system-spec §Repository] [Corpus: adr/ADR-003]

4. `apps/backend/tests/versions/test_version_detector.py`
   - Updated integration-test wording and schema-path discovery to use the detector's current vendored schema path rather than a hard-coded submodule path. [Corpus: tests §TC-M001] [Corpus: tests §TC-M004]

## Residual Historical References

Some references to git submodules remain intentionally in historical or acceptance contexts and do not block `M1` closeout.

- Migration/acceptance artifacts such as `docs/adr/ADR-003-big-bang-monorepo-migration.md`, `docs/ops/migration-plan.md`, and `docs/test-plan.md` still mention git submodules because they describe the historical migration objective and acceptance criteria. [Corpus: adr/ADR-003] [Corpus: tests §TC-M004]

[Corpus: tests §TC-M004] [Corpus: system-spec §Repository]
