# Evolve report — EV-028

| Field | Value |
|-------|-------|
| Cycle | EV-028 |
| Session | S035-empiric2-ops-leftovers-781 |
| Status | **completed** |
| Started | 2026-08-01 |
| Completed | 2026-08-01 |
| Issues | [#781](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/781) **closed** |
| PR | [#824](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/824) → `70312dd` |
| Deploy smoke (13) | **PASS** — OIDC tags `0.1.1` ×3 + `iwxxm-validate-v0.1.2`; clean-venv install smoke |
| Close decision | Merge approval option **1** (PR #824) |

## Scope

Finish #781 leftovers: Codecov purge; EMPIRIC2 PyPI Trusted Publishers; consumer
landing READMEs; prove OIDC with `tac-validate` / `iwxxm-validate` / `tac2iwxxm`
`0.1.1`, plus native AIXM fix as `iwxxm-validate==0.1.2`.

## Routing

Lean+build: `00→16→01→02→04→07→08→10→13`. Skipped 03/05/06/09/11/12.

## Results

| Gate | Result |
|------|--------|
| A→B | passed (`D-S035-02-phase-a`) |
| B→C | passed (`D-S035-04-plan-approve`) |
| C→D | passed (M0–M3; PR #824; CI green on branch + `main`) |
| Deploy (13) | passed — PyPI publish + install smoke (`t34-pypi-install-smoke.md`) |

## Package publishes

| Package | Version | Evidence |
|---------|---------|----------|
| `tac-validate` | `0.1.1` | OIDC tag publish |
| `tac2iwxxm` | `0.1.1` | OIDC tag publish |
| `iwxxm-validate` | `0.1.1` then `0.1.2` | AIXM 5.1.1 native XSD fix; run 30726416585 |

## Follow-ups

- Cosmetic: published `iwxxm-validate==0.1.2` still exposes `__version__ == "0.1.1"`;
  string sync is on `main` for the next wheel (`D-S035-14d` — no 0.1.3 this cycle).
- Optional out-of-scope #781 items remain deferred (e2e/load secrets, Render rename,
  Supabase Site URL, #777 dissemination publish).
