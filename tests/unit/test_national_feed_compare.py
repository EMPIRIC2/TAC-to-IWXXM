"""Canonical TAC comparison for TC-LIVE-FEEDS. No network."""

from __future__ import annotations

import pytest
from tests.live.national_feeds import (
    canonical_report,
    ensure_product_keyword,
    extract_knmi_tac,
    iwxxm_root_local_name,
    knmi_latest_filename,
    observation_key,
    reports_by_station,
)


def test_canonical_report_ignores_keyword_auto_and_terminator() -> None:
    norway = "EDDF 231520Z 21004KT 160V310 CAVOK 21/05 Q1023 NOSIG="
    awc = "METAR EDDF 231520Z AUTO 21004KT 160V310 CAVOK 21/05 Q1023 NOSIG"
    assert canonical_report(norway) == canonical_report(awc)


def test_canonical_report_drops_taf_amendment_marker() -> None:
    amended = "TAF AMD YSSY 230530Z 2306/2406 11008KT CAVOK="
    plain = "TAF YSSY 230530Z 2306/2406 11008KT CAVOK"
    assert canonical_report(amended) == canonical_report(plain)


def test_observation_key_uses_metar_time_or_taf_period() -> None:
    assert observation_key("ENGM 231520Z 20003KT=", "METAR") == "231520Z"
    assert observation_key("TAF EGLL 231100Z 2312/2418 31008KT", "TAF") == "2312/2418"


def test_ensure_product_keyword_is_idempotent() -> None:
    assert ensure_product_keyword("VHHH 231500Z NOSIG=", "METAR") == (
        "METAR VHHH 231500Z NOSIG="
    )
    assert ensure_product_keyword("METAR VHHH 231500Z NOSIG=", "METAR").startswith(
        "METAR VHHH"
    )


def test_reports_by_station_joins_taf_continuation_lines() -> None:
    body = (
        "TAF AMD ENGM 231515Z 2315/2412 16005KT 9999 BKN012\n"
        "  BECMG 2315/2317 BKN008\n"
        "  TEMPO 2316/2320 2500 -DZRA BR\n"
    )
    found = reports_by_station(body, ("ENGM",), newest="first")
    assert "TEMPO 2316/2320" in found["ENGM"]
    assert "BECMG 2315/2317" in found["ENGM"]


def test_reports_by_station_keeps_requested_end_of_file() -> None:
    body = "EGLL 231450Z 31008KT=\nEGLL 231520Z 31010KT=\nEDDF 231520Z CAVOK="
    found = reports_by_station(body, ("EGLL", "EDDF"), newest="last")
    assert found["EGLL"].startswith("EGLL 231520Z")
    assert "EDDF" in found


def test_iwxxm_root_local_name() -> None:
    xml = '<iwxxm:METAR xmlns:iwxxm="http://icao.int/iwxxm/2025-2"/>'
    assert iwxxm_root_local_name(xml) == "METAR"


def test_extract_knmi_tac_from_iwxxm_comment() -> None:
    body = (
        "0000305901\nLANL80 EHRD 231552\n"
        '<?xml version="1.0" ?><iwxxm:METAR xmlns:iwxxm="http://icao.int/iwxxm/3.0">'
        "<!-- METAR EHRD 231555Z AUTO 27007KT 9999 NSC 19/14 Q1020 -->"
        "</iwxxm:METAR>"
    )
    assert extract_knmi_tac(body) == [
        "METAR EHRD 231555Z AUTO 27007KT 9999 NSC 19/14 Q1020"
    ]


def test_knmi_latest_filename() -> None:
    payload: dict[str, object] = {"files": [{"filename": "metar_latest.txt"}]}
    assert knmi_latest_filename(payload) == "metar_latest.txt"


def test_knmi_latest_filename_rejects_empty_list() -> None:
    with pytest.raises(ValueError, match="empty"):
        knmi_latest_filename({"files": []})
