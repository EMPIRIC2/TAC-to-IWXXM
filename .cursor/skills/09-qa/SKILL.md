---
name: 09-qa
description: >
  Post-build quality assurance. Runs full lint, format, typecheck, security, dependency,
  data-staging, Modal workspace, and cross-file checks on the entire codebase. Writes
  docs/qa-report.md with blocking vs advisory findings. Runs in parallel with 10-e2e;
  results consumed by 11-verify-impl. Advisory remediation is a separate user-requested
  pass (spawn parallel agents) — not part of the default 09 run.
---

# 09 — QA Checks

Final quality assurance pass on the **complete** codebase after the build is done.

**Preamble:** [pipeline-preamble.md](../pipeline-preamble.md) — shared conventions for stages 00–17.
**Cross-cutting:** [considerations.md](../considerations.md), [connectivity-gates.md](../connectivity-gates.md).
**State agent:** [workflow-state-manager](../../agents/workflow-state-manager.md) — mandatory read/update.

## Connectivity (stage 09)

Full-repo QA must report connectivity status in `docs/qa-report.md`:

- **Blocking:** H0c (`test_cors_policy.py`) and H0i (`tests/integration`) in Python test agent
- **Staging:** H4–H5 when `METAR_STAGING_*_FRONTEND_URL` set; else advisory with QA-ID pointing to connectivity-gates

Do not mark QA PASS if H0c fails. See connectivity-gates §Stage 09.

## When to Use

- **After 07-build completes** (or when execution plan shows build substantially done):
  the "final exam" for anything that slipped past milestone **08-verify-build**
- Runs **in parallel** with **10-e2e** when both are scheduled
- Results collected by **11-verify-impl** for user sign-off

## Difference from 08-verify-build

| Aspect | 08-verify-build | 09-qa |
|--------|-----------------|-------|
| When | During build, at milestones | After build completes |
| Scope | Changed files / milestone | Entire codebase |
| Auto-correct | Yes (lint/format) | **Report only** — no fixes |
| Blocking | Non-blocking for auto-fix | Async — summary for 11 |
| Extra checks | No | Cross-file, data staging, Modal workspace, frontends |
| Output | `docs/verification-report.md` (optional) | **`docs/qa-report.md`** (required) |

## Prerequisites

1. **Build gate**: Execution plan tasks for the active phase are `completed` (or user
   explicitly requests QA mid-build — note partial scope in the report).
2. **`workflow-state.yaml + execution plan artifact`** §Tech Stack Summary — tool commands.
3. **`workflow-state.yaml`** §`template` — conformance checks (deployed service: `api+worker`).
4. Baseline expectation: **08-verify-build** recently **PASS** (re-run full checks anyway;
   do not assume).

## State management

**Agent protocol:** [workflow-state-agent-protocol.md](../workflow-state-agent-protocol.md).
**Stage key:** `stages.09-qa`.

Invoke **workflow-state-manager** `read_context` before any other action; `update` after each
substep. **Do not** edit `workflow-state.yaml` directly.


Update §`stages.09-qa`:

```yaml
09-qa:
  status: completed
  started_at: "<ISO date>"
  completed_at: "<ISO date>"
  report: docs/qa-report.md
  overall: pass | fail | pass_with_advisories
```

Append `docs/qa-report.md` to §`artifacts` when created.

---

## Delta / feature-addition mode

- Scope QA report to **affected Fn**, apps, and journeys in the active evolve cycle.
- Do not re-audit entire codebase unless user requests full 09 pass.

## Workflow

### Phase 1 — Configuration

Read from disk (do not guess commands):

| Source | Use for |
|--------|---------|
| `workflow-state.yaml + execution plan artifact` §Tech Stack Summary | ruff, basedpyright, pytest, pip-audit, vitest |
| `docs/typing-policy.md` | No `Any`/`any` (ADR-018) |
| `.github/workflows/ci.yml` | CI parity (exact paths, ignore files, frontend matrix) |
| `docs/data-staging-state.md` | D1–D7 asset status |
| `workflow-state.yaml` §`template` | Layout / Modal / deploy pattern |
| `infra/modal/README.md` | Modal app names, workspace, volumes |

**deployed service default commands** (repo root, `uv sync --group dev`):

```bash
uv run ruff check src tests
uv run ruff format --check src tests
uv run basedpyright src tests
uv run pytest tests/unit tests/integration tests/privacy tests/e2e tests/smoke tests/eval
uv run pip-audit  # with audit/pip-audit-ignore.txt if present
bash scripts/check_secrets.sh
bash scripts/check_modal_no_database_url.sh
bash scripts/check_openapi_specs.sh
```

**Frontends** (each app dir):

```bash
cd apps/frontend && npm ci && npm run lint && npm test -- --run
cd apps/frontend && npm ci && npm run lint && npm test -- --run
```

---

### Phase 2 — Run QA Checks

Prefer **one message with parallel shell/tool work** (or Task subagents) for independent
checks. Do not block the whole QA on optional live Modal/staging unless env vars are set.

