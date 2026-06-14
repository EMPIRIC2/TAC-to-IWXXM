---
name: bug-investigation
description: >
  Canonical workflow when any failure is caught (14-hotfix, 15-service-health, build, e2e, CI).
  One bug = one markdown report in docs/bug-reports/, one repro test in tests/bugs/, one fix.
  Requires error logs + description, persistent investigation in the MD file, repro test (red),
  user-confirmed root cause via AskQuestion, then fix until green. Interactive interviews only.
---

# Bug investigation (shared)

Use this skill whenever a **failure** is caught or reported — in [14-hotfix](../14-hotfix/SKILL.md),
[15-service-health](../15-service-health/SKILL.md), [07-build](../07-build/SKILL.md), [10-e2e](../10-e2e/SKILL.md),
CI, or ad-hoc user reports. Stage-specific skills add deploy/Modal context; **this skill owns
the artifact layout and TDD loop.**

**Cross-cutting:** [considerations.md](../considerations.md) §1, §7, [connectivity-gates.md](../connectivity-gates.md).

## Connectivity classification

During intake (Phase 0), ask whether the failure is **browser connectivity** vs **logic/data**:

| Class | Examples | Repro focus |
|-------|----------|-------------|
| **connectivity** | Failed to fetch, CORS error, empty `VITE_*` | H4/H5 assertions; OPTIONS + bundle hosts |
| **integration** | Write API 401, Modal key mismatch | H0i or live API with correct headers |
| **domain** | Wrong answer, bad retrieval | H3 / unit tests |

Route connectivity bugs through CORS/`VITE_*` fix before deep RAG changes. See connectivity-gates §Stage 14.

## State management

**Canonical:** repo-root [`workflow-state.yaml`](../../workflow-state.yaml) — update
§`stages.14-hotfix` when invoked from hotfix/deploy health; append blockers to `issue_log`.
Rules: [workflow-state-reference.md](../workflow-state-reference.md).

## One bug, three artifacts

| # | Artifact | Location | Rule |
|---|----------|----------|------|
| 1 | **Bug report** | `docs/bug-reports/BUG-YYYY-MM-DD-[slug].md` | Copy from [`_template.md`](../../../docs/bug-reports/_template.md); update through entire investigation |
| 2 | **Repro test** | `tests/bugs/test_bug_YYYY_MM_DD_[slug].py` | Must go **red** before fix; stays as regression test |
| 3 | **Fix** | `src/` (minimal diff) | One logical fix per bug; separate branch/PR when shipping |

**Bug ID:** `BUG-YYYY-MM-DD-[slug]` — same slug in report filename, test module name, and branch
(`hotfix/[slug]` or `fix/BUG-YYYY-MM-DD-[slug]`).

Do **not** combine multiple unrelated failures in one report or one test file.

## Required report sections

Every bug report must contain, at minimum:

1. **Error description** — what the user/system saw (not only stack traces)
2. **Error logs** — verbatim logs in a fenced block; table for env, entry point, call ID
3. **Investigation** — persistent log (timeline, hypotheses, root cause); append as you learn
4. **Repro test** — path, assertion, red/green dates, TDD iteration log
5. **Fix** — files and approach (fill when patching)
6. **Interview record** — AskQuestion answers
7. **Prevention & countermeasures** — Phase 5.0 answers (detection, automated/process guards, follow-ups)
8. **Cursor rule** — path, draft, declined, or deferred (Phase 5.1 in [14-hotfix](../14-hotfix/SKILL.md))

## Workflow (TDD + interviews)

```
Failure detected
      │
      ▼
┌─────────────┐   AskQuestion: intake batches (below)
│ Open report │   Create docs/bug-reports/BUG-….md from _template.md
│ + paste logs│
└──────┬──────┘
       ▼
┌─────────────┐   AskQuestion: repro matches symptom?
│ Repro test  │◄──────────────────────────────────────┐
│ RED         │                                        │
└──────┬──────┘                                        │
       ▼ yes                                           │
┌─────────────┐   AskQuestion: root cause agreed?      │
│ Investigate │◄──────────────────────────────────────┤
│ (update MD) │                                        │
└──────┬──────┘                                        │
       ▼                                               │
┌─────────────┐   pytest green                         │
│ Fix         │ ───────────────────────────────────────┘
└──────┬──────┘         (max 3 fix cycles — then escalate)
       ▼
 Verify (layered per 14-hotfix when deploying)
       ▼
 Prevention interview + Cursor rule ask (14-hotfix Phase 5)
```

