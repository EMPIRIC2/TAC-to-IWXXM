"""EV-cmo-converter-harden — CMO Week 1 soft/hard convert gaps.

Does **not** mutate authoritative CMO TAC fixtures. [Corpus: product §F6]
"""

from __future__ import annotations

import pytest
from tac2iwxxm.products.metar_speci import parse_metar_speci
from tac2iwxxm.products.sigmet_airmet import parse_sigmet
from tac2iwxxm.products.taf import parse_taf

from tac2iwxxm import convert


def test_bare_icao_obs_accepts_product_hint_speci() -> None:
    tac = "MKJP 192303Z 10022G45KT 0500 +TSRA BKN018 SCT020CB BKN100 24/22 Q1013"
    ir = parse_metar_speci(tac, product="SPECI")
    assert ir["station"] == "MKJP"
    assert ir["report_type"] == "SPECI"
    result = convert(tac, product="SPECI", profile="annex3", iwxxm_version="2025-2")
    assert result.ok
    assert result.xml is not None
    assert "iwxxm:SPECI" in result.xml


def test_bare_icao_obs_accepts_product_hint_metar() -> None:
    tac = "KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005="
    ir = parse_metar_speci(tac, product="METAR")
    assert ir["report_type"] == "METAR"
    assert convert(tac, product="METAR", profile="annex3", iwxxm_version="2025-2").ok


def test_noisg_alias_emits_nosig_trend() -> None:
    tac = "METAR TTCP 080500Z 04004KT 9999 FEW018 28/25 Q1013 NOISG"
    ir = parse_metar_speci(tac, product="METAR")
    assert (
        ir.get("nil_nosig") or any(t.get("nil_nosig") for t in (ir.get("trends") or [])) or ir.get("nosig_typo_alias")
    )
    result = convert(tac, product="METAR", profile="annex3", iwxxm_version="2025-2")
    assert result.ok
    assert "noSignificantChange" in (result.xml or "")


def test_empo_alias_parses_as_tempo() -> None:
    tac = "TAF MWCR 081100Z 0812/0912 08009KT 9999 FEW018 PROB30 EMPO 0906/0909 12010G20KT 5000 TSRA SCT012CB BKN016"
    ir = parse_taf(tac, product="TAF")
    changes = ir.get("change_forecasts") or []
    assert any(c.get("change_indicator") == "TEMPORARY_FLUCTUATIONS" for c in changes)
    assert convert(tac, product="TAF", profile="annex3", iwxxm_version="2025-2").ok


def test_sigmet_alphanumeric_sequence_parses() -> None:
    tac = (
        "SYGC SIGMET A1 VALID 081450/081850 SYCJ - "
        "SYGC GEORGETOWN FIR ISOL EMBD TS OBS AT 1450Z WI N0829 W05925 - "
        "N0641 W05820 - N0601 W05908 - N0756 W06012 - N0829 W05925 TOP FL500 "
        "MOV W-NW INTSF="
    )
    ir = parse_sigmet(tac, product="SIGMET")
    assert ir["sequence"] == 1
    assert ir.get("sequence_label", "A1").upper() in {"A1", "1"}
    result = convert(tac, product="SIGMET", profile="annex3", iwxxm_version="2025-2")
    assert result.ok
    assert not any(i.code == "TRANSLATION_FAILED" for i in result.issues)


def test_siga0_dual_fir_phonetic_sequence_parses() -> None:
    tac = (
        "SIGA0F\n"
        "KZWY KZMA SIGMET FOXTROT 20 VALID 182003/190003 KKCI-\n"
        "NEW YORK OCEANIC FIR MIAMI OCEANIC FIR FRQ TS OBS AT 2003Z WI\n"
        "N2951 W04604 - N2611 W04611 - N2309 W06932 - N2659 W06901 - N2853\n"
        "W05650 - N2951 W04604. TOP FL470. STNR. NC."
    )
    ir = parse_sigmet(tac, product="SIGMET")
    assert ir["fir"] == "KZWY"
    assert ir.get("additional_firs") == ["KZMA"]
    assert ir["sequence"] == 20
    result = convert(tac, product="SIGMET", profile="annex3", iwxxm_version="2025-2")
    assert result.ok
    assert result.xml is not None
    assert not any(i.code == "PARSE_ERROR" for i in result.issues)


def test_sigmet_cnl_letter_sequence_label() -> None:
    tac = "TTZP SIGMET A4 VALID 141815/142145 TTPP- TTZP PIARCO FIR CNL SIGMET A3 141545/142145="
    ir = parse_sigmet(tac, product="SIGMET")
    assert ir.get("cancel") is True
    assert ir.get("cancelled_sequence") == 3
    assert ir.get("cancelled_sequence_label") == "A3"


def test_parse_sequence_token_rejects_garbage() -> None:
    from tac2iwxxm.products.sigmet_airmet import _parse_sequence_token

    with pytest.raises(ValueError, match="unable to parse"):
        _parse_sequence_token("??")


def test_airmet_letter_sequence_label() -> None:
    from tac2iwxxm.products.sigmet_airmet import parse_airmet

    tac = (
        "LIMM AIRMET A1 VALID 081200/081600 LIIB- "
        "LIMM MILANO FIR MOD ICE OBS AT 1200Z WI N4500 E01000 - N4600 E01100 "
        "FL100/200 STNR NC="
    )
    ir = parse_airmet(tac, product="AIRMET")
    assert ir["sequence"] == 1
    assert ir.get("sequence_label") == "A1"
