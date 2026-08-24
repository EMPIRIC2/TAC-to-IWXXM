# Export Cursor Toolkit — Reference

## Copy inventory

### Pipeline skills (always)

| Path | Notes |
|------|-------|
| `.cursor/skills/00-context/` | Strip deployed service sibling-repo examples |
| `.cursor/skills/01-requirements/` | Update approved-doc manifest to minimal set |
| `.cursor/skills/02-verify-plan/` | |
| `.cursor/skills/03-plan-tooling/` | |
| `.cursor/skills/04-tech-plan/` | Ephemeral execution-plan → workflow-state only |
| `.cursor/skills/05-verify-tech/` | |
| `.cursor/skills/06-tech-tooling/` | References hooks — note "target configures hooks separately" |
| `.cursor/skills/07-build/` | |
| `.cursor/skills/08-verify-build/` | |
| `.cursor/skills/09-qa/` | Point qa gates at test-plan.md §QA |
| `.cursor/skills/10-e2e/` | Generic journey tiers |
| `.cursor/skills/11-verify-impl/` | |
| `.cursor/skills/12-verify-deploy/` | |
| `.cursor/skills/13-deploy-smoke/` | Reference deploy.md not deploy-checklist + runbook separately |
| `.cursor/skills/14-hotfix/` | Strip deployed service smoke URLs |
| `.cursor/skills/15-service-health/` | **Generalize** — see below |
| `.cursor/skills/16-evolve/` | + reference.md |
| `.cursor/skills/17-retrospective/` | + reference.md |
| `.cursor/skills/18-pr-review/` | + checklist.md, reference.md |
| `.cursor/skills/19-address-pr-review/` | + reference.md |
| `.cursor/skills/pipeline/` | Replace "deployed service (RAG + data management)" in description |

### Shared skill files (always)

- `pipeline-preamble.md`, `considerations.md`, `connectivity-gates.md`
- `workflow-state-reference.md`, `workflow-state-agent-protocol.md`
- `deployment-catalog.md`, `template-registry.md`
- `doc-planner/` (update `doc-types.md` manifest)
- `gather-context/`, `audit-docs/`, `audit-licenses/`
- `build-planner/`, `build-executor/`, `verify-build/`, `deploy-verify/`
- `bug-investigation/`

### Generalize (domain → template)

| Source | Action |
|--------|--------|
| `data-management/SKILL.md` | Rename conceptually to "data asset staging"; replace pgvector/corpus/Modal embed with `{{DATA_STORE}}`, `{{STAGING_COMMAND}}` |
| `15-service-health/SKILL.md` | Replace RAG ingest/query smokes with generic H0–H3 API/DB/live tiers; `{{STAGING_URL}}`, `{{HEALTH_ENDPOINT}}` |
| `config-validator/SKILL.md` | Replace `VECINITA_*` with `METAR_*` or generic validation rules |

### Exclude by default

| Path | Reason |
|------|--------|
| `.cursor/hooks/` | User choice: no hooks in export |
| `hooks.json` | Target project configures separately |
| `.cursor/agents/repo-researcher.md` | Not in minimal agent set |
| `.cursor/agents/paper-analyst.md` | Optional; 00-context can reference externally |
| `.cursor/agents/license-researcher.md` | Covered by audit-licenses skill |
| `modal-jobs-monorepo/` | CogniChem modal-jobs monorepo, not generic pipeline |
| `clone-repos/` | Org-specific multi-repo clone workflow |
| `modal-proxy-header/` | deployed service Modal proxy convention |

## Rule tiers

### core/ (always export)

| Rule | Sanitize |
|------|----------|
| `atomic-commits.mdc` | Replace deployed service CI parity commands with `uv run pytest tests`, `uv run ruff check src tests && uv run ruff format --check src tests` |
| `build-execution.mdc` | Generic execution-plan → workflow-state language |
| `spec-adherence.mdc` | Empty feature/component tables + instructions to fill from feature-list/spec |
| `plan-adherence.mdc` | Merge into spec-adherence or export as template with `{{FEATURE_TABLE}}` |
| `tdd.mdc` | Generic |
| `bug-investigation.mdc` | Generic paths `docs/bug-reports/`, `tests/bugs/` |

### optional/ (user selects at intake)

| Tier | Rules | When to include |
|------|-------|-----------------|
| `modal` | `modal-service-client-init.mdc`, `modal-image-deps.mdc`, `modal-llm-method-calls.mdc`, `factory-app-env-deps.mdc`, `job-terminal-state.mdc` | Target uses Modal workers |
| `browser` | `cors-browser-methods.mdc`, `connectivity-gates` cross-refs | Target has browser frontends |
| `typing` | `strict-typing.mdc`, `pydantic-field-metadata.mdc` | Target adopts ADR-style strict typing |
| `ci` | `ci-after-push.mdc` | Target uses GitHub Actions with similar watch script |
| `deploy-secrets` | `no-operator-spec-commits.mdc` | Target uses DO/Railway operator spec exports |

### deployed service-only rules (never export)

