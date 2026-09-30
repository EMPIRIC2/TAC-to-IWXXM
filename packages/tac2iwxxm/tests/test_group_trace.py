"""Emit-time group trace for METAR and SPECI."""

from __future__ import annotations

import pytest
from tac2iwxxm.group_trace import trace_emitted_groups, trace_entries

METAR = "METAR KJFK 121251Z 18004KT 10SM FEW250 SCT040 22/14 A3012 NOSIG="


def test_trace_pairs_groups_with_emitted_elements_in_order() -> None:
    rows = trace_emitted_groups(METAR, "METAR")
    wind = next(row for row in rows if row["token"] == "18004KT")
    assert wind["element"] == "surfaceWind"
    assert wind["occurrence"] == 0
    assert wind["scope"] == "block"
    clouds = [row for row in rows if row["element"] == "CloudLayer"]
    assert [row["token"] for row in clouds] == ["FEW250", "SCT040"]
    assert [row["occurrence"] for row in clouds] == [0, 1]
    temps = [row for row in rows if row["token"] == "22/14"]
    assert [row["element"] for row in temps] == ["airTemperature", "dewpointTemperature"]
    assert rows[0]["element"] == "METAR"
    assert rows[0]["scope"] == "line"


def test_trace_shifts_offsets_and_skips_other_products() -> None:
    assert trace_emitted_groups("   ", "METAR") == []
    assert trace_emitted_groups(METAR, "TAF") == []
    assert trace_entries([(METAR, 4)], "TAF") == []
    shifted = trace_entries([(METAR, 4)], "METAR")
    assert shifted[0]["start"] == 4
    assert shifted[0]["token"] == "METAR"


def test_trace_returns_empty_when_the_pack_is_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "tac2iwxxm.group_trace.pack_id_for_product",
        lambda _product, _tac: "missing",
    )
    assert trace_emitted_groups(METAR, "METAR") == []


def test_trace_returns_empty_when_matching_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    def _boom() -> list[object]:
        raise ValueError("packs unavailable")

    monkeypatch.setattr("tac2iwxxm.group_trace.load_packs", _boom)
    assert trace_emitted_groups(METAR, "METAR") == []
