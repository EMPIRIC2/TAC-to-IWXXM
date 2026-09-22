"""TC-EV1210-001 — VAA, TCA, SWXA, and VONA shadow does not change convert XML.

These products use the label-field packs. XML still comes from the legacy
parser. Annex 3 keeps ``2023-1`` and ``2025-2`` and still rejects ``3.0.0``.
Vendor copies that are not on disk stay absent. [Corpus: tests] [Corpus: adr/ADR-045]
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from tac2iwxxm.convert import convert
from tac2iwxxm.shadow import convert_shadow

from metar_shared.xml_canonical import canonicalize_xml

_REPO = Path(__file__).resolve().parents[3]
_VENDOR = _REPO / "vendor" / "schemas" / "iwxxm"
_ANNEX3 = Path(__file__).resolve().parent / "fixtures" / "annex3_golden"
_MANIFEST = json.loads((_ANNEX3 / "manifest.json").read_text(encoding="utf-8"))

_CASES = (
    ("vaa_a7_2", "VAA", "va-advisory-A7-2", ("2025-2",)),
    ("tca_a2_2", "TCA", "tc-advisory-A2-2", ("2023-1", "2025-2", "3.0.0")),
    ("swxa_a7_3", "SWXA", "spacewx-A7-3", ("2025-2",)),
    ("vona_a7_1", "VONA", "vona-A7-1", ("2025-2",)),
)
_ANNEX3_PINS = ("2025-2", "2023-1")
_NS = {
    "2025-2": "http://icao.int/iwxxm/2025-2",
    "2023-1": "http://icao.int/iwxxm/2023-1",
}


def _case(case_id: str) -> dict:
    return next(item for item in _MANIFEST["cases"] if item["id"] == case_id)


def _tac(case_id: str) -> str:
    return (_ANNEX3 / _case(case_id)["tac"]).read_text(encoding="utf-8")


@pytest.mark.parametrize(("case_id", "_product", "stem", "pins"), _CASES)
def test_vendor_example_stays_on_pins_already_on_disk(
    case_id: str,
    _product: str,
    stem: str,
    pins: tuple[str, ...],
) -> None:
    """Do not drop a pin that already has this example, and do not require a missing copy."""
    del case_id
    for pin in pins:
        path = _VENDOR / pin / "IWXXM" / "examples" / f"{stem}.xml"
        assert path.is_file(), path


@pytest.mark.parametrize(("case_id", "product", "_stem", "_pins"), _CASES)
@pytest.mark.parametrize("iwxxm_version", _ANNEX3_PINS)
def test_label_shadow_xml_matches_legacy(
    case_id: str,
    product: str,
    _stem: str,
    _pins: tuple[str, ...],
    iwxxm_version: str,
) -> None:
    tac = _tac(case_id)
    legacy = convert(tac, product=product, profile="annex3", iwxxm_version=iwxxm_version)
    shadow = convert_shadow(tac, product=product, profile="annex3", iwxxm_version=iwxxm_version)
    assert shadow.ok is legacy.ok
    assert shadow.xml == legacy.xml
    assert shadow.iwxxm_version == iwxxm_version
    assert shadow.profile == "annex3"
    assert shadow.xml is not None
    assert _NS[iwxxm_version] in shadow.xml
    assert shadow.match is not None
    assert shadow.match.iwxxm_version == iwxxm_version
    assert shadow.match.profile == "annex3"
    # Label packs are filled (EV-pack-fill-delete-gate) — spans are expected.
    assert shadow.match.spans


@pytest.mark.parametrize(("case_id", "product", "_stem", "_pins"), _CASES)
def test_label_shadow_keeps_2025_2_golden(
    case_id: str,
    product: str,
    _stem: str,
    _pins: tuple[str, ...],
) -> None:
    case = _case(case_id)
    golden = (_ANNEX3 / case["golden"]).read_text(encoding="utf-8")
    shadow = convert_shadow(_tac(case_id), product=product, profile="annex3", iwxxm_version="2025-2")
    assert shadow.xml is not None
    assert canonicalize_xml(shadow.xml) == canonicalize_xml(golden)


@pytest.mark.parametrize(("case_id", "product", "_stem", "_pins"), _CASES)
def test_same_tac_explains_the_same_on_both_annex3_pins(
    case_id: str,
    product: str,
    _stem: str,
    _pins: tuple[str, ...],
) -> None:
    tac = _tac(case_id)
    older = convert_shadow(tac, product=product, profile="annex3", iwxxm_version="2023-1")
    newer = convert_shadow(tac, product=product, profile="annex3", iwxxm_version="2025-2")
    assert older.xml is not None
    assert newer.xml is not None
    assert older.xml != newer.xml
    assert older.match is not None
    assert newer.match is not None
    assert tuple(item.code for item in older.match.residuals) == tuple(item.code for item in newer.match.residuals)


@pytest.mark.parametrize(("case_id", "product", "_stem", "_pins"), _CASES)
def test_annex3_rejects_3_0_0_in_shadow_the_same_way(
    case_id: str,
    product: str,
    _stem: str,
    _pins: tuple[str, ...],
) -> None:
    tac = _tac(case_id)
    legacy = convert(tac, product=product, profile="annex3", iwxxm_version="3.0.0")
    shadow = convert_shadow(tac, product=product, profile="annex3", iwxxm_version="3.0.0")
    assert legacy.ok is False
    assert shadow.ok is False
    assert shadow.xml == legacy.xml
    assert shadow.match is None
    assert any(issue.code == "INVALID_IWXXM_VERSION" for issue in legacy.issues)


@pytest.mark.parametrize(("case_id", "product", "_stem", "_pins"), _CASES)
def test_ca_eccc_does_not_take_these_products(
    case_id: str,
    product: str,
    _stem: str,
    _pins: tuple[str, ...],
) -> None:
    tac = _tac(case_id)
    legacy = convert(tac, product=product, profile="ca_eccc", iwxxm_version="3.0.0")
    shadow = convert_shadow(tac, product=product, profile="ca_eccc", iwxxm_version="3.0.0")
    assert legacy.ok is False
    assert shadow.ok is False
    assert shadow.xml == legacy.xml
    assert shadow.match is None
    assert any(issue.code == "UNSUPPORTED_PROFILE" for issue in legacy.issues)
