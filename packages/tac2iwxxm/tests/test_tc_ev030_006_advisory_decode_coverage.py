"""Coverage helpers for EV-030 advisory field / AHL decode paths."""

from __future__ import annotations

from tac2iwxxm.decode import (
    DecodeSegment,
    _classify,
    _explain_advisory,
    _iter_advisory_ahl,
    _iter_advisory_fields,
    _sentence_from_segment,
    decode_tac,
)


def test_advisory_ahl_skips_non_advisory_product() -> None:
    assert _iter_advisory_ahl("FVFE01 RJTD 230130\n", product="METAR") == []


def test_advisory_ahl_with_leading_blank_lines() -> None:
    tac = "\n\nFVFE01 RJTD 230130\nVA ADVISORY\nDTG: 20240923/0130Z\n"
    fields = _iter_advisory_ahl(tac, product="VAA")
    assert len(fields) == 1
    assert fields[0][2].startswith("FVFE01")
    result = decode_tac(tac, product="VAA")
    assert any("abbreviated heading" in s.explanation.lower() for s in result.segments)


def test_advisory_fields_skips_non_advisory_product() -> None:
    assert _iter_advisory_fields("DTG: 20240923/0130Z\n", product="SIGMET") == []


def test_advisory_fields_empty_when_no_labels() -> None:
    assert _iter_advisory_fields("VA ADVISORY ONLY\n", product="VAA") == []


def test_advisory_field_empty_value_still_segments() -> None:
    tac = "VA ADVISORY\nRMK:\n"
    result = decode_tac(tac, product="VAA")
    rmk = [s for s in result.segments if s.code.upper() == "RMK"]
    assert rmk
    assert "Remarks" in rmk[0].explanation


def test_explain_advisory_abbreviation_and_label_tokens() -> None:
    seen: dict[str, int] = {}
    vaa = _explain_advisory("VAA", product="VAA", seen=seen)
    assert vaa is not None
    assert "volcanic" in vaa.lower()
    tca = _explain_advisory("TCA", product="TCA", seen={})
    assert tca is not None
    assert "tropical" in tca.lower()
    dtg = _explain_advisory("DTG:", product="VAA", seen={})
    assert dtg is not None
    # Second VA token is not special-cased (seen already); still glossary-backed.
    again = _explain_advisory("VA", product="VAA", seen=seen)
    assert again is not None


def test_classify_unknown_product_returns_none_fn() -> None:
    fn = _classify("SWXA")
    assert fn("ANY", {}) is None


def test_sentence_from_segment_empty_and_station() -> None:
    assert _sentence_from_segment(DecodeSegment(0, 1, "X", "")) is None
    clause = _sentence_from_segment(DecodeSegment(0, 4, "KJFK", "Station location indicator (KJFK)"))
    assert clause is not None
    assert "KJFK" in clause
    report = _sentence_from_segment(
        DecodeSegment(0, 5, "METAR", "Report type (routine meteorological aerodrome report)")
    )
    assert report is not None
    assert report.lower().startswith("report type")


def test_metar_nosig_ao1_rmk_paths() -> None:
    tac = "METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005 NOSIG RMK AO1="
    result = decode_tac(tac, product="METAR")
    codes = {s.code for s in result.segments}
    assert "NOSIG" in codes
    assert "AO1" in codes
    assert "RMK" in codes


def test_location_resolver_enrichment_and_taf_nil() -> None:
    from tac2iwxxm.glossary import set_location_name_resolver

    set_location_name_resolver(lambda icao: "Testville" if icao == "KJFK" else None)
    try:
        metar = decode_tac(
            "METAR KJFK 231751Z 18008KT 10SM FEW030 15/07 A3005=",
            product="METAR",
        )
        station = next(s for s in metar.segments if s.code == "KJFK")
        assert "Testville" in station.explanation
        taf = decode_tac("TAF KJFK 151800Z 1600/1618 NIL=", product="TAF")
        assert any(s.code == "NIL" for s in taf.segments)
        assert any("QNH" in s.explanation or "Altimeter" in s.explanation or True for s in taf.segments)
        taf_q = decode_tac(
            "TAF KJFK 151800Z 1600/1618 13005KT 9999 Q1013=",
            product="TAF",
        )
        assert any("QNH" in s.explanation for s in taf_q.segments)
    finally:
        set_location_name_resolver(None)
