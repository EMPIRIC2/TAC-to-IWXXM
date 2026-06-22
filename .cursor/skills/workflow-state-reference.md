# Workflow state reference

**Single source of truth:** repo-root [`workflow-state.yaml`](../../workflow-state.yaml).

Every pipeline skill (00–19), orchestrator ([pipeline](pipeline/SKILL.md)), auxiliary skills
(build-executor, gather-context, doc-planner, etc.), and
[workflow-state-manager](../agents/workflow-state-manager.md) use this file.

**Only workflow-state-manager may write `workflow-state.yaml`.** Other skills invoke the agent
for `read_context` and `update` operations — see
[workflow-state-agent-protocol.md](workflow-state-agent-protocol.md).

Stage conventions: [pipeline-preamble.md](pipeline-preamble.md). Orchestration policy:
[considerations.md](considerations.md) §11.

**Connectivity:** All stages 00–15 apply [connectivity-gates.md](connectivity-gates.md); record
connectivity artifacts in `artifacts[]` when produced (`test_cors_policy.py`, `verify_connectivity.sh`, etc.).

## Path and lifecycle

| Rule | Requirement |
|------|-------------|
| **Location** | `<repo-root>/workflow-state.yaml` only — never under `docs/` or `.cursor/` |
| **Create** | [pipeline](pipeline/SKILL.md) or first stage skill on greenfield start |
| **Read** | First action on every skill invocation |
| **Write** | Immediately after each substep completes or fails — never buffer |
| **Resume** | Stage `status` + timestamps determine resume position |

## Top-level schema

```yaml
overall_status: pending | in_progress | completed | failed
project:
  name: string
  description: string
  output_directory: docs/   # default
  stages: {}     # historical baseline — last completed per stage (dual-layer)

session_counter: 0          # increment when allocating S{NNN}-{slug}
active_session: null        # see §Sessions — null when no session in flight
sessions: []                # archived completed sessions — see §Sessions

stages:          # keyed by skill id — see mapping table (legacy mirror; prefer project.stages)
template:        # set in 00-context or 01-requirements
applications: [] # deployed service deployables (when applicable)
agents:          # subagent status (00-context)
phase1b_ecosystem: {}
constraints: {}  # cost, sovereignty, privacy
deployment: {}   # local build + staging URLs + health tiers — see §Deployment
issue_log: []
decisions_log: []
artifacts: []    # paths produced; append on completion; optional session_id
evolve_cycles: []      # 16-evolve — must include session_id — see 16-evolve/reference.md
retrospective_cycles: [] # 17-retrospective — see 17-retrospective/reference.md
pr_review_cycles: []    # 18-pr-review — see 18-pr-review/reference.md
pr_remediation_cycles: []  # 19-address-pr-review — see 19-address-pr-review/reference.md

git_history:     # commit and branch tracking — see §Git history
  current_branch: string
  branches: []   # active branches with purpose and base
  commits: []    # recent commit log (append-only); optional session_id
```

## Sessions

Session-first work model: [sessions-reference.md](sessions-reference.md).

### `active_session` schema

Set by **00-context** after user approves `routing-plan.md`. Cleared when session closes.

```yaml
active_session:
  id: S042-live-e2e
  type: integration          # greenfield | feature | new_service | hotfix | integration | ops | process
  intent: "Run live E2E against staging"
  status: in_progress        # in_progress | closing | completed
  branch: feat/S042-live-e2e
  orchestrator: null         # pipeline | 16-evolve | 14-hotfix | null
  evolve_cycle_id: null      # when type feature/new_service and 16-evolve active
  artifacts_dir: docs/sessions/S042-live-e2e/
  routing_plan:
    - stage: 00-context
      mode: scoped
      required: true
      status: completed
      skip_rationale: null
    - stage: 10-e2e
      required: true
      status: in_progress
      skip_rationale: null
  current_stage: 10-e2e
  started_at: "2026-06-22"
  context_briefs: []         # paths under docs/context/
```

### `sessions[]` archive entry

```yaml
sessions:
  - id: S041-export-api
    type: feature
    intent: "Add batch export API"
    status: completed
    branch: evolve/S041-export-api
    orchestrator: 16-evolve
    evolve_cycle_id: EV-001
    routing_plan: [...]
    artifacts_dir: docs/sessions/S041-export-api/
    started_at: "2026-06-20"
    completed_at: "2026-06-21"
    pr_url: null
```

### Rules

