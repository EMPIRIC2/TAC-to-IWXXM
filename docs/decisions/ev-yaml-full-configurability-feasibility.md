# Feasibility — EV-yaml-full-configurability (#1226)

**Session:** EV-yaml-full-configurability  
**Verdict:** **Feasible as a multi-milestone program** (not a single PR)  
**Date:** 2026-09-21

[Corpus: product] [Corpus: adr/ADR-047] [Corpus: adr/ADR-045] [Corpus: adr/ADR-046] [Corpus: tech-spec] [Corpus: tests]

## Summary

End-state (all products × all engines **full**, including convert emit YAML) is achievable by composing existing pack/policy loaders (#1225), ADR-045/046, and a new emit-map runtime (ADR-047). Risk is **scope/review volume**, not unknown platform capability.

## Feasible now

| Area | Why |
|------|-----|
| M1 templates/DX | Extends shipped examples/preflight |
| M2 METAR/SPECI deepen | Strongest existing builtins |
| Overlay-only injection | Already enforced (TC-EVYEC-004) |
| Pin↔SCH asserts | Pins + vendor SCH already in tree |

## Hard / large

| Area | Mitigation |
|------|------------|
| Convert emit YAML | ADR-047 + METAR pilot before SPECI/others |
| All products parallel (M4) | Child issues + small PRs; not one mega-PR |
| “Full” vs Python enrichment hooks | Spec may allow documented N/A/partial for non-YAML hooks if AskQuestion later |

## Non-goals (keep out)

ADR-044 UI · HTTP YAML · Schematron-as-YAML · #1222

## Recommendation

Proceed Spec → tech-plan → verify; open Build only after documenting verify Pass + AskQuestion gate.
