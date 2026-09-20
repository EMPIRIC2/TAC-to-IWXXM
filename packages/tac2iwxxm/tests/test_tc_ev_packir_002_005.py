"""TC-EV-PACKIR-002..005 — pack IR map, emit equality, default flip, boundary.

[Corpus: tests] [Corpus: adr/ADR-045]
"""

from __future__ import annotations

from pathlib import Path

import pytest
from tac2iwxxm.convert import convert
from tac2iwxxm.ir_source import resolve_ir_source
from tac2iwxxm.pack_ir_map import PackIrMapError, map_spans_to_convert_ir
from tac2iwxxm.slot_builders.metar_speci import parse_metar_speci
from tac_decoding.match import MatchContext, MatchResult, MatchSpan, match_tac
from tac_decoding.packs import load_packs

_REPO = Path(__file__).resolve().parents[3]
_VENDOR = _REPO / "vendor" / "schemas" / "iwxxm"
_PRODUCTS = Path(__file__).resolve().parents[1] / "src" / "tac2iwxxm" / "products"
_ALL_PINS = ("2023-1", "2025-2", "3.0.0")
_EXAMPLES = (
    ("metar-A3-1", "METAR"),
    ("speci-A3-2", "SPECI"),
)


def _tac_for(stem: str) -> str:
    for pin in ("2025-2", "2023-1", "3.0.0"):
        path = _VENDOR / pin / "IWXXM" / "examples" / f"{stem}.tac"
        if path.is_file():
            return path.read_text(encoding="utf-8")
    msg = f"missing vendor TAC peer for {stem}"
    raise FileNotFoundError(msg)


def _pins_on_disk(stem: str) -> tuple[str, ...]:
    return tuple(pin for pin in _ALL_PINS if (_VENDOR / pin / "IWXXM" / "examples" / f"{stem}.xml").is_file())


def test_map_spans_to_slots_matches_legacy_ir() -> None:
    tac = _tac_for("metar-A3-1")
    packs = {pack.id: pack for pack in load_packs()}
    matched = match_tac(tac, packs["metar"], context=MatchContext("2025-2", "annex3"))
    mapped = map_spans_to_convert_ir(matched, tac=tac, product="METAR")
    legacy = parse_metar_speci(tac, product="METAR")
    assert mapped == legacy


def test_map_rejects_residuals() -> None:
    match = MatchResult(
        spans=(MatchSpan(0, 5, "METAR", "x", "report_type"),),
        residuals=(MatchSpan(6, 10, "YUDO", "", ""),),
        steps=1,
        iwxxm_version="2025-2",
        profile="annex3",
    )
    with pytest.raises(PackIrMapError, match="residual"):
        map_spans_to_convert_ir(match, tac="METAR YUDO", product="METAR")


def test_map_rejects_unsupported_product() -> None:
    match = MatchResult(spans=(), residuals=(), steps=0, iwxxm_version=None, profile=None)
    with pytest.raises(PackIrMapError, match="not supported"):
        map_spans_to_convert_ir(match, tac="WAFS", product="WAFS")


def test_map_rejects_empty_body_spans() -> None:
    match = MatchResult(
        spans=(MatchSpan(0, 1, "=", "x", "equal"),),
        residuals=(),
        steps=1,
        iwxxm_version=None,
        profile=None,
    )
    with pytest.raises(PackIrMapError, match="no body spans"):
        map_spans_to_convert_ir(match, tac="=", product="METAR")


def test_map_rejects_unparseable_spans() -> None:
    match = MatchResult(
        spans=(MatchSpan(0, 5, "METAR", "x", "report_type"),),
        residuals=(),
        steps=1,
        iwxxm_version=None,
        profile=None,
    )
    with pytest.raises(PackIrMapError, match="could not fill"):
        map_spans_to_convert_ir(match, tac="METAR", product="METAR")


def test_resolve_ir_source_rejects_unknown() -> None:
    with pytest.raises(ValueError, match="ir_source must be"):
        resolve_ir_source("METAR", ir_source="nope")


