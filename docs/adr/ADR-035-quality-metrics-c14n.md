# ADR-035: Quality metrics match/diff uses W3C C14N (not ADR-032 canonicalize)

> **Status**: Accepted  
> **Date**: 2026-08-11  
> **Deciders**: User (`D-S064-c14n=1`, `D-S064-c14n-host=1`, `D-S064-04-plan=1`,
> `D-S064-c14n-volatile=1`)  
> **Stage**: 07-build (S064 / EV-055)  
> **Related**: F7.q, F2, F13; #982; ADR-032; [Corpus: product §F7] [Corpus: api]

## Context

Quality metrics (EV-054) compared official vs converted XML with ADR-032
`canonicalize_xml` (structural normalize that also strips volatile attrs). EV-055
requires **W3C Canonical XML** so formatting-only pretty-print noise does not dominate
unified diffs, while semantic differences remain visible. ADR-032 must not be silently
overloaded for all callers.

A pure-C14N trial regen (whitespace strip + C14N only) kept `gml:id` / UUID attribute
noise and flipped **every** stem to `match_status=unequal` (including stems that were
`equal` under ADR-032). That trial artifact was reverted; M3 needs an explicit policy for
volatile attributes.

## Decision

1. Quality metrics **`match_status`** and default unified diff peers use **W3C C14N 1.0**
   via `iwxxm_validate.c14n.c14n_xml` (lxml) after:
   - **volatile-attribute strip** (same local-name set / UUID-href / `codes.wmo.int` href
     rules as ADR-032 `strip_volatile_attributes` / `_filter_volatile_attrs`), then
   - stripping whitespace-only text nodes
   (so pretty vs compact IWXXM compare equal, and UUID / `gml:id` churn does not dominate
   match chips). FE peers use `apps/frontend/src/utils/c14nXml.ts` with the same strip order.
2. Host Python helper in **`packages/iwxxm-validate`** (lxml already declared) — not
   `packages/shared` (`D-S064-c14n-host=1`). Do **not** import `metar_shared` from the
   validate package; duplicate the volatile rules next to C14N (parity tests cover both).
3. **ADR-032 `canonicalize_xml` remains** for comparative / WMO golden / other CI paths
   until those callers explicitly migrate. Sibling **reordering** from ADR-032 is **not**
   part of Quality-metrics equality (C14N preserves document order).
4. Detail panes default to C14N XML (post–volatile-strip) with operator override to raw
   (`D-S064-gateA-M2`).
5. **Volatile policy** (`D-S064-c14n-volatile=1`): **C14N after volatile-attr strip** —
   not pure C14N alone, and not “C14N of ADR-032 `canonicalize_xml` output”.

## Consequences

- Generator must switch from `canonicalize_xml` to `c14n_xml` / `c14n_equal` for
  `match_status` (M3).
- Regenerating `corpus_metrics.json` may change equal/unequal counts vs EV-054, but UUID /
  `gml:id`-only peers should remain usable match chips (not blanket `unequal`).
- FE and Python helpers must stay golden-parity for representative stems.
- Element-order differences still yield `unequal` (unlike full ADR-032 structural sort).

## Alternatives considered

- Overload ADR-032 canonicalize for Quality metrics — rejected (different contract).
- Add lxml to `packages/shared` — rejected at Gate B (`D-S064-c14n-host=1`).
- New npm C14N package — rejected (no new npm in v1).
- **Pure C14N only** (no volatile strip) — rejected (`D-S064-c14n-volatile=1`); trial regen
  made every stem `unequal` due to `gml:id` / UUID noise.
- **C14N of ADR-032 `canonicalize_xml` string output** — rejected; that string is a
  Python `repr` of a sorted tree, not XML, and would maximize EV-054 continuity at the
  cost of a non-standard double pipeline.
