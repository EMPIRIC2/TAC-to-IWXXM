# workflows

Thin MET-lib workflow executor: load git `workflows/*.yaml`, run a fixed stage
registry, return `WorkflowResult`. MIT licensed.

Implements ADR-042 MVP (`execute(message, workflow)`). Apps (F8 worker) remain thin
callers. This package has **no** FastAPI, Supabase, or SQLAlchemy imports — store /
quarantine via optional injected ports.

## Install (from source)

```bash
# from the monorepo root
uv sync --package workflows
```

Requires Python ≥ 3.12.

## Quick start

```python
from workflows import WorkflowMessage, execute

result = execute(
    WorkflowMessage(tac="METAR KJFK ...=", product="METAR", job_id="1"),
    "f8-metar-ingest-default",
)
assert result.ok
```

## Reference workflow

See repo-root `workflows/f8-metar-ingest-default.yaml`.