| Rule | Detail |
|------|--------|
| **ID allocation** | Increment `session_counter`; format `S{NNN:03d}-{slug}` |
| **Sole opener** | **00-context** creates `active_session` (or orchestrator after 00) |
| **Block without session** | Stages 01–19 block if `active_session` null (unless user waives via agent) |
| **Reports** | Session stage outputs under `artifacts_dir/reports/` |
| **Dual layer** | `project.stages.*` = historical; `active_session` = current work unit |
| **Evolve link** | `evolve_cycles[].session_id` must match `active_session.id` when both exist |
| **Close** | All routing-plan stages done + checkpoint AskQuestion → archive → `active_session: null` |

### Session counter seed

On first session in an existing repo, set `session_counter` to `max(len(sessions[]), evolve_cycles count) + 1`
or start at `1` if none exist.

## Deployment

Shared record of local build status and staging deployment state. Written by **13-deploy-smoke**,
consumed by **11-verify-impl**, **15-service-health**, and any future skill that needs the
deployed URL or tier status without re-discovering it.

```yaml
deployment:
  local_build:
    status: green | red | pending     # T0 e2e suite pass/fail
    last_verified: "YYYY-MM-DD"
    commit: <short sha>               # HEAD when T0 was last run
    branch: main
    command: "uv run pytest tests/e2e/ -m 'e2e and not live' -v"
    t0_result: pass | fail
    t0_journeys_passed: <int>
  staging:
    status: deployed | pending | failed | rolled_back
    last_verified: "YYYY-MM-DD"
    commit_deployed: <short sha>      # what is actually live
    commit_head: <short sha>          # repo HEAD at last check
    drift: true | false               # commit_deployed != commit_head
    urls:
      chat_rag_backend: <url> | null
      internal_write_api: <url> | null
      chat_rag_frontend: <url> | null
      admin_frontend: <url> | null
      modal_data_management: <url> | null
    health_tiers:
      h0ci_github_main: pass | fail | pending   # latest .github/workflows/ci.yml on main (15-service-health)
      h1_liveness: pass | fail | pending
      h2_db_ready: pass | fail | pending
      h3_rag_smoke: pass | fail | pending
      h4_cors_preflight: pass | fail | pending
      h5_frontend_bundle: pass | fail | pending
      h6_browser_uj: pass | fail | pending | waived_v1
    notes: []                          # advisory strings
  url_discovery:
    method: "uv run --with pydo --with pyyaml scripts/deploy/do_apps.py urls --frontend"
    modal_admin_manual: true           # Modal admin URL must be set manually
```

### Rules

| Rule | Detail |
|------|--------|
| **Writer** | 13-deploy-smoke is the primary writer; 15-service-health updates `health_tiers` after re-checks |
| **Reader** | 11-verify-impl and 15-service-health read on invocation to avoid re-discovery |
| **Null URLs** | If a URL is `null` and the tier needs it, run `url_discovery.method` first |
| **Drift** | Set `drift: true` when `commit_deployed` != `commit_head`; recommend H1–H3 revalidation |
| **Tier updates** | After any H-tier check, update the corresponding field immediately |
| **Notes** | Append advisory strings (cold-start, waivers, blockers) — append-only, prune on deploy |

## Git history

Skills that produce code, docs, tests, infra, or config changes **must commit as they go**
and record the commit in `workflow-state.yaml` §`git_history`. This is the persistent
record that survives session boundaries.

### Branch naming

| Change type | Branch pattern | Base |
|-------------|----------------|------|
| Feature / milestone task | `feat/{slug}` | `main` or phase branch |
| Bug fix (hotfix) | `fix/{slug}` | `main` |
| Docs-only change | `docs/{slug}` | `main` |
| Skill / tooling change | `chore/{slug}` | `main` |
| Connectivity / infra | `infra/{slug}` | `main` |
| Evolve cycle | `evolve/{cycle-id}-{slug}` | `main` |

Slug should be short and descriptive (e.g. `feat/cors-middleware`, `fix/vllm-shutdown`,
`docs/staging-runbook`).

### Commit protocol (commit-as-you-go)

Every skill that writes files **must** commit before:

1. **Transitioning to the next stage** — uncommitted work is lost if the session ends
2. **Asking the user a blocking question** — commits preserve progress
3. **Running a gate check** — gates operate on committed state
4. **Ending a turn** — always commit before returning control

Steps per commit:

