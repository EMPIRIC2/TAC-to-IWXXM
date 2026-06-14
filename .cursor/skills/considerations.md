# Cross-cutting considerations (`.cursor/skills`)

**Numbered stages (00–17):** Shared structure, gates, state (via
[workflow-state-manager](../agents/workflow-state-manager.md)), and AskQuestion rules are in
[pipeline-preamble.md](pipeline-preamble.md). This file holds policy detail referenced from
the preamble and from each stage skill.

Use this file from any skill here so behavior stays aligned without copying long prose into every `SKILL.md`.

## 1. Root cause: spec vs code vs infra

Before choosing a fix path, classify the failure:

| Kind | Signals | Typical remediation |
|------|---------|---------------------|
| **Spec / docs wrong** | Acceptance criteria, test plan, or deployment plan contradict requirements or reality; validation "fails" but implementation matches code + spec mismatch | Correct the specific spec section, then re-run only the affected check. **Do not re-run entire phases.** |
| **Code wrong** | Implementation diverges from audited spec; unit/integration failures with clear spec reference | Targeted code fix in the build branch. |
| **Infra / ops** | Secrets, image build, platform quotas, network; deploy succeeds but runtime misconfigured | Deploy-verify / platform fixes. |
| **Tooling gap** | Hook or rule fails to catch an issue it should have caught | Patch the specific hook or rule. |

Individual skills handle local failures; **cross-stage issues** (e.g., deploy exposes a spec error) need explicit handoff (workflow-state.yaml issue_log, execution-plan notes).

### Fix in place (D10)

The pipeline uses **fix in place** — targeted patches rather than re-running entire phases:
- Code bugs: patch the code, re-run affected test
- Spec mismatches: patch the spec section surgically
- Missing features: add task to execution plan, implement
- Tooling gaps: patch the hook or rule
- Never reset phase status or re-run upstream stages unless the user explicitly requests it
- Post-deployment fixes use [14-hotfix](14-hotfix/SKILL.md) — same fix-in-place principle, dedicated triage + branch workflow
- Production investigation (deploy drift, API/DB health, ingest backlog) uses [15-service-health](15-service-health/SKILL.md) — report first; code fixes still go through 14-hotfix
- **Every caught failure** uses [bug-investigation](bug-investigation/SKILL.md): one `docs/bug-reports/BUG-*.md` (logs + persistent investigation), one `tests/bugs/test_bug_*.py` (red → green), one fix; interactive gates via AskQuestion only

### Implementation throughput

**07-build** should complete as many tasks and milestones as practical in **one agent invocation**: open PRs when milestones/phases complete, but do not treat each PR as the end of the session unless the user asked for that cadence.

## 2. Feedback loop (non-linear remediation)

The default pipeline is **linear**, but **recovery** is allowed when validation shows something was wrong.

1. **Record**: Append to `workflow-state.yaml` issue_log with category, evidence, and affected artifacts.
2. **Classify**: Is this a code, spec, infra, or tooling issue? (see §1)
3. **Fix in place**: Apply the targeted patch. Do not re-run entire phases.
4. **Re-verify**: Re-run only the affected check, not the full verification suite.
5. **Staleness**: After spec edits, check if downstream artifacts consumed the old version. If yes, warn the user but do not automatically re-run.

## 3. Release notes and changelog

Atomic commits and PRs use structured messages, but **nothing automatically becomes** user-facing **release notes**.

**Convention** (when cutting a release or completing 13-deploy-smoke):
- Append a release section to `docs/deploy-report.md` or maintain `docs/CHANGELOG.md`
- Aggregate merge commits and PR titles since the last deploy tag
- Include: version/date, deployment URL, merged milestones, notable decisions

## 4. Performance testing

| Stage | Responsibility |
|-------|----------------|
| **01-requirements / 04-tech-plan** | Ensure specs cover query latency, ingest throughput, embedding/LLM cost, and DB sizing where requirements imply them. Stack choices per [deployment-catalog.md](deployment-catalog.md). If unknown, surface `[Ambiguity]`. |
| **08-verify-build** | When test-plan.md defines perf commands/thresholds, run them. |
| **09-qa** | Report perf-related findings in QA report. |
| **13-deploy-smoke** | Post-deploy smoke: H1–H3 **plus** H4–H5 browser connectivity per [connectivity-gates.md](connectivity-gates.md). |

