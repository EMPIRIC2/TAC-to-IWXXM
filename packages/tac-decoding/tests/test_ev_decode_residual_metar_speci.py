"""Decode regressions for METAR/SPECI non-RMK residual conventions (F9).

[Corpus: product §F9] [Corpus: tests]
"""

from __future__ import annotations

from tac_decoding.decode import _explain_metar_remark, _explain_metar_speci, decode_tac


def _codes(tac: str, product: str = "METAR") -> dict[str, str]:
    result = decode_tac(tac, product=product)
    return {segment.code: segment.explanation for segment in result.segments}


def _residual(tac: str, product: str = "METAR") -> str:
    return " ".join(item.text for item in decode_tac(tac, product=product).residuals)


def test_ca_rvr_ft_tendency_and_cloud_chain() -> None:
    rvr = "SPECI CYSB 032015Z CCA 19011KT 1/2SM R22/3000V6000FT/D -RA FG VV002 14/14 A2991"
    codes = _codes(rvr, "SPECI")
    assert "R22/3000V6000FT/D" in codes
    assert "ft" in codes["R22/3000V6000FT/D"].lower()
    assert "downward" in codes["R22/3000V6000FT/D"].lower()
    assert "R22/3000V6000FT/D" not in _residual(rvr, "SPECI")
    clouds = "METAR CYXC 031740Z 31002KT 3SM BR SCT003 SCT014 OVC027 M01/M01 A3025 RMK FG1SF2ST1SC4 SLP281"
    assert "FG1SF2ST1SC4" in _codes(clouds)
    assert "FG1SF2ST1SC4" not in _residual(clouds)


def test_vis_variable_and_vrb_range() -> None:
    vrb = "METAR CYBG 040200Z 09018G24KT 3SM -RA BR SCT006 OVC046 02/02 A3010 RMK SF3SC5 VIS VRB 2-4 SLP200"
    codes = _codes(vrb)
    assert codes["VIS"] == "Visibility"
    assert codes["VRB"] == "Variable"
    assert "2-4" in codes
    assert "2-4" not in _residual(vrb)
    vary = "METAR KJFK 051200Z 18010KT 10SM SCT020 20/10 A2990 RMK AO2 VIS 1/2V2"
    assert "1/2V2" in _codes(vary)
    assert "1/2V2" not in _residual(vary)


def test_sog_sea_missing_cloud8_and_temp_slash() -> None:
    sog = "METAR CWKO 040200Z AUTO 23011KT 02/M04 RMK AO1 SOG 02 6009 SLP204 T00221041"
    assert "02" in _codes(sog) or "SOG" in _codes(sog)
    assert "SOG" not in _residual(sog) or "02" not in _residual(sog).split()
    sea = "METAR ENNE 031450Z 25010KT 9999 SCT020 05/03 Q1010 W///S5"
    assert "W///S5" in _codes(sea)
    assert "not reported" in _codes(sea)["W///S5"].lower()
    cloud8 = "METAR MMMX 031450Z 00000KT 5SM SCT020 20/10 A3012 RMK 8/101"
    assert "8/101" in _codes(cloud8)
    temp = "METAR K40B 031455Z AUTO 00000KT 10SM CLR 07/ A3000"
    assert "07/" in _codes(temp)
    assert "dewpoint" in _codes(temp)["07/"].lower()


def test_missing_wind_qnh_rtd_hzy_cb_loc_ohd() -> None:
    miss = "METAR FNUE 031500Z AUTO /////KT //// // ///// Q////"
    codes = _codes(miss)
    assert "/////KT" in codes
    assert "Q////" in codes
    rtd = "METAR PHNL 031455Z RTD 06008KT 10SM FEW030 27/20 A3005"
    assert "delayed" in _codes(rtd)["RTD"].lower()
    cb = "METAR PTRO 040050Z 07005KT 10SM SCT016TCU 30/26 A2994 RMK CB-NE"
    assert "CB-NE" in _codes(cb)
    ohd = "SPECI KDFW 030645Z 22009KT 10SM -TSRA BKN036CB 22/19 A2980 RMK AO2 OCNL LTGIC SW-OHD-N-NE"
    assert "SW-OHD-N-NE" in _codes(ohd, "SPECI")
    assert "SW-OHD-N-NE" not in _residual(ohd, "SPECI")


