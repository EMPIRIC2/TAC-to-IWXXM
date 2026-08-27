# ADR-007: Universal 100% Coverage Gate

## Status: Accepted (amended EV-080 / #1077)

## Context

The legacy repo enforced a high coverage floor on the backend. The monorepo extended a
**universal** gate across Python packages/apps and frontend Vitest (originally **95%**,
ADR-007 v1; restored/enforced in EV-047 / EV-052 / EV-053).

EV-080 / [#1077](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1077) raises the floor to
**100% line and branch** unit coverage and extends the gate to repo **scripts** (Python
coverage + **bats-core** for every `scripts/**/*.sh`).

## Decision

Enforce **100% line and branch** coverage on all measurable Python packages and apps:

- `apps/backend`, `apps/worker`
- `packages/auth`, `packages/shared`, `packages/tac2iwxxm`, `packages/tac-validate`,
  `packages/iwxxm-validate`, `packages/dissemination`
- Root / workspace pytest-cov configs (`fail_under = 100`, `branch = true`)
- Per-file floor **100%** via `scripts/ci/check_per_file_coverage.py --min-pct 100`

Enforce **100%** lines/statements/functions/branches on TypeScript unit surfaces:

- `apps/frontend` (Vitest)
- `packages/shared` (Vitest)

Enforce script coverage:

- All `scripts/**/*.py` under a dedicated coverage job with fail_under **100**
- Every `scripts/**/*.sh` covered by ≥1 **bats-core** test in CI

CI fails if any gated surface falls below 100%.

### Approved measurement omits (only)

- `vendor/**` and third-party schema snapshots
- Generated XSD/codegen trees (e.g. `iwxxm_xsd/v*/`, FE `src/generated/**`)
- Non-executable fixtures (e.g. FE `src/fixtures/**`), type-only `*.d.ts`, test files themselves
- Playwright e2e specs are **not** a unit coverage surface

Do **not** omit executable product modules (including `__init__.py` and previously excluded
FE modules such as `App.tsx` / editor helpers) without an explicit AskQuestion waiver.

## Consequences

- Large test uplift across packages, FE, and ~56 shell scripts + Python scripts.
- CI runtime increases (NFR: AskQuestion if any job exceeds 2× prior median).
- Supersedes EV-052/053 **95%** floors for new work; historical TC-EV052/053 remain archive
  evidence of the prior bar.

## Alternatives Considered

- **Keep 95%**: Rejected — operator requested strictest 100% interpretation (EV-080).
- **100% line only (no branch)**: Rejected — strict intake requires line **and** branch.
- **Waive shell scripts / FE excludes**: Rejected — bats for every `.sh`; remove executable
  FE coverage excludes.
- **Remove coverage gate**: Rejected — regression risk.

## Amendment history

| Date | Cycle | Change |
|------|-------|--------|
| (original) | Phase 1 / T1.9 | Universal **95%** gate |
| 2026-08 | EV-047 / EV-052 / EV-053 | Per-file ≥95%; FE branches ≥95; FileConverter re-include |
| 2026-08-27 | EV-080 / #1077 | Floor **100%** line+branch; scripts py + bats-core |

[Corpus: adr/ADR-007] [Corpus: tests] [Corpus: tech-spec]