If perf requirements are unknown, surface `[Ambiguity]` during planning — do not invent SLOs.

## 5. Security considerations

Every skill that touches dependencies, secrets, or deployment should be security-aware:

| Stage | Check | Action on failure |
|-------|-------|-------------------|
| **00-context** | Flag hardcoded secrets in repo | `[Decision]` — use secrets management |
| **01-requirements** | Note security requirements in specs | Include in user-journeys.md and test-plan.md |
| **04-tech-plan** | Include security scan in hooks/CI | Add pip-audit, secret scan |
| **07-build** | Never commit secrets | Pre-commit hook |
| **08-verify-build** | Run dependency vulnerability scan | Surface with approve/deny/modify |
| **09-qa** | Full security scan (CVEs, secrets, patterns) | Report in QA report |
| **12-verify-deploy** | Verify secrets management, no .env deployed | Block deploy if exposed |

Security findings are **always blocking** — do not silently suppress.

## 6. Data & corpus management (deployed service)

RAG services need schema, seed corpus, and eval fixtures before integration tests pass:

| Stage | Responsibility |
|-------|----------------|
| **00-context** | Identify existing DB, vector extension, corpus sources |
| **01-requirements** | Data management scope in specs (ingest, retention, ACLs) |
| **04-tech-plan** | `docs/spec.md §Data`, migration tasks |
| **data-management** skill | Migrations + seed + verify before build |
| **07-build** | Block tasks that need DB until data-management is `complete` |
| **12-verify-deploy** | Migrations on target env; no dev fixtures in production |

## 7. Uncertainty / AskQuestion protocol

### Categories

| Category | Blocking? | Example |
|----------|-----------|---------|
| **Decision** | Yes | Multiple valid approaches |
| **Ambiguity** | Yes | Under-defined requirement |
| **Contradiction** | Yes | Sources disagree |
| **Bloat** | Advisory | Content adds noise |
| **Uncertainty** | Advisory | Low confidence fact |

### Rules

1. **Never silently resolve** a blocking issue. Always surface via AskQuestion.
2. **Batch** multiple issues in a single AskQuestion call when found at the same stage.
3. **First option = recommendation** with rationale.
4. **Last option** = "Let me explain / provide more context" escape hatch.
5. **Advisory issues** proceed with recommended option if user doesn't respond, marked `⚠️ Assumed:`.
6. **Evidence required**: Cite the source (spec section, code path, user answer).

## 8. ADR logging

Every decision surfaced via AskQuestion that selects between multiple valid approaches
must be recorded as an **Architecture Decision Record** in `docs/adr/`.

### When to create an ADR

| Trigger | Example |
|---------|---------|
| `[Decision]` resolved by user | REST vs gRPC, SQL vs NoSQL, deploy target |
| `[Contradiction]` resolved by choosing one side | Paper says X, repo does Y — user picks Y |
| `[Ambiguity]` resolved with a non-obvious default | "Standard preprocessing" clarified as specific steps |
| Tech choice made during interview | Framework, library, or tool selection |
| On-the-fly decision during build | New dependency added, algorithm changed |
| Scope decision during verification | Feature added, deferred, or removed |

Do **not** create ADRs for:
- Auto-approved high-confidence statements (user explicitly stated the fact)
- Advisory issues resolved with the recommended default (`⚠️ Assumed:`)
- Formatting, naming, or style choices already covered by linter rules

### ADR format

Use the template in `docs/adr/`:

```markdown
# ADR-{NNN}: {Title}

> **Status**: Accepted | Superseded | Deprecated
> **Date**: {YYYY-MM-DD}
> **Deciders**: {who made this decision}
> **Stage**: {pipeline stage where decision was made, e.g., 01-requirements}

## Context
{What problem or question triggered this decision?}

## Decision
{What was decided and why?}

## Alternatives Considered
| # | Alternative | Pros | Cons | Why Rejected |
|---|-------------|------|------|--------------|
| 1 | ... | ... | ... | ... |

## Consequences
### Positive
- ...
### Negative
- ...

## References
- {spec section, user answer, or evidence that informed the decision}
```

### Numbering

ADR numbers are sequential across all stages. Read `docs/adr/` to find the next
available number. Never reuse a number.

### Cross-referencing

When an ADR is created:
1. Add a reference in the stage's decision log (e.g., `product-decisions.md`,
   `tech-decisions.md`, `requirements-decisions.md`)
