"""TC-EV1210-001 — TAF, AIRMET, and SIGMET shadow does not change convert XML.

HTTP and ``convert`` keep one SIGMET product. Ordinary, volcanic-ash, and
tropical-cyclone reports select different packs from the legacy parse.
Annex 3 keeps ``2023-1`` and ``2025-2``. ``ca_eccc`` keeps ``3.0.0`` for TAF
and AIRMET, and still rejects SIGMET. [Corpus: tests] [Corpus: adr/ADR-045] [Corpus: api]
"""

from __future__ import annotations

from pathlib import Path

import pytest
from tac2iwxxm.convert import convert
from tac2iwxxm.shadow import convert_shadow

from metar_shared.xml_canonical import canonicalize_xml

_REPO = Path(__file__).resolve().parents[3]
_VENDOR = _REPO / "vendor" / "schemas" / "iwxxm"
_ANNEX3 = Path(__file__).resolve().parent / "fixtures" / "annex3_golden"
_CA = Path(__file__).resolve().parent / "fixtures" / "profiles" / "CA_ECCC"

# product stays SIGMET for all three SIGMET packs.
_CASES = (
    ("taf_a5_2.tac", "TAF", "taf", "taf-A5-2", "taf_a5_2.golden.xml"),
    ("airmet_a6_1a_ts.tac", "AIRMET", "airmet", "airmet-A6-1a-TS", "airmet_a6_1a_ts.golden.xml"),
    ("sigmet_a6_1a_ts.tac", "SIGMET", "sigmet", "sigmet-A6-1a-TS", "sigmet_a6_1a_ts.golden.xml"),
    ("sigmet_va_eggx.tac", "SIGMET", "va_sigmet", "sigmet-VA-EGGX", "sigmet_va_eggx.golden.xml"),
    ("sigmet_a6_2_tc.tac", "SIGMET", "tc_sigmet", "sigmet-A6-2-TC", ""),
)
_ANNEX3_PINS = ("2025-2", "2023-1")
_NS = {
    "2025-2": "http://icao.int/iwxxm/2025-2",
    "2023-1": "http://icao.int/iwxxm/2023-1",
    "3.0.0": "http://icao.int/iwxxm/3.0",
}
_PINS = ("2023-1", "2025-2", "3.0.0")


def _tac(name: str) -> str:
    return (_ANNEX3 / name).read_text(encoding="utf-8")


@pytest.mark.parametrize(("_tac_name", "_product", "_pack", "stem", "_golden"), _CASES)
def test_vendor_example_stays_on_every_existing_pin(
    _tac_name: str,
    _product: str,
    _pack: str,
    stem: str,
    _golden: str,
) -> None:
    for pin in _PINS:
        path = _VENDOR / pin / "IWXXM" / "examples" / f"{stem}.xml"
        assert path.is_file(), path


@pytest.mark.parametrize(("tac_name", "product", "pack_id", "_stem", "_golden"), _CASES)
@pytest.mark.parametrize("iwxxm_version", _ANNEX3_PINS)
def test_shadow_xml_matches_legacy_and_selects_pack(
    tac_name: str,
    product: str,
    pack_id: str,
    _stem: str,
    _golden: str,
    iwxxm_version: str,
) -> None:
    tac = _tac(tac_name)
    legacy = convert(tac, product=product, profile="annex3", iwxxm_version=iwxxm_version)
    shadow = convert_shadow(tac, product=product, profile="annex3", iwxxm_version=iwxxm_version)
    assert shadow.ok is legacy.ok
    assert shadow.xml == legacy.xml
    assert shadow.iwxxm_version == iwxxm_version
    assert shadow.profile == "annex3"
    assert shadow.xml is not None
    assert _NS[iwxxm_version] in shadow.xml
    assert shadow.match is not None
    assert shadow.pack_id == pack_id
    assert shadow.match.iwxxm_version == iwxxm_version
    assert shadow.match.profile == "annex3"


@pytest.mark.parametrize(("tac_name", "product", "_pack", "stem", "golden"), _CASES)
def test_shadow_keeps_2025_2_golden(
    tac_name: str,
    product: str,
    _pack: str,
    stem: str,
    golden: str,
) -> None:
    if golden:
        expected = (_ANNEX3 / golden).read_text(encoding="utf-8")
    else:
        expected = (_VENDOR / "2025-2" / "IWXXM" / "examples" / f"{stem}.xml").read_text(encoding="utf-8")
    shadow = convert_shadow(_tac(tac_name), product=product, profile="annex3", iwxxm_version="2025-2")
    assert shadow.xml is not None
    assert canonicalize_xml(shadow.xml) == canonicalize_xml(expected)


