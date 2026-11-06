# ADR-055: Product → region → country → station inheritance factory

**Status:** Accepted (EV-lint-inherit-factory L0 — shared contract, 2026-11-01)  
**Date:** 2026-11-01  
**Deciders:** Parent (recommended AskQ answers applied; Spec→Build open for L0)  
**Session:** `~/.cursor/workflow/EMPIRIC2/TAC-to-IWXXM/sessions/EV-lint-inherit-factory`  
**Related:** [ADR-036](ADR-036-semantic-vs-exchange-profiles.md), [ADR-037](ADR-037-platform-logical-layers.md), [ADR-038](ADR-038-conversion-profile-contract.md), [ADR-045](ADR-045-shared-tac-pack-engine.md), [ADR-046](ADR-046-validation-policy-layers.md)  
**Corpus:** [Corpus: product §F15] [Corpus: product §F36] [Corpus: adr/ADR-036] [Corpus: adr/ADR-038] [Corpus: adr/ADR-045] [Corpus: adr/ADR-046] [Corpus: domain-profiles] [Corpus: pack-engine-boundary] [Corpus: system-spec] [Corpus: decisions]

> **Numbering:** ADR-054 is reserved by severity-strict-ui. This decision is **ADR-055**.

## Context

National and station dialects exist in pieces today:

- Lint: single-parent `inherits` + leaf `stations` / `station_prefixes` + **TAF-only** ICAO prefer ([ADR-046] amends).
- Convert: flat semantic/emit keys + policy id bind that walks the lint chain ([ADR-038], [ADR-046]).
- IWXXM: policy document `extends` lists ([ADR-046]).
- Decode: product pack `extends` ([ADR-045]); MatchPort into lint only.

`tac-validate.lint_with_profile` currently imports `tac2iwxxm.profile_resolve` for policy
ids — that cross-engine import violates the target boundary (ports + shared contract only).

Operators need one mental model: effective rules for a **product** along
**product → region → country → station**, with explicit overrides, without merging packages.

## Decision

### 1. Inheritance factory contract in `packages/shared`

Place **types + pure merge helpers + Protocol ports** in `packages/shared`
(`metar_shared.inherit_factory`). No engine runtimes there.

Each engine package **implements ports** and owns its YAML/runtime:

| Package | Port responsibility |
|---------|---------------------|
| `tac-validate` | Lint profile DAG + ICAO prefer + TAC quality policy apply |
| `tac2iwxxm` | Emit / conversion binding + policy id selection via shared types |
| `iwxxm-validate` | Load IWXXM output policy id (dumb loader) |
| `tac-decoding` | Pack / MatchPort resolution only |

**Must not:** `tac-validate` ↔ `tac2iwxxm` imports (either direction) for resolve.
Apps/backend may wire ports. [Corpus: pack-engine-boundary]

Conceptual API:

```text
resolve(product, region?, country?, station?, explicit_profile?) → EffectiveBundle
```

`EffectiveBundle` carries **ids and override maps** only.

### 2. Product is the DAG root

```text
product → region → country → station
```

Empty region/country nodes are allowed during migration.

### 3. Region is a new semantic layer

**Region** = optional multi-country **semantic** dialect grouping above country.
Not ADR-036 exchange / TT packaging (orthogonal).

### 4. Override merge

| Kind | Rule |
|------|------|
| Scalars / map values | **Child wins** |
| Allow / deny / suppress **sets** | **Additive union**, unless the child **replace**s that set |

### 5. ICAO / national prefer — beyond TAF

Prefer applies for default annex3 / `ICAO_2025` when catalog maps the station, for
**METAR**, **SPECI**, **TAF**, **SIGMET** (where profiles exist). Explicit national
profiles still win. Catalog-driven honesty (e.g. CA `CW*` METAR) remains.

### 6. Decode v1

Pack id / MatchPort context only. No lint overlays from decode ([ADR-045]).

### 7. Wire v1

Internal resolution first; optional response echo of resolved chain; no breaking
public API enums in v1.

### 8. Non-goals

In-app editor; umbrella validation package; collapsing region into exchange;
Schematron re-authoring. Full engine migrates are later evolves (post L0).

## Alternatives considered

| # | Alternative | Outcome |
|---|-------------|---------|
| A | Status quo only | Rejected as end-state |
| B | Resolve owned in `tac2iwxxm` with validator imports | Rejected |
| C | Region = exchange | Rejected |
| D | Product orthogonal to geo | Rejected — product is DAG root |
| E | Shared contract + ports | **Accepted** |

## Consequences

- L0 ships `metar_shared.inherit_factory` + tests.
- Later package evolves (≤500 LOC) implement ports and drop cross-engine imports.
- Prefer expansion needs honesty fixtures in those evolves.

## Amends (implement evolves)

- **ADR-046:** lint inherit + prefer become factory backends; prefer product scope expands.
- **ADR-038:** convert uses `EffectiveBundle`; no validator→convert import.
- **ADR-036:** semantic region ≠ exchange.
- **ADR-045:** decode = pack/MatchPort resolution only.

## Migration

1. **L0 (this PR):** shared types/merge/ports + ADR Accepted.
2. Later: tac-validate → tac2iwxxm → iwxxm-validate → tac-decoding → optional backend echo.
