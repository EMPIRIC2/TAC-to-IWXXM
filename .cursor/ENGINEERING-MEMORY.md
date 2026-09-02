# Engineering Memory — workspace install

**Installed:** 2026-08-31 (EV-095 portable paths / [#1095](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1095))

| Item | Path |
|------|------|
| Plugin (workspaceOpen) | `$EM_ENGINEERING_MEMORY_ROOT/cursor-plugin` (or sibling / in-repo; resolved at runtime) |
| MCP | `.cursor/mcp.json` (prefer `${userHome}/...` when under `$HOME`) |
| Pack symlink | `.cursor/pack` → plugin pack (re-created by install per machine) |
| CLI | `.cursor/bin/` (`verify`, `session-store`, `memory-hook`) |
| CLI symlinks | `.cursor/skills/bin/` → `../../bin/` |
| Hook templates | `.cursor/hooks/pack/` (scope_check, feature_drift + lib) |
| Bootstrap | `.cursor/hooks/pack/bootstrap-engineering-memory.sh` |
| Cursor session hooks | `sessionStart` / `sessionEnd` → `.cursor/hooks/pack/cursor-session-*.sh` |
| Hook config | `.cursor/hooks/config/` (TAC scope-map, feature-map) |
| Plugin rules | Via `workspaceOpen` plugin — not copied to `.cursor/rules/` |
| EM root (Neo4j venv) | `$EM_ENGINEERING_MEMORY_ROOT` (default sibling or `~/Documents/GitHub/spec-dev-knowledge-graph`) |
| Project id | `tac-to-iwxxm` (from `EMPIRIC2/TAC-to-IWXXM` git remote) |

## Project-only skills (kept local)

| Skill / ref | Purpose |
|-------------|---------|
| `deep-research-domain-handoff` | Evolve deep-research handoff prompts + user gates (EV-097) |
| `mine-domain-sources` | Domain mining → `docs/domain/` |
| `monorepo-migration-checklist` | ADR-003 monorepo migration |
| `connectivity-gates.md` | H4–H6′ browser/API gates |
| `considerations.md` | TAC pipeline detail |
| `deployment-catalog.md` | Render deploy targets |
| `protocol-card.md` | Pack orchestrator quick ref |
| `template-registry.md` | Service archetypes |

Pack duplicates and numbered `00–19` live under `.cursor/skills/_archive/`.

## Graph database access

**Prerequisite:** Neo4j running in the engineering-memory repo (`docker compose up -d`).

### Health

```bash
.cursor/bin/memory-hook check
```

### Resolve project

```bash
.cursor/bin/memory-hook resolve-project-id
# → {"project_id": "tac-to-iwxxm"}
```

### Retrieve knowledge (decisions, patterns, docs)

```bash
.cursor/bin/memory-hook retrieve \
  --project-id tac-to-iwxxm \
  --query "METAR conversion validation deploy"
```

### Build recommendations (advisory envelope)

```bash
.cursor/bin/memory-hook recommend \
  --project-id tac-to-iwxxm \
  --query "verification gates before merge"
```

### MCP tools (preferred in agent chat)

After **Reload Window**, use Cursor MCP **engineering-memory** (see tools in MCP panel).

### Re-ingest corpus / git

```bash
EM_ROOT="${EM_ENGINEERING_MEMORY_ROOT:-$HOME/Documents/GitHub/spec-dev-knowledge-graph}"
PY="$EM_ROOT/packages/engineering-memory/.venv/bin/python"
cd "$EM_ROOT"
# load EM .env without sourcing comments/special chars — see install docs

"$PY" -m engineering_memory.cli ingest corpus \
  --project-id tac-to-iwxxm \
  --docs-root "$OLDPWD/docs"

"$PY" -m engineering_memory.cli ingest git \
  --project-id tac-to-iwxxm \
  --repo-path "$OLDPWD" \
  --limit 100
```

### Optional: semantic embeddings

Token-overlap retrieval works without extras. For embedding search:

```bash
cd "${EM_ENGINEERING_MEMORY_ROOT:-$HOME/Documents/GitHub/spec-dev-knowledge-graph}/packages/engineering-memory"
source .venv/bin/activate
pip install sentence-transformers
```

## Re-install

```bash
EM_ENGINEERING_MEMORY_ROOT="${EM_ENGINEERING_MEMORY_ROOT:-$HOME/Documents/GitHub/spec-dev-knowledge-graph}"
"$EM_ENGINEERING_MEMORY_ROOT/cursor-plugin/scripts/install-workspace.sh" "$PWD"
```

Reload Cursor after pack/plugin updates.

See [MIGRATED-TO-PLUGIN.md](MIGRATED-TO-PLUGIN.md) and [docs/decisions/ev-023-plugin-migration.md](../docs/decisions/ev-023-plugin-migration.md). Portable-path policy: [docs/decisions/ev-095-em-portable-paths.md](../docs/decisions/ev-095-em-portable-paths.md).
