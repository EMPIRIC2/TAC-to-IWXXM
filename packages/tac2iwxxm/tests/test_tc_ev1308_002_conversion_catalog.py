"""TC-EV1308-002 — Conversion catalog descriptions + issue_type=profile.

[Corpus: product §F7.v] [Corpus: tests] #1308
"""

from __future__ import annotations

from pathlib import Path

import pytest
from tac2iwxxm.conversion_catalog import (
    _BOILERPLATE_PREFIX,
    _profiles_meta_from_mapping,
    catalog_entries,
    load_conversion_catalog_meta,
    reload_conversion_catalog_meta,
)
from tac2iwxxm.profile_registry import known_semantic_profile_ids


def test_every_semantic_profile_has_non_boilerplate_summary() -> None:
    rows = catalog_entries()
    by_id = {row["id"]: row for row in rows}
    assert set(by_id) == set(known_semantic_profile_ids())
    for pid, row in by_id.items():
        assert row["issue_type"] == "profile"
        assert "conversion" in row["tags"]
        assert "profile" in row["tags"]
        summary = row["summary"]
        assert isinstance(summary, str)
        assert summary.strip()
        assert not summary.startswith(_BOILERPLATE_PREFIX)
        assert f"Semantic conversion profile {pid}" not in summary
        # 1-3 sentences: at least enough prose for an operator summary
        assert len(summary) >= 40


def test_policy_unused_this_cycle() -> None:
    assert all(row["issue_type"] != "policy" for row in catalog_entries())


def test_profiles_meta_from_mapping_guards() -> None:
    assert _profiles_meta_from_mapping(None) == {}
    assert _profiles_meta_from_mapping(["x"]) == {}
    assert _profiles_meta_from_mapping({"profiles": "bad"}) == {}
    assert _profiles_meta_from_mapping({"profiles": {"": {"summary": "x" * 50}}}) == {}
    assert _profiles_meta_from_mapping({"profiles": {"xx": "not-map"}}) == {}
    assert _profiles_meta_from_mapping({"profiles": {"yy": {"summary": "  "}}}) == {}
    out = _profiles_meta_from_mapping(
        {"profiles": {"ICAO-2025": {"summary": "  Hello   world.  ", "severity": 1}}},
    )
    assert out == {"icao_2025": {"summary": "Hello world."}}


def test_reload_conversion_catalog_meta_roundtrip() -> None:
    first = load_conversion_catalog_meta()
    second = reload_conversion_catalog_meta()
    assert first == second
    assert "icao_2025" in second


def test_catalog_entries_limit() -> None:
    assert catalog_entries(limit=0) == []
    assert len(catalog_entries(limit=2)) == 2


def test_load_conversion_catalog_meta_resources_not_file(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from tac2iwxxm import conversion_catalog as cat

    class FakeData:
        def is_file(self) -> bool:
            return False

        def read_text(self, encoding: str = "utf-8") -> str:
            raise AssertionError("packaged path should fall back")

    class FakeRoot:
        def joinpath(self, *parts: str) -> FakeData:
            return FakeData()

    monkeypatch.setattr(cat.resources, "files", lambda _name: FakeRoot())
    cat.load_conversion_catalog_meta.cache_clear()
    meta = cat.load_conversion_catalog_meta()
    assert "icao_2025" in meta


def test_load_conversion_catalog_meta_resources_boom(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from tac2iwxxm import conversion_catalog as cat

    class Boom:
        def joinpath(self, *_args: object) -> object:
            raise OSError("missing")

    monkeypatch.setattr(cat.resources, "files", lambda _name: Boom())
    cat.load_conversion_catalog_meta.cache_clear()
    meta = cat.load_conversion_catalog_meta()
    assert "icao_2025" in meta


def test_load_conversion_catalog_meta_fallback_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from tac2iwxxm import conversion_catalog as cat

    class Boom:
        def joinpath(self, *_args: object) -> object:
            raise OSError("missing")

    monkeypatch.setattr(cat.resources, "files", lambda _name: Boom())
    monkeypatch.setattr(
        cat.Path,
        "is_file",
        lambda self: False if self.name == "conversion_catalog_meta.yaml" else Path.is_file(self),
    )
    cat.load_conversion_catalog_meta.cache_clear()
    assert cat.load_conversion_catalog_meta() == {}


def test_load_conversion_catalog_meta_bad_yaml(monkeypatch: pytest.MonkeyPatch) -> None:
    from tac2iwxxm import conversion_catalog as cat

    class FakeData:
        def is_file(self) -> bool:
            return True

        def read_text(self, encoding: str = "utf-8") -> str:
            return ":\n  - bad: ["

    class FakeRoot:
        def joinpath(self, *parts: str) -> FakeData:
            return FakeData()

    monkeypatch.setattr(cat.resources, "files", lambda _name: FakeRoot())
    cat.load_conversion_catalog_meta.cache_clear()
    assert cat.load_conversion_catalog_meta() == {}


def test_fallback_summary_when_meta_empty(monkeypatch: pytest.MonkeyPatch) -> None:
    from tac2iwxxm import conversion_catalog as cat

    monkeypatch.setattr(cat, "load_conversion_catalog_meta", lambda: {})
    rows = cat.catalog_entries(limit=1)
    assert rows
    assert rows[0]["issue_type"] == "profile"
    assert not rows[0]["summary"].startswith(_BOILERPLATE_PREFIX)
