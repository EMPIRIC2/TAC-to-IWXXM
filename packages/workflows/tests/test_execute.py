"""Unit tests for execute / stages."""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import pytest
from workflows.execute import WorkflowExecuteError

from workflows import WorkflowDefinition, WorkflowMessage, execute
from workflows import stages as stages_mod

pytestmark = pytest.mark.unit


def _def(*, pipeline: list[str] | None = None) -> WorkflowDefinition:
    return WorkflowDefinition(
        id="unit",
        version="1.0.0",
        pipeline=pipeline
        or [
            "validate-tac",
            "convert-iwxxm",
            "validate-xsd",
            "validate-schematron",
        ],
        profile_id="annex3",
        iwxxm_version="2025-2",
        on_valid_store=["iwxxm_reports"],
        on_invalid_store=["quarantine-db"],
    )


def _msg(tac: str = "METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005=") -> WorkflowMessage:
    return WorkflowMessage(tac=tac, product="METAR", job_id="j1")


def test_execute_happy_path_metar() -> None:
    result = execute(_msg(), _def())
    assert result.ok is True
    assert result.xml
    assert result.stage_failed is None
    assert "METAR" in result.xml


def test_execute_lint_fail() -> None:
    result = execute(_msg("NOT A METAR"), _def())
    assert result.ok is False
    assert result.stage_failed in {"validate-tac", "convert-iwxxm"}


def test_unknown_stage_fail_closed() -> None:
    with pytest.raises(WorkflowExecuteError, match="unknown stage"):
        execute(_msg(), _def(pipeline=["validate-tac", "nope"]))


def test_convert_fail(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        stages_mod,
        "tac_lint_fn",
        lambda *_a, **_k: SimpleNamespace(ok=True, issues=[]),
    )
    monkeypatch.setattr(
        stages_mod,
        "tac2iwxxm_convert_fn",
        lambda *_a, **_k: SimpleNamespace(
            ok=False,
            xml=None,
            issues=[
                SimpleNamespace(severity="error", code="CONVERT_FAIL", message="x"),
            ],
        ),
    )
    result = execute(_msg(), _def())
    assert result.ok is False
    assert result.stage_failed == "convert-iwxxm"


def test_schematron_skipped_soft_pass(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        stages_mod,
        "tac_lint_fn",
        lambda *_a, **_k: SimpleNamespace(ok=True, issues=[]),
    )
    monkeypatch.setattr(
        stages_mod,
        "tac2iwxxm_convert_fn",
        lambda *_a, **_k: SimpleNamespace(
            ok=True,
            xml="<iwxxm:METAR/>",
            issues=[],
        ),
    )

    def _validate(*_a: Any, **kwargs: Any) -> Any:
        levels = kwargs.get("levels") or ()
        if "schematron" in levels:
            return SimpleNamespace(
                ok=False,
                issues=[
                    SimpleNamespace(
                        severity="error",
                        code="SCHEMATRON_SKIPPED",
                        message="sch skipped",
                    ),
                    SimpleNamespace(severity="warning", code="NOTE", message="info"),
                ],
            )
        return SimpleNamespace(ok=True, issues=[])

    monkeypatch.setattr(stages_mod, "iwxxm_validate_fn", _validate)
    result = execute(_msg(), _def())
    assert result.ok is True
    assert result.stage_failed is None
    assert all(i.code != "SCHEMATRON_SKIPPED" for i in result.issues)
    assert any(i.code == "NOTE" for i in result.issues)


def test_store_ports(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        stages_mod,
        "tac_lint_fn",
        lambda *_a, **_k: SimpleNamespace(ok=True, issues=[]),
    )
    monkeypatch.setattr(
        stages_mod,
        "tac2iwxxm_convert_fn",
        lambda *_a, **_k: SimpleNamespace(ok=True, xml="<x/>", issues=[]),
    )
    monkeypatch.setattr(
        stages_mod,
        "iwxxm_validate_fn",
        lambda *_a, **_k: SimpleNamespace(ok=True, issues=[]),
    )
    seen: list[str] = []

    def store_valid(_r: Any, *, sink: str) -> None:
        seen.append(f"ok:{sink}")

    result = execute(_msg(), _def(), store_valid=store_valid)
    assert result.ok is True
    assert seen == ["ok:iwxxm_reports"]


def test_skip_validate_tac(monkeypatch: pytest.MonkeyPatch) -> None:
    def boom(*_a: Any, **_k: Any) -> Any:
        raise AssertionError("lint should be skipped")

    monkeypatch.setattr(stages_mod, "tac_lint_fn", boom)
    monkeypatch.setattr(
        stages_mod,
        "tac2iwxxm_convert_fn",
        lambda *_a, **_k: SimpleNamespace(ok=True, xml="<x/>", issues=[]),
    )
    monkeypatch.setattr(
        stages_mod,
        "iwxxm_validate_fn",
        lambda *_a, **_k: SimpleNamespace(ok=True, issues=[]),
    )
    result = execute(_msg(), _def(), skip_stages=frozenset({"validate-tac"}))
    assert result.ok is True


def test_xsd_missing_xml(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        stages_mod,
        "tac_lint_fn",
        lambda *_a, **_k: SimpleNamespace(ok=True, issues=[]),
    )
    monkeypatch.setattr(
        stages_mod,
        "tac2iwxxm_convert_fn",
        lambda *_a, **_k: SimpleNamespace(ok=True, xml="", issues=[]),
    )
    # empty xml treated as convert fail
    result = execute(_msg(), _def())
    assert result.ok is False
    assert result.stage_failed == "convert-iwxxm"


def test_load_by_id_string() -> None:
    result = execute(_msg(), "f8-metar-ingest-default")
    assert result.workflow_id == "f8-metar-ingest-default"
    assert result.ok is True
