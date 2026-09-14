"""TC-EV970-S3b/S3c: native Schematron dsdl remap + Batch B stand-ins.

[Corpus: product §F13] [Corpus: decisions §ev-970-s3-validate-fill]
"""

from __future__ import annotations

import re

import pytest

from tac2iwxxm import convert


@pytest.mark.unit
def test_tc_ev970_s3b_report1_amendment_fails_native() -> None:
    """AMENDMENT on METAR must fail METAR_SPECI.MeteorologicalAerodromeObservationReport-1."""
    from iwxxm_validate import rust_available, validate_iwxxm

    if not rust_available():
        pytest.skip("iwxxm_validate._rust not built (make build-iwxxm-validate-native)")

    result = convert(
        "METAR KJFK 121251Z 18008KT 10SM FEW250 22/12 A3012=",
        product="METAR",
        profile="annex3",
        iwxxm_version="2025-2",
    )
    assert result.ok
    assert result.xml
    xml = result.xml.replace('reportStatus="NORMAL"', 'reportStatus="AMENDMENT"', 1)
    assert 'reportStatus="AMENDMENT"' in xml

    report = validate_iwxxm(xml, iwxxm_version="2025-2", profile="annex3")
    assert report.ok is False
    messages = " | ".join(i.message or "" for i in report.issues)
    assert "METAR_SPECI.MeteorologicalAerodromeObservationReport-1" in messages
    assert not any(i.code == "SCHEMATRON_SKIPPED" for i in report.issues)


@pytest.mark.unit
def test_tc_ev970_s3b_valid_metar_not_flooded_by_xpath_errors() -> None:
    """Valid convert METAR must stay ok under native SCH (XPath2 if-rewrites)."""
    from iwxxm_validate import rust_available, validate_iwxxm

    if not rust_available():
        pytest.skip("iwxxm_validate._rust not built (make build-iwxxm-validate-native)")

    result = convert(
        "METAR KJFK 121251Z 18008KT 10SM FEW250 22/12 A3012=",
        product="METAR",
        profile="annex3",
        iwxxm_version="2025-2",
    )
    assert result.ok
    assert result.xml
    report = validate_iwxxm(result.xml, iwxxm_version="2025-2", profile="annex3")
    xpath_errs = [i for i in report.issues if i.severity == "error" and (i.message or "").startswith("XPath error")]
    assert xpath_errs == [], f"unexpected XPath error floods: {xpath_errs[:3]}"
    # Soft XPath-unsupported warnings are OK; hard fail only for real asserts.
    hard = [i for i in report.issues if i.severity == "error"]
    assert hard == [], f"valid METAR should not hard-fail SCH: {hard[:5]}"


@pytest.mark.unit
def test_tc_ev970_s3c_observation2_low_vis_no_rvr() -> None:
    """Observation-2 fires when prevailing vis &lt; 1500 m and RVR is absent."""
    from iwxxm_validate import rust_available, validate_iwxxm
    from iwxxm_validate.native import rust_module

    if not rust_available():
        pytest.skip("iwxxm_validate._rust not built (make build-iwxxm-validate-native)")

    rust_module().clear_schema_caches()
    result = convert(
        "METAR KJFK 121251Z 18008KT 1/2SM R04/P6000FT FEW250 22/12 A3012=",
        product="METAR",
        profile="annex3",
        iwxxm_version="2025-2",
    )
    assert result.ok
    assert result.xml
    xml = re.sub(r"<iwxxm:rvr>.*?</iwxxm:rvr>\s*", "", result.xml, count=1, flags=re.S)
    xml = re.sub(
        r'(<iwxxm:prevailingVisibility uom="m">)[^<]+',
        r"\g<1>800",
        xml,
        count=1,
    )
    report = validate_iwxxm(xml, iwxxm_version="2025-2", profile="annex3")
    assert report.ok is False
    messages = " | ".join(i.message or "" for i in report.issues)
    assert "METAR_SPECI.MeteorologicalAerodromeObservation-2" in messages


@pytest.mark.unit
def test_tc_ev970_s3c_document_codelist_bogus_href() -> None:
    """Mirrored href + document() stand-in fails closed on non-WMO presentWeather."""
    from iwxxm_validate import rust_available, validate_iwxxm
    from iwxxm_validate.native import rust_module

    if not rust_available():
        pytest.skip("iwxxm_validate._rust not built (make build-iwxxm-validate-native)")

    rust_module().clear_schema_caches()
    result = convert(
        "METAR KJFK 121251Z 18008KT 10SM FEW250 22/12 A3012=",
        product="METAR",
        profile="annex3",
        iwxxm_version="2025-2",
    )
    assert result.ok
    assert result.xml
    marker = "</iwxxm:MeteorologicalAerodromeObservation>"
    frag = (
        "<iwxxm:presentWeather>"
        "<iwxxm:AerodromePresentWeather "
        'xlink:href="http://example.invalid/not-a-codelist"/>'
        "</iwxxm:presentWeather>"
    )
    xml = result.xml.replace(marker, frag + marker, 1)
    report = validate_iwxxm(xml, iwxxm_version="2025-2", profile="annex3")
    assert report.ok is False
    messages = " | ".join(i.message or "" for i in report.issues)
    assert "AerodromePresentWeather" in messages
    assert "should be a member of code list" in messages


@pytest.mark.unit
def test_tc_ev970_s3c_report9_arp_missing_srs_attrs() -> None:
    """Report-9 fires when ARP gml:pos lacks srsDimension/axisLabels."""
    from iwxxm_validate import rust_available, validate_iwxxm
    from iwxxm_validate.native import rust_module

    if not rust_available():
        pytest.skip("iwxxm_validate._rust not built (make build-iwxxm-validate-native)")

    rust_module().clear_schema_caches()
    result = convert(
        "METAR KJFK 121251Z 18008KT 10SM FEW250 22/12 A3012=",
        product="METAR",
        profile="annex3",
        iwxxm_version="2025-2",
    )
    assert result.ok
    assert result.xml
    arp = (
        '<aixm:ARP><aixm:ElevatedPoint gml:id="arp.bad" '
        'srsName="urn:ogc:def:crs:EPSG::4326">'
        "<gml:pos>40.64 -73.78</gml:pos>"
        "</aixm:ElevatedPoint></aixm:ARP>"
    )
    xml = result.xml.replace(
        "</aixm:AirportHeliportTimeSlice>",
        arp + "</aixm:AirportHeliportTimeSlice>",
        1,
    )
    assert "<aixm:ARP>" in xml
    report = validate_iwxxm(xml, iwxxm_version="2025-2", profile="annex3")
    assert report.ok is False
    messages = " | ".join(i.message or "" for i in report.issues)
    assert "METAR_SPECI.MeteorologicalAerodromeObservationReport-9" in messages
