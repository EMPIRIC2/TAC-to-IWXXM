"""TC-EV072-001..006 — CA_ECCC exchange output aerodrome products (EV-072 M1).

[Corpus: product §F36] [Corpus: domain-profiles §CA_ECCC] [Corpus: tests §TC-EV072]
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest

from tac2iwxxm import convert, parse_ahl
from tac2iwxxm.exchange_output import (
    build_ca_eccc_output_spec,
    ca_distribution_path,
    ca_msc_filename,
    ca_wmo_header_designator,
    format_ca_wmo_ahl,
    msc_filename_matches_pattern,
)

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "profiles" / "CA_ECCC"
PROFILE = "ca_eccc"
IWXXM_VERSION = "3.0.0"
CATALOG = Path(__file__).resolve().parents[3] / "docs" / "domain" / "profiles" / "catalog.yaml"
_ISSUED = datetime(2023, 6, 23, 18, 0, 0, tzinfo=UTC)

_AERODROME_PRODUCTS = (
    pytest.param(
        "SPECI",
        "SPUL31 CYUL 231800",
        "A_LPCN",
        "speci",
        "SPECI CYUL 231800Z 24010KT 9999 FEW240 22/12 A3012=",
        None,
        "METAR/valid/metar_basic.golden.xml",
        id="speci",
    ),
    pytest.param(
        "TAF",
        "FTUL31 CYUL 231800",
        "A_LTCN",
        "taf",
        None,
        "TAF/valid/taf_amd.tac",
        "TAF/valid/taf_amd.golden.xml",
        id="taf",
    ),
    pytest.param(
        "AIRMET",
        "WAUL31 CYUL 231800",
        "A_LWCN",
        "airmet",
        None,
        "AIRMET/valid/airmet_gfa.tac",
        "AIRMET/valid/airmet_gfa.golden.xml",
        id="airmet",
    ),
)


@pytest.mark.parametrize(
    ("product", "ahl", "designator", "path_segment"),
    [
        ("SPECI", "SPUL31 CYUL 231800", "A_LPCN", "speci"),
        ("TAF", "FTUL31 CYUL 231800", "A_LTCN", "taf"),
        ("AIRMET", "WAUL31 CYUL 231800", "A_LWCN", "airmet"),
    ],
)
def test_tc_ev072_001_003_wmo_header_and_filename(
    product: str,
    ahl: str,
    designator: str,
    path_segment: str,
) -> None:
    """SPECI/TAF/AIRMET MSC filename + WMO header designators (TC-EV072-001..003)."""
    parts = parse_ahl(ahl)
    assert ca_wmo_header_designator(product) == designator
    wmo_ahl = format_ca_wmo_ahl(parts, product=product)
    assert wmo_ahl == f"{designator}{parts.ii} {parts.cccc} {parts.yygggg}"

    filename = ca_msc_filename(parts, issued_at=_ISSUED)
    assert msc_filename_matches_pattern(filename)
    assert filename.startswith(f"A_{parts.iwxxm_tt}")
    assert ca_distribution_path(product, issuer_code=parts.cccc, hour=_ISSUED.hour).endswith(
        f"/{path_segment}/{parts.cccc}/{_ISSUED.hour:02d}"
    )

    spec = build_ca_eccc_output_spec(product=product, parts=parts, issued_at=_ISSUED)
    assert spec.wmo_header_designator == designator
    assert spec.suggested_filename == filename
    assert spec.wmo_ahl_header == wmo_ahl


@pytest.mark.parametrize(
    ("product", "ahl", "designator", "_path_segment", "tac_inline", "tac_path", "golden_rel"),
    _AERODROME_PRODUCTS,
)
def test_tc_ev072_004_layer6_packaging_goldens(
    product: str,
    ahl: str,
    designator: str,
    _path_segment: str,
    tac_inline: str | None,
    tac_path: str | None,
    golden_rel: str,
) -> None:
    """Layer-6 exchange validate accepts product-appropriate AHL; wrong designator fails."""
    from iwxxm_validate.ca_exchange_validate import validate_ca_exchange_packaging

    parts = parse_ahl(ahl)
    wmo_ahl = format_ca_wmo_ahl(parts, product=product)
    golden = (FIXTURES / golden_rel).read_text(encoding="utf-8")
    assert validate_ca_exchange_packaging(golden, product=product, ahl_header=wmo_ahl) == []

    wrong = "A_LACN31 CYUL 231800" if product != "METAR" else "A_LTCN31 CYUL 231800"
    bad = validate_ca_exchange_packaging(golden, product=product, ahl_header=wrong)
    assert bad and bad[0].code == "CA_EXCHANGE_AHL_PRODUCT"

    if tac_inline is not None:
        tac = tac_inline
    else:
        assert tac_path is not None
        tac = (FIXTURES / tac_path).read_text(encoding="utf-8").strip()
    result = convert(tac, product=product, profile=PROFILE, iwxxm_version=IWXXM_VERSION)
    assert result.ok is True, result.issues
    assert result.xml is not None
    filename = ca_msc_filename(parts, issued_at=_ISSUED)
    packaging = validate_ca_exchange_packaging(
        result.xml,
        product=product,
        ahl_header=wmo_ahl,
        expected_filename=filename,
        require_translation_centre=True,
    )
    assert packaging == [], [(issue.code, issue.message) for issue in packaging]


def test_tc_ev072_006_catalog_exchange_output_all_products() -> None:
    """``catalog.yaml`` documents all four aerodrome exchange products (TC-EV072-006)."""
    assert CATALOG.is_file(), f"missing catalog: {CATALOG}"
    text = CATALOG.read_text(encoding="utf-8")
    assert "ev072_slice: [METAR, SPECI, TAF, AIRMET]" in text
    assert "ev071_slice" not in text
    for product, designator in (
        ("METAR", "A_LACN"),
        ("SPECI", "A_LPCN"),
        ("TAF", "A_LTCN"),
        ("AIRMET", "A_LWCN"),
    ):
        assert f'{product}: "{designator}"' in text
