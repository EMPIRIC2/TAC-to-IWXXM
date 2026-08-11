# ADR-035: Quality metrics match/diff uses W3C C14N (not ADR-032 canonicalize)

> **Status**: Accepted  
> **Date**: 2026-08-11  
> **Deciders**: User (`D-S064-c14n=1`, `D-S064-c14n-host=1`, `D-S064-04-plan=1`)  
> **Stage**: 07-build (S064 / EV-055)  
> **Related**: F7.q, F2, F13; #982; ADR-032; [Corpus: product §F7] [Corpus: api]

## Context

Quality metrics (EV-054) compared official vs converted XML with ADR-032
`canonicalize_xml` (structural normalize that also strips volatile attrs). EV-055
requires **W3C Canonical XML** so formatting-only pretty-print noise does not dominate
unified diffs, while semantic differences remain visible. ADR-032 must not be silently
overloaded for all callers.

## Decision

1. Quality metrics **`match_status`** and default unified diff peers use **W3C C14N 1.0**
   via `iwxxm_validate.c14n.c14n_xml` (lxml) after stripping whitespace-only text nodes
   (so pretty vs compact IWXXM compare equal). FE peers use `apps/frontend/src/utils/c14nXml.ts`.
2. Host Python helper in **`packages/iwxxm-validate`** (lxml already declared) — not
   `packages/shared` (`D-S064-c14n-host=1`).
3. **ADR-032 `canonicalize_xml` remains** for comparative / WMO golden / other CI paths
   until those callers explicitly migrate.
4. Detail panes default to C14N XML with operator override to raw (`D-S064-gateA-M2`).

## Consequences

- Generator must switch from `canonicalize_xml` to `c14n_xml` for `match_status` (M3).
- Regenerating `corpus_metrics.json` may change equal/unequal counts.
- FE and Python helpers must stay golden-parity for representative stems.

## Alternatives considered

- Overload ADR-032 canonicalize for Quality metrics — rejected (different contract).
- Add lxml to `packages/shared` — rejected at Gate B (`D-S064-c14n-host=1`).
- New npm C14N package — rejected (no new npm in v1).
