---
name: 14-hotfix
description: >
  Post-deployment surgical edits for hotfix sessions: bug fixes, patches, small behavioral
  changes, and dependency updates. Open via 00-context (type hotfix) or resume active_session.
  NOT for new features or multi-doc spec changes — use 00 → 16-evolve. Test-driven investigation:
  one bug = docs/bug-reports/BUG-*.md, tests/bugs/test_bug_*.py. Report: docs/sessions/{id}/reports/hotfix.md.
---

# 14 — Hotfix

Apply surgical edits to a deployed (or post-build) codebase: bug fixes, security
patches, behavioral tweaks, dependency bumps, and config corrections — without
re-running the pipeline.

**Bug artifacts (required):** [bug-investigation](../bug-investigation/SKILL.md) —
`docs/bug-reports/BUG-*.md`, `tests/bugs/test_bug_*.py`, one fix per bug.

**Preamble:** [pipeline-preamble.md](../pipeline-preamble.md) — shared conventions for stages 00–19.
**Sessions:** [sessions-reference.md](../sessions-reference.md) — requires `active_session` unless waived; reports under `docs/sessions/{id}/reports/`.
**Routing:** [docs/skill-routing.md](../../docs/skill-routing.md) — hotfix vs evolve vs pipeline.
**Cross-cutting:** [considerations.md](../considerations.md), [connectivity-gates.md](../connectivity-gates.md).  
**Infra access:** [infra-access.mdc](../../rules/infra-access.mdc) — Render/Supabase via `.env` creds (CLI/REST), no MCP-auth stalls.  
**State agent:** [workflow-state-manager](../../agents/workflow-state-manager.md) — mandatory read/update.
**Modal data-mgmt auth header:** [modal-proxy-header](../modal-proxy-header/SKILL.md).

## Connectivity (stage 14)

Classify failures before coding:

| Symptom class | First checks |
|---------------|--------------|
| “Failed to fetch”, CORS in DevTools | H4 (`test_staging_connectivity` or curl OPTIONS) |
| Wrong API host in UI | H5 bundle grep |
| Bad RAG answer, API 200 | H3 — not connectivity |

Repro tests in `tests/bugs/` may import `tests.helpers.connectivity`. After fix, run
`verify_connectivity.sh` if deployables changed. See connectivity-gates §Stage 14.

## Infrastructure access (Render + Supabase)

For any deployed-symptom hotfix, **access infra directly — do not stall on MCP auth**.
Credentials live in `.env`; full patterns in
[infra-access.mdc](../../rules/infra-access.mdc).

**Triage a deployed 5xx in this order (logs/env first, hypotheses last):**

1. **Real error** — pull service logs and read the actual exception/traceback. Handlers
   (e.g. `_handle_db_error`) log the root cause (PostgREST `APIError` code+message) before
   returning an opaque 5xx. `GET /v1/logs?ownerId=&resource={serviceId}&type=app` with
   `Bearer $RENDER_API_KEY`.