2. If the decision affects a spec document, add an inline citation:
   `<!-- ADR-{NNN} -->` next to the affected claim
3. Add the ADR path to `workflow-state.yaml` §artifacts

### Superseding

When a later decision overrides an earlier one:
1. Set the old ADR's status to `Superseded by ADR-{NNN}`
2. Reference the old ADR in the new one's Context section

## 9. Multi-app browser connectivity (skills 00–15)

Hybrid deploys (static frontend on host A, API on host B) require **two** wiring layers plus
**integration** tests for server-side paths:

| Layer | Mechanism | Verified by |
|-------|-----------|-------------|
| In-process integration | APIs + DB + mocked upstreams | **H0i** `tests/integration` |
| Build-time | `VITE_*` baked into JS | **H5** bundle check |
| Run-time | `METAR_CORS_ORIGINS` on APIs | **H0c** unit + **H4** live |

**Every pipeline skill 00–15** has stage-specific obligations in
[connectivity-gates.md](connectivity-gates.md) §Pipeline stages 00–15. The orchestrator
([pipeline/SKILL.md](pipeline/SKILL.md)) enforces phase gates that reference those rows.

Do not treat `curl` API smokes (H1–H3) or Vitest mocks as proof the UI works in production.

## 10. Template conformance

When a project is built from an org template (see [template-registry.md](template-registry.md)),
every stage should respect the template's structural patterns:

| Concern | Rule |
|---------|------|
| **File layout** | Do not create files outside the template's expected structure without an ADR |
| **Service layout** | API vs worker vs monolith per [template-registry.md](template-registry.md) |
| **Separation of concerns** | RAG core in `src/rag/` — no FastAPI/DB imports in pure retrieval tests |
| **Naming** | Service id `deployed-service`; routers and tables match `docs/api-contract.md` |
| **CI/CD** | Deploy workflow matches template pattern; changes require an ADR |
| **Drift detection** | Template-structural changes have higher blast radius than domain-specific changes. Surface as `[Template Drift]` when detected without a prior ADR. |

**Template drift is advisory, not blocking** — it warns but does not prevent the change.
If the user approves the drift, create an ADR documenting the deviation and why it was
accepted. The template is a starting point, not a cage.

## 11. State management

### YAML state

The pipeline uses repo-root [`workflow-state.yaml`](../workflow-state.yaml) as the **only**
canonical pipeline state file. Full schema, skill→key mapping, and update rules:
[workflow-state-reference.md](workflow-state-reference.md).

- Tracks pipeline stages 00–17 plus auxiliary keys (`gather-context`, `build-planner`, …)
- Phase gates with criteria checklists
- `issue_log` for cross-stage issues
- `decisions_log` for user decisions
- `artifacts` list; `evolve_cycles` / `retrospective_cycles` for 16/17

### Per-skill detail state

Detail files (e.g. `workflow-state.yaml + execution plan artifact` §Current State for 07-build,
`docs/deploy-state.md` for deploy) hold substeps. **Stage completion** must still be written
to `workflow-state.yaml` immediately. Do not use legacy-only files
(`gather-context-state.md`, `audit-state.md`) without mirroring into YAML.

### Persistence rules

- State writes are **immediate** — never buffer
- Every substep completion triggers a state write
- If a session ends mid-skill, all progress up to the last completed substep is preserved
- On re-invocation, the state file determines resume position

### Commit-as-you-go (§12)

All skills that produce files **must commit before**:

1. Transitioning to the next stage
2. Asking the user a blocking AskQuestion
3. Running a gate check
4. Ending a session/turn

Branch naming by change type, commit recording in `git_history`, and per-skill branch
type: see [workflow-state-reference.md](workflow-state-reference.md) §Git history.

| Change type | Branch pattern |
|-------------|----------------|
| Feature / milestone | `feat/{slug}` |
| Bug fix | `fix/{slug}` |
| Docs-only | `docs/{slug}` |
| Skill / tooling | `chore/{slug}` |
| Infra / deploy | `infra/{slug}` |
| Evolve cycle | `evolve/{cycle-id}-{slug}` |

Every commit appends to `workflow-state.yaml` §`git_history.commits` with stage
attribution. The git history in workflow-state is the persistent record that survives
session boundaries — on resume, read it to know what was committed and where.
