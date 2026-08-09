"""Unit coverage for pipeline failure / soft-pass branches (EV-047 T2.5.4)."""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import pytest
from metar_worker.pipeline import process_job
from metar_worker.poller import IngestJob

pytestmark = pytest.mark.unit


def _job(tac: str = "METAR KJFK 231751Z NIL=") -> IngestJob:
    return IngestJob(
        job_id="pipe-1",
        product="METAR",
        tac=tac,
        source_url="https://example.test/feed",
    )


def test_process_job_skip_lint_bypasses_tac_lint(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[str] = []

    def boom_lint(*_a: Any, **_k: Any) -> Any:
        calls.append("lint")
        raise AssertionError("lint should be skipped")

    monkeypatch.setattr("metar_worker.pipeline.tac_lint", boom_lint)
    monkeypatch.setattr(
        "metar_worker.pipeline.tac2iwxxm_convert",
        lambda *_a, **_k: SimpleNamespace(
            ok=True,
            xml="<iwxxm:METAR/>",
            issues=[],
        ),
    )
    monkeypatch.setattr(
        "metar_worker.pipeline.iwxxm_validate",
        lambda *_a, **_k: SimpleNamespace(ok=True, issues=[]),
    )
    result = process_job(_job(), skip_lint=True)
    assert result.ok is True
    assert result.xml == "<iwxxm:METAR/>"
    assert calls == []


def test_process_job_convert_fail(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "metar_worker.pipeline.tac_lint",
        lambda *_a, **_k: SimpleNamespace(ok=True, issues=[]),
    )
    monkeypatch.setattr(
        "metar_worker.pipeline.tac2iwxxm_convert",
        lambda *_a, **_k: SimpleNamespace(
            ok=False,
            xml=None,
            issues=[
                SimpleNamespace(
                    severity="error",
                    code="CONVERT_FAIL",
                    message="cannot convert",
                )
            ],
        ),
    )
    result = process_job(_job())
    assert result.ok is False
    assert result.stage_failed == "convert"
    assert result.issues[0]["code"] == "CONVERT_FAIL"


def test_process_job_convert_ok_but_empty_xml(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "metar_worker.pipeline.tac_lint",
        lambda *_a, **_k: SimpleNamespace(ok=True, issues=[]),
    )
    monkeypatch.setattr(
        "metar_worker.pipeline.tac2iwxxm_convert",
        lambda *_a, **_k: SimpleNamespace(ok=True, xml="", issues=[]),
    )
    result = process_job(_job())
    assert result.ok is False
    assert result.stage_failed == "convert"


def test_process_job_iwxxm_validate_blocking_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "metar_worker.pipeline.tac_lint",
        lambda *_a, **_k: SimpleNamespace(ok=True, issues=[]),
    )
    monkeypatch.setattr(
        "metar_worker.pipeline.tac2iwxxm_convert",
        lambda *_a, **_k: SimpleNamespace(
            ok=True,
            xml="<iwxxm:METAR/>",
            issues=[],
        ),
    )
    monkeypatch.setattr(
        "metar_worker.pipeline.iwxxm_validate",
        lambda *_a, **_k: SimpleNamespace(
            ok=False,
            issues=[
                SimpleNamespace(
                    severity="error",
                    code="XSD_ERROR",
                    message="schema fail",
                )
            ],
        ),
    )
    result = process_job(_job())
    assert result.ok is False
    assert result.stage_failed == "iwxxm_validate"
    assert result.xml == "<iwxxm:METAR/>"
    assert any(i["code"] == "XSD_ERROR" for i in result.issues)


def test_process_job_schematron_skipped_soft_pass(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "metar_worker.pipeline.tac_lint",
        lambda *_a, **_k: SimpleNamespace(ok=True, issues=[]),
    )
    monkeypatch.setattr(
        "metar_worker.pipeline.tac2iwxxm_convert",
        lambda *_a, **_k: SimpleNamespace(
            ok=True,
            xml="<iwxxm:METAR/>",
            issues=[],
        ),
    )
    monkeypatch.setattr(
        "metar_worker.pipeline.iwxxm_validate",
        lambda *_a, **_k: SimpleNamespace(
            ok=False,
            issues=[
                SimpleNamespace(
                    severity="error",
                    code="SCHEMATRON_SKIPPED",
                    message="sch skipped",
                ),
                SimpleNamespace(
                    severity="warning",
                    code="NOTE",
                    message="info",
                ),
            ],
        ),
    )
    result = process_job(_job())
    assert result.ok is True
    assert result.stage_failed is None
    assert all(i["code"] != "SCHEMATRON_SKIPPED" for i in result.issues)
    assert any(i["code"] == "NOTE" for i in result.issues)
