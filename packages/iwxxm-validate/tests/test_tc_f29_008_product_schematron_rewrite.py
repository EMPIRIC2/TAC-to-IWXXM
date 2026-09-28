"""TC-F29-008 — product Schematron if/document stand-ins beyond METAR_SPECI.

[Corpus: product §F13] [Corpus: product §F29] [Corpus: tests]
"""

from __future__ import annotations

import pytest

from tac2iwxxm import convert


@pytest.mark.unit
def test_tc_f29_008_taf_cavok_fires_after_product_rewrite() -> None:
    """TAF CAVOK-with-cloud fails TAF.MeteorologicalAerodromeForecast-1 via native rewrite."""
    from iwxxm_validate import rust_available, validate_iwxxm
    from iwxxm_validate.native import rust_module

    if not rust_available():
        pytest.skip("iwxxm_validate._rust not built (make build-iwxxm-validate-native)")

    rust_module().clear_schema_caches()
    result = convert(
        "TAF YUDO 151800Z 1600/1618 13005MPS 9000 BKN020=",
        product="TAF",
        profile="annex3",
        iwxxm_version="2025-2",
    )
    assert result.ok
    assert result.xml
    xml = result.xml.replace(
        'cloudAndVisibilityOK="false"',
        'cloudAndVisibilityOK="true"',
        1,
    )
    report = validate_iwxxm(xml, iwxxm_version="2025-2", profile="annex3")
    assert report.ok is False
    messages = " | ".join(i.message or "" for i in report.issues)
    assert "TAF.MeteorologicalAerodromeForecast-1" in messages


@pytest.mark.unit
def test_tc_f29_008_valid_taf_stays_ok_under_product_rewrite() -> None:
    """Valid convert TAF must stay ok after product-pattern XPath1 stand-ins."""
    from iwxxm_validate import rust_available, validate_iwxxm
    from iwxxm_validate.native import rust_module

    if not rust_available():
        pytest.skip("iwxxm_validate._rust not built (make build-iwxxm-validate-native)")

    rust_module().clear_schema_caches()
    result = convert(
        "TAF YUDO 151800Z 1600/1618 13005MPS 9000 BKN020=",
        product="TAF",
        profile="annex3",
        iwxxm_version="2025-2",
    )
    assert result.ok
    assert result.xml
    report = validate_iwxxm(result.xml, iwxxm_version="2025-2", profile="annex3")
    hard = [i for i in report.issues if i.severity == "error"]
    assert hard == [], f"valid TAF should not hard-fail SCH: {hard[:5]}"
