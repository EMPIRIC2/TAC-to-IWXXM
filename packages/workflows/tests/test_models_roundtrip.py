"""Workflow model field round-trips (construction / identity edges)."""

from __future__ import annotations

from dataclasses import asdict, replace

import pytest
from workflows.models import (
    StageIssue,
    WorkflowDefinition,
    WorkflowMessage,
    WorkflowResult,
)

pytestmark = pytest.mark.unit


def test_workflow_message_roundtrip_defaults_and_meta() -> None:
    msg = WorkflowMessage(tac="METAR KJFK NIL=", product="metar")
    assert msg.job_id == ""
    assert msg.meta == {}
    filled = replace(msg, job_id="j1", meta={"src": "unit"}, product="METAR")
    rebuilt = WorkflowMessage(**asdict(filled))
    assert rebuilt == filled
    assert rebuilt.meta["src"] == "unit"


def test_workflow_definition_roundtrip_store_lists() -> None:
    definition = WorkflowDefinition(
        id="roundtrip",
        version="1.2.3",
        pipeline=["validate-tac", "convert-iwxxm"],
        on_valid_store=["iwxxm_reports"],
        on_invalid_store=["quarantine-db"],
        description="unit",
        raw={"id": "roundtrip"},
    )
    rebuilt = WorkflowDefinition(**asdict(definition))
    assert rebuilt == definition
    assert rebuilt.on_valid_store == ["iwxxm_reports"]
    assert rebuilt.profile_id == "annex3"
    assert rebuilt.iwxxm_version == "2025-2"


def test_stage_issue_and_result_roundtrip_failure_shape() -> None:
    issue = StageIssue(
        stage="validate-xsd",
        severity="error",
        code="MISSING_XML",
        message="no XML to validate",
    )
    result = WorkflowResult(
        ok=False,
        workflow_id="roundtrip",
        product="METAR",
        profile="annex3",
        xml=None,
        issues=[issue],
        stage_failed="validate-xsd",
        job_id="j-rt",
    )
    rebuilt = WorkflowResult(**{**asdict(result), "issues": [StageIssue(**asdict(issue))]})
    assert rebuilt.ok is False
    assert rebuilt.stage_failed == "validate-xsd"
    assert rebuilt.issues[0].code == "MISSING_XML"
    assert asdict(rebuilt.issues[0]) == asdict(issue)
