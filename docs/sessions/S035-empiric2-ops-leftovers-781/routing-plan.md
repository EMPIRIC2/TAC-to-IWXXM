# Routing plan — S035 / EV-028

**Preset (proposed):** Lean+build  
**Base:** `main` @ tip when branch created  
**Branch:** `evolve/EV-028-empiric2-ops-leftovers-781`

## Required stages

| Stage | Mode | Why |
|-------|------|-----|
| `00-context` | scoped | Session open + this brief |
| `16-evolve` | orchestrator | EV-028 general cycle |
| `01-requirements` | delta | Scope + acceptance in evolve-decisions / test-plan touch if needed |
| `02-verify-plan` | delta | Consistency on packaging/CI docs touched |
| `04-tech-plan` | delta | Task list: Codecov, Trusted Publisher, README, version bump + tag |
| `07-build` | delta | Implement CI/README/version tasks |
| `08-verify-build` | delta | Lint/tests on changed paths; confirm no Codecov in workflows |
| `10-e2e` | delta | Packaging/OIDC smoke (not browser H4–H5) |
| `13-deploy-smoke` | delta | Tag → `pypi-publish.yml` green; PyPI version visible |

## Skipped (rationale)

| Stage | Why skip |
|-------|----------|
| `03-plan-tooling` | No new Cursor rules/hooks required |
| `05-verify-tech` | Thin tech plan; lean gate via 02 + 08 |
| `06-tech-tooling` | No new dependency/tooling surface |
| `09-qa` | No product journeys; packaging smoke covers acceptance |
| `11-verify-impl` | Lean; acceptance checked in 10/13 + PR |
| `12-verify-deploy` | No Render/Supabase deploy change |

## Connectivity

No browser UI — H4–H5 N/A. PyPI OIDC + CI are the deploy surfaces.

## Status

**Approved** 2026-08-01 — `D-S035-routing`: **5a** Lean+build; **6b** all three packages → `0.1.1`.