1. Verify the working tree is on the correct branch (create if needed)
2. `git add` only files related to the current logical unit
3. Commit with the message format from `atomic-commits.mdc`
4. Append to `workflow-state.yaml` §`git_history.commits`
5. Verify clean state (`git status`)

### `git_history` schema

```yaml
git_history:
  current_branch: feat/connectivity-gates
  branches:
    - name: feat/connectivity-gates
      purpose: "H0c/H4/H5 connectivity gates across skills"
      base: main
      status: open          # open | merged | closed
      created_at: "2026-05-20"
      pr_url: null           # set when PR is created
    - name: fix/vllm-shutdown
      purpose: "vLLM fp16 kwargs + NCCL shutdown warnings"
      base: main
      status: merged
      created_at: "2026-05-20"
      merged_at: "2026-05-20"
  commits:
    - sha: abc1234
      branch: feat/connectivity-gates
      message: "feat: add connectivity gates (H0c/H0i/H4/H5) across skills 00-15"
      stage: "14-hotfix"      # which pipeline stage produced this
      files_changed: 31
      timestamp: "2026-05-20T19:00:00Z"
    - sha: def5678
      branch: feat/connectivity-gates
      message: "feat: CORS middleware + H0c/H4/H5 tests"
      stage: "14-hotfix"
      files_changed: 12
      timestamp: "2026-05-20T19:05:00Z"
```

### Rules

| Rule | Detail |
|------|--------|
| **Append-only** | Never remove commits from the log; branches move to `merged`/`closed` |
| **Stage attribution** | Every commit records which pipeline stage produced it |
| **Branch lifecycle** | Create → work → PR → merge → record `merged_at` |
| **Session boundary** | On session end, `current_branch` reflects actual `git branch --show-current` |
| **Resume** | On session start, read `git_history` to know which branches exist and their purpose |

### Which skills commit

| Skill | Commits? | Branch type |
|-------|----------|-------------|
| 00-context through 03-plan-tooling | Yes (docs, rules, hooks) | `docs/*` or `chore/*` |
| 04-tech-plan through 06-tech-tooling | Yes (execution plan, tooling) | `docs/*` or `chore/*` |
| 07-build / build-executor | Yes (code, tests, specs) | `feat/M{N}-*` per milestone |
| 08-verify-build | Amend or new commit (auto-fixes) | Same branch as 07-build |
| 09-qa | Yes (report) | `docs/sessions/{id}/reports/qa-report.md` |
| 10-e2e | Yes (tests, report) | `docs/sessions/{id}/reports/e2e-report.md` |
| 11-verify-impl | Yes (patches, report) | `docs/sessions/{id}/reports/verify-impl.md` |
| 12-verify-deploy | Yes (checklist) | `docs/sessions/{id}/reports/deploy-checklist.md` |
| 13-deploy-smoke | Yes (deploy state, report) | `docs/sessions/{id}/reports/deploy-smoke.md` |
| 14-hotfix | Yes (fix + test) | `fix/*` |
| 15-service-health | Yes (reports) | `docs/health-*` or `fix/*` if code changes |
| 16-evolve | Yes (delta specs + code) | `evolve/*` |
| 17-retrospective | Yes (skill patches) | `chore/retro-*` |

## Stage status values

`pending` | `in_progress` | `completed` | `failed` | `skipped` | `pass_with_advisories`

Use `started_at` / `completed_at` (ISO date `YYYY-MM-DD`) when transitioning.

## Skill → `stages.*` mapping

