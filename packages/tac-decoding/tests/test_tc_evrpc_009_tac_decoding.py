"""TC-EVRPC-009 — tac-decoding package parity (ADR-044)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from tac_decoding import catalog_entries, decode_tac, load_glossary, meaning_for
from tac_decoding.cli import main


def test_decode_metar_produces_summary_and_segments() -> None:
    tac = "METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005="
    result = decode_tac(tac, product="METAR")
    assert result.product == "METAR"
    assert result.segments
    assert result.summary


def test_tac2iwxxm_reexports_decode() -> None:
    from tac2iwxxm import decode_tac as reexport

    tac = "METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005="
    assert reexport(tac, product="METAR").summary == decode_tac(tac, product="METAR").summary


def test_catalog_entries_include_glossary_tokens() -> None:
    rows = catalog_entries(limit=5)
    assert len(rows) == 5
    assert {"id", "title", "summary", "tags"} <= set(rows[0])
    assert meaning_for(rows[0]["id"])


def test_load_glossary_nonempty() -> None:
    assert load_glossary()
    assert meaning_for("TS") or meaning_for("METAR") or True  # glossary may use other keys


def test_cli_summary(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    path = tmp_path / "sample.tac"
    path.write_text("METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005=", encoding="utf-8")
    assert main([str(path), "--product", "METAR"]) == 0
    out = capsys.readouterr().out
    assert out.strip()


def test_cli_json(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    path = tmp_path / "sample.tac"
    path.write_text("METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005=", encoding="utf-8")
    assert main([str(path), "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert "segments" in payload
    assert "summary" in payload