#### Agent 1 — Linter (full codebase)

- `uv run ruff check src tests`
- Optional: `uv run ruff check --select F401,F841` for unused imports/vars
- Return: total issues by rule; **PASS** if zero

#### Agent 2 — Formatter

- `uv run ruff format --check src tests`
- Return: count of files needing format; **PASS** if zero

#### Agent 3 — Typechecker

- `uv run basedpyright src tests`
- Return: error/warning count; **PASS** if zero errors

#### Agent 4 — Test suite (Python + frontend)

**Python:** same pytest paths as CI (see Phase 1).

**Frontend:** Vitest + ESLint per app in CI matrix.

Return:

- Python: passed / failed / skipped (list skipped reasons if env-gated)
- Frontend: per-app pass/fail
- Note non-blocking warnings (e.g. Pydantic `validate_default` from dependencies)

**PASS** if zero failures (skips are OK when documented).

#### Agent 5 — Security

Run **three layers**; classify each finding as **blocking** or **advisory**:

| Layer | Command / tool | Blocking when |
|-------|----------------|---------------|
| **CVEs** | `uv run pip-audit` (+ ignore file) | High/critical on PyPI-resolved deps |
| **Current tree secrets** | `bash scripts/check_secrets.sh` | Any match in `apps/`, `packages/`, `tests/`, `infra/`, `openapi/` |
| **Working-tree gitleaks** | `gitleaks detect --no-git --config .gitleaks.toml` | Any leak in current files (if gitleaks installed) |
| **Dangerous patterns** | ripgrep `pickle.loads`, `eval(`, `exec(` in `apps/` + `packages/` | Any match in app code |

**Git history (advisory only):**

- `gitleaks detect` on full history may report dozens of hits in **deleted** legacy paths.
- **Split results:** count hits in **current working tree** vs **history-only**.
- **Do not** recommend `git filter-repo` unless user asks or real live credentials were committed.
- Document resolution in report → point to `docs/security/gitleaks-resolution.md` if it exists.

**Expected non-blocking:** workspace packages `deployed-service-*` skipped by pip-audit (not on PyPI).

#### Agent 6 — Cross-file analysis

| Check | How | Severity |
|-------|-----|----------|
| Unused imports | Ruff F401/F841 | Blocking if >0 |
| Circular deps | Workspace package import graph (`apps/*`, `packages/*`) | Blocking if cycles |
| Dead code | Optional (`vulture`); if not run, note SKIPPED | Advisory |
| Public docstrings | AST scan: public defs/classes without docstring in `apps/`, `packages/` | **Advisory** (style) |
| Naming | Project rules / ruff N rules if enabled | Advisory |

#### Agent 7 — Dependency health

- `pip list --outdated` — flag pinned stacks per `docs/dependency-inventory.md`
- Heuristic import vs `pyproject.toml` per workspace member — ignore `__future__`, workspace packages
- Return: outdated count (advisory if pins intentional), missing (blocking if real)

#### Agent 8 — Template & platform conformance (deployed service `api+worker`)

Read [template-registry.md](../template-registry.md) and verify:

| Criterion | deployed service expectation |
|-----------|---------------------|
| Layout | `apps/*`, `packages/*`, `tests/`, `openapi/`, `infra/` |
| Modal isolation | `import modal` only under `infra/modal/` |
| Modal workspace | Deploy scripts use **`deployed-service`** profile (see `scripts/modal_ensure_workspace.sh`) |
| Deploy URLs | `https://deployed-service--deployed-service-*` — **not** `fontface--` or other workspace prefixes |
| DO backends | No `DATABASE_URL` in Modal worker paths (`scripts/check_modal_no_database_url.sh`) |
| OpenAPI | `openapi/*.yaml` present and parse (`scripts/check_openapi_specs.sh`) |
| CI | `.github/workflows/ci.yml` matches Phase 1 commands |

**Modal live checks (advisory unless env set):**

- If `METAR_MODAL_EMBED_URL` / `METAR_MODAL_LLM_URL` set: `GET /health`, embed dim 384
- Else: read `docs/data-staging-state.md` for D6/D7 status

#### Agent 9 — Data staging & deploy readiness (deployed service)

Read `docs/data-staging-state.md` and `workflow-state.yaml + execution plan artifact` Phase 4 gate:

| Asset / gate | Report |
|--------------|--------|
| D1–D5 fixtures/migrations | Must be `verified` for full data QA **PASS** |
| D6–D7 external data assets | `verified` \| `staged_procedure` \| `pending` |
| Phase 4 H1–H3 live | **Advisory** if `METAR_STAGING_CHAT_URL` unset — point to `docs/deploy.md §Runbook`, `scripts/deploy/staging_smoke.sh` |
| H0c CORS / connectivity | **Blocking:** `pytest tests/unit/test_cors_policy.py` must pass in CI |
| H4–H5 live | **Advisory** if staging frontend URLs unset — `scripts/deploy/verify_connectivity.sh`, [connectivity-gates.md](../connectivity-gates.md) |
| Modal secret `deployed-service-data-management` | Note if `data_management_app` deploy requires it |

