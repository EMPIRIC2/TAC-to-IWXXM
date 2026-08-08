# 01-requirements — S054 / EV-045

**Status**: completed — D-S054-01-ac=1  
**Date**: 2026-08-08  
**Mode**: delta (deepen F13 + F14)  
**Issue**: [#725](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/725)

## Corpus

[Corpus: product §F13] [Corpus: product §F14] [Corpus: journeys] [Corpus: tech-spec]
[Corpus: tests] [Corpus: adr/ADR-017] [Corpus: decisions]

## Standing doc deltas

| Doc | Change |
|-----|--------|
| `docs/feature-list.md` | F13/F14 deepen AC + summary row |
| `docs/test-plan.md` | TC-EV045-001..007; CI/CD table; UJ map |
| `docs/user-journeys.md` | UJ-DEV-006 |
| `docs/tech-spec.md` | Rust native crates pointer |
| `docs/decisions/requirements-decisions.md` | EV-045 section |
| `docs/decisions/evolve-decisions.md` | EV-045 AC table |

## Skipped (N/A)

- Browser UI / H4–H5 / deploy.md / api-contract — CI-only
- New ADR — extends ADR-017 tooling; no new architectural choice yet
- Dependency inventory — no new Python/runtime package

## Defaults (confirmed — D-S054-01-ac=1)

1. Extend `ci-cd.yml` with crate matrix (not separate `rust-ci.yml`)
2. `clippy -- -D warnings` hard-fail
3. `make rust-check` local mirror

**Next:** 02-verify-plan (Gate A)
