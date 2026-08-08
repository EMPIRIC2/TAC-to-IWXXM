# Build Plan Card

> Session: S054-rust-ci-crates | Updated: 2026-08-08 | Active: Phase 1 / M1 / T1.7

## Goal (one sentence)

Gate PRs on fmt/clippy/`cargo test` + maturin smokes for both Rust crates, with
`make rust-check` local parity (#725).

## Constraints

- [Corpus: product §F13] [Corpus: product §F14] [Corpus: tech-spec] [Corpus: tests]
  [Corpus: adr/ADR-017]
- Branch: `evolve/EV-045-rust-ci` from `main`
- Locked check names: `Rust crates (fmt/clippy/test)`, `tac2iwxxm PyO3 (maturin)`,
  `iwxxm-validate PyO3 (maturin)`
- AC6 ops waived (D-S054-ac6-waive=2); docs + apply script only
- No UI / no deploy smoke (skip 10/12/13)

## In scope (this batch)

- [x] T1.1 — Test — contract tests for Makefile + `ci-cd.yml` job names / deploy.needs — Spec: test-plan TC-EV045-*
- [x] T1.2 — Config — `make rust-check` (cargo both + both native smokes) — Spec: tech-spec §Rust
- [x] T1.3 — Config — rust matrix + gate job locked name — Spec: D-S054-04-jobs
- [x] T1.4 — Config — maturin two-package matrix — Spec: D-S054-04-maturin
- [x] T1.5 — Config — deploy.needs + always-on CI trigger — Spec: D-S054-04-trigger/local
- [x] T1.6 — Docs — tech-spec / script confirm — Spec: tech-spec; test-plan
- [ ] T1.7 — Code — tip CI green / clippy-fmt debt — Spec: TC-EV045-*

## Out of scope (explicit)

- Separate `rust-ci.yml`; path-filter-only jobs; live ruleset apply; multi-arch wheels;
  browser E2E; staging/prod smoke

## Dependencies / blockers

- Data: none
- Prior: 01/02 complete; AC6 ops waived
- Tooling: 06 skipped (ADR-017); Rust/maturin already in repo

## Acceptance for this batch

- [ ] Contract tests green
- [ ] Tip `ci-cd.yml` shows locked check names green
- [ ] `make rust-check` mirrors CI cargo + maturin
- [ ] TC-EV045-006 docs/script met; ops deferred

## Next Plan prompt

Refine M1 task order only if tip CI latency forces splitting the cargo matrix differently;
otherwise Agent runs T1.1→T1.7 per execution-plan.md.
