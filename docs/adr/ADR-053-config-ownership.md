# ADR-053: Config file ownership

## Status: Accepted

## Context

Toolchain and runtime settings are split across files that no longer match how the repo runs. Root lint rules live in `ruff.toml` while root `pyproject.toml` also has a `[tool.ruff]` block and packages extend the standalone file. Optional Compose stacks live in overlay files that scripts must pass with `-f`. Product-family quality checks are near-copies of the same workflow. `render.yaml` still describes a suspended Render blueprint after DOKS became the live deploy path ([Corpus: adr/ADR-033], [Corpus: adr/ADR-034]).

This does not add a product feature. It is workspace tooling under [Corpus: product §M5] and [Corpus: tech-spec].

## Decision

| Owner | What it owns |
|-------|----------------|
| Root `pyproject.toml` `[tool.ruff]` | The workspace Ruff rule set. Delete `ruff.toml`. Packages keep `extend` and point it at `../../pyproject.toml`. Do not copy the rule set into each package. |
| `docker-compose.yml` | The wis2box and mock-BYOC services, still behind profiles `wis2box` and `mock-byoc`. Delete the two overlay files after callers stop passing them as extra `-f` files. Default `docker compose up` does not start those profiles. |
| `.github/workflows/` reusable workflow | The shared quality-check steps. Each existing per-family workflow file stays, keeps its `name:`, and keeps its path filters. |
| `deploy/doks/` | Live staging and prod deploy. Delete `render.yaml` and update references that would dangle. |
| `start-dev-servers.sh` | Local API and UI launch. Delete `apps/backend/scripts/start_dev.sh`, `scripts/launchers/launch_api.sh`, and `scripts/launchers/launch_gui.sh`, and update their READMEs and bats tests. |

Build order is those launcher, Ruff, Compose, and workflow edits first, then `render.yaml`. Each edit runs the full local CI suite before it is committed.

## Consequences

- Lint behavior stays the same only if the whole `ruff.toml` rule set moves. The small exclude block already in `pyproject.toml` is merged, not used as a replacement.
- Compose callers and docs that name the overlay files must change in the same edit as the fold.
- GitHub check names stay stable because the thin workflow files remain.
- Docs that still tell operators to keep `render.yaml` are updated, including the Render decommission note.
- `Brewfile`, `config/*.json`, and the DOKS overlays stay. They are separate owners.

## Alternatives considered

- Leave `ruff.toml` as the extend target. Rejected: two Ruff owners at the repo root.
- Start wis2box and mock-BYOC on every `docker compose up`. Rejected: those stacks are optional.
- Replace the family workflows with one matrix workflow. Rejected: matrix cells rename the GitHub checks.
- Keep `render.yaml` as a historical blueprint. Rejected for this cycle: the live path is DOKS, and the file was chosen for removal.

[Corpus: tech-spec] [Corpus: deploy] [Corpus: adr/ADR-033] [Corpus: adr/ADR-034] [Corpus: product §M5]
