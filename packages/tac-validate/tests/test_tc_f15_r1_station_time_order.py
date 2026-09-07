"""TC-F15-003 / Research R1 - station, observation time, and field-order fixtures (T3.1/T3.2).

Accept + missing CCCC/ddhhmmZ assert error codes. Odd-order cases expect
``ODD_FIELD_ORDER`` (warning) without failing ``report.ok``.
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
_R1_ACCEPT = [c for c in _MANIFEST["accept"] if c.get("theme") == "R1"]
_R1_MISSING = [
    c
    for c in _MANIFEST["negative"]
    if c.get("theme") == "R1" and set(c["expected_codes"]) <= {"MISSING_CCCC", "MISSING_OBS_TIME"}
]
_ORDER_WARNINGS = list(_MANIFEST.get("order_warnings", []))


def test_r1_manifest_has_accept_missing_and_order_warning_cases() -> None:
    assert len(_R1_ACCEPT) >= 2
    products = {c["product"] for c in _R1_ACCEPT}
    assert products == {"METAR", "SPECI"}
    assert len(_R1_MISSING) >= 3  # METAR CCCC+time, SPECI CCCC+time (at least one each theme)
    assert {c["product"] for c in _R1_MISSING} == {"METAR", "SPECI"}
    assert len(_ORDER_WARNINGS) >= 3
    assert {c["product"] for c in _ORDER_WARNINGS} == {"METAR", "SPECI"}
    for case in _ORDER_WARNINGS:
        assert case["ok"] is True
        assert case["expected_codes"] == ["ODD_FIELD_ORDER"]
        assert case["expected_severity"] == "warning"
        assert (_read_tac(case["tac"])).strip()


@pytest.mark.parametrize("case", _R1_ACCEPT, ids=_case_ids(_R1_ACCEPT))
def test_r1_accept_station_time_order_ok(case: dict[str, Any]) -> None:
    report = lint(_read_tac(case["tac"]), product=case["product"])
    assert report.ok is True
    assert not any(i.severity == "error" for i in report.issues)
    assert not any(i.code == "ODD_FIELD_ORDER" for i in report.issues)


@pytest.mark.parametrize("case", _R1_MISSING, ids=_case_ids(_R1_MISSING))
def test_r1_missing_cccc_or_obs_time_errors(case: dict[str, Any]) -> None:
    report = lint(_read_tac(case["tac"]), product=case["product"])
    assert report.ok is False
    codes = {i.code for i in report.issues if i.severity == "error"}
    for expected in case["expected_codes"]:
        assert expected in codes
        assert by_code(expected).severity == "error"


@pytest.mark.parametrize("case", _ORDER_WARNINGS, ids=_case_ids(_ORDER_WARNINGS))
def test_r1_odd_field_order_emits_warning(case: dict[str, Any]) -> None:
    """Warning-only odd order - report.ok stays True (errors absent)."""
    report = lint(_read_tac(case["tac"]), product=case["product"])
    assert report.ok is True
    matched = [i for i in report.issues if i.code == "ODD_FIELD_ORDER"]
    assert matched, f"{case['id']}: expected ODD_FIELD_ORDER in {[i.code for i in report.issues]}"
    assert all(i.severity == "warning" for i in matched)
    assert by_code("ODD_FIELD_ORDER").severity == "warning"
    if case.get("require_spans"):
        assert any(i.start is not None and i.end is not None and i.end > i.start for i in matched)
