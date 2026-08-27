# Scoped context — EV-080 unit coverage 100%

**status:** active  
**created:** 2026-08-27  
**session:** `~/.cursor/workflow/EMPIRIC2/TAC-to-IWXXM/sessions/EV-080-unit-coverage-100`  
**mode:** scoped (evolve)  
**template:** static+api+worker (unchanged)  
**UI preview:** N/A — no product UI change; Vitest only  

[Corpus: adr/ADR-007] [Corpus: tests] [Corpus: tech-spec] (typing-policy) [Corpus: product] (F34 adjacent; quality gates)

## Goal

Strictest interpretation: **100% line + branch** unit coverage on all measurable Python (`apps/`, `packages/`), TypeScript unit surfaces, and repo `scripts/`, enforced in CI with **no silent measurement excludes** of executable product/script code.

## Out of scope

- `vendor/**`, third-party schema snapshots  
- Generated XSD/codegen (`iwxxm_xsd/v*/`, FE `src/generated/**`, static fixtures)  
- Playwright e2e as a *unit* coverage surface (`apps/e2e`, `*.e2e.spec.ts`)  
- Product features, promote, PyPI, weakening non-coverage gates  

## Problem / users

| Who | Pain |
|-----|------|
| Maintainers / CI | Floor is 95–98%; gaps and intentional FE excludes hide untested executable code |
| Operators | Indirect — higher confidence that unit suite exercises all shipped logic |

No operator UJ change. Touches **developer quality** (ADR-007 / F34 complement), not F1–F23 product behavior.

## Must-not-break

- Existing green unit matrix jobs; H4–H5 / live markers remain separate  
- Dissemination SSRF / allowlist; no secrets in coverage artifacts  
- Vendor read-only; generated trees stay omit-from-measure (approved out)  
- No internal-doc refs on user-facing surfaces  

## Baseline inventory (2026-08-27)

Prior inventory: `docs/sessions/S061-ci-polish-quality-pr-stats/reports/coverage-surface-inventory.yaml` (EV-052 / target_floor **95**).

### Python `fail_under` (today)

| Surface | Config | Enforced |
|---------|--------|----------|
| root | `pyproject.toml` | **98** |
| backend | `apps/backend/pyproject.toml` | **98** |
| shared | `packages/shared/pyproject.toml` | **98** |
| worker, auth, tac2iwxxm, tac-validate, iwxxm-validate, dissemination | per-package | **95** |

Root omit (measurement): `**/__init__.py`, `**/tests/**`, `*/iwxxm_xsd/v*/**` — **strict cycle must remove `__init__.py` omit** unless waived.

`branch = true` already set at root.

Approx. non-test `.py` files (excl. xsd): backend ~99, tac2iwxxm ~38, tac-validate ~24, iwxxm-validate ~23, dissemination ~20, shared ~7, auth ~4, worker ~8. `packages/gifts` **absent** (post-F6 cutover).

### TypeScript (today)

| Surface | Thresholds | Notes |
|---------|------------|-------|
| `@metar/frontend` Vitest | lines/stmts/fns/branches **95** | Multiple `coverage.exclude` paths (strict: remove) |
| `@metar/shared` Vitest | **98** all four | Small surface |

**FE measurement excludes to eliminate under strict reading** (`apps/frontend/vitest.config.ts`):

- `src/utils/tacEditorSpans.ts`, `src/app/components/TacEditor.tsx`  
- `src/utils/liveAssist.ts`, `src/hooks/useLiveWorkbenchAssist.ts`  
- `src/utils/gunzip.ts`, `src/app/App.tsx`  
- Plus fixtures/generated (keep as non-executable / generated — aligned with Out)  

S061 listed a subset as “intentional_excludes”; EV-080 **revokes** those for unit measurement unless AskQuestion re-waives.

### Scripts (today)

- ~94 files under `scripts/` (`.py` / `.sh` / `.ts` / `.mjs`)  
- Partial unit coverage: `check_per_file_coverage.py`, PR comment formatters, quality stats, etc.  
- **No** dedicated “all scripts ≥100%” CI surface — **new harness required** (tech-plan)  
- Shell (`.sh`) coverage tooling TBD — see Open resolutions  

### Per-file checker

`scripts/ci/check_per_file_coverage.py` default `--min-pct 95` on `percent_covered` (with branch=true this is line+partial branch blend). Strict: raise default/CI invocations to **100**.

### CI wiring

`.github/workflows/ci-cd.yml` unit matrix runs package cov + per-file check + FE `test:coverage` + sticky PR coverage comment (EV-036). Bugs job `--no-cov` (keep).

## CORPUS / doc delta (for draft-docs)

| Doc | Change needed |
|-----|----------------|
| `[Corpus: adr/ADR-007]` | Amend Accepted decision **95% → 100%** line+branch (or superseding ADR) |
| `[Corpus: tech-spec]` typing-policy §Coverage | 95 → 100; script surface |
| `[Corpus: tests]` test-plan | New TC-EV080-*; update gate table 95→100; supersede TC-EV052 floors |
| `docs/decisions/evolve-decisions.md` | D-EV080-* |
| Inventory YAML | New EV-080 inventory (session reports or refresh S061 file via draft-docs decision) |

No new CORPUS **member** required if ADR amend + typing-policy + test-plan suffice.

## Feature map

| Fn | Relevance |
|----|-----------|
| F34 | Adjacent quality gates (mutation/contract) — **do not weaken**; coverage is separate ADR-007 |
| M5 / CI | Primary delivery surface |
| F1–F23 | Regression fence only |

## Historical / prior cycles

- EV-047 / EV-052 / EV-053 / S061–S062 — restored ≥95%, FE branches, FileConverter re-include  
- Memory-hook session-open: **skipped** (engineering-memory venv missing) — fail-open  

## Open resolutions (requirements)

| ID | Question | Recommendation |
|----|----------|----------------|
| R1 | Shell `.sh` scripts under 100% how? | **LOCKED:** bats/shunit for every `.sh` (strictest) + Python scripts 100% cov |
| R2 | Re-waive any FE exclude? | **None** under locked strict intake |
| R3 | `__init__.py` omit? | **Remove** omit; empty/trivial inits still measured |
| R4 | GitHub issue? | **LOCKED:** create tracking issue when requirements land |
| R5 | Measured % gap size unknown until M1 inventory run | Feasibility must budget multi-PR / multi-milestone |

## Build intent (not execution)

- Apps/packages: all Python + FE Vitest + shared Vitest + `scripts/` harness  
- Deploy: **none** this cycle  
- QA depth: unit + documenting/implementing verify angles; e2e skipped for unit gate  
- Observability: coverage JSON artifacts + PR comment thresholds updated  

## Exit → next

Next skill: **spec-development/requirements** (AC + TC-EV080 + milestone AC).  
Gate remains **closed**.


## Resolutions (2026-08-27)

- **R1** = bats/shunit for every `.sh` (option 2 strictest)
- **R4** = create GitHub issue when requirements land
- **R2/R3** = no FE re-waive; remove `__init__.py` omit (locked intake)
