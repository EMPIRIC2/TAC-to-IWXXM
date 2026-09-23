"""TC-EVYRY-002: YAML ICAO name table (ADR-049 / #1255)."""

from __future__ import annotations

from pathlib import Path

import pytest
from tac_decoding import decode_tac
from tac_decoding.glossary import (
    ENV_LOCATION_NAMES_PATH,
    resolve_location_name,
    set_location_name_resolver,
)


@pytest.fixture(autouse=True)
def _clear_resolver() -> None:
    set_location_name_resolver(None)
    yield
    set_location_name_resolver(None)


def test_table_hit_and_miss(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    table = tmp_path / "names.yaml"
    table.write_text("KJFK: John F. Kennedy International Airport\n", encoding="utf-8")
    monkeypatch.setenv(ENV_LOCATION_NAMES_PATH, str(table))
    assert resolve_location_name("kjfk") == "John F. Kennedy International Airport"
    assert resolve_location_name("KORD") is None


def test_hook_wins_over_table(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    table = tmp_path / "names.yaml"
    table.write_text("KJFK: From Table\n", encoding="utf-8")
    monkeypatch.setenv(ENV_LOCATION_NAMES_PATH, str(table))
    set_location_name_resolver(lambda icao: "From Hook" if icao == "KJFK" else None)
    assert resolve_location_name("KJFK") == "From Hook"
    assert resolve_location_name("KORD") is None


def test_unset_and_bad_file_stay_empty(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(ENV_LOCATION_NAMES_PATH, raising=False)
    assert resolve_location_name("KJFK") is None
    bad = tmp_path / "bad.yaml"
    bad.write_text("- not-a-map\n", encoding="utf-8")
    monkeypatch.setenv(ENV_LOCATION_NAMES_PATH, str(bad))
    assert resolve_location_name("KJFK") is None
    monkeypatch.setenv(ENV_LOCATION_NAMES_PATH, str(tmp_path / "missing.yaml"))
    assert resolve_location_name("KJFK") is None


def test_table_skips_malformed_entries(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    table = tmp_path / "names.yaml"
    table.write_text("names: plain\n", encoding="utf-8")
    monkeypatch.setenv(ENV_LOCATION_NAMES_PATH, str(table))
    assert resolve_location_name("KJFK") is None
    table.write_text(
        "names:\n  1: two\n  ' ': skipped\n  KJFK: '   '\n  KORD: O Hare\n",
        encoding="utf-8",
    )
    assert resolve_location_name("KJFK") is None
    assert resolve_location_name("KORD") == "O Hare"
    table.write_text(":\n", encoding="utf-8")
    assert resolve_location_name("KORD") is None


def test_decode_uses_table_name(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    table = tmp_path / "names.yaml"
    table.write_text("names:\n  KJFK: Test Field\n", encoding="utf-8")
    monkeypatch.setenv(ENV_LOCATION_NAMES_PATH, str(table))
    decoded = decode_tac("METAR KJFK 121255Z 10SM=", product="METAR")
    station = next(segment for segment in decoded.segments if segment.code.upper() == "KJFK")
    assert "Test Field" in station.explanation
    assert "Test Field" in decoded.summary
