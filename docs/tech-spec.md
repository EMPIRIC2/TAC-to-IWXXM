# Technical specification hub

> **Corpus ID:** `tech-spec` — see [CORPUS.md](CORPUS.md).  
> **Architecture / components:** [spec.md](spec.md) (`system-spec`).  
> **Last updated:** 2026-07-12 (S007)

This file is the **entry point** for runtime, configuration, deployment, and dependency
truth. Detail lives in the satellites below — do not duplicate long tables here.

## Satellites

| Doc | What it owns |
|-----|----------------|
| [config-spec.md](config-spec.md) | `config/{env}.json` fields, defaults, precedence, non-secret vs secret |
| [env-contract.md](env-contract.md) | Env var names, who consumes them (API / frontend / CI) |
| [deploy.md](deploy.md) | Render (and related) topology, deploy commands, integration checklist |
| [dependency-inventory.md](dependency-inventory.md) | Allowed packages; new deps need `[Decision]` + inventory update |

## Related corpus

| Doc | Role |
|-----|------|
| [spec.md](spec.md) | System architecture, component map, hard constraints |
| [api-contract.md](api-contract.md) | HTTP routes and payloads |
| [adr/](adr/) | Architecture decisions that constrain tech choices |
| [decisions/tech-decisions.md](decisions/tech-decisions.md) | Interview / stage tech decision log |

## Parity checklist (quick)

When changing runtime behavior or deploy/config:

1. Config key or env name exists in **config-spec** / **env-contract** (exact spelling).
2. Deploy topology and service names match **deploy.md**.
3. New library appears in **dependency-inventory** (or AskQuestion before adding).
4. Component boundaries still match **spec.md** §Component Overview.
5. If the change is a non-obvious trade-off, add or cite an **ADR**.
