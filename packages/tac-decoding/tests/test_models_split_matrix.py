"""Mandatory evolve-auto test matrix for tac-decoding models split.

Covers success / mutation / failure / validation permutations across
METAR, TAF, and SIGMET. [Corpus: product §F9] [Corpus: tests]
"""

from __future__ import annotations

from pathlib import Path

import pytest
from tac_decoding.decode import DecodeResidual, DecodeResult, DecodeSegment, decode_tac
from tac_decoding.ir import project_ir
from tac_decoding.match import MatchContext, MatchResult, MatchSpan, match_tac
from tac_decoding.models.catalog import CatalogEntry
from tac_decoding.models.dictionary import DictionaryEntry, DictionaryTokenFields
from tac_decoding.models.ir import PackIr
from tac_decoding.models.packs import Pack, Rule
from tac_decoding.packs import PackSchemaError, _read_file, clear_pack_cache, load_packs


def test_success_decode_metar_returns_typed_result() -> None:
    """Happy-path METAR decode returns typed msgspec models."""
    result = decode_tac(
        "METAR KJFK 121755Z 18010KT 10SM FEW050 22/12 A2992=",
        product="METAR",
    )
    assert isinstance(result, DecodeResult)
    assert result.product == "METAR"
    assert result.segments
    assert all(isinstance(seg, DecodeSegment) for seg in result.segments)
    assert all(isinstance(res, DecodeResidual) for res in result.residuals)
    assert result.summary


def test_success_decode_taf_and_sigmet() -> None:
    """Happy-path TAF and SIGMET decode return typed results."""
    taf = decode_tac(
        "TAF KJFK 121730Z 1218/1324 18010KT P6SM FEW050=",
        product="TAF",
    )
    sigmet = decode_tac(
        "WSSS SIGMET A01 VALID 121800/122200 WSJC- WSJC SINGAPORE FIR EMBD TS=",
        product="SIGMET",
    )
    assert isinstance(taf, DecodeResult)
    assert taf.product == "TAF"
    assert taf.segments
    assert isinstance(sigmet, DecodeResult)
    assert sigmet.product == "SIGMET"


def test_mutation_redecode_same_tac_is_stable() -> None:
    """Re-decode of the same TAC is stable (update / re-read)."""
    tac = "METAR KJFK 121755Z 18010KT 10SM FEW050 22/12 A2992="
    first = decode_tac(tac, product="METAR")
    second = decode_tac(tac, product="METAR")
    assert first.product == second.product
    assert [(s.start, s.end, s.code, s.explanation) for s in first.segments] == [
        (s.start, s.end, s.code, s.explanation) for s in second.segments
    ]
    assert [(r.start, r.end, r.text) for r in first.residuals] == [(r.start, r.end, r.text) for r in second.residuals]
    assert first.summary == second.summary


def test_mutation_product_change_updates_decode() -> None:
    """Changing the leading product keyword updates the decode product."""
    metar = decode_tac("METAR KJFK 121755Z 18010KT 10SM FEW050 22/12 A2992=", product="METAR")
    speci = decode_tac("SPECI KJFK 121755Z 18010KT 10SM FEW050 22/12 A2992=", product="SPECI")
    assert metar.product == "METAR"
    assert speci.product == "SPECI"
    assert metar.summary != speci.summary or metar.segments[0].code != speci.segments[0].code


def test_failure_malformed_empty_tac() -> None:
    """Empty TAC still returns a DecodeResult without raising."""
    result = decode_tac("", product="METAR")
    assert isinstance(result, DecodeResult)
    assert result.product == "METAR"
    assert result.segments == [] or result.residuals is not None


def test_failure_unsupported_product_is_residual_only() -> None:
    """Unsupported product yields residuals only (no segments)."""
    result = decode_tac("METAR KJFK 121755Z=", product="NOTAPRODUCT")
    assert isinstance(result, DecodeResult)
    assert result.product == "NOTAPRODUCT"
    assert result.segments == []
    assert result.residuals


