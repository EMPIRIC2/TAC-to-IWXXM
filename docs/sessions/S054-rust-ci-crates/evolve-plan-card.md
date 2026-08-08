# Evolve Plan Card

> Cycle: EV-045 | Session: S054-rust-ci-crates | Updated: 2026-08-08

## Goal

Add required CI (and local Makefile parity) for Rust crates behind F13/F14 so
unformatted, clippy-noisy, or failing `cargo test` / maturin bridges cannot merge green.

## Features

- F13 — Fast IWXXM validate (Rust core) — deepen CI gates — [Corpus: product §F13]
- F14 — Publish `tac2iwxxm` + validate extras — deepen native CI — [Corpus: product §F14]

## In / out of scope

- In: `cargo fmt --check`, `clippy -D warnings`, `cargo test`, maturin/PyO3 smoke for
  `packages/tac2iwxxm/rust` + `packages/iwxxm-validate/rust`; Cargo cache; `make rust-check`;
  required GH checks; docs deltas in tech-spec / test-plan / feature AC as needed
- Out: Rust HTTP service; multi-arch wheel CI beyond `pypi-publish`; Schematron perf gates;
  browser E2E; staging/prod deploy

## Preset + routing

- Preset: Standard (skips 03/06/10/12/13)
- Stages (ordered): `00 → 16 → 01 → 02 → 04 → 05 → 07 → 08 → 09 → 11`

## Next child stage

**07-build** — T1.1–T1.6 done locally; **T1.7** tip CI after commit/push. Then 08→09→11.

## Locked defaults (D-S054-01-ac=1 + D-S054-04)

- Extend `ci-cd.yml`: cargo **matrix** + gate job; maturin **two-package matrix**
- `cargo clippy -- -D warnings` hard-fail
- `make rust-check` = cargo both + both maturin smokes
- Default CI triggers; `deploy.needs` gated on new jobs

## Risks / open decisions

- AC6 ops: rulesets still empty until admin runs `apply_gh_branch_rulesets.sh`
  (waived for this cycle — D-S054-ac6-waive=2)
- Gate-job pattern required so locked check name stays exact under matrix
