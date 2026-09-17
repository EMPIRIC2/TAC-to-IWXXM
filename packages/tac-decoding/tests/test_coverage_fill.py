"""Coverage fills for tac-decoding (ADR-044 / ADR-007)."""

from __future__ import annotations

from pathlib import Path

import pytest
from tac_decoding import catalog_entries
from tac_decoding.decode import (
    _explain_taf,
    _looks_like_ahl_bulletin,
)
from tac_decoding.glossary import (
    _load_yaml_tokens,
    _tokens_from_mapping,
    reload_glossary,
    resolve_location_name,
    set_location_name_resolver,
)


def test_catalog_entries_all_rows() -> None:
    rows = catalog_entries()
    assert len(rows) >= 5
    assert catalog_entries(limit=0) == []


def test_taf_altimeter_and_change_group_fallbacks() -> None:
    seen: dict[str, int] = {}
    assert _explain_taf("A2992", seen=seen) is not None
    assert _explain_taf("FMBOGUS", seen=seen) == "Change / probability group"


def test_looks_like_ahl_empty_and_blank() -> None:
    assert _looks_like_ahl_bulletin("") is False
    assert _looks_like_ahl_bulletin("\n\n") is False


def test_glossary_token_mapping_and_missing_file(tmp_path: Path) -> None:
    assert _tokens_from_mapping(None) == {}
    assert _tokens_from_mapping({"tokens": {"AB": 1}}) == {}
    assert _tokens_from_mapping(["x"]) == {}
    missing = tmp_path / "nope.yaml"
    assert _load_yaml_tokens(missing) == {}


def test_location_resolver_soft_fail() -> None:
    set_location_name_resolver(lambda _icao: (_ for _ in ()).throw(RuntimeError("boom")))
    assert resolve_location_name("KJFK") is None
    set_location_name_resolver(None)


def test_reload_glossary(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    overlay = tmp_path / "g.yaml"
    overlay.write_text("tokens:\n  ZZTEST: custom meaning\n", encoding="utf-8")
    monkeypatch.setenv("TAC_DECODING_GLOSSARY_PATH", str(overlay))
    reload_glossary()
    from tac_decoding.glossary import meaning_for

    assert meaning_for("ZZTEST") == "custom meaning"
    monkeypatch.delenv("TAC_DECODING_GLOSSARY_PATH", raising=False)
    reload_glossary()


def test_packaged_overlay_fallback_paths(monkeypatch: pytest.MonkeyPatch) -> None:
    from tac_decoding import glossary as gloss

    class Boom:
        def joinpath(self, *_args: object) -> object:
            raise FileNotFoundError("missing")

    monkeypatch.setattr(gloss.resources, "files", lambda _name: Boom())
    gloss.reload_glossary()
    assert gloss.load_glossary()


def test_packaged_overlay_not_file(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    from tac_decoding import glossary as gloss

    class FakeData:
        def is_file(self) -> bool:
            return False

        def read_text(self, encoding: str = "utf-8") -> str:
            raise AssertionError("should not read")

    class FakeRoot:
        def joinpath(self, *parts: str) -> FakeData:
            return FakeData()

    monkeypatch.setattr(gloss.resources, "files", lambda _name: FakeRoot())
    tokens = gloss._packaged_overlay_tokens()
    assert isinstance(tokens, dict)