def test_validation_decode_segment_construction() -> None:
    """DecodeSegment accepts valid fields and rejects incomplete construction."""
    seg = DecodeSegment(0, 5, "METAR", "Meteorological aerodrome report")
    assert seg.start == 0
    assert seg.end == 5
    with pytest.raises(TypeError):
        DecodeSegment(0, 5, "METAR")  # type: ignore[call-arg]


def test_validation_pack_ir_and_dictionary_models() -> None:
    """Pack IR and dictionary/catalog TypedDicts validate at construction."""
    match = MatchResult(
        spans=(MatchSpan(0, 5, "METAR", "Meteorological aerodrome report", "type"),),
        residuals=(),
        steps=1,
        iwxxm_version="2025-2",
        profile="annex3",
    )
    ir: PackIr = project_ir(match, product="metar", pack_id="metar")
    assert ir["ir_version"] == 1
    assert ir["spans"][0]["rule_id"] == "type"
    assert isinstance(ir["spans"], list)

    fields: DictionaryTokenFields = {"products": ["METAR"], "countries": ["US"]}
    assert fields["products"] == ["METAR"]
    entry: DictionaryEntry = {
        "id": "METAR",
        "code": "METAR",
        "meaning": "Meteorological aerodrome report",
        "products": ["METAR"],
        "countries": ["INTL"],
        "wmo_amendment": None,
    }
    assert entry["code"] == "METAR"
    catalog: CatalogEntry = {
        "id": "METAR",
        "title": "METAR",
        "summary": "Meteorological aerodrome report",
        "tags": ["decoding"],
        "issue_type": "content",
        "severity": None,
        "source_url": None,
        "source_attribution": None,
        "source_access": None,
        "source_locator": None,
        "conform_note": None,
    }
    assert catalog["tags"] == ["decoding"]


def test_validation_pack_schema_reject_and_match_success(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Valid packs match; invalid pack files raise PackSchemaError."""
    packs = load_packs()
    metar = next(p for p in packs if p.id == "metar")
    assert isinstance(metar, Pack)
    assert all(isinstance(rule, Rule) for rule in metar.rules)
    result = match_tac("METAR KJFK=", metar, context=MatchContext(iwxxm_version="2025-2"))
    assert isinstance(result, MatchResult)
    assert result.spans or result.residuals

    bad = tmp_path / "bad.yaml"
    bad.write_text("id: \nlayout: token_stream\nrules: []\n", encoding="utf-8")
    monkeypatch.setenv("TAC_DECODING_PACK_DIR", str(tmp_path))
    clear_pack_cache()
    with pytest.raises(PackSchemaError):
        _read_file(bad)
    clear_pack_cache()


def test_mutation_clear_pack_cache_reload() -> None:
    """Clearing the pack cache and reloading preserves pack ids."""
    first = load_packs()
    clear_pack_cache()
    second = load_packs()
    assert [p.id for p in first] == [p.id for p in second]


def test_bulletin_skips_blank_inner_summary(monkeypatch: pytest.MonkeyPatch) -> None:
    """Cover the empty-summary branch when assembling a bulletin paragraph."""
    import tac_decoding.decode as decode_mod
    from tac_decoding import decode_api

    class _Meta:
        ahl = "SAUS31 KJFK 121755"
        report_count = 2

    class _Split:
        reports = ("AAAA", "BBBB")
        meta = _Meta()

    calls = {"n": 0}

    def _fake_decode(report: str, *, product: str) -> DecodeResult:
        calls["n"] += 1
        if report == "AAAA":
            return DecodeResult(product=product, segments=[], residuals=[], summary="")
        return DecodeResult(
            product=product,
            segments=[DecodeSegment(0, 4, "BBBB", "Second report body")],
            residuals=[],
            summary="Second report body.",
        )

    previous = decode_mod._bulletin_splitter
    monkeypatch.setattr(decode_api, "_decode_single_report", _fake_decode)
    try:
        decode_mod.set_bulletin_splitter(lambda _tac, _product: _Split())
        result = decode_tac("SAUS31 KJFK 121755\nAAAA\nBBBB", product="METAR")
        assert "Bulletin SAUS31 KJFK 121755" in result.summary
        assert "Second report body" in result.summary
        assert "1)" in result.summary
        assert calls["n"] == 2
    finally:
        decode_mod.set_bulletin_splitter(previous)