2. **Deployed artifact** — confirm what is actually live before assuming a code fix is.
   `GET /services/{id}/deploys`. The API is **image-based** (`backend:main-latest` via GHCR
   from `ci-cd.yml`'s deploy job, which `needs: test`) — a green `main` merge only deploys if
   CI's deploy job ran; env-var edits need an explicit `POST /services/{id}/deploys`.
3. **Service config** — `GET /services/{id}/env-vars` (e.g. a stray `DISABLE_AUTH=true`).
4. **Reproduce live** — `POST $API/auth/login` with `ADMIN_EMAIL`/`ADMIN_PASSWORD`, then hit
   the failing endpoint; parse `.env` in Python (never `source` it).

Only after 1–4 form a root-cause hypothesis (see BUG-2026-06-25-prod-disable-auth example:
symptom looked like a known code bug but was a prod env-var config defect found via logs).

## When to use / when NOT to use

| Situation | Skill |
|-----------|-------|
| Bug, regression, production incident | **14-hotfix** |
| Small patch — config, copy, one behavioral tweak | **14-hotfix** |
| Dependency bump with no spec/API change | **14-hotfix** |
| **New feature** or new Fn in `feature-list.md` | [16-evolve](../16-evolve/SKILL.md) |
| **Large change** — API redesign, multi-service, breaking change | [16-evolve](../16-evolve/SKILL.md) |
| Multi-doc spec update or new acceptance criteria | [16-evolve](../16-evolve/SKILL.md) |
| Greenfield service | [pipeline](../pipeline/SKILL.md) |

See [docs/skill-routing.md](../../docs/skill-routing.md). If workflow-state-manager blocks
feature intent, route to **16-evolve** — do not force a hotfix path.

## Main CI (GitHub Actions)

Hotfixes that merge to `main` must not leave **main CI red**. Source of truth:
`.github/workflows/ci.yml` (jobs: `python`, `frontend`). Command parity:
[09-qa](../09-qa/SKILL.md) Phase 1 — do not invent alternate lint/test paths.

### Bug-repro CI job (regression suite)

Every repro test under `tests/bugs/` **runs in CI** as the `bugs` matrix entry of the
`ci-cd.yml` `test` job (`uv run pytest tests/bugs -m "not live and not live_api"`), and
locally via `make test-bugs` (wired into `make test-unit` / `make ci`). This is how a
hotfix's regression test keeps protecting `main` after the session closes.

| Requirement | Detail |
|-------------|--------|
| **Placement = wiring** | Naming the test `tests/bugs/test_bug_YYYY_MM_DD_[slug].py` is what enrolls it in the CI `bugs` job — no extra config needed |
| **Must be collected + green** | Run `make test-bugs` before PR; confirm the new module is collected and passing (not silently skipped) |
| **Live probes excluded** | `-m live` / `live_api` tests are deselected in the `bugs` job; gate those through the live-E2E harness, not the blocking CI job |
| **Playwright-only repros** | When the regression is a `.e2e.spec.ts` (no pytest), record in the bug report that the spec is the regression test and which workflow runs it |
| **Don't let it rot** | If a fix changes the surface the test asserts (file path, image tag, route), update the repro test in the same PR so it stays green and meaningful |

| When | Check | Blocking |
|------|-------|----------|
| **Before PR** (Phase 2 Step 4, Layer 1) | **CI parity (local)** — run the same steps as `ci.yml` on the fix branch | **Yes** — do not open/merge PR with known CI failures |
| **After push** (Phase 3 Step 2, before merge) | **PR branch CI (remote)** — latest `CI` run on the pushed fix branch is `success` | **Yes** — fix and re-push before merge when feasible |
| **After merge** (Phase 3 Step 2 or Phase 2b closure) | **Main CI (remote)** — latest `CI` workflow on `main` for merged SHA is `success` | **Yes** for hotfix closure unless user waives via AskQuestion (`id`: `main_ci_waiver`) |

**CI parity (local) — minimum before PR**

```bash
uv sync --group dev
bash scripts/check_modal_no_database_url.sh
bash scripts/check_openapi_specs.sh
bash scripts/check_secrets.sh
uv run ruff check src tests
uv run ruff format --check src tests
uv run basedpyright src tests
uv run pytest tests/unit tests/integration tests/privacy tests/e2e tests/smoke tests/eval
make test-bugs   # runs tests/bugs/ (the CI `bugs` matrix job) — every repro test must be green
# pip-audit: see ci.yml + audit/pip-audit-ignore.txt
# migrations: apps/database — alembic upgrade head (needs Postgres; match CI service or skip with waiver)
cd apps/frontend && npm ci && npm run lint && npm test
cd apps/frontend && npm ci && npm run lint && npm test
```

**PR branch CI (remote) — after `git push`**

```bash
bash scripts/ci/watch_github_ci.sh fix/<slug>   # or current branch
# or: gh run list --branch <branch> --workflow ci.yml --limit 3 && gh run watch <run-id>
```

Fix failing steps locally (§CI parity), push again, re-watch. Do not merge with a red PR CI run
unless user waives via AskQuestion (`id`: `pr_ci_waiver`).

**Main CI (remote) — after merge to `main`**

```bash
gh run list --branch main --workflow ci.yml --limit 3
gh run watch <run-id>   # until python + frontend jobs complete
gh run view <run-id> --json conclusion,status,headSha,url
```

Record in the bug report **Verification → CI**: local parity pass/fail, run URL, job conclusions.
If a step fails on `main` but is **unrelated** to the hotfix (pre-existing), call **AskQuestion**
(`id`: `main_ci_unrelated_fail`) — fix in same hotfix · separate chore PR · waive with documented risk.

**User is the source of truth.** Do not assume symptoms, severity, or deploy intent — ask
via interview (Phase 0) before investigation or code.

## Test-driven investigation (required)

When the user describes a **failure** (error, crash, wrong output, timeout), investigation
and remediation follow **TDD for bugs** — same red → green discipline as
[`.cursor/rules/tdd.mdc`](../../rules/tdd.mdc), applied to bugs:

```
User failure report
       │
       ▼
┌──────────────┐     AskQuestion: repro test matches symptom?
│ Repro test   │ ◄────────────────────────────────────────────┐
│ (RED)        │                                              │
└──────┬───────┘                                              │
       │ no — adjust payload/assertion with user feedback     │
       ▼ yes                                                  │
┌──────────────┐     AskQuestion: root cause / next hypothesis?
│ Investigate  │ ◄────────────────────────────────────────────┤
│ (spec, logs) │                                              │
└──────┬───────┘                                              │
       │ agreed cause                                          │
       ▼                                                       │
┌──────────────┐     tests pass (GREEN)                        │
│ Minimal fix  │ ─────────────────────────────────────────────┘
└──────┬───────┘         (if still RED after fix → iterate, max 3)
       ▼
 Layered verification (2b) + deploy (4) per verification plan
       ▼
 Phase 5 prevention interview (countermeasures) + optional Cursor rule
```

| Rule | Detail |
|------|--------|
| **Test before fix** | Do not merge a code fix until a repro test existed and was **red** before the patch |
| **Test encodes user report** | Derive inputs from interview (payload, log excerpt, call ID, entry point) — not invented scenarios |
| **User confirms repro** | **AskQuestion** after first red run — test must match what they saw before triage/fix |
| **Interactive iteration** | Each failed hypothesis or wrong repro → AskQuestion, update test or investigation, re-run |
| **Green = necessary, not sufficient** | All repro/regression tests green **plus** verification layers per Step 0.5 |
| **Investigate-only** | Still write a repro test when symptoms are concrete; hand off test to Phase 2 later |

**Exempt:** Config-only changes with no behavioral assertion (e.g. secret name typo in deploy
docs) — record waiver in bug report via AskQuestion.

## Interactive questions (required)

**Every user-facing question in this skill must use the AskQuestion tool.** Do not post
interview prompts as markdown bullets, numbered lists, or fenced `prompt:` blocks in chat
and expect inline replies.

Reference: [considerations.md](../considerations.md) §7 (Uncertainty / AskQuestion protocol).

| Situation | Pattern |
|-----------|---------|
| Single choice (intent, triage, deploy) | One AskQuestion with `options`; first option = recommendation; last = `Let me explain / provide more context` |
| Interview batch (Step 0.2) | One AskQuestion call with **2–4 `questions`** per batch; wait for all answers before the next batch |
| Confirm plan (Step 0.4) | AskQuestion: Proceed / Adjust answers / Exit hotfix mode |
| Verification plan (Step 0.5) | One AskQuestion with 2–3 `questions` (success criteria, checks, monitoring) |
| Post-deploy verified? (Phase 4) | AskQuestion: Production fixed · Still broken · I'll verify later |
| Follow-up monitoring (Phase 4.4) | AskQuestion: schedule 15-service-health · user monitors · no follow-up |
| Prevention / countermeasures (Phase 5.0) | **2–3 AskQuestion batches** (detection, countermeasures, priority) — see Phase 5 |
| Cursor rule offer (Phase 5.1) | AskQuestion: create rule now · draft for review · no · defer to 03/06 · explain |
| Repro test matches symptom? (Phase 1.25) | AskQuestion: Yes · Adjust test · Can't reproduce yet · I'll explain |
| Investigation iteration (Phase 1) | AskQuestion: Agree root cause · Different hypothesis · Pause |
| Repro still red after fix? (Phase 2) | AskQuestion before next patch — iterate / escalate |
| Blocking issues | `[Decision]`, `[Contradiction]`, `[Ambiguity]` in the prompt text |
| Spec drift / scope | Batch in one AskQuestion; cite `[Spec: path §section]` in prompt |

**Blocking:** Do not start Phase 1+ until the user responds to the current AskQuestion.

**Open detail:** When the user selects `Let me explain / provide more context`, accept their
free-text reply in chat, record it in the bug report, then continue with the next
AskQuestion batch — do not re-ask the same choice as prose.

## Spec conformance (required)

Hotfixes must stay within approved product and technical specs. **Read specs before
classifying or patching**; cite sections in the bug report; surface drift via
**AskQuestion** — never silently “fix around” a spec gap.

### Spec registry

**Canonical list:** [`docs/CORPUS.md`](../../../docs/CORPUS.md). Read the corpus rows
relevant to the affected component / symptom. Skip only when clearly N/A
(e.g. no API involved — still check `[Corpus: product]` + `[Corpus: system-spec]`).

| Corpus ID | Document | Check for |
|-----------|----------|-----------|
| product | `docs/feature-list.md` | Map symptom to **F1–F4**; reject out-of-scope hotfix work |
| system-spec | `docs/spec.md` | Component behavior, constraints, hard limits (§Constraints) |
| tech-spec | `docs/tech-spec.md` (+ satellites) | Config/env/deploy/deps parity |
| — | `docs/config-spec.md` | Parameter names, defaults, validation rules |
| api | `docs/api-contract.md` | Payload shape, errors, return types |
| — | `docs/deploy.md` §Integration | Service topology, secrets, deploy command |
| — | `docs/dependency-inventory.md` | Version pins; new deps need `[Decision]` |
| tests | `docs/test-plan.md` | Expected smoke thresholds and pass criteria |
| journeys | `docs/user-journeys.md` | UJ sign-off when UI journeys affected |
| adr | `docs/adr/` | Existing architecture constraints |
| — | `.cursor/skills/template-registry.md` | Job template patterns when `workflow-state.yaml` §template is set |

### When to run spec checks

| Phase | Action |
|-------|--------|
| **On invocation** | Pre-read `[Corpus: product]` + `[Corpus: system-spec]` (§Component Overview) |
| **Phase 1 Step 1.25** | Repro assertions vs `[Corpus: tech-spec]` / `api` / `tests` |
| **Phase 1 Step 1.5** | Full cross-check vs `docs/CORPUS.md` before triage AskQuestion |
| **Phase 2 Step 3** | Re-verify fix does not violate corpus; patch surgically if behavior changes |
| **Phase 3 PR** | List corpus IDs / sections touched in PR body |

### Drift and spec issues

| Finding | Category | Action |
|---------|----------|--------|
| Code ≠ spec (spec is source of truth) | Implementation drift | Recommend code hotfix; cite `[Spec: …]` |
| Code matches spec but behavior wrong | **Spec mismatch** or **Spec bug** | `[Ambiguity]` or `[Contradiction]` — user picks spec vs code fix |
| Two spec sections disagree | **Spec contradiction** | `[Contradiction]` — user resolves before patch |
| Spec under-defined for this case | **Spec ambiguity** | `[Ambiguity]` — user clarifies; back-add to spec on resolve |
| Fix needs new feature (not F1–F9) | **Scope drift** | `[Decision]` — defer to pipeline, not hotfix |
| Implementation ≠ `deployment-integration.md` | Deploy/config drift | Note in report; 15-service-health may have already filed |
| Code ≠ template-registry | **Template drift** | Advisory per considerations §9; ADR if user approves change |

**Blocking:** Do not call `issue_triage` or write a fix until **blocking** `[Contradiction]` /
`[Ambiguity]` / scope items are resolved via AskQuestion (batch multiple spec questions in
one AskQuestion call when found together).

**Non-blocking drift:** Record in bug report **Spec conformance**; include in triage prompt;
user may accept as follow-up.

## When to Use

- **Post-deployment bug**: A user or smoke test surfaces a defect after 13-deploy-smoke
- **Security patch**: CVE disclosed for a dependency or a vulnerability found in code
- **Behavioral tweak**: Small change in logic, thresholds, or defaults
- **Dependency bump**: Library update for compatibility, security, or performance
- **Config fix**: Environment variable, secret rotation, or platform setting
- **Regression from merge**: A merged PR introduced a regression
- **User-reported issue**: Any issue surfaced after the pipeline completed

**Not for**: New features (go back to 01/04), large refactors (new pipeline pass),
or architectural changes (new ADR + plan update).

## Prerequisites

1. **Deployed codebase**: Pipeline stages 07-build through 13-deploy-smoke have run
   (at minimum, 07-build is `completed` so code exists to patch)
2. `workflow-state.yaml + execution plan artifact` — for tech stack, branch strategy, test commands
3. **Spec suite** — [`docs/CORPUS.md`](../../../docs/CORPUS.md) at minimum `product` +
   `system-spec`; plus `tech-spec` / `api` / `tests` when relevant
4. Git repo is clean (no uncommitted work)


## Session management

Per [sessions-reference.md](../sessions-reference.md) §10 and [workflow-state-agent-protocol.md](../workflow-state-agent-protocol.md).

1. Agent `read_context` must return `active_session` (or blocking deviation).
2. Current stage must appear in `active_session.routing_plan` unless user amends plan.
3. Write stage reports to `active_session.artifacts_dir/reports/` when this stage produces a report.
4. On completion: update routing-plan entry status; mirror `project.stages.{key}` via agent `update`.
5. **00-context** exempt from active_session requirement (session opener).
Report: `reports/hotfix.md`; BUG reports stay in `docs/bug-reports/`.

## State management

**Agent protocol:** [workflow-state-agent-protocol.md](../workflow-state-agent-protocol.md).
**Stage key:** `stages.14-hotfix`.

Invoke **workflow-state-manager** `read_context` before any other action; `update` after each
substep. **Do not** edit `workflow-state.yaml` directly.

(append section if missing). Rules: [workflow-state-reference.md](../workflow-state-reference.md).

### Hotfix log: `docs/hotfix-log.md`

Index of all hotfixes applied. Created on first invocation if absent. One row per
resolved bug; links to the full bug report.

```markdown
# Hotfix Log

| # | Date | Type | Summary | Bug report | Branch | Commit | Deployed | Verified |
|---|------|------|---------|------------|--------|--------|----------|----------|
```

### Bug reports: `docs/bug-reports/`

One markdown file per bug — durable investigation record (error description, **error logs**,
persistent **Investigation** section, repro test metadata, fix, verification).

**Naming:** `BUG-BUG-YYYY-MM-DD-[slug].md` (e.g. `BUG-2026-05-17-null-pipeline-response.md`)

**Template:** Copy [`docs/bug-reports/_template.md`](../../../docs/bug-reports/_template.md) on
first open. **Workflow and AskQuestion gates:** [bug-investigation](../bug-investigation/SKILL.md).

**Repro test (required):** `tests/bugs/test_bug_YYYY_MM_DD_[slug].py` — one module per bug;
see bug-investigation skill. Extend the template **Verification plan**, layered verification,
**Prevention & countermeasures**, and **Cursor rule** sections when running this skill (Phase 0
Step 0.5 onward; prevention filled in Phase 5).

### On invocation

1. Read `workflow-state.yaml` — confirm pipeline has reached at least Phase C
2. Read `docs/hotfix-log.md` (create if absent)
3. Read `docs/deploy-state.md` and `docs/deploy-report.md` if present (last deploy URL)
4. Skim `[Corpus: product]` + `[Corpus: system-spec]` §Component Overview (spec baseline)
5. Report current state in chat (status summary only — not a question), then **immediately
   call AskQuestion Step 0.1** — do not jump to code.

## Delta / feature-addition mode

If user request is **feature addition** (not a bug):

- workflow-state-manager will **block** — route to [16-evolve](16-evolve/SKILL.md).
- Hotfix remains surgical: one bug, one repro test, one fix.

## Workflow

Hotfixes are **interview-driven**. The user chooses intent and whether to fix live in
production before any patch or deploy.

```
┌──────────┐     ┌─────────────┐     ┌──────────────┐     ┌─────────────┐     ┌──────────────┐
│ Interview│ ──► │ Repro test  │ ──► │ Investigate  │ ──► │ Fix (green) │ ──► │ Verify (2b)  │
│ + verify │     │ RED (1.25)  │     │ + user loop  │     │ (Phase 2)  │     │ + deploy (4) │
│ plan (0) │     │ user confirms│     │ (Phase 1)   │     │              │     └──────┬───────┘
└──────────┘     └─────────────┘     └──────────────┘     └─────────────┘            │
                                                                                        ▼
                                                                              ┌──────────────────┐
                                                                              │ Prevent (5.0)    │
                                                                              │ + Cursor rule?   │
                                                                              │ (5.1) → close    │
                                                                              └──────────────────┘
```

Do not skip Phase 0, **repro test (red) + user confirmation**, the verification plan, the
bug report, layered verification, deploy approval, or **Phase 5 prevention interview** to rush
a patch. **Do not patch production code before a failing repro test matches the user's report**
(unless waived via AskQuestion). **Green repro tests alone are not closure** — complete
verification layers in the environment the user cares about, then **AskQuestion countermeasures**
and whether to add a **Cursor rule**.

### Phase 0 — User interview (required)

Conduct a short, structured interview before Phase 1. **Only AskQuestion** — batch with
2–4 `questions` per tool call where noted below.

#### Step 0.1 — What do you want to do next?

Call **AskQuestion** first — do not assume this is a new bug.

| Field | Value |
|-------|-------|
| `id` | `hotfix_intent` |
| `prompt` | `Hotfix — what would you like to do next?` |
| `options` | Report a new issue (production or local) · Continue an open BUG-* report · Deploy a fix we already have (branch/PR ready) · Investigate only — no code changes yet · Config / dependency / secret patch (not a logic bug) · Review hotfix history or last deploy · Nothing right now — exit hotfix mode · **Let me explain / provide more context** (last) |

| Choice | Next step |
|--------|-----------|
| New issue | Step 0.2 problem intake → Step 0.3 remediation path |
| Continue bug | Open existing `docs/bug-reports/BUG-*.md`; resume at its status |
| Deploy ready fix | Skip to Phase 4 (confirm deploy + live verification) |
| Investigate only | Phase 1 through classification; stop before Phase 2 unless user approves |
| Config / dependency | Problem intake (lighter) → Phase 1 classify → Phase 2 |
| Review history | Summarize `docs/hotfix-log.md` + deploy state; ask if they want Step 0.1 again |
| Exit | No code; optional note in workflow-state only |

#### Step 0.2 — Problem intake (from the user)

Gather details **from the user** via **AskQuestion only** (and only then from logs/repo).
Record answers in the bug report as they arrive. One AskQuestion tool call per batch
below; wait for all answers in that call before the next batch.

**Batch A — What broke** (`id`s: `symptom_type`, `where_seen`, `when_started`)

| `id` | `prompt` | Example `options` |
|------|----------|-------------------|
| `symptom_type` | What is wrong? | Error / crash · Wrong output · Performance / timeout · Other — I'll explain |
| `where_seen` | Where did you see it? | Production Modal · Local run · CI · Multiple — I'll explain |
| `when_started` | When did it start / what changed? | After last deploy · After merge · After config/data change · Unknown — I'll explain |

**Batch B — Reproduction** (`id`s: `repro_frequency`, `repro_environment`)

| `id` | `prompt` | Example `options` |
|------|----------|-------------------|
| `repro_frequency` | How often does it happen? | Every time · Intermittent · Cannot reproduce yet · I'll explain |
| `repro_environment` | Where can you reproduce? | Production only · Local only · Both · Neither yet — I'll explain |

**Batch C — Impact & evidence** (`id`s: `user_severity`, `evidence_available`, `already_tried`)

| `id` | `prompt` | Example `options` |
|------|----------|-------------------|
| `user_severity` | Impact in your words | Critical / blocked · High / wrong results · Medium · Low / cosmetic · I'll explain |
| `evidence_available` | Do you have logs or IDs to share? | Yes — I'll paste or link next · Partial · None yet |
| `already_tried` | Anything already tried? | Rollback · Redeploy · Config change · Nothing · I'll explain |

If the user cannot provide repro or evidence, note gaps in the bug report, then call
**AskQuestion** (`id`: `intake_gaps`): Proceed investigate-only · Wait for more input · Exit.

Create or update `docs/bug-reports/BUG-YYYY-MM-DD-[slug].md` from `_template.md` during
intake (status `investigating`); paste **Error logs** as user provides them; slug from
symptom. Run [bug-investigation](../bug-investigation/SKILL.md) intake AskQuestion batches.

#### Step 0.3 — Remediation path & live deploy intent

Before investigation completes, call **AskQuestion** (`id`: `remediation_path`) — how to
remedy, especially whether to fix **live in production**. Embed interview summary in the
`prompt` (symptom, environment, severity). First option = recommended path + one-sentence why.

| `options` (order) |
|-------------------|
| Fix locally first — deploy to production only after I approve |
| Fix and deploy to production now — need this live ASAP |
| Investigate in production first — don't change code yet |
| Local fix only — I'll deploy myself later |
| Not sure — recommend based on severity (only when no clear recommendation) |
| **Let me explain / provide more context** (last) |

Record the choice in the bug report **Remediation path** field and
`workflow-state.yaml` §stages.14-hotfix (current bug report pointer if tracked).

| Path | Behavior |
|------|----------|
| **local-first** (default for medium/low) | Phase 2–2b locally → Phase 3 PR → Phase 4 asks deploy again |
| **deploy-live** | Same build flow, but Phase 4 is **expected**; prioritize minimal smoke on affected endpoint after deploy |
| **investigate-only** | Phase 1 only; re-ask Step 0.3 before any code |
| **deferred deploy** | Complete fix + PR; skip Phase 4 unless user later chooses deploy |

**Critical / production-down:** Recommend option 2, but still require explicit user
approval before ` platform deploy` or equivalent.

**Never deploy without user approval** — even on "deploy-live", confirm immediately
before deploy commands (Phase 4).

#### Step 0.4 — Confirm plan before Phase 1

Summarize intent, problem, environment, remediation path, and next steps in the **AskQuestion
`prompt`** (do not ask "Proceed?" as plain chat text). Call **AskQuestion** (`id`:
`confirm_hotfix_plan`):

| `options` |
|-----------|
| Proceed |
| Adjust answers (re-run relevant Step 0.x batches) |
| Exit hotfix mode |

Only after the user selects **Proceed** continue to Step 0.5 (or Phase 4 if deploying an
existing fix that already has a verification plan in its bug report).

#### Step 0.5 — Verification plan (required)

Before Phase 1 investigation completes (or immediately before Phase 2 if investigate-only
then approved), define **what proves the fix worked**. Call **AskQuestion** with 2–3
`questions` in one tool call; record answers in the bug report **Verification plan**
section.

| `id` | `prompt` | Example `options` |
|------|----------|-------------------|
| `success_criterion` | What must be true for you to call this fixed? | Original error gone · Specific output/behavior · Test case passes · I'll define in text |
| `verification_checks` | Which checks should we run after the fix? | Unit tests only · **Full main CI parity (local) + gh on main after merge** (recommended) · Unit + user repro · Unit + Modal smoke on affected class · Full pipeline smoke · I'll explain |
| `monitoring_followup` | After deploy, how should we confirm it stays fixed? | I'll watch production myself · Re-check Modal logs in 24h · Run 15-service-health follow-up · No deploy — local only · I'll explain |

**Derive checks from specs when the user is unsure:**

1. Read `docs/acceptance-criteria.md` for the affected feature (F1–F9).
2. Read `docs/test-plan.md` for matching TC-IDs (e.g. TC-001 for pipeline smoke).
3. Map to concrete commands: `pytest tests/…`, `python tests/e2e_verify.py`, ` curl or httpx …`,
   or the smoke payload from `docs/deploy-report.md` / `tests/e2e_verify.py`.

| Symptom area | Typical Layer 3 smoke |
|--------------|----------------------|
| Config / validation | Minimal invalid payload → expect `ValueError` or `partial_failure` ZIP |
| Single stage (RFdiffusion, MPNN, RF2) | Cheapest GPU class for that stage + minimal valid PDB |
| Full pipeline | Smallest pipeline class + `num_designs=1` (user must approve GPU cost) |
| FineTune | FineTuneT4 + minimal valid training PDB |
| Deploy / registration | `modal app list` + class count vs `src/app.py` (no GPU invoke) |

**Blocking:** Do not mark bug report `resolved` until every check listed in the verification
plan has a recorded pass/fail (or explicit user waiver via AskQuestion).

**Iteration limit:** After 3 failed fix-verify cycles, stop and escalate to the user
with the bug report, hypotheses tried, and a recommended next path (deeper
refactor, upstream issue, or manual repro).

### Phase 1 — Investigate & triage (test-driven)

Understand the issue before fixing production code. The bug report should already exist
from Phase 0. **When the user described a concrete failure**, Phase 1.25 (repro test) runs
**before** final triage — investigation refines the test and root cause with user feedback.

#### Step 1 — Gather evidence

**Primary source:** Phase 0 interview answers (already in the bug report).

**Secondary source:** codebase, CI, Modal logs, `docs/deploy-report.md`, prior bug reports.

Add or refine:
- **Scope**: Which feature / endpoint / component is affected?
- **Severity** (agent assessment): Map user impact to critical / high / medium / low
- **Logs / traces**: Fill gaps the user did not supply
- **Timeline**: Correlate with deploys and merges

If interview answers contradict repo evidence, call **AskQuestion** with `[Contradiction]` in
the prompt; do not reconcile silently before classifying.

Update **Summary**, **Symptoms & reproduction**, and **Investigation** before proposing a fix.

**Investigate-only path:** Complete Step 1.25 (repro test) when symptoms are concrete; stop
after classification (Step 2) unless the user approves moving to Phase 2 via another
Step 0.3 choice. Hand off the **failing repro test** and bug report to a later fix session.

#### Step 1.25 — Codify failure as repro test (required when user reported a failure)

Turn the user's failure description into an **automated, failing test** before writing a fix.
This is the **red** phase of test-driven investigation — not optional for code-behavior bugs.

**1. Draft the test**

| Source from Phase 0 | Encode in test as |
|----------------------|-------------------|
| Error / stack trace | `pytest.raises`, message substring, or `partial_failure` ZIP assertion |
| Payload / overrides | Fixture dict or `tests/fixtures/…` file (minimal repro) |
| Modal class / function | `modal.App` mock, `run()` on wired class, or pure `parse_config` / stage call |
| Log signature | Assert log line via `caplog` or mocked subprocess stderr |

- Place under `tests/unit/` or `tests/integration/` mirroring the component (see `tdd.mdc`).
- Name: `test_bug_YYYY_MM_DD_[slug]_[behavior]` under `tests/bugs/` (e.g.
  `test_bug_2026_05_17_rfdiffusion_rejects_chunk_size_below_15`).
- Prefer **fast, local** tests (mock GPU/subprocess) over Modal GPU unless only production reproduces.
- Pull thresholds and error shapes from `docs/api-contract.md`, `docs/config-spec.md`,
  `docs/test-plan.md` — raise `[Ambiguity]` via AskQuestion if the assertion is not spec-backed.

**2. Run the test — expect RED**

```bash
pytest tests/bugs/test_bug_....py -v
```

| Outcome | Action |
|---------|--------|
| **Fails as expected** | Record output in bug report **Repro test** + **TDD iteration log**; proceed to Step 1.25b |
| **Passes unexpectedly** | Do not triage as “fixed” — call **AskQuestion** (`id`: `repro_test_no_fail`, `[Uncertainty]`): wrong test · env gap · already fixed on branch · I'll explain |
| **Errors / can't run** | Fix test harness first; log iteration row; ask user if import/path wrong |

**3. Step 1.25b — User confirms repro (AskQuestion)**

Call **AskQuestion** (`id`: `repro_test_matches_symptom`). Embed in the `prompt`: test name,
assertion summary, and one-line pytest failure (not full log wall).

| `options` |
|-----------|
| Yes — this matches what I saw |
| Close — adjust test inputs or assertion (I'll explain) |
| Not yet — need more evidence before we trust this test |
| Symptom is production-only — approve GPU/Modal repro test instead |
| **Let me explain / provide more context** (last) |

| Choice | Next |
|--------|------|
| **Yes** | Continue Step 1.5 spec cross-check → hypotheses → triage |
| **Adjust** | User provides corrections; update test; re-run red; re-ask (counts toward iteration limit) |
| **Not yet** | Gather more logs/evidence (Step 1); do not call `issue_triage` until repro confirmed or waived |
| **Production-only** | Document Modal repro in **Verification plan** Layer 3/4; keep local test for what *is* locally testable |

**Blocking:** Do not call `issue_triage` or start Phase 2 fix work until repro is **confirmed**
or user waives via AskQuestion (`id`: `repro_test_waiver`, `[Decision]`).

**4. Iterate investigation with the test**

As hypotheses are tested (Step 1.5, logs, code reading):

- Update the repro test when the failure mode sharpens (same AskQuestion gate if behavior changes).
- Log each cycle in **TDD iteration log**.
- Before `issue_triage`, call **AskQuestion** (`id`: `investigation_root_cause`) when root cause
  is believed known — embed failing test name + hypothesis in the `prompt`:

| `options` |
|-----------|
| Agree — proceed to fix (Phase 2) |
| Different root cause — I'll explain |
| Repro test still wrong — adjust before fixing |
| Not a code bug — close without fix |
| **Let me explain / provide more context** (last) |

#### Step 1.5 — Spec cross-check (required)

Before triage, compare **implementation** (code, config, deployed state) to the Spec
registry. For each relevant row:

1. **Locate** the spec section (cite `§` or heading in the bug report).
2. **Compare** to observed behavior (logs, code path, user report).
3. **Record** in bug report **Spec conformance** table: pass · implementation drift · spec
   ambiguity · spec contradiction · out of scope.
4. **Raise** via AskQuestion (do not proceed silently):
   - `[Contradiction]` — spec vs implementation vs user report disagree
   - `[Ambiguity]` — spec does not define behavior for this case
   - `[Decision]` — multiple valid fixes (code vs spec update vs defer)
   - Scope outside F1–F9 — recommend pipeline, not hotfix

Batch blocking spec issues into **one AskQuestion** with multiple `questions` when possible.
Include evidence: `[Spec: path §section]`, `[Code: path:Lx-y]`, user interview quote.

If no spec issues: note “Spec conformance: no blocking drift” in the report before triage.

#### Step 2 — Classify the issue

Use the root-cause taxonomy from [considerations.md](../considerations.md) §1:

| Kind | Signals | Fix path |
|------|---------|----------|
| **Code bug** | Logic error, missing edge case, wrong return value | Targeted code patch |
| **Spec mismatch** | Code does what spec says, but spec was wrong | Spec patch + code patch |
| **Dependency issue** | Upstream library broke, CVE, version conflict | Dependency bump + test |
| **Config / infra** | Wrong env var, missing secret, platform misconfiguration | Config patch |
| **Data issue** | Corrupt input, missing corpus fixtures, stale cache | Data fix + validation |
| **Regression** | Previously working behavior broken by recent merge | Revert or targeted fix |

Call **AskQuestion** (`id`: `issue_triage`) — embed symptom, root cause, severity, scope,
**repro test path + red-run summary**, **spec conformance summary** (pass / drift items), and
recommended fix in the `prompt`. First option = Proceed with this fix (recommendation).

**Blocking:** `issue_triage` requires a **confirmed repro test** (Step 1.25) or documented waiver.

| Remaining `options` |
|---------------------|
| Different root cause — I'll explain |
| Change severity — more/less critical |
| Not a bug — close without fixing |
| **Let me explain / provide more context** (last) |

#### Step 3 — Scope the blast radius

Before writing any code, identify:

1. **Files to change**: List specific files the fix will touch
2. **Tests affected**: Which existing tests cover this area?
3. **Downstream impact**: Could this fix break other features?
4. **Spec impact**: Which spec files/sections change? If behavior changes, spec patch is
   required in the same PR unless user chose “code-only workaround” via AskQuestion.
5. **Unresolved spec issues**: Any open `[Ambiguity]` / `[Contradiction]` from Step 1.5?
6. **Template impact** (if template selected): Read `workflow-state.yaml` §template.
   Classify each file as **template-structural** (app.py scaffolding, CI/CD workflow,
   Modal class definitions) vs **domain-specific** (core logic in service.py/utils.py,
   tests, docs). Template-structural changes have higher blast radius — they can break
   CI/CD, deployment, or job manager integration.

Report the scope:

```
Fix Scope:
  Files:      [list]
  Tests:      [N] existing tests cover this area
  New tests:  [N] needed for this fix
  Spec update: [yes/no — which section]
  Risk:       [low / medium / high — why]
```

Update the bug report **Root cause** and **Hypotheses tested** sections before
moving to Phase 2.

### Phase 2 — Branch & Fix

#### Step 1 — Create fix branch

Branch from the current deployed state (main or the deploy tag):

```
fix/[issue-slug]
```

Examples:
- `fix/null-response`
- `fix/bump-torch-2.3.1`
- `fix/rotate-api-key`

Record the branch in `workflow-state.yaml` §`git_history.branches`:

```yaml
- name: fix/null-response
  purpose: "Fix null pipeline response on empty input"
  base: main
  status: open
  created_at: "YYYY-MM-DD"
```

#### Step 2 — Confirm repro test still red

Phase 1.25 should have already created the failing repro test. Before patching:

1. Re-run `pytest` on the bug repro test(s) — must still be **red**.
2. If green unexpectedly, return to Phase 1 Step 1.25 (do not patch blindly).
3. Copy repro test path(s) into **Regression prevention** (they are the regression suite).
4. Confirm the test lives under `tests/bugs/test_bug_YYYY_MM_DD_[slug].py` so it is enrolled
   in the CI `bugs` job (§Main CI → Bug-repro CI job). A repro test that only ran ad-hoc in
   the session — and never in CI — is **not** a regression guard.

If Phase 1 was skipped (e.g. deploy-ready fix from a prior session), write the repro test now
using the bug report — same rules as Step 1.25 — before any fix.

#### Step 3 — Apply the fix (green)

Write the minimal code change to make the repro test(s) pass:

1. **Minimal diff**: Change only what's necessary. No drive-by refactors.
2. **Spec consistency**: Re-read affected spec sections. If the fix changes documented
   behavior, update the spec in the same change set (surgical edit + cite section in
   commit/PR). If the fix contradicts an unchanged spec, call **AskQuestion** `[Decision]`:
   update spec · change code to match spec · defer.
3. **Config/API names**: Use exact names from `config-spec.md` / `api-contract.md` (see
   domain-vocabulary rule).
4. **No scope creep**: If the fix reveals a larger issue, log it as a follow-up
   and finish the current fix first

**After patch — confirm GREEN**

1. Re-run bug repro test(s) — must pass.
2. If still **red**, call **AskQuestion** (`id`: `fix_still_red`): iterate fix · revise repro test ·
   escalate · I'll explain. Log row in **TDD iteration log**. Counts toward iteration limit.
3. Record green run date in **Repro test** table.

#### Step 4 — Post-fix checks

1. Run linter on changed files
2. Run typechecker
3. Run full test suite — all must pass (not just the new test). Include `make test-bugs`
   so the new repro test runs in the **same suite CI runs** (the `bugs` job).
4. If any previously passing test fails, fix the regression before committing
5. **Main CI parity (local):** Run **CI parity** commands from §Main CI on the fix branch.
   Both `python`-equivalent and `frontend` matrix must pass before Phase 3 PR. If Postgres
   is unavailable locally, run pytest without migration-dependent tests only after
   **AskQuestion** waiver — note gap in bug report.

Set bug report status to `fixing` when the branch is created; move to `verifying` after
post-fix checks pass locally.

### Phase 2b — Verify & iterate (layered)

Do not treat "tests pass locally" as done until the **Verification plan** success criterion
is met in the environments it specifies. Work through layers in order; record evidence in
the bug report after each layer.

#### Verification layers

| Layer | When | What to run | Pass criteria |
|-------|------|-------------|---------------|
| **1 — Automated** | Always | Linter, typecheck, full `pytest`; **CI parity (local)** per §Main CI; new regression test red→green | All pass; new test guards the bug; CI parity green before PR |
| **2 — Reproduction** | Always (unless investigate-only) | User repro from Phase 0; or scripted equivalent | Symptom absent; capture log/output |
| **3 — Pre-deploy smoke** | Before Phase 4 deploy | Checks from Step 0.5 `verification_checks` that do not need production | Modal invoke or `e2e_verify` journey passes |
| **4 — Production** | After Phase 4 deploy | Post-deploy smoke + log review on affected function | No recurrence; user confirms |

**Layer 1 — Automated (required)**

1. Confirm repro test was **red** before fix and **green** after (document in **Repro test** + Layer 1).
2. Run full unit test suite — all must pass.
3. Run **CI parity (local)** per §Main CI; record pass/fail per job (`python`, `frontend`).
4. If verification plan or changed files touch orchestration/config/output: run
   `python tests/e2e_verify.py` and record pass/fail summary in the report.
5. Update bug report **Verification → Layer 1** checkboxes.

**Layer 2 — Reproduction (required)**

1. Re-run the **user's** reproduction steps from Phase 0 exactly (same payload, env, entry point).
2. If user could not repro locally, run the closest automated substitute (e.g. same payload
   against ` curl or httpx` or mocked `run()` in tests) and note the gap.
3. Save evidence: command, Modal call ID, first 20 lines of relevant log, or test output.
4. Update **Verification → Layer 2**.

**Layer 3 — Pre-deploy smoke (when deploy is planned)**

Skip only for **local fix only** / **deferred deploy** paths where Layer 4 is explicitly waived.

1. Pick the **cheapest** check that exercises the fixed path (see Step 0.5 table).
2. **AskQuestion** before any GPU Modal invoke — embed estimated cost/time in the prompt.
3. For validation-only fixes, negative tests count: send the bad payload that used to fail;
   confirm the new error shape (e.g. `ValueError` before GPU, or `partial_failure` ZIP).
4. Record deploy commit SHA you intend to ship.
5. Update **Verification → Layer 3**.

**Closure for local-first path**

Layers 1–2 (and 3 if run) must pass before Phase 3 PR. Tell the user which layers passed;
call **AskQuestion** Step 4.1 in Phase 4 (they may have changed their mind since Phase 0).

#### If verification fails

1. Increment iteration count in the bug report (note what was tried per layer).
2. Update **Hypotheses tested** with the failed fix attempt and which layer failed.
3. Return to Phase 1 investigation with new evidence — do not stack unrelated changes.
4. Re-ask Step 0.3 if remediation path should change (e.g. escalate to deploy-live).
5. Re-ask Step 0.5 if success criteria or checks were wrong.
6. After 3 iterations without resolution, escalate (see iteration limit above).

#### If verification passes (locally)

Proceed to Phase 3, then Phase 4 per remediation path. Set bug report status to `verifying`
during Layer 2–3; keep `fixing` until Layer 1 passes.

### Phase 3 — Commit & PR

#### Step 1 — Atomic commit & record

```
hotfix: [description] (#[issue] if applicable)
```

One commit per hotfix. If the fix touches multiple concerns, split into
multiple hotfixes (separate branches, separate PRs).

After committing, append to `workflow-state.yaml` §`git_history.commits`:

```yaml
- sha: <short-sha>
  branch: fix/<slug>
  message: "hotfix: <description>"
  stage: "14-hotfix"
  files_changed: <count>
  timestamp: "<ISO-8601>"
```

**Commit-as-you-go:** Also commit the bug report and repro test as separate
earlier commits on the fix branch (e.g. after Phase 1.25 repro test is written,
commit it even though the test is red — it documents the failure).

#### Step 2 — Create PR

PR from hotfix branch to main (or current deploy branch):

- Title: `[hotfix] [summary]`
- Body:
  - **Issue**: What was wrong
  - **Bug report**: Link to `docs/bug-reports/BUG-YYYY-MM-DD-[slug].md`
  - **Root cause**: Classification from triage
  - **Spec**: Sections checked; drift resolved or deferred (with links)
  - **Fix**: What was changed and why
  - **Tests**: New regression test(s) added
  - **Blast radius**: Files changed, downstream impact assessment

Call **AskQuestion** (`id`: `hotfix_pr_merge`) before merge — embed **CI parity (local)** and
**PR branch CI (remote)** summary in the `prompt`. Options: Approve merge · Request changes ·
Merge later · Let me explain / provide more context. Never auto-merge.

**After merge — main CI (required for closure)**

1. `gh run watch` (or poll) until the latest `CI` workflow on `main` for the merge commit finishes.
2. Both `python` and `frontend` jobs must be `success`. Record run URL in bug report **Verification → CI**.
3. If main CI fails, **try to fix** (chore PR or same-session patch) before marking `resolved`.
   Do not mark `resolved` while main is red — treat as verify iteration (Phase 2b) or open
   follow-up per AskQuestion `main_ci_unrelated_fail` (§Main CI).

### Phase 4 — Deploy to production (user-approved)

Deployment fixes the **live** issue. Always interview before deploy — even if Phase 0
chose `deploy-live`, confirm again with current context (PR merged? which commit?).

#### Step 4.1 — Deploy decision

Call **AskQuestion** (`id`: `deploy_hotfix`). Embed fix summary, branch/PR, last deploy,
remediation path, and local verification in the `prompt`.

| `options` (first = recommended when deploy-live path) |
|-------------------------------------------------------|
| Yes — deploy now and verify in production |
| Deploy now — I'll verify production myself |
| Queue for next scheduled deploy |
| Skip deploy — fix lands in next release |
| **Let me explain / provide more context** (last) |

Skip this phase only when the user chose **deferred deploy** or **local fix only** and
reaffirms skip. For **deploy ready fix** (Phase 0.1 option 3), this is the first step.

#### Step 4.2 — Live deploy & verify (Layer 4)

If the user approves deploy, complete **all** items before closing the bug report. This is
**monitoring that the fix worked in production**, not just that deploy succeeded.

**Deploy**

1. Deploy the hotfix branch/commit (` platform deploy -m src.app` or project's deploy command).
2. Capture deploy stdout/stderr; record app URL, commit SHA, and timestamp in the bug report
   report and `docs/deploy-state.md` (hotfix deploy row).

**Post-deploy checks (required)**

| # | Check | How | Record in report |
|---|-------|-----|------------------|
| 1 | App registered | `modal app list` — app name per `deployment-integration.md` | App ID, status |
| 2 | Commit matches | Compare deployed image/commit to hotfix SHA | pass / fail |
| 3 | Targeted functional smoke | Same repro as Phase 0 / Layer 3 on **production** | pass / fail + call ID |
| 4 | Logs clean | `modal app logs` (or dashboard) for affected function — no recurrence of original error signature | pass / fail + excerpt |
| 5 | Error shape (if applicable) | For validation fixes: bad payload returns expected error, not Modal crash | pass / fail |

**User confirmation**

6. Call **AskQuestion** (`id`: `production_verified`) — embed smoke and log summary in the
   `prompt`: Production fixed · Still broken · I'll verify later · **Let me explain** (last).
7. Update bug report **Verification → Layer 4** and **Timeline → Verified in production**.
8. If user chose **I'll verify later**, bug report stays `verifying` until they confirm or
   Phase 4.4 follow-up runs — do not mark `resolved` yet.

Do NOT re-run the full pipeline smoke (TC-001, multi-design GPU runs) unless the verification
plan or user explicitly requires it.

**Handoff to 15-service-health:** If logs are ambiguous or multiple entry points were touched,
invoke [15-service-health](../15-service-health/SKILL.md) with intent "Verify after a recent
deploy or config change" instead of guessing — attach this bug report.

#### Step 4.3 — If live issue persists after deploy

1. Update bug report — deploy did not resolve symptom
2. Call **AskQuestion** (`id`: `post_deploy_still_broken`): iterate investigation · roll back
   deploy · pause for more info · Let me explain / provide more context
3. Count as a verify iteration (Phase 2b limit)
4. Clear **Verification → Layer 4** checkboxes; note deploy did not satisfy success criterion

#### Step 4.4 — Post-deploy monitoring (follow-up)

After Layer 4 passes (or user defers with a scheduled check), call **AskQuestion**
(`id`: `hotfix_monitoring_followup`). Embed `monitoring_followup` from Step 0.5 in the prompt.

| `options` (first = match Step 0.5 when possible) |
|--------------------------------------------------|
| Schedule 15-service-health re-check (I'll run / remind user) |
| User will monitor — note what to watch (logs, metric, endpoint) |
| No follow-up — one-shot verification is enough |
| **Let me explain / provide more context** (last) |

| Choice | Action |
|--------|--------|
| **15-service-health** | Invoke [15-service-health](../15-service-health/SKILL.md) — intent "Verify after recent deploy"; link bug report; compare logs to pre-fix baseline |
| **User monitors** | Record in bug report **Post-deploy monitoring** (what, where, by when); optional calendar note in workflow-state |
| **No follow-up** | Record "none" in **Post-deploy monitoring** |

**When follow-up runs:** Re-run Layer 4 log check (and smoke if intermittent). Update the
monitoring table with date and result. If the issue recurred, reopen bug report status to
`fixing` and loop Phase 1–2b (counts toward iteration limit).

### Phase 5 — Record, prevent & close

Phase 5 closes the hotfix loop with a **mandatory prevention interview** (how to counter this
bug class in the future) and an **optional Cursor rule** so agents do not repeat the same
mistake. **Every step uses AskQuestion** — do not skip by proposing countermeasures in chat only.

**Blocking:** Do not set the bug report to `resolved` until Phase 5.0 completes (or user
waives via AskQuestion `id`: `prevention_interview_waiver`, `[Decision]`). Phase 5.1 (Cursor rule)
is optional but must still be **asked** — user may decline.

**Investigate-only / wont-fix:** Run a shortened Phase 5.0 (detection + process countermeasures);
still offer Phase 5.1 Cursor rule when the failure class is repeatable.

#### Step 5.0 — Prevention & countermeasures interview (required)

Embed in each batch `prompt`: one-line **root cause**, **symptom class** (connectivity / code /
config / data), and **what we already shipped** (fix + tests). Record all answers in the bug
report section **Prevention & countermeasures** and **Interview record**.

**Batch P-A — Recurrence & detection** (`id`s: `prevention_recurrence_risk`, `prevention_detect_earlier`)

| `id` | `prompt` | Example `options` |
|------|----------|-------------------|
| `prevention_recurrence_risk` | How likely is this exact failure (or same class) to happen again? | Very likely without changes · Possible on similar changes · Unlikely once fixed · I'll explain |
| `prevention_detect_earlier` | Where should we catch this **before** production? | **Main CI (ci.yml) on PR** · CI unit/H0c · Deploy smoke H4–H5 · Code review checklist · Runtime monitoring · Multiple — I'll explain |

**Batch P-B — What to do (countermeasures)** (`id`s: `prevention_automated`, `prevention_code_hardening`, `prevention_process`)

| `id` | `prompt` | Example `options` |
|------|----------|-------------------|
| `prevention_automated` | What **automated** guards should we add or strengthen? | Bug repro test only (done) · **Strengthen ci.yml step** (secrets, H0c, new test) · Extend H0c/H4 in CI · New integration test · Staging smoke in 13 · None — fix is enough · I'll explain |
| `prevention_code_hardening` | Any **code** changes beyond the minimal hotfix? | Allow-list all HTTP methods in CORS helper · Stricter validation at boundary · Refactor risky module · No — hotfix only · I'll explain |
| `prevention_process` | What **process / docs** changes? | Update connectivity-gates · Deploy checklist row · Spec patch (config/api) · ADR · None · I'll explain |

**Batch P-C — Priority & ownership** (`id`s: `prevention_when`, `prevention_who`)

| `id` | `prompt` | Example `options` |
|------|----------|-------------------|
| `prevention_when` | When should follow-up countermeasures land? | Now (same session/PR) · Next PR · Backlog / 16-evolve · Won't do — accept risk · I'll explain |
| `prevention_who` | Who implements follow-ups? | Agent now (if in scope) · I'll do it · Team ticket · Defer to pipeline 03/06 tooling stage |

**Agent actions after P-A–P-C**

1. Map answers to concrete artifacts (test path, `docs/deploy-checklist.md` row, `.cursor/rules/*.mdc`,
   `connectivity-gates.md`, ADR). List each in **Prevention & countermeasures → Planned actions**.
2. Implement items the user chose **Now** and that fit hotfix scope (e.g. extra H4 test — already
   done for CORS DELETE). Log deferred items under **Follow-ups** with owner and trigger.
3. If user selects **Backlog / 16-evolve** or **03/06 tooling**, append `workflow-state.yaml`
   `issue_log` with category `prevention-deferred` and link to BUG report.

Call **AskQuestion** (`id`: `prevention_plan_confirm`) — embed planned actions summary in `prompt`:

| `options` |
|-----------|
| Proceed — record plan and continue to Cursor rule question |
| Adjust countermeasures — I'll explain |
| Skip follow-ups — hotfix + repro test is enough |
| **Let me explain / provide more context** (last) |

#### Step 5.1 — Cursor rule to prevent recurrence (required ask, optional create)

After Step 5.0 confirms, call **AskQuestion** (`id`: `prevention_cursor_rule`).

Embed in `prompt`: root cause, symptom class, and **recommended rule scope** (one sentence —
e.g. "CORS `allow_methods` must include every HTTP verb exposed by FastAPI routes").

| `options` (first = recommend when recurrence risk is not "Unlikely") |
|---------------------------------------------------------------------|
| Yes — create `.cursor/rules/` rule now (I'll approve draft) |
| Draft rule text for my review — don't write file yet |
| No — tests and docs are sufficient |
| Defer — handle in 03-plan-tooling or 06-tech-tooling |
| **Let me explain / provide more context** (last) |

| Choice | Action |
|--------|--------|
| **Yes — create now** | Draft rule (name, globs, 5–15 lines). Call **AskQuestion** (`id`: `cursor_rule_approve_draft`) with draft body summary. On approve, write `.cursor/rules/<slug>.mdc` using [create-rule](/root/.cursor/skills-cursor/create-rule/SKILL.md); link path in bug report **Cursor rule** |
| **Draft for review** | Paste draft in chat + save under bug report **Cursor rule → Draft**; no file until user approves in a later session |
| **No** | Record "declined" in bug report |
| **Defer** | Record target stage (03/06) in **Follow-ups** |

**Rule content guidelines**

- **One concern per rule** — match this bug class, not generic coding standards.
- Cite evidence: BUG ID, root cause, repro test path.
- Prefer `globs` targeting affected files (e.g. `packages/shared-schemas/**/cors.py`, `**/app.py`).
- Do not duplicate existing rules — read `.cursor/rules/` first; extend or reference if overlap.

#### Step 5.2 — Finalize bug report

1. Set status to `resolved` (or `wont-fix` if closed without code change) — only when all
   required verification layers in the plan are **pass** or explicitly waived by user **and**
   Phase 5.0 (and 5.1 ask) are complete
2. Complete **Timeline**, **Fix**, **Verification plan**, all **Verification** layers,
   **Post-deploy monitoring**, **Prevention & countermeasures**, **Cursor rule** (if any), and **Follow-ups**
3. Ensure **Regression prevention** lists every new test and any smoke/monitoring updates,
   and confirm each pytest repro test is under `tests/bugs/` (enrolled in the CI `bugs` job)
   or, for Playwright-only repros, names the workflow that runs the spec. Do not mark
   `resolved` if the regression test exists only locally / outside CI.

#### Step 5.3 — Update hotfix log

Append to `docs/hotfix-log.md`:

| Field | Value |
|-------|-------|
| # | Sequential number |
| Date | Today |
| Type | Classification from triage |
| Summary | One-line description |
| Bug report | `docs/bug-reports/BUG-YYYY-MM-DD-[slug].md` |
| Branch | `hotfix/[slug]` |
| Commit | Short SHA |
| Deployed | Yes/No + date |
| Verified | Layer summary (e.g. L1–4 pass, or L1–2 local-only) |

#### Step 5.4 — Update state

- `workflow-state.yaml` §stages.14-hotfix: increment hotfix count, log entry; note if Cursor rule created
- If spec was patched, check staleness: warn if downstream artifacts consumed
  the old spec version

#### Step 5.5 — Create ADR (if applicable)

If the hotfix involved a non-obvious decision (e.g., chose workaround over proper
fix, changed behavior intentionally, accepted a known limitation), create an ADR
per [considerations.md](../considerations.md) §ADR logging. Set Stage to `14-hotfix`.

#### Step 5.6 — Summary

```
Hotfix Complete.

  Issue:       [summary]
  Root cause:  [classification]
  Severity:    [level]
  Fix:         [what was changed]
  Tests:       [N] added, [N] total passing
  Verified:    Layer 1 [pass] · Layer 2 [pass] · Layer 3 [pass/skip] · Layer 4 [pass/skip]
  Deployed:    [yes/no] — commit [SHA]
  Monitoring:  [none | user | 15-service-health scheduled]
  Prevention:  [countermeasures recorded; follow-ups]
  Cursor rule: [path or declined/deferred]
  PR:          [URL]
  Commit:      [SHA]

  Bug report:  docs/bug-reports/BUG-YYYY-MM-DD-[slug].md
  Hotfix log:  docs/hotfix-log.md (#[N])
  Follow-ups:  [any larger issues noted during fix]
```

## Batch Mode

When multiple issues are reported at once:

1. Run Phase 0 interview per issue (or one interview listing all, then split bug reports)
2. Triage each (Phase 1) — sort by severity (critical first)
3. Check for related issues — can any be fixed together?
4. Execute Phase 2–5 per issue, sequentially (one branch per fix); deploy each only with
   separate Phase 4 approval
5. If two fixes conflict, call **AskQuestion** `[Contradiction]` before proceeding

## Escalation Rules

| Condition | Action |
|-----------|--------|
| Fix requires > 5 files changed | **AskQuestion**: proceed hotfix vs defer to refactor |
| Fix requires new dependency | **AskQuestion** `[Decision]` — back-add to specs |
| Fix reveals spec is fundamentally wrong | **AskQuestion** `[Contradiction]` — may need plan update |
| Blocking spec drift unresolved | Do not merge — AskQuestion until resolved or wont-fix |
| Spec patched without user awareness | **AskQuestion** — confirm spec change is intended |
| Fix breaks > 2 existing tests | **AskQuestion** `[Decision]` — regression risk |
| User reports 3+ hotfixes in same component | **AskQuestion**: continue hotfix vs schedule refactor |
| Fix requires schema/API change | **AskQuestion** `[Decision]` — breaking change risk |
| Repro test won't go red after 3 adjust cycles | **AskQuestion** — waive, production-only repro, or pause for evidence |
| Fix applied but repro still red after 3 cycles | Escalate per iteration limit — bug report + recommended path |
| User skips prevention interview | **AskQuestion** `prevention_interview_waiver` — document waiver in bug report |
| Same bug class ≥2 hotfixes in 90 days | Recommend Cursor rule + 16-evolve; batch in Phase 5.0 |

## Output Rules

1. **Interactive questions only**: Every user-facing question uses **AskQuestion** (see
   Interactive questions section). No prose interview bullets.
2. **Interview first**: Phase 0 required — intent, problem from user, remediation/deploy path.
3. **User approves deploy**: Never deploy to production without explicit AskQuestion approval.
4. **Spec checks required**: Phase 1 Step 1.5 before triage; cite specs in report and PR.
5. **Raise spec drift**: Implementation ≠ spec, spec contradictions, and ambiguities go to
   AskQuestion — never silent workaround.
6. **Test-driven investigation**: User-described failure → repro test (red) → user confirms via
   AskQuestion → investigate with feedback → fix → green. No fix before confirmed repro (unless waived).
7. **Investigate before code**: Codify failure in tests and document before proposing a fix.
8. **Bug report required**: Every hotfix gets `docs/bug-reports/BUG-YYYY-MM-DD-[slug].md` with
   **Error description**, **Error logs**, **Investigation**, **Repro test**, and **TDD iteration
   log**; update through each cycle (see bug-investigation skill).
9. **Minimal diff**: Change only what's necessary. No drive-by improvements.
10. **Regression tests required + in CI**: Repro test from Phase 1.25 is the regression test;
    place it under `tests/bugs/` so it runs in the CI `bugs` job, verify with `make test-bugs`,
    and link in PR. A repro test that never runs in CI does not count as closure (Playwright-only
    repros: name the workflow that runs the spec in the bug report).
11. **Verification plan required**: Step 0.5 defines success criteria and checks before fix
    work; cite acceptance-criteria / test-plan TC-IDs in the bug report.
12. **Layered verification**: Layers 1–2 always; Layer 3 before deploy; Layer 4 after deploy.
    Record pass/fail and evidence per layer. Do not mark `resolved` with open Layer 4.
12b. **Main CI**: CI parity (local) before PR; **PR branch CI after push**; `gh run` on `main`
    after merge — both jobs `success` unless explicitly waived (§Main CI). See
    [ci-after-push.mdc](../../rules/ci-after-push.mdc).
13. **Iterate until verified**: Green repro tests are not closure — confirm the verification
    plan in the environments it specifies; loop back if not (max 3 iterations per skill).
14. **Post-deploy monitoring**: Phase 4.4 — schedule 15-service-health, user watch, or
    document one-shot closure; re-open bug report if follow-up shows recurrence.
15. **One fix per branch**: Separate concerns, separate PRs.
16. **Merge requires approval**: Never auto-merge hotfixes — **AskQuestion** before merge.
17. **Record everything**: Bug report (logs, investigation, repro test, TDD log, verification layers), hotfix log,
    state file, ADR if applicable.
18. **Fix in place**: Never re-run pipeline phases. Surgical patches only.
19. **Escalate scope creep**: If the fix grows beyond a patch, **AskQuestion** before continuing.
20. **Prevention interview required**: Phase 5.0 countermeasures via AskQuestion (batches P-A–P-C +
    confirm) before `resolved`; record in bug report **Prevention & countermeasures**.
21. **Cursor rule ask required**: Phase 5.1 — always AskQuestion whether to create a rule; implement
    only on user approval per [create-rule](/root/.cursor/skills-cursor/create-rule/SKILL.md).

## Related stages

| Stage | Use during hotfix |
|-------|-------------------|
| [13-deploy-smoke](../13-deploy-smoke/SKILL.md) | Smoke patterns, deploy-state format, monitoring baseline |
| [15-service-health](../15-service-health/SKILL.md) | Ambiguous production logs; post-hotfix follow-up (Phase 4.4); may originate repro test handed to hotfix |
| [tdd.mdc](../../rules/tdd.mdc) | Test-first naming, placement, spec-aligned assertions |
