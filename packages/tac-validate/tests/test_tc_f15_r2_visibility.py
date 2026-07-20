"""Research R2 / TC-F15-003 — visibility SM / meters / fractions / 9999 (T3.3/T3.4).

Baseline + fraction SM accepts; malformed vis emits ``INVALID_VISIBILITY``.
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
_R2_BASELINE = [c for c in _MANIFEST["accept"] if c.get("theme") == "R2"]
_R2_FRACTION = list(_MANIFEST.get("r2_fraction_accept", []))
_VIS_ERRORS = list(_MANIFEST.get("visibility_errors", []))


def test_r2_manifest_sections_present() -> None:
    assert len(_R2_BASELINE) >= 4
    assert {c["product"] for c in _R2_BASELINE} == {"METAR", "SPECI"}
    assert len(_R2_FRACTION) >= 3
    assert len(_VIS_ERRORS) >= 3
    for case in _R2_FRACTION + _VIS_ERRORS:
        assert (_read_tac(case["tac"])).strip()
    for case in _VIS_ERRORS:
        assert case["expected_codes"] == ["INVALID_VISIBILITY"]


@pytest.mark.parametrize("case", _R2_BASELINE, ids=_case_ids(_R2_BASELINE))
def test_r2_baseline_sm_meters_9999_ok(case: dict[str, Any]) -> None:
    report = lint(_read_tac(case["tac"]), product=case["product"])
    assert report.ok is True
    assert not any(i.code == "MISSING_VISIBILITY" for i in report.issues)
    assert not any(i.code == "INVALID_VISIBILITY" for i in report.issues)


@pytest.mark.parametrize("case", _R2_FRACTION, ids=_case_ids(_R2_FRACTION))
def test_r2_fraction_sm_accept_ok(case: dict[str, Any]) -> None:
    """US SM fractions / M-prefix must clear MISSING_VISIBILITY (R2)."""
    report = lint(_read_tac(case["tac"]), product=case["product"])
    assert report.ok is True
    assert not any(i.code == "MISSING_VISIBILITY" for i in report.issues)


@pytest.mark.parametrize("case", _VIS_ERRORS, ids=_case_ids(_VIS_ERRORS))
def test_r2_invalid_visibility_emits_error(case: dict[str, Any]) -> None:
    report = lint(_read_tac(case["tac"]), product=case["product"])
    assert report.ok is False
    codes = {i.code for i in report.issues if i.severity == "error"}
    assert "INVALID_VISIBILITY" in codes
    assert by_code("INVALID_VISIBILITY").severity == "error"
    if case.get("require_spans"):
        matched = [i for i in report.issues if i.code == "INVALID_VISIBILITY"]
        assert any(i.start is not None and i.end is not None and i.end > i.start for i in matched)
