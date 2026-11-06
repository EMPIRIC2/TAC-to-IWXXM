"""TC-EVDR-001 — staging TAF residual families (legacy decode + pack)."""

from __future__ import annotations

from tac_decoding.decode import decode_tac
from tac_decoding.match import match_tac
from tac_decoding.packs import load_packs


def _codes(tac: str) -> dict[str, str]:
    result = decode_tac(tac, product="TAF")
    return {segment.code: segment.explanation for segment in result.segments}


def _pack_codes(tac: str) -> dict[str, str]:
    packs = {pack.id: pack for pack in load_packs()}
    result = match_tac(tac, packs["taf"])
    return {span.code: span.explanation for span in result.spans}


def test_taf_tx_tn_temperature_extremes() -> None:
    tac = "TAF KJFK 031730Z 0318/0424 18008KT P6SM SKC TX26/0320Z TNM02/0311Z="
    codes = _codes(tac)
    assert "maximum" in codes["TX26/0320Z"].lower()
    assert "26" in codes["TX26/0320Z"]
    assert "minimum" in codes["TNM02/0311Z"].lower()
    assert codes["TX26/0320Z"]
    residual_text = " ".join(r.text for r in decode_tac(tac, product="TAF").residuals)
    assert "TX26/0320Z" not in residual_text
    assert "TNM02/0311Z" not in residual_text
    pack = _pack_codes("TX26/0320Z TNM02/0311Z")
    assert "TX26/0320Z" in pack
    assert "TNM02/0311Z" in pack


def test_taf_spaced_cavok_decodes_as_ceiling_and_visibility_ok() -> None:
    """Live HAAB typo ``C A V O K`` is one CAVOK span (#1553 coverage)."""
    tac = "TAF HAAB 032130Z 0400/0506 14008KT C A V O K"
    result = decode_tac(tac, product="TAF")
    cavok = [s for s in result.segments if s.code.replace(" ", "") == "CAVOK" or s.code == "C A V O K"]
    assert cavok
    assert any("ceiling" in s.explanation.lower() for s in cavok)
    residual_text = " ".join(r.text for r in result.residuals)
    assert "C A V O K" not in residual_text


def test_taf_cavok_nsw_vv_inter() -> None:
    tac = (
        "TAF YSSY 030400Z 0306/0412 06015KT CAVOK "
        "FM031200 08012KT 9999 NSW SCT030 "
        "INTER 0318/0322 4000 SHRA BKN012 "
        "TEMPO 0400/0406 VV002="
    )
    codes = _codes(tac)
    assert codes["CAVOK"] == "Ceiling and visibility OK"
    assert "significant weather" in codes["NSW"].lower()
    assert codes["INTER"].lower().startswith("intermittent")
    assert "200 ft" in codes["VV002"]
    residual_text = " ".join(r.text for r in decode_tac(tac, product="TAF").residuals)
    for token in ("CAVOK", "NSW", "INTER", "VV002"):
        assert token not in residual_text
    pack = _pack_codes("CAVOK NSW INTER VV002 VV///")
    assert pack["CAVOK"]
    assert pack["NSW"]
    assert pack["INTER"]
    assert pack["VV002"]
    assert pack["VV///"]
    missing = _codes("TAF YSSY 030400Z 0306/0412 06015KT VV///=")
    assert missing["VV///"] == "Vertical visibility not reported"


def test_taf_qnh_ins_and_wind_shear() -> None:
    tac = "TAF KNHK 031200Z 0312/0412 21010KT P6SM SCT040 WS020/21040KT QNH2966INS="
    codes = _codes(tac)
    assert "29.66" in codes["QNH2966INS"]
    assert "altimeter" in codes["QNH2966INS"].lower() or "qnh" in codes["QNH2966INS"].lower()
    assert "2000 ft" in codes["WS020/21040KT"] or "2,000" in codes["WS020/21040KT"]
    assert "210" in codes["WS020/21040KT"]
    residual_text = " ".join(r.text for r in decode_tac(tac, product="TAF").residuals)
    assert "QNH2966INS" not in residual_text
    assert "WS020/21040KT" not in residual_text
    pack = _pack_codes("WS020/21040KT QNH2966INS")
    assert pack["QNH2966INS"]
    assert pack["WS020/21040KT"]


def test_taf_fractional_sm_and_turbulence_icing() -> None:
    tac = "TAF KNID 031800Z 0318/0418 27012KT 1 1/2SM BR BKN008 520003 621305="
    result = decode_tac(tac, product="TAF")
    codes = {segment.code: segment.explanation for segment in result.segments}
    residual_text = " ".join(r.text for r in result.residuals)
    assert "1/2SM" in codes or any("statute" in e.lower() for e in codes.values())
    assert "520003" not in residual_text
    assert "621305" not in residual_text
    assert "turbulence" in codes["520003"].lower()
    assert "icing" in codes["621305"].lower()
    pack = _pack_codes("520003 621305 1/2SM")
    assert pack["520003"]
    assert pack["621305"]