@pytest.mark.parametrize(("tac_name", "product", "pack_id", "_stem", "_golden"), _CASES)
def test_same_tac_selects_the_same_pack_on_both_pins(
    tac_name: str,
    product: str,
    pack_id: str,
    _stem: str,
    _golden: str,
) -> None:
    tac = _tac(tac_name)
    older = convert_shadow(tac, product=product, profile="annex3", iwxxm_version="2023-1")
    newer = convert_shadow(tac, product=product, profile="annex3", iwxxm_version="2025-2")
    assert older.xml is not None
    assert newer.xml is not None
    assert older.xml != newer.xml
    assert older.pack_id == pack_id
    assert newer.pack_id == pack_id
    assert older.match is not None
    assert newer.match is not None
    assert tuple(item.code for item in older.match.residuals) == tuple(item.code for item in newer.match.residuals)


@pytest.mark.parametrize(("tac_name", "product", "_pack", "_stem", "_golden"), _CASES)
def test_annex3_rejects_3_0_0_the_same_way(
    tac_name: str,
    product: str,
    _pack: str,
    _stem: str,
    _golden: str,
) -> None:
    tac = _tac(tac_name)
    legacy = convert(tac, product=product, profile="annex3", iwxxm_version="3.0.0")
    shadow = convert_shadow(tac, product=product, profile="annex3", iwxxm_version="3.0.0")
    assert legacy.ok is False
    assert shadow.ok is False
    assert shadow.xml == legacy.xml
    assert shadow.match is None
    assert shadow.pack_id is None
    assert any(issue.code == "INVALID_IWXXM_VERSION" for issue in legacy.issues)


def test_sigmet_aliases_are_not_products() -> None:
    """Ordinary, VA, and TC stay ``product=SIGMET``. No new product id."""
    tac = _tac("sigmet_va_eggx.tac")
    for product in ("VA_SIGMET", "TC_SIGMET"):
        legacy = convert(tac, product=product, profile="annex3", iwxxm_version="2025-2")
        shadow = convert_shadow(tac, product=product, profile="annex3", iwxxm_version="2025-2")
        assert legacy.ok is False
        assert shadow.ok is False
        assert shadow.xml == legacy.xml
        assert shadow.match is None
        assert any(issue.code == "UNSUPPORTED_PRODUCT" for issue in legacy.issues)


def test_unparsed_sigmet_still_uses_the_ordinary_pack() -> None:
    legacy = convert("SIGMET", product="SIGMET", profile="annex3", iwxxm_version="2025-2")
    shadow = convert_shadow("SIGMET", product="SIGMET", profile="annex3", iwxxm_version="2025-2")
    assert legacy.ok is True
    assert shadow.xml == legacy.xml
    assert shadow.pack_id == "sigmet"
    assert shadow.match is not None


@pytest.mark.parametrize(
    ("product", "relative"),
    [
        ("TAF", "TAF/valid/taf_amd.tac"),
        ("AIRMET", "AIRMET/valid/airmet_gfa.tac"),
    ],
)
def test_ca_eccc_shadow_keeps_3_0_0_xml(product: str, relative: str) -> None:
    tac = (_CA / relative).read_text(encoding="utf-8")
    legacy = convert(tac, product=product, profile="ca_eccc", iwxxm_version="3.0.0")
    shadow = convert_shadow(tac, product=product, profile="ca_eccc", iwxxm_version="3.0.0")
    assert legacy.ok is True
    assert shadow.xml == legacy.xml
    assert shadow.iwxxm_version == "3.0.0"
    assert shadow.profile == "ca_eccc"
    assert shadow.pack_id == product.lower()
    assert shadow.xml is not None
    assert _NS["3.0.0"] in shadow.xml


def test_ca_eccc_rejects_sigmet_the_same_way() -> None:
    tac = _tac("sigmet_a6_1a_ts.tac")
    legacy = convert(tac, product="SIGMET", profile="ca_eccc", iwxxm_version="3.0.0")
    shadow = convert_shadow(tac, product="SIGMET", profile="ca_eccc", iwxxm_version="3.0.0")
    assert legacy.ok is False
    assert shadow.ok is False
    assert shadow.xml == legacy.xml
    assert shadow.match is None
    assert any(issue.code == "UNSUPPORTED_PROFILE" for issue in legacy.issues)
