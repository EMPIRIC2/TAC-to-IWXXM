"""TC-EV1210-001 — METAR/SPECI shadow does not change convert XML.

The pack matcher may run beside the legacy parser. XML still comes from that
parser. Annex 3 keeps ``2023-1`` and ``2025-2``. ``ca_eccc`` keeps ``3.0.0``.
A pack does not choose the pin. [Corpus: tests] [Corpus: adr/ADR-045]
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
_CA = Path(__file__).resolve().parent / "fixtures" / "profiles" / "CA_ECCC"
_METAR_TAC = (_VENDOR / "2025-2" / "IWXXM" / "examples" / "metar-A3-1.tac").read_text(encoding="utf-8")
_SPECI_TAC = (_ANNEX3 / "speci_a3_2.tac").read_text(encoding="utf-8")
_CA_TAC = (_CA / "METAR" / "valid" / "metar_basic.tac").read_text(encoding="utf-8")

_ANNEX3_PINS = ("2025-2", "2023-1")
_NS = {
    "2025-2": "http://icao.int/iwxxm/2025-2",
    "2023-1": "http://icao.int/iwxxm/2023-1",
    "3.0.0": "http://icao.int/iwxxm/3.0",
}


def test_vendor_metar_example_stays_on_every_existing_pin() -> None:
    """Do not drop a pin that already has ``metar-A3-1.xml``."""
    for pin in ("2023-1", "2025-2", "3.0.0"):
        path = _VENDOR / pin / "IWXXM" / "examples" / "metar-A3-1.xml"
        assert path.is_file(), path


@pytest.mark.parametrize("iwxxm_version", _ANNEX3_PINS)
def test_metar_shadow_xml_matches_legacy_on_annex3_pins(iwxxm_version: str) -> None:
    legacy = convert(_METAR_TAC, product="METAR", profile="annex3", iwxxm_version=iwxxm_version)
    shadow = convert_shadow(_METAR_TAC, product="METAR", profile="annex3", iwxxm_version=iwxxm_version)
    assert legacy.ok is True
    assert shadow.ok is True
    assert shadow.xml == legacy.xml
    assert shadow.iwxxm_version == iwxxm_version
    assert shadow.profile == "annex3"
    assert shadow.xml is not None
    assert _NS[iwxxm_version] in shadow.xml
    assert shadow.match is not None
    assert shadow.match.iwxxm_version == iwxxm_version
    assert shadow.match.profile == "annex3"


def test_metar_shadow_keeps_2025_2_vendor_golden() -> None:
    """The existing 2025-2 golden compare is unchanged when shadow runs."""
    manifest = json.loads((_ANNEX3 / "manifest.json").read_text(encoding="utf-8"))
    case = next(item for item in manifest["cases"] if item["id"] == "metar_a3_1")
    golden = (_ANNEX3 / case["golden"]).read_text(encoding="utf-8")
    shadow = convert_shadow(_METAR_TAC, product="METAR", profile="annex3", iwxxm_version="2025-2")
    assert shadow.xml is not None
    assert canonicalize_xml(shadow.xml) == canonicalize_xml(golden)


def test_same_tac_keeps_distinct_pin_namespaces() -> None:
    older = convert_shadow(_METAR_TAC, product="METAR", profile="annex3", iwxxm_version="2023-1")
    newer = convert_shadow(_METAR_TAC, product="METAR", profile="annex3", iwxxm_version="2025-2")
    assert older.xml is not None
    assert newer.xml is not None
    assert _NS["2023-1"] in older.xml
    assert _NS["2025-2"] in newer.xml
    assert older.xml != newer.xml
    assert older.match is not None
    assert newer.match is not None
    assert older.match.spans == newer.match.spans
    assert tuple(item.code for item in older.match.residuals) == tuple(item.code for item in newer.match.residuals)


def test_annex3_rejects_3_0_0_in_shadow_the_same_way() -> None:
    legacy = convert(_METAR_TAC, product="METAR", profile="annex3", iwxxm_version="3.0.0")
    shadow = convert_shadow(_METAR_TAC, product="METAR", profile="annex3", iwxxm_version="3.0.0")
    assert legacy.ok is False
    assert shadow.ok is False
    assert shadow.xml == legacy.xml
    assert shadow.match is None
    assert any(issue.code == "INVALID_IWXXM_VERSION" for issue in legacy.issues)


def test_ca_eccc_shadow_keeps_3_0_0_xml() -> None:
    legacy = convert(_CA_TAC, product="METAR", profile="ca_eccc", iwxxm_version="3.0.0")
    shadow = convert_shadow(_CA_TAC, product="METAR", profile="ca_eccc", iwxxm_version="3.0.0")
    assert legacy.ok is True
    assert shadow.xml == legacy.xml
    assert shadow.iwxxm_version == "3.0.0"
    assert shadow.profile == "ca_eccc"
    assert shadow.xml is not None
    assert _NS["3.0.0"] in shadow.xml
    assert shadow.match is not None
    assert shadow.match.profile == "ca_eccc"


def test_speci_shadow_xml_matches_legacy() -> None:
    legacy = convert(_SPECI_TAC, product="SPECI", profile="annex3", iwxxm_version="2025-2")
    shadow = convert_shadow(_SPECI_TAC, product="SPECI", profile="annex3", iwxxm_version="2025-2")
    assert legacy.ok is True
    assert shadow.xml == legacy.xml
    assert shadow.match is not None


def test_non_shadow_product_does_not_run_the_pack() -> None:
    legacy = convert("not a product", product="GAMET", profile="annex3", iwxxm_version="2025-2")
    shadow = convert_shadow("not a product", product="GAMET", profile="annex3", iwxxm_version="2025-2")
    assert shadow.xml == legacy.xml
    assert shadow.match is None
    assert shadow.pack_id is None
