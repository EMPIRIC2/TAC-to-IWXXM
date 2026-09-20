"""T1.1 — pack directory unset uses built-ins; unknown keys fail closed.

[Corpus: adr/ADR-045]
"""

from __future__ import annotations

from pathlib import Path

import pytest
from tac_decoding.packs import PackSchemaError, load_packs


def test_unset_pack_dir_uses_builtins(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("TAC_DECODING_PACK_DIR", raising=False)
    packs = {pack.id: pack for pack in load_packs()}
    assert packs["metar"].layout == "token_stream"
    assert packs["wafs"].layout == "stub"
    assert packs["qvaci"].layout == "stub"


def test_unknown_pack_key_fails(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    (tmp_path / "bad.yaml").write_text(
        "id: metar\nlayout: token_stream\nnot_a_field: true\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("TAC_DECODING_PACK_DIR", str(tmp_path))
    with pytest.raises(PackSchemaError, match="not_a_field"):
        load_packs()


def test_overlay_adds_pack_and_keeps_builtins(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    (tmp_path / "extra.yaml").write_text(
        "id: extra\nlayout: label_fields\n",
        encoding="utf-8",
    )
    (tmp_path / "notes.txt").write_text("ignore", encoding="utf-8")
    monkeypatch.setenv("TAC_DECODING_PACK_DIR", str(tmp_path))
    packs = {pack.id: pack for pack in load_packs()}
    assert packs["metar"].layout == "token_stream"
    assert packs["extra"].layout == "label_fields"


def test_overlay_json_replaces_builtin(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    (tmp_path / "metar.json").write_text(
        '{"id": "metar", "layout": "stub"}',
        encoding="utf-8",
    )
    monkeypatch.setenv("TAC_DECODING_PACK_DIR", str(tmp_path))
    packs = {pack.id: pack for pack in load_packs()}
    assert packs["metar"].layout == "stub"


def test_missing_builtin_pack_dir_still_loads_shells(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.delenv("TAC_DECODING_PACK_DIR", raising=False)
    monkeypatch.setattr("tac_decoding.packs._BUILTIN_PACK_DIR", tmp_path / "absent")
    packs = {pack.id: pack for pack in load_packs()}
    assert packs["metar"].layout == "token_stream"
    assert packs["metar"].rules == ()


def test_overlay_rejects_bad_files(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("TAC_DECODING_PACK_DIR", str(tmp_path / "missing"))
    with pytest.raises(PackSchemaError, match="not a folder"):
        load_packs()

    (tmp_path / "nope.yaml").write_text("[\n", encoding="utf-8")
    monkeypatch.setenv("TAC_DECODING_PACK_DIR", str(tmp_path))
    with pytest.raises(PackSchemaError, match="not valid"):
        load_packs()

    (tmp_path / "nope.yaml").write_text("- just-a-list\n", encoding="utf-8")
    with pytest.raises(PackSchemaError, match="mapping"):
        load_packs()

    (tmp_path / "nope.yaml").write_text("layout: token_stream\n", encoding="utf-8")
    with pytest.raises(PackSchemaError, match="string id"):
        load_packs()

    (tmp_path / "nope.yaml").write_text("id: '   '\nlayout: token_stream\n", encoding="utf-8")
    with pytest.raises(PackSchemaError, match="string id"):
        load_packs()

    (tmp_path / "nope.yaml").write_text("id: x\nlayout: csv\n", encoding="utf-8")
    with pytest.raises(PackSchemaError, match="unknown layout"):
        load_packs()


def test_blank_pack_dir_matches_unset(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TAC_DECODING_PACK_DIR", "  ")
    packs = {pack.id: pack for pack in load_packs()}
    assert "metar" in packs
