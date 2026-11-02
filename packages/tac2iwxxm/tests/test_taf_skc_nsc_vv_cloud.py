"""TAF SKC/NSC/NCD/VV cloud IR + emit coverage (TAF-8 residual).

Live-eval regression lives under tests/bugs/; this module keeps package
unit coverage at 100% for the parse/emit branches.

[Corpus: product §F6] [Corpus: tests]
"""

from __future__ import annotations

from tac2iwxxm.profiles.annex3_emit.taf_cloud import taf_cloud_block
from tac2iwxxm.slot_builders.taf import parse_taf

from tac2iwxxm import convert

_NIL_NCD = "http://codes.wmo.int/common/nil/notDetectedByAutoSystem"
_NIL_NOT_OBS = "http://codes.wmo.int/common/nil/notObservable"
_SKC_HREF = "http://codes.wmo.int/49-2/CloudAmountReportedAtAerodrome/SKC"


def test_parse_ncd_sets_ncd_flag() -> None:
    ir = parse_taf("TAF YUDO 151800Z 1600/1618 13005MPS 9999 NCD=", product="TAF")
    assert ir.get("ncd") is True
    assert not ir.get("clouds")


def test_emit_ncd_nil_cloud() -> None:
    xml = taf_cloud_block({"ncd": True}, gml_id="cloud.ncd")
    assert _NIL_NCD in xml
    assert "AerodromeCloudForecast" not in xml


def test_parse_and_emit_vv_numeric() -> None:
    ir = parse_taf("TAF YUDO 151800Z 1600/1618 13005MPS 0500 FG VV002=", product="TAF")
    assert ir.get("vertical_visibility_ft") == 200
    result = convert(
        "TAF YUDO 151800Z 1600/1618 13005MPS 0500 FG VV002=",
        product="TAF",
        iwxxm_version="2025-2",
        profile="annex3",
    )
    assert result.ok is True
    assert result.xml is not None
    assert '<iwxxm:verticalVisibility uom="[ft_i]">200</iwxxm:verticalVisibility>' in result.xml


def test_parse_and_emit_vv_not_observable() -> None:
    ir = parse_taf("TAF YUDO 151800Z 1600/1618 13005MPS 0300 FG VV///=", product="TAF")
    assert ir.get("vertical_visibility_not_observable") is True
    xml = taf_cloud_block(
        {"vertical_visibility_not_observable": True},
        gml_id="cloud.vv",
    )
    assert _NIL_NOT_OBS in xml


def test_parse_skc_emits_clear_layer() -> None:
    ir = parse_taf("TAF YUDO 151800Z 1600/1618 13005MPS 9999 SKC=", product="TAF")
    clouds = ir.get("clouds")
    assert isinstance(clouds, list)
    assert clouds[0]["amount"] == "SKC"
    result = convert(
        "TAF YUDO 151800Z 1600/1618 13005MPS 9999 SKC=",
        product="TAF",
        iwxxm_version="2025-2",
        profile="annex3",
    )
    assert result.ok is True
    assert result.xml is not None
    assert _SKC_HREF in result.xml


def test_emit_base_not_observable_layer() -> None:
    xml = taf_cloud_block(
        {"clouds": [{"amount": "BKN", "base_not_observable": True}]},
        gml_id="cloud.base",
    )
    assert _NIL_NOT_OBS in xml
    assert "CloudLayer" in xml
