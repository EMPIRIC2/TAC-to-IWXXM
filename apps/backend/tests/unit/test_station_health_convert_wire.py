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
