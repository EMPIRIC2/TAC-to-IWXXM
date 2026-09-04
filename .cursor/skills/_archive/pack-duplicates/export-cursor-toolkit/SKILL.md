---
name: export-cursor-toolkit
description: >
  Exports .cursor/skills, .cursor/rules, and .cursor/agents from this repo to another
  repository, stripping deployed service-specific content and seeding a minimal docs/ set.
  Uses Mustache placeholders, tiered rules, and interview-driven sanitization. Supports
  greenfield scaffold and merge-into-existing targets. Does not export hooks.
  Use when exporting the Cursor pipeline toolkit, bootstrapping a new project from deployed service
  tooling, sanitizing skills/rules for reuse, or consolidating docs to the minimal standing set.
---

# Export Cursor Toolkit

Copy the spec-driven pipeline (skills 00–19, shared references, workflow-state-manager) to a
target repository with deployed service-specific content removed and a minimal `docs/` stub set.

**Detailed inventories, strip lists, and doc merge map:** [reference.md](reference.md)

## Preconditions

- Source: this repository's `.cursor/` tree (and `doc-planner/templates/` for doc stubs).
- Target path is known (local directory or git clone).
- User has chosen export mode and optional rule tiers (see §Intake).

## Intake (AskQuestion)

Run before copying files:

1. **Target path** — absolute path to destination repo root.
2. **Mode** — `greenfield` (create `.cursor/` + `docs/` + `workflow-state.yaml`) or
   `merge` (overlay into existing repo; never overwrite without confirming conflicts).
