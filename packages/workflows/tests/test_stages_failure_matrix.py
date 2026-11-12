"""Stage failure matrix — hard IWXXM fail and store-port errors."""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import pytest
from workflows.execute import execute
from workflows.models import WorkflowDefinition, WorkflowMessage, WorkflowResult
from workflows.stages import run_validate_schematron

from workflows import stages as stages_mod

pytestmark = pytest.mark.unit


def _msg() -> WorkflowMessage:
    return WorkflowMessage(
        tac="METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005=",
        product="METAR",
        job_id="j-fail",
    )


def _def(*, pipeline: list[str] | None = None) -> WorkflowDefinition:
    return WorkflowDefinition(
        id="unit-fail",
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


def test_stage_validate_iwxxm_hard_fail(monkeypatch: pytest.MonkeyPatch) -> None:
    """Non-soft Schematron error must halt the pipeline (hard fail)."""
    monkeypatch.setattr(
        stages_mod,
        "tac_lint_fn",
        lambda *_a, **_k: SimpleNamespace(ok=True, issues=[]),
    )
    monkeypatch.setattr(
        stages_mod,
        "tac2iwxxm_convert_fn",
        lambda *_a, **_k: SimpleNamespace(ok=True, xml="<iwxxm:METAR/>", issues=[]),
    )

    def _validate(*_a: Any, **kwargs: Any) -> Any:
        levels = kwargs.get("levels") or ()
        if "schematron" in levels:
            return SimpleNamespace(
                ok=False,
                issues=[
                    SimpleNamespace(
                        severity="error",
                        code="SCHEMATRON_RULE_FAIL",
                        message="rule broken",
                    ),
                ],
            )
        return SimpleNamespace(ok=True, issues=[])

    monkeypatch.setattr(stages_mod, "iwxxm_validate_fn", _validate)
    result = execute(_msg(), _def())
    assert result.ok is False
    assert result.stage_failed == "validate-schematron"
    assert any(i.code == "SCHEMATRON_RULE_FAIL" for i in result.issues)

    # Direct stage call: hard error is blocking (unlike SCHEMATRON_SKIPPED).
    outcome = run_validate_schematron(
        _msg(),
        _def(pipeline=["validate-schematron"]),
        xml="<iwxxm:METAR/>",
    )
    assert outcome.ok is False
    assert outcome.issues[0].code == "SCHEMATRON_RULE_FAIL"


def test_stage_disseminate_port_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """Store-invalid port exceptions propagate (disseminate/store failure path)."""
    monkeypatch.setattr(
        stages_mod,
        "tac_lint_fn",
        lambda *_a, **_k: SimpleNamespace(
            ok=False,
            issues=[SimpleNamespace(severity="error", code="E", message="bad")],
        ),
    )

    def store_invalid(_result: WorkflowResult, *, sink: str) -> None:
        raise RuntimeError(f"store sink failed: {sink}")

    with pytest.raises(RuntimeError, match="store sink failed: quarantine-db"):
        execute(_msg(), _def(pipeline=["validate-tac"]), store_invalid=store_invalid)