| Gate | Blocking? | AskQuestion `id` |
|------|-----------|------------------|
| Intake complete | Yes | `bug_intake_*` batches |
| Repro test red + user match | Yes | `bug_repro_matches` |
| Root cause agreed | Yes | `bug_root_cause` |
| Fix verified | Yes | `bug_verified` |
| Prevention & countermeasures | Yes (14-hotfix close) | `prevention_*` batches, `prevention_plan_confirm` |
| Cursor rule offer | Yes (ask always) | `prevention_cursor_rule`, optional `cursor_rule_approve_draft` |

**No fix before confirmed repro** unless user waives via AskQuestion (`bug_repro_waiver`, `[Decision]`).

**No `resolved` before prevention interview** unless waived (`prevention_interview_waiver`) — see 14-hotfix Phase 5.

## Interactive questions (required)

**Every user-facing question uses the AskQuestion tool** — see considerations §7.

### Step 1 — Intent

| `id` | `prompt` | Options (last = Let me explain…) |
|------|----------|----------------------------------|
| `bug_intent` | What would you like to do with this failure? | New bug · Continue open BUG-* report · Investigate only · Apply existing fix / deploy |

### Step 2 — Intake (2–4 questions per AskQuestion call)

**Batch A** — `bug_symptom_type`, `bug_where_seen`, `bug_when_started`

**Batch B** — `bug_repro_frequency`, `bug_repro_environment`

**Batch C** — `bug_user_severity`, `bug_evidence_available`, `bug_already_tried`

Record answers in the report **Interview record** and **Error description**.

### Step 3 — Remediation path

| `id` | `prompt` |
|------|----------|
| `bug_remediation_path` | Fix locally first · Fix and deploy now · Investigate only · I'll deploy myself |

### Step 4 — Confirm plan

| `id` | `prompt` |
|------|----------|
| `bug_confirm_plan` | Proceed · Adjust answers · Exit |

### Step 5 — After repro test (red)

| `id` | `prompt` |
|------|----------|
| `bug_repro_matches` | Yes — matches · Adjust test · Not yet · Production-only repro |

### Step 6 — Before fix

| `id` | `prompt` |
|------|----------|
| `bug_root_cause` | Agree — proceed to fix · Different cause · Repro still wrong · Not a code bug |

### Step 7 — After fix

| `id` | `prompt` |
|------|----------|
| `bug_verified` | Fixed · Still broken · I'll verify later |

When the user selects **Let me explain / provide more context**, accept free text, append to
**Interview record** or **Investigation**, then continue with the next AskQuestion.

## Writing the repro test

- Path: `tests/bugs/test_bug_YYYY_MM_DD_[slug].py` only (no shared multi-bug modules).
- Name: `test_bug_YYYY_MM_DD_[slug]_[behavior]`.
- Encode interview evidence: payload, log line, exception type, ZIP status.
- Prefer fast local tests (mocks); Modal GPU only when user approves (`bug_repro_matches` → production-only).
- Assertions must align with `docs/config-spec.md`, `docs/api-contract.md`, `docs/test-plan.md`.

```bash
pytest tests/bugs/test_bug_YYYY_MM_DD_[slug].py -v
```

## Investigation log discipline

After each hypothesis, log pull, or code read:

1. Add a row to **Hypotheses** or **Timeline** in the bug report.
2. Paste new log excerpts under **Error logs** (dated subheading if long).
3. Do not keep investigation only in chat — the MD file is the source of truth.

## Handoffs between stages

| From | To | Carry |
|------|-----|-------|
| 15-service-health | 14-hotfix | Same `BUG-*` report + failing `tests/bugs/…` — do not rewrite test from scratch |
| 14-hotfix | 15-service-health | BUG ID + link; schedule post-fix health check |
| 07-build / 10-e2e | 14-hotfix | Failing pytest path + output → create BUG report if not exists |

Link related Modal health report in **Related** when both exist.

## Index

Append closed bugs to `docs/hotfix-log.md` (column **Bug report** → `docs/bug-reports/BUG-….md`).
Optional rolling list in `docs/bug-reports/README.md` only if the team maintains it.

## Output rules

1. One bug → one report, one test file, one fix scope.
2. Error logs + description required before investigation ends.
3. Investigation persists in the bug report MD.
4. Repro test red → user confirm → fix → green.
5. All user questions via AskQuestion.
6. Cite specs in **Spec conformance**; raise `[Decision]` / `[Contradiction]` per considerations §7.
