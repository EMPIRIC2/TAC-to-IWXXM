# ADR-001: Vendor Snapshots for Authoritative iwxxm Schemas

**Status**: Accepted  
**Stage**: 01-requirements  
**Date**: 2026-06-14

## Context

The project depends on four wmo-im repositories (iwxxm, iwxxm-codelists, iwxxm-modelling,
iwxxm-translation) as source-of-truth for XSD/Schematron content. These are currently git
submodules pointing at forks with upstream remotes to wmo-im.

Requirements: schemas must be **read-only** in our repo; we still need to pull new releases
from wmo-im without submodule complexity.

## Decision

Replace iwxxm-* submodules with **vendored snapshots** under `vendor/schemas/`, pinned by
`vendor/manifest.json`. Updates arrive via **scheduled GitHub Actions** that open PRs when
wmo-im publishes new tags.

## Alternatives Considered

| Option | Rejected because |
|--------|------------------|
| Git submodules (status quo) | Six submodules; SHA drift; clone friction |
| Git subtree | Still embeds full git history; overkill for read-only SoT |
| Live fetch at runtime | Non-deterministic builds; air-gapped deploy fails |

## Consequences

**Positive**: Single clone; explicit version pins; clear read-only boundary; CI can verify manifest integrity.

**Negative**: Larger repo size; manual PR review for schema updates; sync script maintenance.

## References

- REQ-002, REQ-009, REQ-015
- docs/spec.md §vendor/schemas
