"""EV-040 - catalog_attribution join for lint issue source lines."""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest
import tac_validate.catalog_attribution as ca

_INTERNAL_DOC_REF_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("Corpus", re.compile(r"\[Corpus:")),
    ("docs/sessions", re.compile(r"docs/sessions/")),
    ("docs/feature-list", re.compile(r"docs/feature-list")),
    ("ADR", re.compile(r"\bADR-\d+\b")),
    ("EV", re.compile(r"\bEV-\d+\b")),
    ("S0", re.compile(r"\bS0\d+\b")),
    ("TC", re.compile(r"\bTC-[A-Z0-9-]+\b")),
    ("E##", re.compile(r"\bE\d{2}-\d+\b")),
    ("#NNN", re.compile(r"(?<!\w)#\d{3,}\b")),
    ("Fn", re.compile(r"\bF\d+\b")),
)


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
        "family": "lint",
        "source_type": None,
        "status": None,
        "semantic_identifier": None,
        "last_verified": None,
        "replacement_url": None,
        "source_locator": None,
        "source_access": None,
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
    assert attr["source_attribution"] == "codes-wmo-int - https://codes.wmo.int/"


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
    assert attr["source_attribution"] == ("icao-annex-3 - access:paywall - https://example.invalid/annex3 - Table A3-2")


def test_packaged_source_attribution_has_no_internal_doc_refs() -> None:
    """Operator-facing attribution must not leak EV/ADR/#/Fn planning ids (EV-048)."""
    payload = json.loads(ca._DATA.read_text(encoding="utf-8"))
    codes = payload.get("codes") or {}
    hits: list[str] = []
    for code, row in codes.items():
        if not isinstance(row, dict):
            continue
        for key in ("note", "source_attribution"):
            text = row.get(key)
            if not isinstance(text, str):
                continue
            for name, pattern in _INTERNAL_DOC_REF_PATTERNS:
                hits.extend(f"{code}.{key}: {name}={match.group(0)!r}" for match in pattern.finditer(text))
        joined = ca.attribution_for(str(code)).get("source_attribution")
        if isinstance(joined, str):
            for name, pattern in _INTERNAL_DOC_REF_PATTERNS:
                hits.extend(f"{code}.joined: {name}={match.group(0)!r}" for match in pattern.finditer(joined))
    assert hits == [], "planning vocabulary in lint attribution:\n" + "\n".join(hits)


def test_attribution_omits_note_with_internal_doc_refs(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Runtime join drops planning-vocabulary notes from the operator string."""
    path = tmp_path / "codes.json"
    path.write_text(
        json.dumps(
            {
                "codes": {
                    "X": {
                        "source_id": "codes-wmo-int",
                        "source_url": "https://codes.wmo.int/49-2",
                        "status": "ok",
                        "note": "EV-050 / #959 tracked membership gate",
                    }
                }
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(ca, "_DATA", path)
    ca._load.cache_clear()
    attr = ca.attribution_for("X")
    assert attr["source_attribution"] == "codes-wmo-int - https://codes.wmo.int/49-2"
