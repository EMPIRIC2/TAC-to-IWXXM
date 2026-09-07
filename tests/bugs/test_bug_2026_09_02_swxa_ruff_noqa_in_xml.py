"""BUG-2026-09-02 — SWXA emit must not leak ruff noqa into XML (quality PR Fail)."""

from __future__ import annotations

from pathlib import Path

from metar_shared.xml_canonical import canonicalize_xml
from tac2iwxxm import convert

FIXTURES = Path(__file__).resolve().parents[2] / (
    "packages/tac2iwxxm/tests/fixtures/annex3_golden"
)


def test_bug_2026_09_02_swxa_a7_3_xml_has_no_ruff_noqa() -> None:
    tac = (FIXTURES / "swxa_a7_3.tac").read_text(encoding="utf-8")
    golden = (FIXTURES / "swxa_a7_3.golden.xml").read_text(encoding="utf-8")
    result = convert(tac, product="SWXA", profile="annex3", iwxxm_version="2025-2")
    assert result.ok is True
    assert result.xml is not None
    assert "# ruff:" not in result.xml
    assert "noqa" not in result.xml
    assert canonicalize_xml(result.xml) == canonicalize_xml(golden)
