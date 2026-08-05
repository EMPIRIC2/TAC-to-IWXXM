---
session_id: S044-local-precommit-long-jobs
type: feature
status: in_progress
branch: evolve/EV-036-local-precommit-long-jobs
started_at: 2026-08-05
intent: "Offload local-capable long-running jobs onto local pre-commit to save CI runner time"
orchestrator: 16-evolve
evolve_cycle_id: EV-036
prior_session: S043-rule-source-traceability
context_briefs:
  - docs/context/local-precommit-long-jobs.md
standing_docs_touched:
  - docs/feature-list.md
  - docs/test-plan.md
  - docs/dependency-inventory.md
  - docs/ops/DEVELOPMENT.md
  - docs/decisions/evolve-decisions.md
  - .pre-commit-config.yaml
  - .husky/
  - Makefile
  - .github/workflows/ci-cd.yml
feature_ids: []
deepen_feature_ids:
  - M5
feature_note: "Deepen M5 workspace tooling (pre-commit / CI gate placement) — no product Fn; no UI"
route_status: approved_lean
current_stage: 07-build
status_note: "02 COMPLETE (D-S044-02-gate-a); 07 T1–T5 impl done pending commit → 08"
---

# Session S044 — local-precommit-long-jobs

## Intent

Move **local-capable long-running** quality jobs onto **local pre-commit** so developers
pay the cost before push, **saving CI runner time**. Combines “reverse EV-002” direction
(long suites on pre-commit) with consolidating work that today lives on husky **pre-push**.

## Phase 0 (locked)

| ID | Decision |
|----|----------|
| Q1 | Open **S044** → **EV-036** |
| Q2 | **4+1** — local-capable long jobs on developer hooks to save CI minutes |
| Q3 | **N/A tooling only** — no product UI / no deploy surface |
| B1 | **3** — fast+medium on **commit**; full `ci-prepush` on **push** |
| B2 | **1** — slim remote CI — **amended by Gate A** (`D-S044-02-gate-a`): keep units+coverage+PR comment; drop validate+Compose only |
| B3 | **1** — job set = `validate-ci` + `ci-prepush` only |
| B4 | **1** — deepen **M5**; **Lean** routing |
| Gate A | **PASS** — contradiction `1,1,1,1` then Gate A `1,1,1,1` amended (S02.M2 modified) |

### Why “frontend” came up (Q3)

Not product UI. Local gates already include **`test-unit-frontend`** (Vitest) and
**`audit-frontend`** (npm audit) inside `make ci-prepush` / `make validate-ci`. Those are
tooling jobs, not workbench UX. This cycle does **not** change React surfaces.

## Resource model (Gate A amend)

| Tier | When | Jobs |
|------|------|------|
| Fast + medium | `git commit` | existing fast pre-commit + `validate-ci-medium` (de-duped) |
| Long local | `git push` | `make ci` = `ci-prepush` + Compose integration |
| Remote | GitHub Actions | no validate / no Compose; **keep** units + coverage + PR comment; native / e2e-smoke / alembic / deploy |

Corpus: `[Corpus: tech-spec]` · `[Corpus: tests]` · `[Corpus: product]` M5 · ops `docs/ops/DEVELOPMENT.md`

## Scope

### In

- pre-commit: medium `validate-ci` / `validate-ci-medium`
- pre-push: `make ci` (units + Compose)
- `ci-cd.yml`: drop validate + Compose; **keep** unit matrix + coverage + PR coverage comment; rewire deploy `needs`
- Docs + TC-EV036-001..003

### Out

- Product Fn / browser UI / deploy runtime product changes
- Family quality packs / Playwright on every local push
- Non-local jobs (GHCR publish path, live prod E2E)

## Progress

| Stage | Status |
|-------|--------|
| 02-verify-plan | **completed** — `D-S044-02-gate-a` |
| 07-build | **in_progress** — T1–T5 implementation complete; **commit pending** → 08-verify-build |

## Branch

`evolve/EV-036-local-precommit-long-jobs`
