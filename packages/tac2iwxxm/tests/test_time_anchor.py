"""Bulletin time anchor: operator dates, example pins, impossible days."""

from __future__ import annotations

import pytest
from tac2iwxxm.time_anchor import anchor_from_bulletin_date, fit_year_month, iso_stamp

from tac2iwxxm import convert


def test_fit_year_month_steps_back_until_the_day_exists() -> None:
    assert fit_year_month(2023, 6, 31) == (2023, 5)
    assert fit_year_month(2026, 10, 8) == (2026, 10)


def test_fit_year_month_steps_into_the_previous_year() -> None:
    assert fit_year_month(2026, 0, 15) == (2025, 12)


def test_fit_year_month_stops_when_every_candidate_month_rejects_the_day(monkeypatch: pytest.MonkeyPatch) -> None:
    def _reject(*_args: object) -> None:
        raise ValueError("nope")

    monkeypatch.setattr("tac2iwxxm.time_anchor.date", _reject)
    with pytest.raises(ValueError, match="no month contains"):
        fit_year_month(2026, 10, 15)


def test_anchor_from_a_year_month_does_not_slice_the_text() -> None:
    assert anchor_from_bulletin_date("20261013") == "2026-10"


def test_taf_bulletin_date_sets_the_issue_month() -> None:
    result = convert(
        "TAF TNCM 081200Z 0812/0912 14006KT 9999 FEW020=",
        product="TAF",
        bulletin_date="2026-10-13",
    )
    assert result.ok
    assert result.xml is not None
    assert "2026-10-08T12:00:00Z" in result.xml


def test_fit_year_month_rejects_a_day_outside_1_to_31() -> None:
    with pytest.raises(ValueError, match="calendar day"):
        fit_year_month(2026, 10, 32)


def test_iso_stamp_uses_time_anchor_when_present() -> None:
    ir = {"time_anchor": "2026-10", "station": "YUDO"}
    assert iso_stamp(ir, 8, 12, 0, legacy="2012-08") == "2026-10-08T12:00:00Z"


def test_iso_stamp_keeps_legacy_prefix_without_an_anchor() -> None:
    assert iso_stamp({"station": "TNCM"}, 8, 12, 0, legacy="2023-06") == "2023-06-08T12:00:00Z"


def test_convert_without_bulletin_date_keeps_the_example_month() -> None:
    result = convert(
        "METAR TNCM 081200Z 14006KT 9999 FEW020 28/24 Q1013=",
        product="METAR",
    )
    assert result.ok
    assert result.xml is not None
    assert "2023-06-08T12:00:00Z" in result.xml
    assert "2026-10-08T12:00:00Z" not in result.xml


def test_convert_bulletin_date_sets_the_issue_month() -> None:
    result = convert(
        "METAR TNCM 081200Z 14006KT 9999 FEW020 28/24 Q1013=",
        product="METAR",
        bulletin_date="2026-10-13",
    )
    assert result.ok
    assert result.xml is not None
    assert "2026-10-08T12:00:00Z" in result.xml


def test_convert_bulletin_date_moves_an_impossible_day_to_the_previous_month() -> None:
    result = convert(
        "METAR TNCM 311200Z 14006KT 9999 FEW020 28/24 Q1013=",
        product="METAR",
        bulletin_date="2023-06-15",
    )
    assert result.ok
    assert result.xml is not None
    assert "2023-06-31" not in result.xml
    assert "2023-05-31T12:00:00Z" in result.xml


def test_convert_rejects_a_bulletin_date_that_is_not_a_date() -> None:
    result = convert(
        "METAR TNCM 081200Z 14006KT 9999 FEW020 28/24 Q1013=",
        product="METAR",
        bulletin_date="not-a-date",
    )
    assert result.ok is False
    assert result.issues[0].code == "INVALID_BULLETIN_DATE"


def test_sigmet_bulletin_date_replaces_the_2012_example_year() -> None:
    tac = (
        "SYGC SIGMET 1 VALID 081200/081600 SYCJ-\n"
        "SYCJ GEORGETOWN FIR EMBD TS OBS AT 1200Z WI N0630 E05800 - "
        "N0700 E05900 - N0600 E05930 - N0630 E05800 TOP FL310 MOV NW 15KT INTSF="
    )
    result = convert(tac, product="SIGMET", bulletin_date="2026-10-13")
    assert result.ok
    assert result.xml is not None
    assert "2012-08" not in result.xml
    assert "2026-10-08T12:00:00Z" in result.xml
