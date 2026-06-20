# ADR-004: Manual GIFTs Upstream Merges

**Status**: Accepted  
**Stage**: 02-verify-plan  
**Date**: 2026-06-14

## Context

ADR-001 and REQ-014 originally specified scheduled GitHub Actions for GIFTs subtree pulls from
mgoberfield/GIFTs. During product plan verification (statement S-gifts), the user chose
**manual merges only** — no automated sync for GIFTs.

Vendor iwxxm schemas remain on scheduled wmo-im sync (ADR-001).

## Decision

- **GIFTs** (`packages/gifts`): editable in monorepo; upstream merges from mgoberfield/GIFTs
  are **manual** when maintainers choose.
- **Vendor schemas**: scheduled Action opens PRs on new wmo-im tags (unchanged).

## Alternatives Considered

| Option | Rejected because |
|--------|------------------|
| Scheduled subtree PRs (REQ-014 original) | User preference; GIFTs diverges from forks; manual control preferred |
| No upstream tracking | Loses path to canonical GIFTs improvements |

## Consequences

**Positive**: No surprise PRs; full control over GIFTs divergence; simpler CI.

**Negative**: Upstream fixes may lag; maintainers must remember to merge.

## References

- REQ-014 (modified), REQ-003
- docs/product-decisions.md — S-gifts verdict
- Statement S-gifts in 02-verify-plan audit