3. **Optional rule tiers** — from [reference.md §Rule tiers](reference.md#rule-tiers); default
   none unless user selects Modal, CORS/browser, strict-typing, CI-after-push, etc.
4. **Placeholder values** — collect Mustache bindings (minimum: `PROJECT_NAME`, `REPO_URL`;
   optional: `ORG_NAME`, `DEPLOY_TARGET`, `PRIMARY_LANGUAGE`).
5. **Conflict policy (merge mode)** — skip / overwrite / ask per file.

## Standing vs ephemeral documents

**Export these `docs/` stubs** (Mustache placeholders, no deployed service content):

| File | Contents |
|------|----------|
| `spec.md` | Architecture, roadmap phases, data section, glossary |
| `feature-list.md` | Feature table + per-feature acceptance bullets |
| `user-journeys.md` | Single-file journey index + details |
| `test-plan.md` | Test matrix + QA assurance gates |
| `api-contract.md` | API surface (when applicable) |
| `dependency-inventory.md` | Dependencies and licenses |
| `risk-register.md` | Risks and mitigations |
| `deploy.md` | Deploy checklist + integration + runbook (merged) |
| `adr/README.md` | ADR process + link to template |

**Do not export as standing docs** — session/ephemeral content lives in
`workflow-state.yaml` only:

- `execution-plan.md`, `config-spec.md`, `research-brief.md`, `context-brief.md`
- Audit/verification outputs: `qa-report.md`, `e2e-report.md`, `deploy-report.md`, etc.
- Session logs: `hotfix-log.md`, `bug-reports/`, `service-health-reports/`

Update exported `doc-planner` skill and `doc-types.md` to reflect this manifest.

## Export workflow

Copy this checklist and track progress:

```
Export progress:
- [ ] Intake complete (target, mode, tiers, placeholders, conflicts)
- [ ] Copy pipeline skills 00–19 + shared refs
- [ ] Generalize domain skills (data-management, service-health)
- [ ] Copy workflow-state-manager agent only
- [ ] Copy tiered rules (core + selected optional)
- [ ] Sanitize all copied files (interview-driven)
- [ ] Write docs/ stubs from merged templates
- [ ] Write empty workflow-state.yaml template
- [ ] Run post-export validation checklist
- [ ] Present summary + unresolved [TBD] items to user
```

### Step 1 — Copy inventory

**Always copy** (see [reference.md §Copy inventory](reference.md#copy-inventory)):

- `.cursor/skills/00-context` through `19-address-pr-review`
- Shared skill files: `pipeline-preamble.md`, `workflow-state-reference.md`,
  `workflow-state-agent-protocol.md`, `considerations.md`, `connectivity-gates.md`,
  `deployment-catalog.md`, `template-registry.md`, `build-planner/`, `doc-planner/`,
  `gather-context/`, `audit-docs/`, `audit-licenses/`, `verify-build/`, `build-executor/`,
  `build-planner/`, `deploy-verify/`, `bug-investigation/`, `github-projects/` (if user wants)
- `.cursor/agents/workflow-state-manager.md` only

**Generalize in place** (rewrite deployed service domain → generic templates):

- `data-management/SKILL.md` — corpus/DB staging → generic data-asset staging
- `15-service-health/SKILL.md` — RAG smokes → generic deployed-service health tiers
- `config-validator/SKILL.md` — remove deployed service env var names; use `METAR`

**Never copy by default** (confirm via AskQuestion if user wants optional extras):

- `.cursor/hooks/` and `hooks.json`
- `.cursor/agents/` except `workflow-state-manager.md`
- `modal-jobs-monorepo/`, `clone-repos/`, `modal-proxy-header/` (org-specific)
- deployed service-only rules (see [reference.md §deployed service-only rules](reference.md#deployed-service-only-rules))

**Rules layout in target:**

```
.cursor/rules/
  core/          # always exported
  optional/      # user-selected tiers only
```

Flatten to `.cursor/rules/*.mdc` only if the target project already uses a flat layout and
user explicitly requests it.

### Step 2 — Interview-driven sanitization

For **each** copied file (skills, rules, agents, templates):

1. Read the file.
2. Apply [reference.md §Mustache bindings](reference.md#mustache-bindings) for identity fields.
3. **Delete** deployed service-only sections (RAG apps, chat-rag, DigitalOcean operator specs,
   bilingual i18n EV cycles, deployed service env vars, feature IDs F1–F31 table content).
4. **Replace** with generic placeholders or empty template sections (`## Feature Scope` with
   `{{FEATURE_TABLE}}` or instructional comment).
5. When ambiguous (shared pattern vs deployed service-specific), use **AskQuestion** — cite the file
   and line range; do not guess.

Sanitization is **agent-led**, not fully scripted. Use
[scripts/grep_deployed-service_leftovers.sh](scripts/grep_deployed-service_leftovers.sh) only for verification,
not as the primary strip mechanism.

### Step 3 — Docs stubs

Generate from `.cursor/skills/doc-planner/templates/` with merges per
[reference.md §Doc merge map](reference.md#doc-merge-map):

- Build `docs/deploy.md` from deployment-integration + deploy-checklist + staging-runbook
  sections (new merged template in export if not present in source).
- Fold acceptance-criteria bullets into `feature-list.md` template.
- Fold QA gates into `test-plan.md` template.
- Fold roadmap, data-management, glossary into `spec.md` template.

Use Mustache placeholders throughout. Remove HTML comment instruction blocks before presenting
as final stubs unless user wants generator comments retained.

### Step 4 — workflow-state.yaml

Copy [templates/workflow-state.yaml](templates/workflow-state.yaml) to the target repo root.
Fill `project.name` and `project.description` from intake placeholders. All stages `pending`;
empty `git_history`, `artifacts`, `issue_log`, `decisions_log`.

### Step 5 — Post-export validation

Run the checklist in [reference.md §Validation checklist](reference.md#validation-checklist).
Then:

```bash
bash .cursor/skills/export-cursor-toolkit/scripts/grep_deployed-service_leftovers.sh "{{TARGET_REPO}}"
```

Fix or flag every hit. Do not declare export complete while critical hits remain.

## Merge mode notes

- If target already has `.cursor/skills/pipeline/`, diff before overwrite; prefer merging
  shared reference updates into existing files when the user chose `ask` conflict policy.
- Never copy deployed service `workflow-state.yaml` session data — always the empty template.
- Never copy `docs/` content from deployed service — only generate stubs.

## Output summary

Present to the user:

1. Target path and mode
2. Files copied / generalized / excluded counts
3. Optional rule tiers included
4. Standing docs created
5. Validation results (pass / warnings / manual follow-ups)
6. List of `[TBD]` / `{{PLACEHOLDER}}` fields the target project must fill before pipeline stage 01

## Examples

**Greenfield:**

```
User: Export the cursor toolkit to ~/projects/acme-api — new repo, include Modal optional rules.

→ Intake → copy inventory → sanitize with interviews → docs/ stubs + workflow-state.yaml
→ validate → summary with PROJECT_NAME=acme-api
```

**Merge:**

```
User: Merge sanitized skills into ../legacy-app without hooks.

→ merge mode, conflict policy ask → skip existing hooks → overlay skills/rules
→ flag 3 files with manual merge needed
```
