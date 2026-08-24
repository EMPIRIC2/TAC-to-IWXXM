# Engineering Memory — workspace install

**Installed:** 2026-08-24 (EV-024)

| Item | Path |
|------|------|
| Plugin (workspaceOpen) | `/Users/bigme/Documents/GitHub/spec-dev-knowledge-graph/cursor-plugin` |
| MCP | `.cursor/mcp.json` → `engineering-memory` stdio server |
| Pack symlink | `.cursor/pack` → plugin pack (orchestrators, spec-*, build-*, verify) |
| CLI | `.cursor/bin/` (`verify`, `session-store`, `memory-hook`) |
| CLI symlinks | `.cursor/skills/bin/` → `../../bin/` |
| Hook templates | `.cursor/hooks/pack/` (scope_check, feature_drift) |
| Hook config | `.cursor/hooks/config/` (TAC scope-map, feature-map) |
| Plugin rules | Via `workspaceOpen` plugin — not copied to `.cursor/rules/` |
| EM root (Neo4j venv) | `/Users/bigme/Documents/GitHub/spec-dev-knowledge-graph` |
| Project id | `tac-to-iwxxm` (from `EMPIRIC2/TAC-to-IWXXM` git remote) |

## Project-only skills (kept local)

| Skill / ref | Purpose |
|-------------|---------|
| `mine-domain-sources` | Domain mining → `docs/domain/` |
| `monorepo-migration-checklist` | ADR-003 monorepo migration |
| `connectivity-gates.md` | H4–H6′ browser/API gates |
| `considerations.md` | TAC pipeline detail |
| `deployment-catalog.md` | Render deploy targets |
| `protocol-card.md` | Pack orchestrator quick ref |
| `template-registry.md` | Service archetypes |

Pack duplicates and numbered `00–19` live under `.cursor/skills/_archive/`.

## Graph database access

**Prerequisite:** Neo4j running in spec-dev-knowledge-graph (`docker compose up -d`).

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

After **Reload Window**, use Cursor MCP **engineering-memory**:

| Tool | Use |
|------|-----|
| `health_check` | Neo4j connectivity |
| `list_projects` | Confirm `tac-to-iwxxm` |
| `retrieve_relevant_knowledge` | Ranked context for a query |
| `get_recommendations` | Advisory recommendations + ambiguities |
| `ingest_corpus` / `sync_repository` | Refresh graph from docs/git |
| `record_session` | Close pack sessions into graph |

### Re-ingest corpus / git

```bash
EM_ROOT="$HOME/Documents/GitHub/spec-dev-knowledge-graph"
PY="$EM_ROOT/packages/engineering-memory/.venv/bin/python"
cd "$EM_ROOT" && export $(grep -v '^#' .env | xargs)

"$PY" -m engineering_memory.cli ingest corpus \
  --project-id tac-to-iwxxm \
  --docs-root "$PWD/../TAC-to-IWXXM/TAC-to-IWXXM/docs"

"$PY" -m engineering_memory.cli ingest git \
  --project-id tac-to-iwxxm \
  --repo-path "$PWD/../TAC-to-IWXXM/TAC-to-IWXXM" \
  --limit 100
```

### Optional: semantic embeddings

Token-overlap retrieval works without extras. For embedding search:

```bash
cd "$EM_ROOT/packages/engineering-memory" && source .venv/bin/activate
pip install sentence-transformers
```

## Re-install

```bash
"$EM_ROOT/cursor-plugin/scripts/install-workspace.sh" "$PWD"
```

Reload Cursor after pack/plugin updates.

See [MIGRATED-TO-PLUGIN.md](MIGRATED-TO-PLUGIN.md) and [docs/decisions/ev-023-plugin-migration.md](../docs/decisions/ev-023-plugin-migration.md).