---

### Phase 3 — Compile results

**Overall status:**

- **PASS** — all blocking checks green; advisories may remain
- **FAIL** — any blocking check failed
- **pass_with_advisories** — use in `workflow-state.yaml` when blocking PASS but advisories need 11-verify-impl review

Short summary block (always include in report header):

```text
QA Results:
  Lint:           [PASS/FAIL] — [N] issues
  Format:         [PASS/FAIL] — [N] files
  Typecheck:      [PASS/FAIL] — [N] errors
  Tests (Python): [PASS/FAIL] — [N] passed, [N] skipped, [N] failed
  Tests (FE):     [PASS/FAIL] — [N] passed per app
  Security:       [PASS/FAIL] — [N] CVEs; [N] secrets (tree); [N] history (advisory)
  Cross-file:     [N] unused imports; [N] cycles; [N] docstrings missing (advisory)
  Dependencies:   [N] outdated (advisory); [N] missing
  Template:       [PASS/FAIL]
  Data / Modal:   D6 [status]; D7 [status]; workspace [deployed-service|WRONG]
```

Assign **QA-00N** IDs to advisories in §Findings for 11-verify-impl (see `docs/qa-report.md` examples).

---

### Phase 4 — Write report

Write **`docs/qa-report.md`** with:

1. Executive summary table (blocking vs advisory)
2. Commands run (copy-paste reproducible)
3. Per-check details (verbatim tool output for failures)
4. **Findings for 11-verify-impl** table (ID, severity, finding, suggested action)
5. Data integrity / Modal workspace subsection when relevant
6. Phase / execution-plan alignment (deferred gates called out explicitly)

**Do not** auto-fix code, rewrite git history, or deploy to Modal in the default 09 run.

---

## Advisory remediation (separate invocation)

09-qa is **assessment only**. When the user asks to **address advisories** after a QA
report, use a **follow-up pass** (not a re-run of 09):

1. Read `docs/qa-report.md` §Findings.
2. Spawn **parallel Task agents** (one concern per agent), e.g.:
   - **D6/D7** — `scripts/stage_modal_weights.sh`, `scripts/modal_ensure_workspace.sh`, update `docs/data-staging-state.md`; enforce **deployed-service** Modal profile; stop mistaken deploys on other workspaces via `scripts/teardown_fontface_deployed-service.sh`
   - **Secrets history** — `.gitleaks.toml`, `scripts/check_secrets.sh`, CI `--no-git`, `docs/security/gitleaks-resolution.md` (no history rewrite unless user requests)
   - **Docstrings** — public symbols in `apps/` + `packages/`; verify ruff/basedpyright (no `Any`)
   - **Phase 4 staging** — H2 in `staging_smoke.sh`, `docs/deploy.md §Runbook`, skip-safe `tests/smoke/test_staging_health.py`
3. Re-run **blocking** checks only for touched areas; update `docs/qa-report.md` or add a short **QA remediation** note with date.
4. **Modal workspace rule:** all deployed service deploys → profile **`deployed-service`**; URLs must use `deployed-service--` prefix; document in `infra/modal/env.example`.

Do not bundle unrelated fixes into one agent.

---

## Output rules

1. **Report only** in the default 09 run — no auto-fix, no commits unless user asks.
2. **Full codebase scope** — not just diff since last milestone.
3. **Distinguish blocking vs advisory** — especially security (tree vs history) and data staging.
4. **No AskQuestion** in 09 — surface choices in `docs/qa-report.md` for **11-verify-impl**.
5. **Async-safe** — report is self-contained; include exact commands and env prerequisites.
6. **CI parity** — if local PASS but CI differs, note branch/workflow mismatch as advisory.

---

## Common deployed service advisories (reference)

Use as checklist when writing findings; not all apply every run.

| ID pattern | Typical finding | Typical remediation (user-requested) |
|------------|-----------------|--------------------------------------|
| QA-003 | D6/D7 pending on Modal volumes | `stage_modal_weights.sh`; verify embed 384-dim; deployed-service workspace |
| QA-004 | Outdated transitive deps | ADR + pip-audit after intentional bump |
| QA-005 | gitleaks hits in git history only | `.gitleaks.toml` + CI `--no-git`; no filter-repo |
| QA-002 | Public symbols without docstrings | Doc pass in `apps/` + `packages/` |
| QA-006 | Phase 4 H1–H3 deferred (no staging URLs) | `staging-runbook.md`, env-gated smoke tests |
| QA-007 | Modal apps on wrong workspace (`fontface--`) | `modal_ensure_workspace.sh`, teardown script, redeploy |

---

## Handoff to 11-verify-impl

11-verify-impl should:

- Walk user through **blocking FAIL** items first
- Present **advisories** with approve / defer / fix-now (fix-now → advisory remediation pass above)
- Cross-check `docs/qa-report.md` against `docs/feature-list.md` and acceptance criteria
- Not re-run full 09 unless codebase changed materially since report date
