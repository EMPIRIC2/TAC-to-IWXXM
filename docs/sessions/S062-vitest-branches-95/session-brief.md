# Session brief — S062-vitest-branches-95

> **Cycle**: EV-053 · **Type**: feature · **Opened**: 2026-08-10  
> **Branch**: `evolve/EV-053-vitest-branches-95` (base `stage@6f25c0b1`)  
> **Orchestrator**: 16-evolve  
> **Corpus**: [Corpus: product §F29] [Corpus: product §M5] [Corpus: tests]
> [Corpus: adr/ADR-007] [Corpus: decisions §EV-052] [Corpus: decisions §EV-053]

## Goal

Close the EV-052 Vitest **branches** waiver: raise frontend coverage `branches` to
**≥95%** (FileConverter-heavy), suite green under that gate, and resolve the explicit
`branch_waiver` / child [#968](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/968).

## Intent (locked — D-S062-route=1)

Follow-up only from `D-S061-cov-branches=3` / S061 close (`D-S061-close=1` left #968 open).
No new product Fn — deepen **F29** / **M5** coverage-gate honesty for Vitest branches.

Parent context: [#950](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/950) / EV-052 /
[Corpus: decisions §EV-052].

| Decision | Choice |
|----------|--------|
| D-S062-route | **1** — Standard as drafted; branch from `stage`; open S062 → 16-evolve |
| D-S062-ui-preview | **2** — No local UI preview; docs/repo + Vitest only |
| D-S062-dirty | **2** — S061 leftovers already on `stage` via [#972](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/972); no extra closeout commit |

## Out of scope

- Lowering lines / statements / functions below 95
- Mutation testing (#874), Schemathesis (#727)
- In-app quality metrics UI (#836)
- Sentry / Redis / openapi-typescript follow-ups (done in EV-052)
- `stage`→`main` promote / tag-driven prod cutover
- Operator UI redesign (tests may exercise FileConverter; no product UX change)

## Features

- Deepen **F29** / **M5** — Vitest branches ≥95; resolve `D-S061-cov-branches` waiver
- No new Fn id

## Acceptance (from #968)

1. Vitest `branches` threshold **≥95** in `apps/frontend/vitest.config.ts`
2. Suite green under that gate (fill tests and/or justified excludes in coverage inventory)
3. Update S061 `coverage-surface-inventory.yaml` `branch_waiver` → resolved (or move
   inventory forward under this session with cite)
4. Cite closeout in `docs/decisions/evolve-decisions.md` / `[Corpus: tests]`

## Related issues

- [#968](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/968) — this session (primary)
- Parent: [#950](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/950) (Done) / epic [#841](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/841)

## UI preview

Declined (`D-S062-ui-preview=2`) — CI / Vitest only; no non-deployed product UI preview.

## Notes

- Current tip on `stage` (post EV-052): excludes `FileConverter.tsx` from Vitest coverage
  collection and keeps `branches: 84` with explicit waiver comments.
- Closing ≥95 may require **re-including** FileConverter and/or targeted branch tests /
  justified excludes — decide in 01/04.