def test_wshft_cig_rwy_sfc_vis_obst_and_sensor_wind() -> None:
    wshft = "METAR KJFK 051230Z 18010KT 10SM SCT020 20/10 A2990 RMK AO2 WSHFT 07"
    assert "07" in _codes(wshft)
    assert "07" not in _residual(wshft)
    cig = "METAR CYOW 031500Z 18005KT 10SM BKN008 05/03 A2990 RMK CIG 004 RWY19 SLP100"
    codes = _codes(cig)
    assert "004" in codes
    assert "RWY19" in codes
    sfc = "SPECI KCVG 022131Z 16006KT 2SM -RA BR BKN010 14/13 A3018 RMK AO2 SFC VIS 5"
    assert "5" in _codes(sfc, "SPECI") or "VIS" in _codes(sfc, "SPECI")
    obst = "METAR ULOO 031200Z 00000KT 0500 FG VV002 01/01 Q1010 RMK OBST OBSC"
    assert _codes(obst)["OBST"] == "Obstacles"
    assert _codes(obst)["OBSC"] == "Obscured"
    skeid = "METAR EKVG 031450Z 24018KT 9999 FEW020 08/05 Q1012 RMK WIND SKEID 26009KT 220V290"
    codes_s = _codes(skeid)
    assert "SKEID" in codes_s
    assert "26009KT" in codes_s
    assert "220V290" in codes_s
    press = "METAR MMMX 031500Z 00000KT 10SM SCT020 25/10 A3012 RMK AO2 5//// 916 HZY ISOL CU SE"
    codes_m = _codes(press)
    assert "5////" in codes_m
    assert "916" in codes_m
    assert codes_m["HZY"] == "Hazy"
    assert codes_m["ISOL"] == "Isolated"
    movd = "SPECI KJFK 051245Z 18010KT 3SM TSRA BKN030CB 20/18 A2990 RMK AO2 TS MOVD NE"
    assert "NE" in _codes(movd, "SPECI") or "MOVD" in _codes(movd, "SPECI")


def test_explain_edge_seen_states() -> None:
    seen: dict[str, int] = {"sensor_wind": 1}
    assert "varying" in (_explain_metar_speci("180V220", product="METAR", seen=seen) or "").lower()
    seen = {"sensor_wind": 1}
    assert _explain_metar_speci("NOPE", product="METAR", seen=seen) is None
    assert seen.get("sensor_wind") == 0
    seen = {"cig_rwy": 1}
    assert _explain_metar_speci("NOPE", product="METAR", seen=seen) is None
    seen = {"vis_expect": 1}
    assert "Higher" in (_explain_metar_speci("HYR", product="METAR", seen=seen) or "")
    seen = {"vis_dir": 1}
    assert "West" in (_explain_metar_speci("W", product="METAR", seen=seen) or "")
    seen = {"sog_expect": 1}
    assert _explain_metar_speci("XX", product="METAR", seen=seen) is None
    seen = {"wshft_expect": 1}
    assert _explain_metar_speci("XX", product="METAR", seen=seen) is None
    seen = {"movd_expect": 1}
    assert _explain_metar_speci("XX", product="METAR", seen=seen) is None
    seen = {"movd_expect": 1}
    assert "Moved" in (_explain_metar_speci("NE", product="METAR", seen=seen) or "")
    seen = {"vis_expect": 1}
    assert "statute" in (_explain_metar_speci("3SM", product="METAR", seen=seen) or "").lower()
    seen = {"rmk": 1}
    assert "Wind shift" in (_explain_metar_remark("WSHFT", seen) or "")
    assert "Moved" in (_explain_metar_remark("MOVD", seen) or "")
    assert "fog 1 okta" in (_explain_metar_remark("FG1", seen) or "").lower()
    assert (_explain_metar_remark("LASTOBS/NEXT", {}) or "").startswith("Last staffed")
    assert "Last staffed observation / next" in (_explain_metar_remark("LASTSTFDOBS/NXT", {}) or "")
    seen = {"last_stfd": 1, "rmk": 1}
    assert "Next staffed" in (_explain_metar_remark("041300Z", seen) or "")
    seen = {"last_stfd": 1, "rmk": 1}
    assert "Staffed" in (_explain_metar_remark("STFD", seen) or "")
    assert "varying" in (_explain_metar_remark("1V3", {}) or "").lower()
    seen = {"vis_expect": 1}
    assert "varying" in (_explain_metar_remark("2-5", seen) or "").lower()
    twr = "SPECI KACY 031219Z 00000KT 2SM BR OVC001 06/06 A3034 RMK AO2 TWR VIS 10"
    assert "10" in _codes(twr, "SPECI")


def test_last_stfd_and_skeid_and_pp_tx() -> None:
    last = "METAR CYCG 040000Z 01006KT 15SM FEW160 06/02 A3015 RMK AC1CI6 LAST STFD OBS/NXT 041300Z SLP228"
    codes = _codes(last)
    assert codes["LAST"] == "Last"
    assert "STFD" in codes
    assert "LAST" not in _residual(last)
    glued = "METAR CYLD 040200Z 19003KT 15SM -RA BKN005 15/15 A2981 RMK SC5 LASTOBS/NEXT041100UTC SLP107"
    assert "LASTOBS/NEXT041100UTC" in _codes(glued) or "NEXT041100UTC" not in _residual(glued)
    skeid = "METAR EKVG 031450Z 24018KT 9999 SCT020 08/05 Q1012 RMK WIND SKEID 26009KT 220V290"
    codes_s = _codes(skeid)
    assert "SKEID" in codes_s
    assert "SKEID" not in _residual(skeid)
    pp = "METAR SPQT 031400Z 00000KT 9999 FEW020 28/24 Q1014 RMK TX37.8 PP000"
    codes_p = _codes(pp)
    assert "TX37.8" in codes_p
    assert "PP000" in codes_p
