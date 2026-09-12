# Canonical documentation corpus

**Single source of truth for skills.** Before design, parity, scope, or hotfix triage work,
read the rows below that apply — do not invent alternate doc sets.

> Skills and rules must cite paths from this file (e.g. `[Corpus: system-spec]`,
> `[Corpus: adr/ADR-00N]`). Folder layout: [README.md](README.md).
>
> **EV-docs-numpy-corpus:** default load is the **engineering spine** only. Domain and
> historical trees are opt-in or archived. See [decisions/ev-docs-numpy-corpus.md](decisions/ev-docs-numpy-corpus.md).

## Minimal corpus (design + parity)

| ID | Role | Path | Skills use it to… |
|----|------|------|-------------------|
| **product** | Approved features & acceptance | [feature-list.md](feature-list.md) | Scope (F*/M*); reject out-of-list work |
| **now** | Ticket-tuned eng index | [engineering/NOW.md](engineering/NOW.md) | Current open epics / priority work |
| **docstrings** | In-code documentation bar | [engineering/docstrings.md](engineering/docstrings.md) | NumPy / TSDoc / comment policy |
| **journeys** | End-user journeys | [user-journeys.md](user-journeys.md) | E2E / verify-impl sign-off (UJ-*) |
| **system-spec** | Architecture, components, constraints | [spec.md](spec.md) | Design parity vs `apps/` + `packages/` + `vendor/` |
| **tech-spec** | Runtime / config / deploy / deps hub | [tech-spec.md](tech-spec.md) | Config names, env, deploy topology, dependency pins |
| **api** | HTTP contract | [api-contract.md](api-contract.md) (+ OpenAPI as truth) | Request/response/error shapes |
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

## Opt-in (load only when the ticket needs it)

| Path | When |
|------|------|
| [domain/](domain/) (incl. profiles) | Domain mining, national/exchange profiles (e.g. CA_ECCC, F35/F36) |
| [guides/](guides/), [ops/](ops/) | Operator runbooks / narrative how-tos |
| [bug-reports/](bug-reports/) | Active hotfix investigation |
| [skill-routing.md](skill-routing.md), [typing-policy.md](typing-policy.md), [hotfix-log.md](hotfix-log.md) | Tooling / process satellites |

## Not in the corpus (do not use for design gates)

| Path | Status |
|------|--------|
| Legacy `docs/sessions/` tree | **Archiving** → orphan `docs-archive` after fixture promote; stub README only on default branch |
| `docs/ARCHIVE/`, `docs/context/`, `docs/evolve-report-EV-*.md`, `docs/reports/`, `docs/archives/`, `docs/retrospectives/` | **Archiving** with sessions |
| Full historical `workflow-state.yaml` blob | **Archiving**; root file becomes a stub |

**Session store (pack orchestrators):** live state at `~/.cursor/workflow/EMPIRIC2/TAC-to-IWXXM/sessions/{id}/` (`state.yaml`, `HANDOFF.md`). Do **not** open new pack cycles under `docs/sessions/`. See [.cursor/MIGRATED-TO-PLUGIN.md](../.cursor/MIGRATED-TO-PLUGIN.md).

## Parity check protocol

When a skill says “check corpus parity” or “spec conformance”:

1. **Scope** — Does the change map to **product** (`feature-list.md`) and **now** (open tickets)? If no → `[Scope Drift]`.
2. **Design** — Does behavior match **system-spec** + **api** (+ **adr** if a decision exists)?
3. **Runtime** — Do names/URLs/env match **tech-spec** (and its satellites)?
4. **Verification** — Are assertions grounded in **tests** (`test-plan.md`) and **journeys**?
5. **Decisions** — If code and corpus disagree, check **decisions/** + **adr/** before patching; raise `[Contradiction]` / `[Ambiguity]` via AskQuestion — do not silently “fix around” the corpus.

Cite as: `[Corpus: <id>]` or `[Corpus: <path> §section]`.

## Skill obligations

| Skill / rule | Must read at least |
|--------------|-------------------|
| All stages (first hop) | This file’s band for the stage + [protocol-card](../.cursor/skills/protocol-card.md) |
| Spec band | product, now, journeys, decisions |
| Tech band | system-spec, tech-spec, adr, dependency-inventory |
| Build band | product, system-spec, api, tests, journeys, docstrings (when touching public APIs) |
| Deploy | tech-spec, deploy, env-contract |
| `hotfix` | product + system-spec; then tech-spec / api / tests as symptom requires |
| Domain mining | **domain** opt-in + product |
| `evolve` / `brownfield` / `greenfield` | CORPUS rows for **touched features only**; every change cites `[Corpus: …]`; missing coverage → AskQuestion doc-add |

Pack skills load from **engineering-memory** plugin. Project-only: `mine-domain-sources`, `monorepo-migration-checklist`.

Do **not** preload `docs/domain/**`, guides, or archived session trees unless the session scope requires them.

## Change control

- **Corpus membership** changes require AskQuestion `[Decision]` and an ADR or `decisions/` log entry.
- Moving a corpus file requires updating this table and grep-fixing `.cursor/skills` + `.cursor/rules`.
- Do not add new standing root docs without updating this file.
