"""Emit-time group trace for every converted product."""

from __future__ import annotations

import re
from pathlib import Path

import pytest
from tac2iwxxm.convert import convert
from tac2iwxxm.group_trace import _emits_for, _occurrence, trace_emitted_groups, trace_entries

_FIXTURES = Path(__file__).parent / "fixtures"

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


def test_trace_shifts_offsets_and_skips_blank_text() -> None:
    assert trace_emitted_groups("   ", "METAR") == []
    assert trace_emitted_groups(METAR, "NOT_A_PRODUCT") == []
    shifted = trace_entries([(METAR, 4)], "METAR")
    assert shifted[0]["start"] == 4
    assert shifted[0]["token"] == "METAR"


def test_occurrence_shares_an_element_or_opens_a_new_one() -> None:
    assert _occurrence({}, "TAF", "previous") == 0
    assert _occurrence({"TAF": 1}, "TAF", "previous") == 0
    assert _occurrence({}, "changeForecast", "next") == 0
    assert _occurrence({"changeForecast": 1}, "changeForecast", "next") == 1
    assert _occurrence({}, "cloud", "emit") == 0
    assert _emits_for("missing", "wind", "18004KT") == ()
    assert _emits_for("taf", "equal", "=") == ()


def _opens(xml: str, element: str) -> int:
    return len(re.findall(rf"<(?:[A-Za-z0-9]+:)?{re.escape(element)}(?=[\s>/])", xml))


def _assert_first_elements_exist(tac: str, product: str) -> None:
    rows = trace_emitted_groups(tac, product)
    assert rows
    result = convert(tac, product=product, preview=True)
    assert result.xml
    seen: set[str] = set()
    for row in rows:
        if row["element"] in seen:
            continue
        seen.add(row["element"])
        assert _opens(result.xml, row["element"]) > row["occurrence"], row


def test_trace_follows_taf_groups_into_the_preview() -> None:
    basic = (_FIXTURES / "product_matrix" / "taf_basic.tac").read_text()
    _assert_first_elements_exist(basic, "TAF")
    wind = next(row for row in trace_emitted_groups(basic, "TAF") if row["token"] == "13005MPS")
    assert wind["element"] == "surfaceWind"
    becmg = "TAF YUDO 151800Z 1600/1618 13005MPS 9000 BKN020 BECMG 1602/1604 15010MPS="
    changes = [row for row in trace_emitted_groups(becmg, "TAF") if row["element"] == "changeForecast"]
    assert [row["token"] for row in changes] == ["BECMG"]
    prob = "TAF YUDO 151800Z 1600/1618 13005MPS 9000 BKN020 PROB30 TEMPO 1608/1612 2000 RA="
    shared = [row for row in trace_emitted_groups(prob, "TAF") if row["token"] in {"PROB30", "TEMPO"}]
    assert [row["occurrence"] for row in shared] == [0, 0]
    amended = "TAF AMD YUDO 151800Z 1600/1618 13005MPS 9000 BKN020="
    amd = next(row for row in trace_emitted_groups(amended, "TAF") if row["token"] == "AMD")
    assert amd["element"] == "TAF"
    assert amd["occurrence"] == 0
    cavok = "TAF YUDO 151800Z 1600/1618 13005MPS CAVOK="
    marked = next(row for row in trace_emitted_groups(cavok, "TAF") if row["token"] == "CAVOK")
    assert marked["element"] == "MeteorologicalAerodromeForecast"
    nsc = "TAF YUDO 151800Z 1600/1618 13005MPS 9999 NSC="
    cloud = next(row for row in trace_emitted_groups(nsc, "TAF") if row["token"] == "NSC")
    assert cloud["element"] == "cloud"


def test_trace_follows_other_products_into_the_preview() -> None:
    cases = (
        ("SIGMET", _FIXTURES / "product_matrix" / "sigmet_basic.tac"),
        ("AIRMET", _FIXTURES / "product_matrix" / "airmet_basic.tac"),
        ("VAA", _FIXTURES / "product_matrix" / "vaa_basic.tac"),
        ("TCA", _FIXTURES / "product_matrix" / "tca_basic.tac"),
        ("SWXA", _FIXTURES / "annex3_golden" / "swxa_a7_3.tac"),
        ("VONA", _FIXTURES / "annex3_golden" / "vona_a7_1.tac"),
        ("SIGMET", _FIXTURES / "annex3_golden" / "sigmet_va_eggx.tac"),
        ("SIGMET", _FIXTURES / "annex3_golden" / "sigmet_a6_2_tc.tac"),
    )
    for product, path in cases:
        _assert_first_elements_exist(path.read_text(), product)


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