def test_convert_rejects_bad_ir_source() -> None:
    result = convert(
        _tac_for("metar-A3-1"),
        product="METAR",
        profile="annex3",
        iwxxm_version="2025-2",
        ir_source="nope",
    )
    assert result.ok is False
    assert result.issues[0].code == "INVALID_IR_SOURCE"


def test_explicit_pack_fails_when_incomplete() -> None:
    # Incomplete body — pack catch-all still matches tokens, but slot builder rejects.
    tac = "METAR"
    result = convert(
        tac,
        product="METAR",
        profile="annex3",
        iwxxm_version="2025-2",
        ir_source="pack",
    )
    # Explicit pack does not fall back — quarantine or parse error.
    assert result.issues
    assert any(issue.code in {"TRANSLATION_FAILED", "PARSE_ERROR"} for issue in result.issues)


def test_pack_ir_missing_pack_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    import importlib

    from tac2iwxxm.pack_ir_map import PackIrMapError

    convert_mod = importlib.import_module("tac2iwxxm.convert")
    monkeypatch.setattr(convert_mod, "load_packs", lambda: ())
    with pytest.raises(PackIrMapError, match="no pack"):
        convert_mod._parse_pack_ir("METAR", "METAR", iwxxm_version="2025-2", profile="annex3")


def test_auto_falls_back_when_pack_incomplete() -> None:
    # CA altimeter is covered now; force residual by explicit incomplete match path
    # via a TAC token the pack does not know (REMARKS AO2) — auto must not quarantine.
    tac = "METAR CYUL 231800Z 24010KT 9999 FEW240 22/12 A3012 RMK AO2="
    auto = convert(tac, product="METAR", profile="ca_eccc", iwxxm_version="3.0.0")
    legacy = convert(tac, product="METAR", profile="ca_eccc", iwxxm_version="3.0.0", ir_source="legacy")
    assert legacy.ok
    assert auto.ok
    assert auto.xml == legacy.xml


@pytest.mark.parametrize(("stem", "product"), _EXAMPLES)
@pytest.mark.parametrize("iwxxm_version", _ALL_PINS)
def test_pack_ir_emit_byte_identical_to_legacy(
    stem: str,
    product: str,
    iwxxm_version: str,
) -> None:
    pins = _pins_on_disk(stem)
    if iwxxm_version not in pins:
        pytest.skip(f"{stem} has no {iwxxm_version} vendor copy")
    tac = _tac_for(stem)
    legacy = convert(tac, product=product, profile="annex3", iwxxm_version=iwxxm_version, ir_source="legacy")
    if not legacy.ok:
        pytest.skip(f"annex3 does not convert {stem} at {iwxxm_version}")
    pack = convert(tac, product=product, profile="annex3", iwxxm_version=iwxxm_version, ir_source="pack")
    assert pack.ok
    assert pack.xml == legacy.xml


@pytest.mark.parametrize(("stem", "product"), _EXAMPLES)
def test_default_convert_uses_pack_ir(stem: str, product: str) -> None:
    assert resolve_ir_source(product) == "pack"
    tac = _tac_for(stem)
    default = convert(tac, product=product, profile="annex3", iwxxm_version="2025-2")
    legacy = convert(tac, product=product, profile="annex3", iwxxm_version="2025-2", ir_source="legacy")
    assert default.ok
    assert legacy.ok
    assert default.xml == legacy.xml
    assert default.ir == legacy.ir


def test_products_metar_speci_module_deleted() -> None:
    path = _PRODUCTS / "metar_speci.py"
    assert not path.is_file()


def test_taf_defaults_to_pack() -> None:
    assert resolve_ir_source("TAF") == "pack"


def test_sigmet_pack_id_from_legacy_root() -> None:
    from tac2iwxxm.shadow import _pack_id

    assert _pack_id("METAR", None) == "metar"
    assert _pack_id("SIGMET", None) == "sigmet"
    assert _pack_id("SIGMET", {"iwxxm_root": "VolcanicAshSIGMET"}) == "va_sigmet"
    assert _pack_id("SIGMET", {"iwxxm_root": "TropicalCycloneSIGMET"}) == "tc_sigmet"
    assert _pack_id("SIGMET", {"iwxxm_root": 1}) == "sigmet"
