# Evolve summary — EV-045 / S054

**Title:** Rust crate CI (fmt/clippy/cargo test + maturin both crates)  
**Branch:** `evolve/EV-045-rust-ci`  
**Status:** **completed** 2026-08-08 — PR [#953](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/953) open → `stage` (awaiting merge)  
**Features:** deepen **F13**, **F14** ([#725](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/725))  
**Preset:** Standard · skip 03/06/10/12/13 · **Deploy:** N/A (CI-only)  
**Tip:** `09ce2bef` · **CI evidence:** [31273500621](https://github.com/EMPIRIC2/TAC-to-IWXXM/actions/runs/31273500621) @ `f270618c` (`D-S054-t17-ci=1`)

## What shipped

1. **`make rust-check`** — fmt + clippy `-D warnings` + `cargo test` both crates + both maturin smokes  
2. **`ci-cd.yml`** — `rust-crates` matrix + gate job **`Rust crates (fmt/clippy/test)`**  
3. **Maturin matrix** — locked names `tac2iwxxm PyO3 (maturin)` / `iwxxm-validate PyO3 (maturin)`  
4. **`deploy.needs`** — rust gate + native matrix (blocks DOKS deploy on red Rust/native)  
5. **TC-EV045-001..007** contract tests; tech-spec / test-plan / ruleset script docs  
6. **AC6 ops** deferred (`D-S054-ac6-waive=2`) until admin applies rulesets

## Gates

| Gate | Result |
|------|--------|
| A (02) | PASS (`D-S054-gateA=2`) |
| B (05) | PASS (`D-S054-gateB=1`) |
| C (07/08) | PASS (`D-S054-phaseC=1`; T1.1–T1.7) |
| 09 | pass_with_advisories |
| 11 | **APPROVED** (`D-S054-11=1`) |
| Deploy 12/13 | **skipped** (routing) |

## Locked CI contexts

| Context | Role |
|---------|------|
| `Rust crates (fmt/clippy/test)` | fmt + clippy + cargo test (both crates) |
| `tac2iwxxm PyO3 (maturin)` | PyO3 smoke |
| `iwxxm-validate PyO3 (maturin)` | PyO3 smoke |

## Corpus cites

`[Corpus: product §F13]` · `[Corpus: product §F14]` · `[Corpus: tests]` ·  
`[Corpus: tech-spec]` · `[Corpus: adr/ADR-017]` · `[Corpus: decisions]` EV-045 ·  
`[Corpus: WAIVED — AC6 ruleset apply; D-S054-ac6-waive=2]`

## Reports

| Artifact | Path |
|----------|------|
| Requirements | `reports/01-requirements.md` |
| Gate A | `reports/02-verify-plan.md` |
| Tech plan | `reports/04-tech-plan.md` |
| Gate B | `reports/05-verify-tech.md` |
| Execution plan | `reports/execution-plan.md` |
| 08 | `reports/verification-report.md` |
| 09 | `reports/qa-report.md` |
| 11 | `reports/verify-impl.md` |

## Follow-ups

- Admin: `bash scripts/deploy/apply_gh_branch_rulesets.sh` (QA-001)  
- Merge [#953](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/953) → `stage` when ready (user approval)  
- Resume parked EV-043 / EV-044 when appropriate
