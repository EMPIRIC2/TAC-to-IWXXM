---
session_id: S054-rust-ci-crates
type: feature
status: in_progress
branch: evolve/EV-045-rust-ci
started_at: 2026-08-08
intent: "CI: lint, typecheck, unit, and integration tests for Rust crates (#725)"
orchestrator: 16-evolve
evolve_cycle_id: EV-045
prior_session: S053-separate-staging-doks-project
github_issues:
  - 725
feature_ids:
  - F13
  - F14
deepen_feature_ids:
  - F13
  - F14
preset: Standard
ui_preview: N/A — no browser UI
---

# Session S054 — Rust crate CI (#725)

## Goal

Gate PRs on `rustfmt`, `clippy`, `cargo test`, and maturin/PyO3 smoke for
`packages/tac2iwxxm/rust` and `packages/iwxxm-validate/rust`, with Makefile local parity.

[Corpus: product §F13] [Corpus: product §F14] [Corpus: tech-spec] [Corpus: tests]
[Corpus: adr/ADR-017] · [#725](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/725)

## In scope

- CI jobs for both Rust crates: `cargo fmt --check`, `clippy -- -D warnings`,
  `cargo test` (typecheck via clippy/test builds)
- Integration: maturin/PyO3 smoke (or pytest with Rust required) for **both** packages
- Cargo cache; stable toolchain (`dtolnay/rust-toolchain`) aligned with S014 / ADR-017
- `make rust-check` (or equivalent) mirroring CI
- Required checks so PRs cannot merge with red Rust CI

## Out of scope

- Replacing FastAPI `apps/backend` with a Rust HTTP service
- Full multi-arch wheel CI beyond existing `pypi-publish.yml` / maturin
- Schematron parity perf gates (F11/F13 publish gates)
- Browser UI / deploy smoke (stages 10/12/13 skipped)

## Routing

**Standard** (approved `D-S054-open=1`):  
`00 → 16 → 01 → 02 → 04 → 05 → 07 → 08 → 09 → 11`  
Skip `03`, `06`, `10`, `12`, `13`.

## Prior work parked

`D-park-doks=1` — S052/EV-043 and S053/EV-044 parked (DOKS staging) so this session can run.
Resume those cycles separately after #725.
