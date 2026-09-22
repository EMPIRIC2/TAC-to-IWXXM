"""TC-EV-PFDG-001..005 — pack fill, mapper independence, flip, selective delete.

[Corpus: tests] [Corpus: adr/ADR-045]
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest
from tac2iwxxm.convert import convert
from tac2iwxxm.ir_source import resolve_ir_source
from tac2iwxxm.pack_ir_map import map_spans_to_convert_ir, pack_id_for_product
from tac2iwxxm.slot_builders.metar_speci import parse_metar_speci
from tac_decoding.match import MatchContext, match_tac
from tac_decoding.packs import load_packs

_REPO = Path(__file__).resolve().parents[3]
_VENDOR = _REPO / "vendor" / "schemas" / "iwxxm"
_PACK_IR_MAP = Path(__file__).resolve().parents[1] / "src" / "tac2iwxxm" / "pack_ir_map.py"
_PRODUCTS = Path(__file__).resolve().parents[1] / "src" / "tac2iwxxm" / "products"
_SLOT = Path(__file__).resolve().parents[1] / "src" / "tac2iwxxm" / "slot_builders"
_ALL_PINS = ("2023-1", "2025-2", "3.0.0")

_IN_BAR: tuple[tuple[str, str], ...] = (
    ("metar-A3-1", "METAR"),
    ("speci-A3-2", "SPECI"),
    ("taf-A5-1", "TAF"),
    ("taf-A5-2", "TAF"),
    ("sigmet-A6-1a-TS", "SIGMET"),
    ("sigmet-A6-1b-CNL", "SIGMET"),
    ("sigmet-VA-EGGX", "SIGMET"),
    ("sigmet-multi-location-VA", "SIGMET"),
    ("sigmet-A6-2-TC", "SIGMET"),
    ("airmet-A6-1a-TS", "AIRMET"),
    ("va-advisory-A7-2", "VAA"),
    ("va-advisory-A2-1", "VAA"),
    ("tc-advisory-A2-2", "TCA"),
    ("spacewx-A7-3", "SWXA"),
    ("spacewx-A2-3", "SWXA"),
    ("vona-A7-1", "VONA"),
)

_DELETED_PRODUCT_MODULES = (
    "metar_speci.py",
    "taf.py",
    "sigmet_airmet.py",
    "vaa_tca.py",
    "swxa.py",
    "vona.py",
)


def _tac_for(stem: str) -> str:
    for pin in ("2025-2", "2023-1", "3.0.0"):
        path = _VENDOR / pin / "IWXXM" / "examples" / f"{stem}.tac"
        if path.is_file():
            return path.read_text(encoding="utf-8")
    raise FileNotFoundError(stem)


def _pins_on_disk(stem: str) -> tuple[str, ...]:
    return tuple(
        pin
        for pin in _ALL_PINS
        if (_VENDOR / pin / "IWXXM" / "examples" / f"{stem}.tac").is_file()
        and (_VENDOR / pin / "IWXXM" / "examples" / f"{stem}.xml").is_file()
    )


def test_pack_ir_map_source_does_not_import_products() -> None:
    """TC-EV-PFDG-002."""
    tree = ast.parse(_PACK_IR_MAP.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            assert not node.module.startswith("tac2iwxxm.products"), node.module
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert not alias.name.startswith("tac2iwxxm.products"), alias.name


def test_map_spans_metar_matches_slot_builder() -> None:
    tac = _tac_for("metar-A3-1")
    packs = {pack.id: pack for pack in load_packs()}
    matched = match_tac(tac, packs["metar"], context=MatchContext("2025-2", "annex3"))
    mapped = map_spans_to_convert_ir(matched, tac=tac, product="METAR")
    assert mapped == parse_metar_speci(tac, product="METAR")


@pytest.mark.parametrize(("stem", "product"), _IN_BAR)
@pytest.mark.parametrize("iwxxm_version", ["2023-1", "2025-2"])
def test_pack_ir_emit_byte_identical_to_legacy(stem: str, product: str, iwxxm_version: str) -> None:
    """TC-EV-PFDG-001 / 003."""
    pins = _pins_on_disk(stem)
    if iwxxm_version not in pins:
        pytest.skip(f"{stem} missing on {iwxxm_version}")
    tac = _tac_for(stem)
    legacy = convert(tac, product=product, profile="annex3", iwxxm_version=iwxxm_version, ir_source="legacy")
    if not legacy.ok:
        pytest.skip(f"legacy convert skipped for {stem}@{iwxxm_version}")
    pack = convert(tac, product=product, profile="annex3", iwxxm_version=iwxxm_version, ir_source="pack")
    assert pack.ok
    assert pack.xml == legacy.xml


@pytest.mark.parametrize("product", ["METAR", "SPECI", "TAF", "SIGMET", "AIRMET", "VAA", "TCA", "SWXA", "VONA"])
def test_core_products_default_to_pack(product: str) -> None:
    """TC-EV-PFDG-003 flip."""
    assert resolve_ir_source(product) == "pack"


def test_swxa_alternate_inventory_present() -> None:
    """D-PFDG-12: primary + _alternate XML exist on 2025-2 for A7-3."""
    base = _VENDOR / "2025-2" / "IWXXM" / "examples"
    assert (base / "spacewx-A7-3.xml").is_file()
    assert (base / "spacewx-A7-3_alternate.xml").is_file()
    tac = (base / "spacewx-A7-3.tac").read_text(encoding="utf-8")
    legacy = convert(tac, product="SWXA", profile="annex3", iwxxm_version="2025-2", ir_source="legacy")
    pack = convert(tac, product="SWXA", profile="annex3", iwxxm_version="2025-2", ir_source="pack")
    assert legacy.ok
    assert pack.ok
    assert pack.xml == legacy.xml


@pytest.mark.parametrize("name", _DELETED_PRODUCT_MODULES)
def test_selective_delete_removed_product_modules(name: str) -> None:
    """TC-EV-PFDG-004 all-or-nothing deletes after goldens passed."""
    assert not (_PRODUCTS / name).is_file()
    assert (_SLOT / name).is_file()


def test_fir_geometry_remains_under_products() -> None:
    assert (_PRODUCTS / "fir_geometry.py").is_file()


def test_pack_id_for_sigmet_variants() -> None:
    assert pack_id_for_product("SIGMET", "EGGX SIGMET VA ERUPTION") == "va_sigmet"
    assert pack_id_for_product("SIGMET", "YUCC SIGMET TC GLORIA") == "tc_sigmet"
    assert pack_id_for_product("SIGMET", "YUDD SIGMET 2 VALID") == "sigmet"


def test_unknown_product_defaults_to_legacy() -> None:
    assert resolve_ir_source("NOTAPRODUCT") == "legacy"