| Skill directory | `workflow-state.yaml` key | Detail file (sync, not substitute) |
|-----------------|---------------------------|-------------------------------------|
| `00-context` | `stages.00-context` | — |
| `gather-context` | `stages.gather-context` | `docs/research-brief.md` |
| `01-requirements` | `stages.01-requirements` | — |
| `doc-planner` | `stages.doc-planner` | manifest in stage block |
| `02-verify-plan` | `stages.02-verify-plan` | — |
| `audit-docs` | `stages.audit-docs` | `docs/audit-state.md` (mirror counts) |
| `03-plan-tooling` | `stages.03-plan-tooling` | — |
| `04-tech-plan` | `stages.04-tech-plan` | — |
| `build-planner` | `stages.build-planner` | seeds `workflow-state.yaml + execution plan artifact` |
| `05-verify-tech` | `stages.05-verify-tech` | — |
| `06-tech-tooling` | `stages.06-tech-tooling` | — |
| `07-build` / `build-executor` | `stages.07-build` | `workflow-state.yaml + execution plan artifact` §Current State |
| `08-verify-build` / `verify-build` | `stages.08-verify-build` | `docs/sessions/{id}/reports/verification-report.md` |
| `data-management` | `stages.data-management` | `docs/data-management-state.md` |
| `09-qa` | `stages.09-qa` | `docs/sessions/{id}/reports/qa-report.md` |
| `10-e2e` | `stages.10-e2e` | `docs/sessions/{id}/reports/e2e-report.md` |
| `11-verify-impl` | `stages.11-verify-impl` | — |
| `12-verify-deploy` | `stages.12-verify-deploy` | `docs/sessions/{id}/reports/deploy-checklist.md` |
| `13-deploy-smoke` / `deploy-verify` | `stages.13-deploy-smoke` | `docs/deploy-state.md` |
| `14-hotfix` | `stages.14-hotfix` | `docs/bug-reports/BUG-*.md` |
| `bug-investigation` | (via `14-hotfix` or `issue_log`) | repro test in `tests/bugs/` |
| `15-service-health` | `stages.15-service-health` | `docs/service-health-state.md` |
| `16-evolve` | `evolve_cycles[]` | per `16-evolve/reference.md` |
| `17-retrospective` | `retrospective_cycles[]` | per `17-retrospective/reference.md` |
| `18-pr-review` | `pr_review_cycles[]` | per `18-pr-review/reference.md` |
| `19-address-pr-review` | `pr_remediation_cycles[]` | per `19-address-pr-review/reference.md` |
| `audit-licenses` | `stages.audit-licenses` | flags in `docs/` or stage `report` |
| `clone-repos` | `stages.clone-repos` | — |
| `config-validator` | `stages.config-validator` | advisory; often nested under 03 |

**Aliases:** `build-executor` and `07-build` share `stages.07-build`. `verify-build` and
`08-verify-build` share `stages.08-verify-build`. `deploy-verify` updates `stages.13-deploy-smoke`.

## Standard skill block (copy pattern)

See [workflow-state-agent-protocol.md](workflow-state-agent-protocol.md) for the mandatory
read/update protocol. Stage-specific **detail file** sync rules belong in each SKILL.md.

```markdown
## State management

**Agent protocol:** [workflow-state-agent-protocol.md](../workflow-state-agent-protocol.md).
**Stage key:** `stages.{key}`.

### Detail tracker (this stage)
{path and sync rules — e.g. execution-plan.md §Current State}
```

## Issue and decision logs

**`issue_log`** — cross-stage blockers, contradictions, template drift. Fields: `id`, `category`,
`summary`, `status`, optional `resolution`, `blocking_for`, `evolve_cycle_id`.

**`decisions_log`** — shorthand pointers (e.g. `R1: … — ADR-00N`). Full text lives in ADRs and
`docs/requirements-decisions.md` / `docs/tech-decisions.md`.

## Template block

Set in `00-context` or `01-requirements`. Consumed by stages that check layout/deploy:

- `template.id` — e.g. `api+worker` (deployed service)
- `template.deploy`, `template.service_name`, `template.database`, etc.

See [template-registry.md](template-registry.md).

## Initializing a new project

When `workflow-state.yaml` is missing, create from this minimal scaffold (adjust `project`):

```yaml
overall_status: in_progress
project:
  name: <ProjectName>
  description: <one line>
  output_directory: docs/
  stages: {}
session_counter: 0
active_session: null
sessions: []
stages:
  00-context: { status: pending }
  01-requirements: { status: pending }
  # … 02 through 17-retrospective — all pending
  gather-context: { status: pending }
  doc-planner: { status: pending }
  audit-docs: { status: pending }
  build-planner: { status: pending }
  data-management: { status: pending }
  audit-licenses: { status: pending }
  clone-repos: { status: pending }
  config-validator: { status: pending }
agents:
  repo_researcher: { status: pending }
  paper_analyst: { status: pending }
issue_log: []
decisions_log: []
artifacts: []
evolve_cycles: []
retrospective_cycles: []
```

[pipeline/SKILL.md](pipeline/SKILL.md) fills stages as the run progresses.

## Deprecated parallel state (migrate to YAML)

| Legacy file | Replace with |
|-------------|----------------|
| `docs/gather-context-state.md` | `stages.gather-context` |
| `docs/audit-state.md` | `stages.audit-docs` (+ keep file as detail mirror if useful) |

Detail files (`execution-plan.md`, `deploy-state.md`, `data-management-state.md`) remain for
granular substeps but **must not** be the only record of stage completion.
