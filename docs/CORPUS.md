# Canonical documentation corpus

**Single source of truth for skills.** Before design, parity, scope, or hotfix triage work,
read the rows below that apply — do not invent alternate doc sets.

> Skills and rules must cite paths from this file (e.g. `[Corpus: system-spec]`,
> `[Corpus: adr/ADR-00N]`). Folder layout: [README.md](README.md).

## Minimal corpus (design + parity)

| ID | Role | Path | Skills use it to… |
|----|------|------|-------------------|
| **product** | Approved features & acceptance | [feature-list.md](feature-list.md) | Scope (F1–F22 / M1–M6); reject out-of-list work |
| **journeys** | End-user journeys | [user-journeys.md](user-journeys.md) | E2E / verify-impl sign-off (UJ-*) |
| **system-spec** | Architecture, components, constraints | [spec.md](spec.md) | Design parity vs `apps/` + `packages/` + `vendor/` |
| **tech-spec** | Runtime / config / deploy / deps hub | [tech-spec.md](tech-spec.md) | Config names, env, deploy topology, dependency pins |
| **api** | HTTP contract | [api-contract.md](api-contract.md) | Request/response/error shapes |
| **tests** | Test matrix & gates | [test-plan.md](test-plan.md) | Parity checks, smoke TC-IDs, CI expectations |
| **adr** | Architecture decisions | [adr/](adr/) ([index](adr/README.md)) | Non-obvious tech choices; cite ADR-NNN |
| **decisions** | Interview / evolve decision logs | [decisions/](decisions/) | Trace *why* a standing doc says X |

### Tech-spec satellites (via [tech-spec.md](tech-spec.md))

| Path | Topic |
|------|--------|
| [config-spec.md](config-spec.md) | Config files, defaults, validation rules |
| [env-contract.md](env-contract.md) | Environment variable contract |
| [deploy.md](deploy.md) | Deploy targets, integration, runbook |
| [dependency-inventory.md](dependency-inventory.md) | Allowed dependencies & licenses |

## Not in the minimal corpus

These are useful but **not** required for every design/parity pass:

| Path | Role |
|------|------|
| [skill-routing.md](skill-routing.md) | Which pipeline skill to invoke |
| [typing-policy.md](typing-policy.md) | Lint/type strictness |
| [hotfix-log.md](hotfix-log.md) | Hotfix index |
| [ops/](ops/), [guides/](guides/), [domain/](domain/) | Runbooks, narrative guides, domain deep-dives |
| [reports/](reports/), [sessions/](sessions/), [bug-reports/](bug-reports/), [context/](context/), [ARCHIVE/](ARCHIVE/) | Ephemeral / historical |

Session artifacts stay under `docs/sessions/{id}/` — see [sessions-reference](../.cursor/skills/sessions-reference.md).

## Parity check protocol

When a skill says “check corpus parity” or “spec conformance”:

1. **Scope** — Does the change map to **product** (`feature-list.md`)? If no → `[Scope Drift]`.
2. **Design** — Does behavior match **system-spec** + **api** (+ **adr** if a decision exists)?
3. **Runtime** — Do names/URLs/env match **tech-spec** (and its satellites)?
4. **Verification** — Are assertions grounded in **tests** (`test-plan.md`) and **journeys**?
5. **Decisions** — If code and corpus disagree, check **decisions/** + **adr/** before patching; raise `[Contradiction]` / `[Ambiguity]` via AskQuestion — do not silently “fix around” the corpus.

Cite as: `[Corpus: <id>]` or `[Corpus: <path> §section]`.

## Skill obligations

| Skill / rule | Must read at least |
|--------------|-------------------|
| All stages (first hop) | This file’s band for the stage + [protocol-card](../.cursor/skills/protocol-card.md) |
| 01–03 (product) | product, journeys, decisions |
| 04–06 (tech) | system-spec, tech-spec, adr, dependency-inventory |
| 07–11 (build/verify) | product, system-spec, api, tests, journeys |
| 12–13 (deploy) | tech-spec, deploy, env-contract |
| 14-hotfix | product + system-spec; then tech-spec / api / tests as symptom requires |
| 15-service-health | tech-spec, deploy, env-contract |
| 16-evolve | CORPUS rows for **touched features only** (not always full minimal set) |
| plan-adherence / spec-adherence rules | this file + rows above |

Do **not** preload `docs/domain/**` or guides unless the session scope is domain mining.

## Change control

- **Corpus membership** changes require AskQuestion `[Decision]` and an ADR or `decisions/` log entry.
- Moving a corpus file requires updating this table and grep-fixing `.cursor/skills` + `.cursor/rules`.
- Do not add new standing root docs without updating this file.
