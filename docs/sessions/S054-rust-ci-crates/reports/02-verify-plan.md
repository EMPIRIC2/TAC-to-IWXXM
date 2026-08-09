# 02-verify-plan — Gate A (S054 / EV-045)

**Date**: 2026-08-08  
**Mode**: delta — F13/F14 Rust CI deepen (#725)  
**Status**: Gate A PASS with blocker — D-S054-gateA=2 (ruleset before 04)

## Inventory (touched)

| # | Document | Delta | Status |
|---|----------|-------|--------|
| 1 | feature-list.md | F13/F14 deepen AC | audited |
| 2 | user-journeys.md | UJ-DEV-006 | audited |
| 3 | test-plan.md | TC-EV045-001..007 + CI table | audited |
| 4 | tech-spec.md | Rust native crates pointer | audited |
| 5 | evolve-decisions / requirements-decisions | EV-045 | reference |
| — | spec.md | No CI-job text change; F13/F14 components already map | OK / no delta |
| — | api-contract / deploy / journeys H4–H5 | N/A (no UI / no deploy) | skipped |

## Consistency checklist

| Check | Result |
|-------|--------|
| Feature ↔ Spec | **PASS** — F13→`packages/iwxxm-validate`, F14→`packages/tac2iwxxm` (+ PyO3) |
| Feature ↔ Journey | **PASS** — UJ-DEV-006 |
| Journey ↔ Test | **PASS** — UJ-DEV-006 → TC-EV045-001..007 |
| Feature ↔ Test | **PASS** — deepen ACs covered by TC-EV045-* |
| Test ↔ Acceptance | **PASS** — AC1–7 ↔ TC-EV045-001..007 |
| Connectivity H4–H5 | **N/A** — no browser UI (routing skip 10/12/13) |
| Spec ↔ Config | **N/A** — no new config/env |

## Statements

### High (auto-approved — D-S054-01-ac=1 / issue #725)

| ID | Statement | Verdict |
|----|-----------|---------|
| S1.1 | Both Rust crates gated by `cargo fmt --check` | auto-approved |
| S1.2 | `clippy -- -D warnings` hard-fail | auto-approved |
| S1.3 | `cargo test` required for both crates | auto-approved |
| S1.4 | Maturin/PyO3 smoke for **both** packages | auto-approved |
| S1.5 | `make rust-check` mirrors CI | auto-approved |
| S1.6 | Extend `ci-cd.yml` (matrix), not new workflow by default | auto-approved |
| S1.7 | Jobs on rust path PRs + default CI | auto-approved |

### Medium (user review)

| ID | Statement | Notes |
|----|-----------|-------|
| S2.1 | Required GH check name(s) block merge when red (AC6) | Docs can name the job; **enabling** branch-protection/ruleset required checks is org ops — may already cover `ci-cd.yml` jobs. Recommend: document job name(s) in test-plan; verify/add ruleset in 07 or ops note if missing. |

### Low

None.

## Contradictions

None blocking. Existing `tac2iwxxm-native` remains; EV-045 **adds** crate-level cargo checks + `iwxxm-validate` maturin smoke (does not remove native job).

## Gate A recommendation

**PASS** with S2.1 accepted as: document required check names in standing docs; confirm ruleset wiring during 07-build (or note if already inherited from CI suite).

## Gate A decision (D-S054-gateA=2)

User chose **option 2**: PASS but **require ruleset update before 04**.

### Evidence (2026-08-08)

| Check | Result |
|-------|--------|
| `GET .../rulesets` | `[]` — **no rulesets** |
| Classic branch protection `main`/`stage` | **404** (none) |
| Token `permissions.admin` | **false** (push/triage only) |
| `apply_gh_branch_rulesets.sh` | Updated to include EV-045 check contexts |

### Locked check names (for 07 `ci-cd.yml` job `name:`)

- `Rust crates (fmt/clippy/test)`
- `tac2iwxxm PyO3 (maturin)` (existing)
- `iwxxm-validate PyO3 (maturin)` (new)

### Blocker → cleared (D-S054-ac6-waive=2)

Cannot create/update rulesets without **repo admin**. Same class of gap as EV-043
(`docs/evolve-report-EV-043.md`). User chose **waive AC6 ops half**: docs +
`apply_gh_branch_rulesets.sh` remain; live ruleset apply deferred. **04-tech-plan
unblocked.**

[Corpus: product §F13] [Corpus: product §F14] [Corpus: tests] [Corpus: journeys] [Corpus: tech-spec] [Corpus: adr/ADR-017]
`[Corpus: WAIVED — AC6 GitHub rulesets apply; decided: D-S054-ac6-waive=2 / EV-045]`
