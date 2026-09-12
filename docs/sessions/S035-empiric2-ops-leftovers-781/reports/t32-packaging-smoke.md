# T3.2 — Packaging / landing smoke (EV-028 / TC-EV028-001)

**Date**: 2026-08-01
**Scope**: Consumer landings + Codecov absence

## Codecov absence

- `.github/workflows`, root README, `apps/backend/README.md`: no `codecov` matches
- `.codecov.yml`: absent

## Landing README forbidden patterns (`ADR-` / Fn / `E10-`)

### `packages/tac-validate/README.md`
PASS — no ADR-/Fn/E10- matches

### `packages/iwxxm-validate/README.md`
PASS — no ADR-/Fn/E10- matches

### `packages/tac2iwxxm/README.md`
PASS — no ADR-/Fn/E10- matches

### `packages/dissemination/README.md`
PASS — no ADR-/Fn/E10- matches

## pyproject `description` fields

### `packages/tac-validate/pyproject.toml`
- description: 'Lint TAC aviation weather products (METAR/SPECI/TAF and related) with structured issues'
PASS

### `packages/iwxxm-validate/pyproject.toml`
- description: 'Validate IWXXM XML with XSD and Schematron (schemas bundled)'
PASS

### `packages/tac2iwxxm/pyproject.toml`
- description: 'Convert TAC aviation weather reports to IWXXM XML'
PASS

### `packages/dissemination/pyproject.toml`
- description: 'IWXXM dissemination sinks, writer-contract DDL, and egress allowlist helpers'
PASS

## Verdict: PASS
