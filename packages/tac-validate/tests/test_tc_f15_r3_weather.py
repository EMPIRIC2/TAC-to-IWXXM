"""Research R3 / TC-F15-003 — present weather phenomena grammar (T3.5/T3.6).

Accept cases cover intensity, descriptor, precip, and VC* combos. Malformed wx
groups emit ``INVALID_WEATHER``.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from tac_validate import lint
from tac_validate.issue_registry import by_code

FIXTURES = Path(__file__).resolve().parent / "fixtures"
MANIFEST_PATH = FIXTURES / "manifest.json"


def _load_manifest() -> dict[str, Any]:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def _read_tac(rel: str) -> str:
    path = FIXTURES / rel
    assert path.is_file(), f"missing fixture: {path}"
    text = path.read_text(encoding="utf-8")
    assert text.strip(), f"empty fixture: {path}"
    return text


def _case_ids(cases: list[dict[str, Any]]) -> list[str]:
    return [str(c["id"]) for c in cases]


_MANIFEST = _load_manifest()
_R3_ACCEPT = [c for c in _MANIFEST["accept"] if c.get("theme") == "R3"]
_WX_ERRORS = list(_MANIFEST.get("weather_errors", []))


def test_r3_manifest_sections_present() -> None:
    assert len(_R3_ACCEPT) >= 6
    assert {c["product"] for c in _R3_ACCEPT} == {"METAR", "SPECI"}
    assert len(_WX_ERRORS) >= 4
    for case in _R3_ACCEPT + _WX_ERRORS:
        assert (_read_tac(case["tac"])).strip()
    for case in _WX_ERRORS:
        assert case["expected_codes"] == ["INVALID_WEATHER"]


@pytest.mark.parametrize("case", _R3_ACCEPT, ids=_case_ids(_R3_ACCEPT))
def test_r3_accept_weather_grammar_ok(case: dict[str, Any]) -> None:
    report = lint(_read_tac(case["tac"]), product=case["product"])
    assert report.ok is True
    assert not any(i.code == "INVALID_WEATHER" for i in report.issues)


@pytest.mark.parametrize("case", _WX_ERRORS, ids=_case_ids(_WX_ERRORS))
def test_r3_invalid_weather_emits_error(case: dict[str, Any]) -> None:
    report = lint(_read_tac(case["tac"]), product=case["product"])
    assert report.ok is False
    codes = {i.code for i in report.issues if i.severity == "error"}
    assert "INVALID_WEATHER" in codes
    assert by_code("INVALID_WEATHER").severity == "error"
    if case.get("require_spans"):
        matched = [i for i in report.issues if i.code == "INVALID_WEATHER"]
        assert any(i.start is not None and i.end is not None and i.end > i.start for i in matched)
