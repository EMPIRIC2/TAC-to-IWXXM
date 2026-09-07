"""Load and validate WorkflowDefinition YAML (ADR-042)."""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import cast

import yaml

from workflows.models import WorkflowDefinition

_ENV_REF = re.compile(r"\$\{ENV:([A-Za-z_][A-Za-z0-9_]*)\}")
_CREDENTIAL_URL = re.compile(
    r"(?i)(?:[a-z][a-z0-9+.-]*://)[^/\s:@]+:[^/\s:@]+@",
)


class WorkflowLoadError(ValueError):
    """Raised when a workflow file is missing, malformed, or unsafe."""


def _find_workflows_dir(start: Path) -> Path | None:
    """Walk parents of ``start`` for a repo ``workflows/`` tree."""
    for parent in start.parents:
        candidate = parent / "workflows"
        if candidate.is_dir() and (candidate / "f8-metar-ingest-default.yaml").is_file():
            return candidate
    return None


def default_workflows_dir() -> Path:
    """
    Resolve the git-managed ``workflows/`` directory.

    Prefers ``WORKFLOWS_DIR``, then walks parents of this package for a
    ``workflows/`` tree containing ``f8-metar-ingest-default.yaml``, else
    ``Path.cwd() / "workflows"``.
    """
    env = os.environ.get("WORKFLOWS_DIR")
    if env:
        return Path(env)
    found = _find_workflows_dir(Path(__file__).resolve())
    if found is not None:
        return found
    return Path.cwd() / "workflows"


def resolve_env_refs(
    value: object,
    *,
    environ: dict[str, str] | None = None,
) -> object:
    """
    Recursively replace ``${ENV:NAME}`` in strings.

    Missing env vars resolve to empty string (caller may apply defaults).
    """
    env = environ if environ is not None else dict(os.environ)
    if isinstance(value, str):

        def _sub(match: re.Match[str]) -> str:
            return env.get(match.group(1), "")

        return _ENV_REF.sub(_sub, value)
    if isinstance(value, list):
        items = cast("list[object]", value)
        return [resolve_env_refs(item, environ=env) for item in items]
    if isinstance(value, dict):
        mapping = cast("dict[object, object]", value)
        return {str(k): resolve_env_refs(v, environ=env) for k, v in mapping.items()}
    return value


def assert_no_embedded_credentials(value: object, *, path: str = "$") -> None:
    """
    Fail-closed when a string looks like a URL with userinfo credentials.

    Parameters
    ----------
    value :
        Nested YAML structure after env resolve.
    path :
        JSON-pointer-like path for error messages.
    """
    if isinstance(value, str):
        if _CREDENTIAL_URL.search(value):
            msg = f"workflow rejects embedded credentials at {path}"
            raise WorkflowLoadError(msg)
        return
    if isinstance(value, list):
        items = cast("list[object]", value)
        for i, item in enumerate(items):
            assert_no_embedded_credentials(item, path=f"{path}[{i}]")
        return
    if isinstance(value, dict):
        mapping = cast("dict[object, object]", value)
        for key, item in mapping.items():
            assert_no_embedded_credentials(item, path=f"{path}.{key}")


def _sink_ids(block: object) -> list[str]:
    if not isinstance(block, dict):
        return []
    mapping = cast("dict[str, object]", block)
    store_obj: object = mapping.get("store") or []
    if not isinstance(store_obj, list):
        return []
    store = cast("list[object]", store_obj)
    out: list[str] = []
    for entry in store:
        if isinstance(entry, dict) and "sink" in entry:
            entry_map = cast("dict[str, object]", entry)
            out.append(str(entry_map["sink"]))
        elif isinstance(entry, str):
            out.append(entry)
    return out


def parse_workflow_mapping(data: dict[str, object]) -> WorkflowDefinition:
    """
    Build a :class:`WorkflowDefinition` from a resolved YAML mapping.

    Raises
    ------
    WorkflowLoadError
        On missing required fields or bad types.
    """
    assert_no_embedded_credentials(data)
    wid = data.get("id")
    if not isinstance(wid, str) or not wid.strip():
        raise WorkflowLoadError("workflow.id is required")
    version = data.get("version", "1.0.0")
    if not isinstance(version, str):
        raise WorkflowLoadError("workflow.version must be a string")
    pipeline_obj = data.get("pipeline")
    if not isinstance(pipeline_obj, list) or not pipeline_obj:
        raise WorkflowLoadError("workflow.pipeline must be a non-empty list")
    pipeline_items = cast("list[object]", pipeline_obj)
    if not all(isinstance(s, str) and s for s in pipeline_items):
        raise WorkflowLoadError("workflow.pipeline entries must be non-empty strings")
    pipeline_stages = [str(s) for s in pipeline_items]

    profile_block_obj: object = data.get("profile", {})
    if profile_block_obj is None:
        profile_block_obj = {}
    if not isinstance(profile_block_obj, dict):
        raise WorkflowLoadError("workflow.profile must be a mapping when present")
    profile_map = cast("dict[str, object]", profile_block_obj)
    raw_profile_id: object = profile_map.get("id") or "annex3"
    profile_id = str(raw_profile_id).strip() or "annex3"
    raw_iwxxm: object = profile_map.get("iwxxm_version") or "2025-2"
    iwxxm_version = str(raw_iwxxm).strip() or "2025-2"
    description = str(data.get("description") or "")

    return WorkflowDefinition(
        id=wid.strip(),
        version=version,
        pipeline=pipeline_stages,
        profile_id=profile_id.lower(),
        iwxxm_version=iwxxm_version,
        description=description,
        on_valid_store=_sink_ids(data.get("onValid")),
        on_invalid_store=_sink_ids(data.get("onInvalid")),
        raw=dict(data),
    )


def load_workflow(
    workflow_id: str,
    *,
    workflows_dir: Path | None = None,
    environ: dict[str, str] | None = None,
) -> WorkflowDefinition:
    """
    Load ``{workflows_dir}/{workflow_id}.yaml``.

    Parameters
    ----------
    workflow_id :
        File stem / workflow id.
    workflows_dir :
        Override search directory.
    environ :
        Optional env map for ``${ENV:}`` resolution (defaults to ``os.environ``).
    """
    root = workflows_dir or default_workflows_dir()
    path = root / f"{workflow_id}.yaml"
    if not path.is_file():
        msg = f"workflow not found: {path}"
        raise WorkflowLoadError(msg)
    try:
        loaded: object = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        msg = f"invalid YAML in {path}: {exc}"
        raise WorkflowLoadError(msg) from exc
    if not isinstance(loaded, dict):
        raise WorkflowLoadError(f"workflow root must be a mapping: {path}")
    loaded_raw = cast("dict[object, object]", loaded)
    loaded_map: dict[str, object] = {str(k): v for k, v in loaded_raw.items()}
    resolved = resolve_env_refs(loaded_map, environ=environ)
    if not isinstance(resolved, dict):
        raise WorkflowLoadError(f"workflow root must be a mapping after resolve: {path}")
    resolved_raw = cast("dict[object, object]", resolved)
    resolved_map: dict[str, object] = {str(k): v for k, v in resolved_raw.items()}
    return parse_workflow_mapping(resolved_map)


__all__ = [
    "WorkflowLoadError",
    "_find_workflows_dir",
    "assert_no_embedded_credentials",
    "default_workflows_dir",
    "load_workflow",
    "parse_workflow_mapping",
    "resolve_env_refs",
]
