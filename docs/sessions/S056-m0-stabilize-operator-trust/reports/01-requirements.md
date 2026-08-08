# 01-requirements — S056 / EV-047

**Status**: drafted — awaiting `D-S056-01-ac`  
**Date**: 2026-08-08  
**Mode**: delta (deepen M5 + F6 + F7)  
**Issues**: [#833](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/833),
[#834](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/834),
[#956](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/956),
[#957](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/957)

## Corpus

[Corpus: product §M5] [Corpus: product §F6] [Corpus: product §F7]
[Corpus: journeys] [Corpus: tests] [Corpus: tech-spec] [Corpus: decisions]

## Standing doc deltas

| Doc | Change |
|-----|--------|
| `docs/feature-list.md` | M5 EV-047 slim husky; F6 converter perf deepen; F7 Help/docs deepen |
| `docs/test-plan.md` | CI/husky policy EV-047 amend; TC-EV047-001..011; UJ map |
| `docs/user-journeys.md` | UJ-054; UJ-DEV-007; UJ-DEV-008 |
| `docs/decisions/evolve-decisions.md` | Phase 0 lock + AC table (this stage) |
| `docs/decisions/requirements-decisions.md` | EV-047 section |

## Skipped (N/A this cycle)

- New ADR (policy deepen of existing M5/F6/F7; EV-036 day-to-day superseded in decisions log)
- `api-contract.md` / `deploy.md` — no new HTTP/env unless Help is static-only
- Dependency inventory — no new runtime deps expected

## Acceptance criteria (proposed → confirm)

| AC | Issue | Criterion | TC |
|----|-------|-----------|-----|
| AC1 | #833 | After `make install-hooks`, commit path = lint/format only (no typecheck/catalog/registry/actionlint/yamllint/medium validate) | TC-EV047-001 |
| AC2 | #833 | Push path = fast unit subset only (not `validate-ci` / Compose) | TC-EV047-002 |
| AC3 | #833 | `DEVELOPMENT.md` + test-plan match shape A; opt-in `make` documented | TC-EV047-003 |
| AC4 | #833 | Offloaded gates still enforced in CI | TC-EV047-004 |
| AC5 | #834 | Artificial convert slowdown → CI perf gate red; revert → green | TC-EV047-005/006 |
| AC6 | #834 | Required CI check; baselines YAML + refresh + flake policy; convert-only p95; METAR/SPECI/TAF + thin SIGMET-family; pure-Python first; >20% or absolute ceiling | TC-EV047-007/008 |
| AC7 | #956 | One-pager at `docs/guides/operator-one-pager.md` (one printed page; convert→validate→download; version; soft preview; no internal cites) | TC-EV047-009 |
| AC8 | #957 | Handbook at `docs/guides/operator-handbook.md` (required sections + ingest pointer; no internal cites; linked from one-pager) | TC-EV047-010 |
| AC9 | #956/#957 | README Quick start + in-app Help → one-pager (UJ-054) | TC-EV047-011 |

## Defaults (from Phase 0)

| ID | Locked |
|----|--------|
| D-S056-husky-shape | A — pre-commit lint; pre-push fast units |
| D-S056-perf | Recommended pack (p95 / 20% / CI-only / …) |
| D-S056-docs | `docs/guides/operator-*.md` + README + Help |
| Routing amend | Re-enable **10-e2e** for UJ-054; 12/13 still waived unless 11 requires deploy |

## Next

Confirm ACs (`D-S056-01-ac`) + UI preview offer → mark 01 completed → **02-verify-plan**.
