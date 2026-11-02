"""TAF SKC/NSC/VV must emit iwxxm:cloud when CAVOK is false (TAF.TAF-8).

After #1524 (P6SM visibility), residual Schematron TAF.TAF-8 fails (~111 on the
7d engines pull) were non-CAVOK bases with SKC/NSC/VV: visibility present but
``_parse_clouds`` skipped those tokens so ``_taf_cloud_block`` emitted nothing.

Product-rule fix in tac2iwxxm TAF parse + annex3 emit — not a severity soften.

[Corpus: product §F6] [Corpus: tests]
"""

from __future__ import annotations

import re

import pytest
from tac2iwxxm.slot_builders.taf import parse_taf

from tac2iwxxm import convert

_NIL_NSC = "http://codes.wmo.int/common/nil/nothingOfOperationalSignificance"
_NIL_INAPPLICABLE = "http://codes.wmo.int/common/nil/inapplicable"
_NIL_NOT_OBS = "http://codes.wmo.int/common/nil/notObservable"
_SKC_HREF = "http://codes.wmo.int/49-2/CloudAmountReportedAtAerodrome/SKC"

# Live-eval residual samples (7d engines RCA).
_CYFC_P6SM_SKC = (
    "TAF CYFC 021140Z 0212/0224 23010KT P6SM SKC FM021400 26010G20KT P6SM SCT040"
)
_EFVA_NSC = "TAF EFVA 021130Z 0212/0312 26003KT 3000 BCFG NSC="
_CYQT_VV002 = "TAF CYQT 021140Z 0212/0224 09005KT 1/2SM -DZ FG VV002="
_EGPF_VV_SLASH = "TAF AMD EGPF 021140Z 0212/0312 09005KT 0300 FG VV///="

_BASE_FCST = re.compile(
    r"<iwxxm:baseForecast>\s*"
    r"<iwxxm:MeteorologicalAerodromeForecast\b(?P<attrs>[^>]*)>"
    r"(?P<body>.*?)"
    r"</iwxxm:MeteorologicalAerodromeForecast>\s*"
    r"</iwxxm:baseForecast>",
    re.DOTALL,
)
_CLOUD_SELF = re.compile(r"<iwxxm:cloud\b([^>]*)/>")
_CLOUD_OPEN = re.compile(
    r"<iwxxm:cloud\b([^>]*)>(.*?)</iwxxm:cloud>",
    re.DOTALL,
)


def _base_forecast(xml: str) -> tuple[str, str]:
    match = _BASE_FCST.search(xml)
    assert match is not None, "expected non-nil baseForecast"
    return match.group("attrs"), match.group("body")


def _base_cloud(xml: str) -> tuple[str, str]:
    _attrs, body = _base_forecast(xml)
    self_closing = _CLOUD_SELF.search(body)
    if self_closing is not None:
        return self_closing.group(1), ""
    match = _CLOUD_OPEN.search(body)
    assert match is not None, "expected iwxxm:cloud in non-CAVOK baseForecast"
    return match.group(1), match.group(2)


def test_cyfc_p6sm_skc_ir_records_clear_cloud_layer() -> None:
    ir = parse_taf(_CYFC_P6SM_SKC, product="TAF")
    assert ir.get("cavok") is not True
    assert ir.get("nsc") is not True
    clouds = ir.get("clouds")
    assert isinstance(clouds, list)
    assert clouds
    assert clouds[0]["amount"] == "SKC"


def test_cyfc_p6sm_skc_emits_skc_cloud_layer() -> None:
    result = convert(
        _CYFC_P6SM_SKC, product="TAF", iwxxm_version="2025-2", profile="annex3"
    )
    assert result.ok is True
    assert result.xml is not None
    attrs, body = _base_forecast(result.xml)
    assert 'cloudAndVisibilityOK="false"' in attrs
    assert "prevailingVisibility" in body
    _cloud_attrs, cloud_body = _base_cloud(result.xml)
    assert _SKC_HREF in cloud_body
    assert _NIL_INAPPLICABLE in cloud_body
    assert "CloudLayer" in cloud_body


def test_efva_nsc_emits_nsc_nil_cloud() -> None:
    ir = parse_taf(_EFVA_NSC, product="TAF")
    assert ir.get("nsc") is True
    assert not ir.get("clouds")

    result = convert(_EFVA_NSC, product="TAF", iwxxm_version="2025-2", profile="annex3")
    assert result.ok is True
    assert result.xml is not None
    cloud_attrs, cloud_body = _base_cloud(result.xml)
    assert _NIL_NSC in cloud_attrs
    assert "CloudLayer" not in cloud_body
    assert "AerodromeCloudForecast" not in cloud_body


def test_cyqt_vv002_emits_vertical_visibility_ft() -> None:
    ir = parse_taf(_CYQT_VV002, product="TAF")
    assert ir.get("vertical_visibility_ft") == 200
    assert not ir.get("clouds")

    result = convert(
        _CYQT_VV002, product="TAF", iwxxm_version="2025-2", profile="annex3"
    )
    assert result.ok is True
    assert result.xml is not None
    _cloud_attrs, cloud_body = _base_cloud(result.xml)
    assert (
        '<iwxxm:verticalVisibility uom="[ft_i]">200</iwxxm:verticalVisibility>'
        in cloud_body
    )
    assert "CloudLayer" not in cloud_body


def test_egpf_vv_slash_emits_nil_vertical_visibility() -> None:
    ir = parse_taf(_EGPF_VV_SLASH, product="TAF")
    assert ir.get("vertical_visibility_not_observable") is True

    result = convert(
        _EGPF_VV_SLASH, product="TAF", iwxxm_version="2025-2", profile="annex3"
    )
    assert result.ok is True
    assert result.xml is not None
    _cloud_attrs, cloud_body = _base_cloud(result.xml)
    assert _NIL_NOT_OBS in cloud_body
    assert 'xsi:nil="true"' in cloud_body
    assert "CloudLayer" not in cloud_body


def test_clr_maps_to_skc_cloud_amount() -> None:
    tac = "TAF KJFK 021140Z 0212/0224 18010KT P6SM CLR="
    ir = parse_taf(tac, product="TAF")
    clouds = ir.get("clouds")
    assert isinstance(clouds, list)
    assert clouds[0]["amount"] == "SKC"
    result = convert(tac, product="TAF", iwxxm_version="2025-2", profile="annex3")
    assert result.ok is True
    assert result.xml is not None
    _attrs, cloud_body = _base_cloud(result.xml)
    assert _SKC_HREF in cloud_body


@pytest.mark.parametrize(
    "tac",
    [_CYFC_P6SM_SKC, _EFVA_NSC, _CYQT_VV002, _EGPF_VV_SLASH],
    ids=["skc", "nsc", "vv002", "vv_slash"],
)
def test_residual_taf8_samples_pass_iwxxm_validate(tac: str) -> None:
    from iwxxm_validate import rust_available, validate_iwxxm

    if not rust_available():
        pytest.skip("iwxxm_validate._rust not built (make build-iwxxm-validate-native)")

    result = convert(tac, product="TAF", iwxxm_version="2025-2", profile="annex3")
    assert result.ok is True
    assert result.xml is not None
    report = validate_iwxxm(result.xml, iwxxm_version="2025-2", profile="annex3")
    hard = [i for i in report.issues if i.severity == "error"]
    taf8 = [i for i in hard if "TAF-8" in (i.message or "") or i.code == "TAF.TAF-8"]
    assert not taf8, taf8
