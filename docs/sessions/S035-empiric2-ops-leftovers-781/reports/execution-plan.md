# Execution plan — S035 / EV-028 (#781)

**Branch**: `evolve/EV-028-empiric2-ops-leftovers-781`  
**Preset**: Lean+build · **Features**: none (F12–F14 deepen)  
**Status**: **approved** — Gate B (`D-S035-04-plan-approve`) · **11b** tag from evolve branch · **12a**

## Policies (locked)

| ID | Policy |
|----|--------|
| E28-2 | Codecov + Trusted Publisher + landings; no e2e/load secrets / Render rename / #777 publish |
| E28-3 | README polish: three public + dissemination |
| E28-6 | All three packages → `0.1.1` OIDC proof |
| E28-T2 | **11b** — Push version tags from evolve branch **before** merge (faster OIDC proof) |
| E28-T3 | No new dependencies without AskQuestion |

## Milestones

### M0 — Codecov purge (TC-EV028-001)

| Task | Status | Spec Source | Depends On | Description |
|------|--------|-------------|------------|-------------|
| T0.1 | **completed** | TC-EV028-001; #781 | — | Remove Codecov steps from `.github/workflows/ci-cd.yml` (keep coverage artifacts) |
| T0.2 | **completed** | TC-EV028-001 | T0.1 | Remove Codecov badges from root + `apps/backend/README.md`; delete `.codecov.yml` |
| T0.3 | **completed** | TC-EV028-001 | T0.2 | Delete GitHub Actions secret `CODECOV_TOKEN` (`gh secret delete`) |

### M1 — Consumer-facing landings (acceptance §4)

| Task | Status | Spec Source | Depends On | Description |
|------|--------|-------------|------------|-------------|
| T1.1 | **completed** | E28-3; F12–F14 AC5 | — | Rewrite `packages/tac-validate/README.md` + `description` (no ADR/Fn/E10) |
| T1.2 | **completed** | E28-3; F13 AC5 | — | Rewrite `packages/iwxxm-validate/README.md` + `description` |
| T1.3 | **completed** | E28-3; F14 AC3 | — | Rewrite `packages/tac2iwxxm/README.md` + `description` |
| T1.4 | **completed** | E28-3 | — | Rewrite `packages/dissemination/README.md` + `description` (library consumers; note not on PyPI yet) |

### M2 — Version bump + Trusted Publisher (TC-EV028-002)

| Task | Status | Spec Source | Depends On | Description |
|------|--------|-------------|------------|-------------|
| T2.1 | **completed** | TC-EV028-003; UJ-023 | T1.1–T1.3 | Bump `tac-validate`, `iwxxm-validate`, `tac2iwxxm` to `0.1.1` in `pyproject.toml` (+ Cargo.toml) |
| T2.2 | **completed** | TC-EV028-002; deploy.md | — | Operator: configure PyPI Trusted Publisher ×3 (`D-S035-E28-T22` / 13a) |
| T2.3 | **completed** | TC-EV028-002 | T2.2 | Operator confirmed `pypi` env (API may auto-create on first publish job) |

### M3 — Build verify + tag publish (TC-EV028-003 / UJ-023)

| Task | Status | Spec Source | Depends On | Description |
|------|--------|-------------|------------|-------------|
| T3.1 | pending | 08-verify-build | T0.3, T1.4, T2.1 | Lint/typecheck/tests on changed paths; assert no `codecov` in workflows |
| T3.2 | pending | 10-e2e; TC-EV028-001 | T3.1 | Packaging smoke report (README grep for ADR-/F\d\d|E10-; Codecov absent) |
| T3.3 | **completed** | TC-EV028-003; UJ-023; E28-T2 | T2.2, T2.3, T3.2 | `0.1.1` OIDC publish ×3 green (`D-S035-14a`); runs 30703582092 / 30703582129 / 30703806187 |
| T3.4 | pending | TC-EV028-003 | T3.3 | Clean-venv `pip install <pkg>==0.1.1` smoke for all three |
| T3.5 | pending | #781 AC | T3.4 | PR merge; close #781 Codecov+PyPI leftovers (or note remaining optional secrets) |

## Suggested commit grain (07)

1. Codecov purge (T0.*)  
2. README/`description` rewrites (T1.*) — can be one commit or per package  
3. Version bump `0.1.1` (T2.1)  
4. Tags after merge/green (T3.3) — tags are not code commits  

## Gate C (close)

1. TC-EV028-001 — Codecov gone; CI green  
2. TC-EV028-002 — Trusted Publishers on EMPIRIC2  
3. TC-EV028-003 — `0.1.1` ×3 on PyPI + install smoke  
4. Landings have no required ADR/Feature/E10 refs  

## Out of scope (do not schedule)

e2e/load secrets · Render hostname rename · Supabase Site URL · `#777` `iwxxm-dissemination` publish · new Fn
