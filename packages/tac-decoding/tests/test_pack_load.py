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


def test_overlay_same_id_without_extends_fails(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    (tmp_path / "metar.json").write_text(
        '{"id": "metar", "layout": "stub"}',
        encoding="utf-8",
    )
    monkeypatch.setenv("TAC_DECODING_PACK_DIR", str(tmp_path))
    with pytest.raises(PackSchemaError, match="must extend one builtin"):
        load_packs(profile="annex3")


def test_overlay_extends_one_builtin_for_profile(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    (tmp_path / "annex3-metar.yaml").write_text(
        "\n".join(
            (
                "id: annex3-metar-extra",
                "profiles: [annex3]",
                "extends: metar",
                "layout: token_stream",
                "rules:",
                "  - id: wind",
                '    pattern: ["VRB00KT"]',
                '    explain: "Overlay wind {0}"',
                "  - id: extra_group",
                '    pattern: ["EXTRA"]',
                '    explain: "Extra {0}"',
            )
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("TAC_DECODING_PACK_DIR", str(tmp_path))
    bare = {pack.id: pack for pack in load_packs()}
    assert any(rule.id == "station" for rule in bare["metar"].rules)
    assert all(rule.explain != "Overlay wind {0}" for rule in bare["metar"].rules)
    scoped = {pack.id: pack for pack in load_packs(profile="annex3")}
    wind = next(rule for rule in scoped["metar"].rules if rule.id == "wind")
    assert wind.explain == "Overlay wind {0}"
    assert any(rule.id == "station" for rule in scoped["metar"].rules)
    assert any(rule.id == "extra_group" for rule in scoped["metar"].rules)
    other = {pack.id: pack for pack in load_packs(profile="iwxxm_us")}
    assert all(rule.explain != "Overlay wind {0}" for rule in other["metar"].rules)


def test_overlay_header_fails_closed(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    cases = (
        ("id: extra\nprofiles: [annex3]\nlayout: token_stream\nrules: []\n", "profiles require extends"),
        (
            "id: extra\nprofiles: annex3\nextends: metar\nlayout: token_stream\nrules: []\n",
            "profiles list",
        ),
        (
            "id: extra\nprofiles: []\nextends: metar\nlayout: token_stream\nrules: []\n",
            "profiles list",
        ),
        (
            "id: extra\nprofiles: ['']\nextends: metar\nlayout: token_stream\nrules: []\n",
            "profiles list",
        ),
        (
            "id: extra\nprofiles: [annex3]\nextends: metar\nlayout: label_fields\nrules: []\n",
            "layout must match",
        ),
    )
    for text, match in cases:
        (tmp_path / "pack.yaml").write_text(text, encoding="utf-8")
        monkeypatch.setenv("TAC_DECODING_PACK_DIR", str(tmp_path))
        with pytest.raises(PackSchemaError, match=match):
            load_packs()
    (tmp_path / "pack.yaml").unlink()
    (tmp_path / "bad.yaml").write_text(
        "id: ghost\nprofiles: [annex3]\nextends: not-a-pack\nlayout: token_stream\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("TAC_DECODING_PACK_DIR", str(tmp_path))
    with pytest.raises(PackSchemaError, match="unknown builtin"):
        load_packs(profile="annex3")


def test_builtin_dir_skips_notes_and_rejects_blank_id(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    from tac_decoding.packs import clear_pack_cache

    builtin = tmp_path / "builtin"
    builtin.mkdir()
    (builtin / "notes.txt").write_text("ignore", encoding="utf-8")
    (builtin / "a.yaml").write_text("id: fixture\nlayout: stub\nrules: []\n", encoding="utf-8")
    monkeypatch.delenv("TAC_DECODING_PACK_DIR", raising=False)
    monkeypatch.setattr("tac_decoding.packs._BUILTIN_PACK_DIR", builtin)
    clear_pack_cache()
    packs = {pack.id: pack for pack in load_packs()}
    assert packs["fixture"].layout == "stub"
    (builtin / "a.yaml").unlink()
    (builtin / "bad.yaml").write_text("id: '   '\nlayout: token_stream\nrules: []\n", encoding="utf-8")
    clear_pack_cache()
    with pytest.raises(PackSchemaError, match="string id"):
        load_packs()
    clear_pack_cache()


def test_missing_builtin_pack_dir_still_loads_shells(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    from tac_decoding.packs import clear_pack_cache

    monkeypatch.delenv("TAC_DECODING_PACK_DIR", raising=False)
    monkeypatch.setattr("tac_decoding.packs._BUILTIN_PACK_DIR", tmp_path / "absent")
    clear_pack_cache()
    packs = {pack.id: pack for pack in load_packs()}
    assert packs["metar"].layout == "token_stream"
    assert packs["metar"].rules == ()
    clear_pack_cache()


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
