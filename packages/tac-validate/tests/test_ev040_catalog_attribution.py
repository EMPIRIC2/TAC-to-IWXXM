"""EV-040 — catalog_attribution join for lint issue source lines."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import tac_validate.catalog_attribution as ca


@pytest.fixture(autouse=True)
def _clear_attribution_cache() -> object:
    ca._load.cache_clear()
    yield
    ca._load.cache_clear()


def test_attribution_for_known_code_has_source_fields() -> None:
    row = ca.attribution_for("INVALID_RVR")
    assert row["source_id"]
    assert row["source_attribution"]
    assert "icao" in (row["source_id"] or "").lower() or "wmo" in (row["source_attribution"] or "").lower()


def test_attribution_for_unknown_code_returns_nones() -> None:
    row = ca.attribution_for("NOT_A_REAL_ISSUE_CODE_ZZZ")
    assert row == {
        "source_id": None,
        "source_url": None,
        "source_attribution": None,
    }


def test_load_missing_file_returns_empty(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    missing = tmp_path / "nope.json"
    monkeypatch.setattr(ca, "_DATA", missing)
    ca._load.cache_clear()
    assert ca._load() == {}
    assert ca.attribution_for("AMD_PRESENT")["source_id"] is None


def test_load_invalid_json_returns_empty(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    bad = tmp_path / "bad.json"
    bad.write_text("{not-json", encoding="utf-8")
    monkeypatch.setattr(ca, "_DATA", bad)
    ca._load.cache_clear()
    assert ca._load() == {}


def test_load_non_object_root_returns_empty(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    path = tmp_path / "arr.json"
    path.write_text("[]", encoding="utf-8")
    monkeypatch.setattr(ca, "_DATA", path)
    ca._load.cache_clear()
    assert ca._load() == {}


def test_load_missing_codes_key_returns_empty(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    path = tmp_path / "nocodes.json"
    path.write_text(json.dumps({"schema_version": 1}), encoding="utf-8")
    monkeypatch.setattr(ca, "_DATA", path)
    ca._load.cache_clear()
    assert ca._load() == {}


def test_load_skips_non_dict_code_rows(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    path = tmp_path / "codes.json"
    path.write_text(
        json.dumps(
            {
                "codes": {
                    "GOOD": {
                        "source_id": "codes-wmo-int",
                        "source_url": "https://codes.wmo.int/",
                        "status": "ok",
                        "note": None,
                    },
                    "BAD": "skip-me",
                }
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(ca, "_DATA", path)
    ca._load.cache_clear()
    loaded = ca._load()
    assert "GOOD" in loaded
    assert "BAD" not in loaded
    attr = ca.attribution_for("GOOD")
    assert attr["source_id"] == "codes-wmo-int"
    assert attr["source_url"] == "https://codes.wmo.int/"
    assert attr["source_attribution"] == "codes-wmo-int — https://codes.wmo.int/"


def test_attribution_includes_access_status_when_paywall(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    path = tmp_path / "codes.json"
    path.write_text(
        json.dumps(
            {
                "codes": {
                    "X": {
                        "source_id": "icao-annex-3",
                        "source_url": "https://example.invalid/annex3",
                        "status": "paywall",
                        "note": "Table A3-2",
                    }
                }
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(ca, "_DATA", path)
    ca._load.cache_clear()
    attr = ca.attribution_for("X")
    assert attr["source_attribution"] == ("icao-annex-3 — access:paywall — Table A3-2")
