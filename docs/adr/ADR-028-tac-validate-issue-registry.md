# ADR-028: Maintainable `tac-validate` issue registry

> **Status**: Accepted  
> **Date**: 2026-07-19  
> **Deciders**: User (S015 intake E11-8 / Feature List E11-9–E11-10)  
> **Stage**: 01-requirements  
> **Related**: feature-list F15; packages/tac-validate; #732; deepen F20/F23/F24/F26/F27  
> **Session**: S015-metar-lint-quality / EV-011 (origin); S027 / EV-021 reuses for VAA/TCA codes  
> **Decision id**: E11-8 / E11-9 / E11-10; amended E11-32 (05-verify-tech)

## Context

`tac-validate` already emits structured `Issue` objects with `severity` (`error` | `warning` |
`info`), `code`, `message`, and optional spans (ADR-016 / ADR-025). Codes and severities are
still defined ad hoc inside rule functions, which makes METAR quality work (#732) hard to
extend, review, or document. Operators and maintainers need a single catalog of lint issues
that can grow without renaming public codes casually.

## Decision

1. **Registry home**: A first-class **registry module** lives in `packages/tac-validate`
   (e.g. `issue_registry` / `registry`). Rules **import** codes and default severities from
   the registry; they do not invent severity string literals for registered issues.
2. **Catalog export**: A docs/generated catalog (Markdown and/or structured export under
   package docs or `docs/domain/`) lists every registered code, default severity, and message
   template for humans and CI drift checks.
3. **Shape**: Registry entries are **product-agnostic** (code namespace may include product
   prefixes). **EV-011 encodes METAR deeply**; other products may have thin rows when existing
   rules already emit codes.
4. **Stability**: Public issue codes are **stable**. Renames require an explicit deprecation
   note (old code → new code). Default severities **may tighten** in minor releases; loosening
   severity for a published code is an ADR/changelog decision.
5. **CI**: Unknown codes emitted by rules fail tests. Registry row without a covering fixture
   may be marked `deferred` **only** for non–R1–R8 / thin non-METAR-SPECI product rows this
   cycle (E11-23/32). **R1–R8 METAR/SPECI themes must ship green fixtures** — no silent deferral.
6. **HTTP catalog (E11-31)**: Additive `GET /api/v1/lint-issue-catalog` exports the registry for
   FE tooltips; `POST /lint-tac` wire shape unchanged.

## Alternatives Considered

| # | Alternative | Why rejected |
|---|-------------|--------------|
| 1 | YAML/JSON data file only | Valid, but Python module keeps types + import graph simpler for PyPI package; may still *generate* YAML/MD from the module |
| 2 | `packages/shared` registry | Premature — only `tac-validate` emits TAC lint issues today |
| 3 | METAR-only registry type | Blocks reuse; product-agnostic shape costs little |
| 4 | Freely rename codes until 0.2.0 | Breaks API/UI consumers and golden expected_codes fixtures |

## Consequences

- F15 implementation adds registry + migrates existing METAR/SPECI (and shared) codes onto it.
- ADR-025 terminator/`info` semantics unchanged; registry records `MISSING_TERMINATOR` as `info`.
- Frontend displays `code` + `severity` from lint-tac; catalog panel/tooltips use
  `GET /api/v1/lint-issue-catalog` (E11-31) without changing lint-tac fields.
- Coverage-matrix and research catalog (EV-011) cite registry codes for METAR/SPECI **R1–R8**
  themes (HARD — E11-23/28).