- `chat-rag-cold-start-retry.mdc`
- `chat-rag-llm-quality.mdc`
- `write-read-parity.mdc` (internal-write-api specific)
- `modal-proxy-header.mdc`
- `domain-vocabulary.mdc` (deployed service/RAG terms) — target generates fresh from 03-plan-tooling
- `constraint-enforcement.mdc` (RFantibody/deployed service pins) — target fills in 04-tech-plan
- `template-conformance.mdc` (RFantibody job template) — omit unless target is Modal job

## Mustache bindings

Apply at export time for identity and environment. Leave unknown values as literal
`{{PLACEHOLDER}}` for the target project.

| Binding | Example | Used in |
|---------|---------|---------|
| `METAR to IWXXM Backend` | Acme API | skills, docs, workflow-state |
| `https://github.com/joseph-c-mcguire/metar-to-IWXXM.git` | https://github.com/org/acme-api | README refs, clone-repos replacements |
| `joseph-c-mcguire` | acme | paths, package names |
| `docker` | render \| modal \| docker \| k8s | deploy.md, 12-verify-deploy |
| `{{STAGING_URL}}` | https://staging.example.com | service-health, deploy smokes |
| `METAR` | ACME | config-validator, env docs |
| `en` | en | remove deployed service bilingual defaults |
| `{{FEATURE_TABLE}}` | markdown table stub | plan-adherence, spec-adherence |
| `uv run pytest tests` | pytest / npm test | rules, CI refs |
| `uv run ruff check src tests && uv run ruff format --check src tests` | ruff / eslint | rules, hooks guidance |

**Strip patterns** (grep verification — should return zero hits after sanitization):

```
deployed service|deployed-service|VECINA|VECINITA
chat-rag|data-management-backend|data-management-frontend
internal-write-api|admin-fe-spec|prod\.env
LlamaIndex|pgvector|FastEmbed|bilingual.*corpus
F1.*Bilingual|EV-00[0-9]|ADR-01[0-9].*deployed-service
doctl apps spec get
```

Add project-specific patterns discovered during sanitization to the target's validation script
copy.

## Doc merge map

| Standing export file | Source templates / docs | Section mapping |
|---------------------|-------------------------|-----------------|
| `docs/spec.md` | `templates/spec.md` | + §Roadmap from `roadmap.md` + §Data from `data-management-plan.md` + §Glossary from `glossary.md` |
| `docs/feature-list.md` | `templates/feature-list.md` | + per-feature acceptance from `acceptance-criteria.md` |
| `docs/test-plan.md` | `templates/test-plan.md` | + §Quality assurance from 09-qa skill gates |
| `docs/deploy.md` | **new merged template** | §Checklist ← deploy-checklist; §Integration ← deployment-integration; §Runbook ← staging-runbook |
| `docs/user-journeys.md` | `templates/user-journeys.md` | Single file (not directory) |
| `docs/api-contract.md` | `templates/api-contract.md` | |
| `docs/dependency-inventory.md` | `templates/dependency-inventory.md` | |
| `docs/risk-register.md` | `templates/risk-register.md` | |
| `docs/adr/README.md` | `templates/adr.md` header + process | No deployed service ADR files |

### Dropped from standing set (ephemeral → workflow-state)

| Former doc | Replacement |
|------------|-------------|
| `execution-plan.md` | `workflow-state.yaml` §stages.* + build-planner session artifacts |
| `config-spec.md` | `workflow-state.yaml` or inline in spec during 04-tech-plan session |
| `research-brief.md` / `context-brief.md` | 00-context artifacts[]; not committed in minimal greenfield |
| `roadmap.md` | spec.md §Roadmap |
| `acceptance-criteria.md` | feature-list.md |
| `data-management-plan.md` | spec.md §Data |
| `glossary.md` | spec.md §Glossary |
| `deployment-integration.md` | deploy.md §Integration |
| `deploy-checklist.md` | deploy.md §Checklist |
| `staging-runbook.md` | deploy.md §Runbook |
| `config-spec.md` | ephemeral |

### doc-planner manifest update

Replace `doc-types.md` generation list with the nine standing files above. Mark merged sources
as "deprecated — see spec.md" in doc-planner interview prompts.

## Validation checklist

Manual review after export:

- [ ] No files under `.cursor/hooks/`
- [ ] `workflow-state.yaml` has all stages `pending`; no deployed service session history
- [ ] `docs/` contains exactly the nine standing files (+ `adr/` README only)
- [ ] `pipeline/SKILL.md` description does not mention deployed service
- [ ] `doc-planner` manifest matches minimal set
- [ ] `plan-adherence` / `spec-adherence` use `{{FEATURE_TABLE}}` not F1–F31
- [ ] `data-management` and `15-service-health` read as domain-agnostic templates
- [ ] Optional rule tiers match intake selection; no deployed service-only rules present
- [ ] `grep_deployed-service_leftovers.sh` exits 0
- [ ] Broken relative links: spot-check `workflow-state-reference.md`, `pipeline/SKILL.md`
- [ ] User summary lists all remaining `{{PLACEHOLDER}}` tokens

## Greenfield vs merge

| Aspect | Greenfield | Merge |
|--------|------------|-------|
| `docs/` | Create all stubs | Create missing only; AskQuestion on existing |
| `.cursor/skills/` | Full copy | Overlay; respect conflict policy |
| `workflow-state.yaml` | Write template | Write only if absent |
| Existing hooks | N/A | Leave untouched |
