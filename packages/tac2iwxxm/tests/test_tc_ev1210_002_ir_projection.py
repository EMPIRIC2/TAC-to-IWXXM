"""T6.2 — pack IR projects beside the legacy parser.

XML still comes from the legacy convert. Pack IR is additive. Parsers and the
version matrix stay. [Corpus: tests] [Corpus: adr/ADR-045]
"""

from __future__ import annotations

from pathlib import Path

from tac2iwxxm.convert import convert
from tac2iwxxm.shadow import convert_shadow

_REPO = Path(__file__).resolve().parents[3]
_VENDOR = _REPO / "vendor" / "schemas" / "iwxxm"
_PRODUCTS = Path(__file__).resolve().parents[1] / "src" / "tac2iwxxm" / "products"
_METAR = (_VENDOR / "2025-2" / "IWXXM" / "examples" / "metar-A3-1.tac").read_text(encoding="utf-8")


def test_pack_ir_sits_beside_legacy_xml() -> None:
    legacy = convert(_METAR, product="METAR", profile="annex3", iwxxm_version="2025-2")
    shadow = convert_shadow(_METAR, product="METAR", profile="annex3", iwxxm_version="2025-2")
    assert shadow.xml == legacy.xml
    assert shadow.xml is not None
    assert shadow.pack_ir is not None
    assert shadow.pack_ir["product"] == "METAR"
    assert shadow.pack_ir["pack_id"] == "metar"
    assert shadow.pack_ir["iwxxm_version"] == "2025-2"
    assert shadow.pack_ir["profile"] == "annex3"
    assert "spans" in shadow.pack_ir
    assert "residuals" in shadow.pack_ir
    # Legacy IR from convert is unchanged and separate from pack projection.
    assert legacy.ir is not None
    assert shadow.legacy_ir == legacy.ir
    assert shadow.pack_ir != legacy.ir


def test_pack_ir_same_on_both_annex3_pins() -> None:
    older = convert_shadow(_METAR, product="METAR", profile="annex3", iwxxm_version="2023-1")
    newer = convert_shadow(_METAR, product="METAR", profile="annex3", iwxxm_version="2025-2")
    assert older.pack_ir is not None
    assert newer.pack_ir is not None
    assert older.pack_ir["spans"] == newer.pack_ir["spans"]
    assert older.pack_ir["residuals"] == newer.pack_ir["residuals"]
    assert older.xml != newer.xml


def test_failed_convert_has_no_pack_ir() -> None:
    shadow = convert_shadow(_METAR, product="METAR", profile="annex3", iwxxm_version="3.0.0")
    assert shadow.ok is False
    assert shadow.pack_ir is None
    assert shadow.legacy_ir is None


def test_parsers_and_pins_still_present_after_ir_projection() -> None:
    slot = Path(__file__).resolve().parents[1] / "src" / "tac2iwxxm" / "slot_builders"
    assert (slot / "metar_speci.py").is_file()
    assert (slot / "sigmet_airmet.py").is_file()
    assert not (_PRODUCTS / "metar_speci.py").is_file()
    from tac2iwxxm.profile_registry import supported_iwxxm_versions_for_profile

    assert "2023-1" in supported_iwxxm_versions_for_profile("annex3")
    assert "2025-2" in supported_iwxxm_versions_for_profile("annex3")
    assert supported_iwxxm_versions_for_profile("ca_eccc") == frozenset({"3.0.0"})
