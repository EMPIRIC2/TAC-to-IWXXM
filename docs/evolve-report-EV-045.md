# Evolve report — Rust crate CI (#725)

- **Cycle**: EV-045
- **Session**: S054-rust-ci-crates
- **Status**: completed
- **Scope**: Deepen F13 + F14 — required Rust fmt/clippy/`cargo test` + maturin smokes for both crates; `make rust-check`; tip CI green
- **Stages run**: 00, 16, 01, 02, 04, 05, 07, 08, 09, 11 (skip 03/06/10/12/13)
- **ADRs**: ADR-017 (toolchain); ADR-034 (PR → `stage`)
- **Deploy**: not deployed (CI-only)
- **PR**: [#953](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/953) → `stage` (open; supersedes #952)
- **Issue**: [#725](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/725)
- **Open follow-ups**: AC6 ruleset apply (admin); merge #953

## Summary

EV-045 adds GitHub Actions and Makefile gates so unformatted, clippy-noisy, or failing
Rust/`maturin` work for `tac2iwxxm` and `iwxxm-validate` cannot merge or deploy green.
Implementation verified (`D-S054-11=1`); tip CI accepted via `D-S054-t17-ci=1`.

See session summary: [`docs/sessions/S054-rust-ci-crates/reports/evolve-summary.md`](sessions/S054-rust-ci-crates/reports/evolve-summary.md).

## Artifacts changed

- `.github/workflows/ci-cd.yml` — rust matrix + gate; maturin two-package matrix; deploy.needs
- `Makefile` — `rust-check` (+ native helpers)
- `tests/test_tc_ev045_rust_ci.py` — contracts
- `docs/feature-list.md`, `docs/test-plan.md`, `docs/tech-spec.md`, `docs/user-journeys.md`
- `scripts/deploy/apply_gh_branch_rulesets.sh` — locked check contexts
- Session reports under `docs/sessions/S054-rust-ci-crates/`

## Verification

- 08-verify-build: PASS
- 09-qa: pass_with_advisories (QA-001..005 accepted at 11)
- 10-e2e: skipped
- 11-verify-impl: APPROVED (`D-S054-11=1`)
- Tip CI: [31273500621](https://github.com/EMPIRIC2/TAC-to-IWXXM/actions/runs/31273500621) SUCCESS for EV-045 jobs

## Corpus

[Corpus: product §F13] [Corpus: product §F14] [Corpus: tests] [Corpus: tech-spec]
[Corpus: adr/ADR-017] [Corpus: decisions]
