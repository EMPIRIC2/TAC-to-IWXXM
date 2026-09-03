"""Unit tests for workflow loader."""

from __future__ import annotations

from pathlib import Path

import pytest
from workflows.loader import (
    WorkflowLoadError,
    load_workflow,
    parse_workflow_mapping,
    resolve_env_refs,
)

pytestmark = pytest.mark.unit


def test_resolve_env_refs(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("INGEST_PROFILE", "iwxxm_us")
    assert resolve_env_refs("${ENV:INGEST_PROFILE}") == "iwxxm_us"
    assert resolve_env_refs({"a": "${ENV:MISSING}"}) == {"a": ""}


def test_load_f8_default() -> None:
    definition = load_workflow("f8-metar-ingest-default")
    assert definition.id == "f8-metar-ingest-default"
    assert definition.pipeline == [
        "validate-tac",
        "convert-iwxxm",
        "validate-xsd",
        "validate-schematron",
    ]
    assert "iwxxm_reports" in definition.on_valid_store
    assert "quarantine-db" in definition.on_invalid_store


def test_reject_embedded_credentials() -> None:
    with pytest.raises(WorkflowLoadError, match="credentials"):
        parse_workflow_mapping(
            {
                "id": "bad",
                "version": "1.0.0",
                "pipeline": ["validate-tac"],
                "profile": {"id": "postgres://user:secret@host/db"},
            }
        )


def test_missing_workflow(tmp_path: Path) -> None:
    with pytest.raises(WorkflowLoadError, match="not found"):
        load_workflow("nope", workflows_dir=tmp_path)


def test_pipeline_required() -> None:
    with pytest.raises(WorkflowLoadError, match="pipeline"):
        parse_workflow_mapping({"id": "x", "version": "1"})
