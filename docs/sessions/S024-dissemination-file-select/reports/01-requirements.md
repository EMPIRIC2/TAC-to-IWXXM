# 01-requirements — S024 / EV-018 (delta)

**Date**: 2026-07-28  
**Mode**: evolve delta — deepen **F16** (#785)  
**UI preview**: Already opened local http://localhost:18000/ (E18-8) — non-deployed

## Scope (locked D-S024-E18-scope-lock)

Deepen F16 multi-file export selection; F17–F19 reuse selection contract; no new Fn;
Lean+build routing; E18-1..8.

## Corpus deltas written

| Doc | Change |
|-----|--------|
| `docs/feature-list.md` | F16 deepen EV-018 acceptance 7–10; F17 note; last-updated |
| `docs/spec.md` | F16–F19 section + frontend drawer multi-select |
| `docs/api-contract.md` | Client N-sequential contract; no batch API; ≤20 cap |
| `docs/user-journeys.md` | UJ-027 multi-select steps; UJ-028 reuse; changelog |
| `docs/test-plan.md` | TC-F16-005; UJ-027 → TC-F16-001..005 |
| `docs/decisions/evolve-decisions.md` | EV-018 Batch 1+2 + scope lock |
| `docs/context/dissemination-file-select.md` | Resolution log |

## Non-goals recorded

Finished IndexedDB history as sources; batched multi-payload API; saved profiles; F8 auto-push.

## Connectivity

H4–H5 / H6′ UJ-027–030 remain the browser gates; no new CORS origins; FE-only selection UX
plus existing dissemination routes.

## Exit

Pending user confirm of deltas → mark 01 **completed** → **02-verify-plan**.
