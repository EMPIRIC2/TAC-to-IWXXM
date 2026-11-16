"""Convert path best-effort station health recorder wiring."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from unittest.mock import MagicMock

import pytest
from src.routers.conversion import _ConvertAccumulator, _record_convert_station_health


@dataclass
class _FakeResult:
    tac_input: str | None
    name: str = "sample"


@pytest.mark.parametrize(
    ("results", "expect_calls"),
    [
        ([_FakeResult("METAR KJFK 010000Z 18008KT 10SM FEW040 15/07 A3005=")], 1),
        ([_FakeResult(""), _FakeResult(None)], 0),
        (
            [
                _FakeResult("METAR KJFK 010000Z 18008KT 10SM FEW040 15/07 A3005="),
                _FakeResult("METAR KLAX 010000Z 25010KT 10SM FEW020 18/10 A2990="),
            ],
            2,
        ),
    ],
)
def test_record_convert_station_health_success_paths(
    monkeypatch: pytest.MonkeyPatch,
    results: list[_FakeResult],
    expect_calls: int,
) -> None:
    calls: list[dict[str, Any]] = []

    def _fake_record(**kwargs: Any) -> dict[str, Any]:
        calls.append(kwargs)
        return {"icao": "KJFK"}

    monkeypatch.setattr(
        "src.services.station_health_recorder.record_tac_observation",
        _fake_record,
        raising=False,
    )
    # Patch import target used inside helper
    import src.services.station_health_recorder as recorder

    monkeypatch.setattr(recorder, "record_tac_observation", _fake_record)

    acc = _ConvertAccumulator()
    acc.results.extend(results)  # type: ignore[arg-type]
    _record_convert_station_health(acc, product="METAR", lint_report=None)
    assert len(calls) == expect_calls
    for call in calls:
        assert call["source"] == "convert"
        assert call["convert_ok"] is True


def test_record_convert_station_health_skips_blank_lint_codes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[dict[str, Any]] = []

    def _fake_record(**kwargs: Any) -> dict[str, Any]:
        calls.append(kwargs)
        return {"icao": "KJFK"}

    import src.services.station_health_recorder as recorder

    monkeypatch.setattr(recorder, "record_tac_observation", _fake_record)
    lint_report = MagicMock()
    lint_report.issues = [
        MagicMock(severity="error", code=""),
        MagicMock(severity="warning", code="  "),
        MagicMock(severity="error", code="MISSING_DIGIT"),
    ]
    acc = _ConvertAccumulator()
    acc.results.append(_FakeResult("METAR KJFK 010000Z 18008KT 10SM FEW040 15/07 A3005="))  # type: ignore[arg-type]
    acc.issues.append(MagicMock(code=""))  # type: ignore[arg-type]
    _record_convert_station_health(acc, product="METAR", lint_report=lint_report)
    assert len(calls) == 1
    assert calls[0]["lint_error_count"] == 2
    assert calls[0]["lint_warning_count"] == 1
    assert calls[0]["issue_codes"] == ["MISSING_DIGIT"]


def test_record_convert_station_health_failure_is_swallowed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def _boom(**_kwargs: Any) -> None:
        raise RuntimeError("db down")

    import src.services.station_health_recorder as recorder

    monkeypatch.setattr(recorder, "record_tac_observation", _boom)
    acc = _ConvertAccumulator()
    acc.results.append(_FakeResult("METAR KJFK 010000Z 18008KT 10SM FEW040 15/07 A3005="))  # type: ignore[arg-type]
    _record_convert_station_health(acc, product="METAR")


def test_record_convert_station_health_import_failure_is_noop(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Cover conversion.py import guard when recorder module is unavailable."""
    import builtins

    real_import = builtins.__import__

    def _boom(name: str, *args: Any, **kwargs: Any) -> Any:
        if name == "src.services.station_health_recorder":
            raise ImportError("forced missing recorder")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", _boom)
    acc = _ConvertAccumulator()
    acc.results.append(_FakeResult("METAR KJFK 010000Z 18008KT 10SM FEW040 15/07 A3005="))  # type: ignore[arg-type]
    _record_convert_station_health(acc, product="METAR", lint_report=None)
