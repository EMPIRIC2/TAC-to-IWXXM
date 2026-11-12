"""Pipeline hard-fail stage mapping (EV-stage coverage expansion).

[Corpus: tests] — lint / convert / IWXXM validate failures quarantine-ready.
"""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import pytest
from metar_worker.pipeline import process_job
from metar_worker.poller import IngestJob

from workflows import stages as stages_mod

pytestmark = pytest.mark.unit


def _job(tac: str = "METAR KJFK 231751Z NIL=") -> IngestJob:
    return IngestJob(
        job_id="hard-fail-1",
        product="METAR",
        tac=tac,
        source_url="https://example.test/feed",
    )


def test_process_job_lint_hard_fail(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        stages_mod,
        "tac_lint_fn",
        lambda *_a, **_k: SimpleNamespace(
            ok=False,
            issues=[
                SimpleNamespace(
                    severity="error",
                    code="TAC_SYNTAX",
                    message="bad TAC",
                )
            ],
        ),
    )
    result = process_job(_job("NOT A METAR"))
    assert result.ok is False
    assert result.stage_failed == "lint"
    assert result.xml is None
    assert any(i["code"] == "TAC_SYNTAX" for i in result.issues)


def test_process_job_convert_hard_fail(monkeypatch: pytest.MonkeyPatch) -> None:
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
                SimpleNamespace(
                    severity="error",
                    code="CONVERT_HARD_FAIL",
                    message="cannot emit IWXXM",
                )
            ],
        ),
    )
    result = process_job(_job())
    assert result.ok is False
    assert result.stage_failed == "convert"
    assert result.issues[0]["stage"] == "convert"
    assert result.issues[0]["code"] == "CONVERT_HARD_FAIL"


def test_process_job_iwxxm_validate_hard_fail(monkeypatch: pytest.MonkeyPatch) -> None:
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
    monkeypatch.setattr(
        stages_mod,
        "iwxxm_validate_fn",
        lambda *_a, **_k: SimpleNamespace(
            ok=False,
            issues=[
                SimpleNamespace(
                    severity="error",
                    code="XSD_HARD_FAIL",
                    message="schema reject",
                )
            ],
        ),
    )
    result = process_job(_job())
    assert result.ok is False
    assert result.stage_failed == "iwxxm_validate"
    assert result.xml == "<iwxxm:METAR/>"
    assert any(i["code"] == "XSD_HARD_FAIL" for i in result.issues)


def test_process_job_unknown_stage_id_passes_through(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Unmapped workflow stage ids remain as-is on PipelineResult."""

    def _fake_execute(*_a: Any, **_k: Any) -> Any:
        return SimpleNamespace(
            ok=False,
            xml=None,
            stage_failed="custom-gate",
            issues=[
                SimpleNamespace(
                    stage="custom-gate",
                    severity="error",
                    code="CUSTOM",
                    message="blocked",
                )
            ],
        )

    monkeypatch.setattr("metar_worker.pipeline.execute", _fake_execute)
    monkeypatch.setattr(
        "workflows.loader.load_workflow",
        lambda _id: SimpleNamespace(
            id="f8-metar-ingest-default",
            version="1",
            pipeline=[],
            profile_id="annex3",
            iwxxm_version="2025-2",
            description="",
            on_valid_store=[],
            on_invalid_store=[],
            raw={},
        ),
    )
    result = process_job(_job())
    assert result.ok is False
    assert result.stage_failed == "custom-gate"
    assert result.issues[0]["stage"] == "custom-gate"
