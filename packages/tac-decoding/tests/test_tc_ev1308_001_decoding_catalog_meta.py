"""TC-EV1308-001 — Decoding catalog additive metadata.

[Corpus: product §F9] [Corpus: tests] #1308
"""

from __future__ import annotations

from pathlib import Path

import pytest
from tac_decoding.catalog import (
    _tokens_meta_from_mapping,
    catalog_entries,
    count_issue_types,
    default_issue_type_for_token,
    load_catalog_meta,
    reload_catalog_meta,
)


def test_catalog_entries_include_additive_keys() -> None:
    rows = catalog_entries()
    assert rows
    sample = rows[0]
    for key in (
        "issue_type",
        "severity",
        "source_url",
        "source_attribution",
        "source_access",
        "source_locator",
        "conform_note",
    ):
        assert key in sample


def test_ts_row_has_yaml_meta() -> None:
    by_id = {row["id"]: row for row in catalog_entries()}
    ts = by_id["TS"]
    assert ts["issue_type"] == "content"
    assert ts["severity"] == "info"
    assert ts["source_url"] is not None
    assert ts["source_url"].startswith("https://")
    assert ts["source_access"] == "public"
    assert ts["conform_note"]


def test_function_word_and_does_not_default_content() -> None:
    assert default_issue_type_for_token("AND") is None
    by_id = {row["id"]: row for row in catalog_entries()}
    assert by_id["AND"]["issue_type"] is None


def test_official_token_defaults_content_when_meta_omits_type() -> None:
    # ICE is official; not in catalog_meta.yaml seed → classifier default
    assert default_issue_type_for_token("ICE") == "content"
    by_id = {row["id"]: row for row in catalog_entries()}
    assert by_id["ICE"]["issue_type"] == "content"
    assert by_id["ICE"]["source_url"] is None


def test_count_issue_types_includes_content_and_null() -> None:
    counts = count_issue_types()
    assert counts.get("content", 0) > 0
    assert "other" not in counts or counts["other"] == 0
    # Function words remain null
    assert counts.get("null", 0) >= 1


def test_tokens_meta_from_mapping_guards() -> None:
    assert _tokens_meta_from_mapping(None) == {}
    assert _tokens_meta_from_mapping(["x"]) == {}
    assert _tokens_meta_from_mapping({"tokens": "bad"}) == {}
    assert _tokens_meta_from_mapping({"tokens": {"": {"issue_type": "content"}}}) == {}
    assert _tokens_meta_from_mapping({"tokens": {"  ": {"issue_type": "content"}}}) == {}
    assert _tokens_meta_from_mapping({"tokens": {"XX": "not-a-map"}}) == {}
    assert _tokens_meta_from_mapping({"tokens": {"yy": {"issue_type": "  "}}}) == {}
    out = _tokens_meta_from_mapping(
        {"tokens": {"ab": {"issue_type": " content ", "severity": 1}}},
    )
    assert out == {"AB": {"issue_type": "content"}}


def test_default_issue_type_unknown_token() -> None:
    assert default_issue_type_for_token("ZZNOTAREALTOKEN") is None


def test_reload_catalog_meta_roundtrip() -> None:
    first = load_catalog_meta()
    second = reload_catalog_meta()
    assert first == second
    assert "TS" in second


def test_load_catalog_meta_resources_not_file(monkeypatch: pytest.MonkeyPatch) -> None:
    from tac_decoding import catalog as cat

    class FakeData:
        def is_file(self) -> bool:
            return False

        def read_text(self, encoding: str = "utf-8") -> str:
            raise AssertionError("packaged path should fall back")

    class FakeRoot:
        def joinpath(self, *parts: str) -> FakeData:
            return FakeData()

    monkeypatch.setattr(cat.resources, "files", lambda _name: FakeRoot())
    cat.load_catalog_meta.cache_clear()
    meta = cat.load_catalog_meta()
    assert "TS" in meta


def test_load_catalog_meta_resources_boom(monkeypatch: pytest.MonkeyPatch) -> None:
    from tac_decoding import catalog as cat

    class Boom:
        def joinpath(self, *_args: object) -> object:
            raise OSError("missing")

    monkeypatch.setattr(cat.resources, "files", lambda _name: Boom())
    cat.load_catalog_meta.cache_clear()
    meta = cat.load_catalog_meta()
    assert "TS" in meta


def test_load_catalog_meta_fallback_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    from tac_decoding import catalog as cat

    class Boom:
        def joinpath(self, *_args: object) -> object:
            raise OSError("missing")

    monkeypatch.setattr(cat.resources, "files", lambda _name: Boom())
    monkeypatch.setattr(
        cat.Path,
        "is_file",
        lambda self: False if self.name == "catalog_meta.yaml" else Path.is_file(self),
    )
    cat.load_catalog_meta.cache_clear()
    assert cat.load_catalog_meta() == {}


def test_load_catalog_meta_bad_yaml(monkeypatch: pytest.MonkeyPatch) -> None:
    from tac_decoding import catalog as cat

    class FakeData:
        def is_file(self) -> bool:
            return True

        def read_text(self, encoding: str = "utf-8") -> str:
            return ":\n  - bad: ["

    class FakeRoot:
        def joinpath(self, *parts: str) -> FakeData:
            return FakeData()

    monkeypatch.setattr(cat.resources, "files", lambda _name: FakeRoot())
    cat.load_catalog_meta.cache_clear()
    assert cat.load_catalog_meta() == {}
