"""TC-EV037 — matrix dispositions #869 / #870 / #872."""

from __future__ import annotations

import re
from pathlib import Path

import pytest
from tests.provenance._helpers import REPO, load_map

COVERAGE = REPO / "docs" / "domain" / "rules" / "COVERAGE_MATRIX.md"

AHL_FAMILIES = [
    "METAR",
    "SPECI",
    "TAF",
    "SIGMET gen",
    "VA SIGMET",
    "TC SIGMET",
    "AIRMET",
    "VAA",
    "TCA",
    "SWXA",
    "VONA",
]


def test_tc_ev037_001_vona_sot_guidance_nonblocking() -> None:
    data = load_map()
    text = COVERAGE.read_text(encoding="utf-8")
    assert "non-blocking" in text.lower() or "SoT" in text
    assert "cookbook" in text.lower() and "derived" in text.lower()
    assert "#869" in text

    silent = next(
        r for r in data["full_stack_rules"] if r["rule_id"] == "VONA_GUIDANCE_SILENT"
    )
    assert silent["status"] == "N/A"
    assert silent.get("ticket") in {"#869", "869"}
    note = (silent.get("note") or "").lower()
    assert "non-blocking" in note or "upstream" in note

    cell = next(
        c
        for c in data["matrix_cells"]
        if c["product"] == "VONA" and c["role"] == "conversion"
    )
    assert cell["disposition"] == "warn"
    assert cell.get("ticket") in {"#869", "869"}


def test_tc_ev037_002_us_schematron_na() -> None:
    data = load_map()
    text = COVERAGE.read_text(encoding="utf-8")
    assert "US SCH N/A" in text or "US Schematron" in text
    assert "#870" in text

    absent = next(
        r for r in data["full_stack_rules"] if r["rule_id"] == "US_SCH_ABSENT"
    )
    assert absent["status"] == "N/A"
    assert absent.get("ticket") in {"#870", "870"}

    cell = next(
        c
        for c in data["matrix_cells"]
        if c["product"] == "METAR_US" and c["role"] == "iwxxm-validation"
    )
    assert cell["disposition"] == "ok"
    note = (cell.get("note") or "").lower()
    assert "n/a" in note or "schematron" in note


def test_tc_ev037_003_ahl_source_columns() -> None:
    text = COVERAGE.read_text(encoding="utf-8")
    for col in (
        "AHL source",
        "T1T2 map",
        "parser",
        "BBB",
        "body splitter",
        "filename",
        "COLLECT",
        "fixtures",
        "CI",
    ):
        assert col in text, f"missing redesigned column: {col}"

    # Every family row in the redesign table should show AHL source ✅
    for family in AHL_FAMILIES:
        # Match table row starting with | Family |
        pattern = rf"\| {re.escape(family)} \|[^|]+\|[^|]+\|[^|]+\| ✅ \|"
        assert re.search(pattern, text), f"{family}: expected AHL source ✅ column"


def test_tc_ev037_004_disposals_recorded() -> None:
    data = load_map()
    assert data.get("cycle") == "EV-037"
    disposals = data.get("ev037_dispositions") or {}
    assert "869" in disposals and "870" in disposals and "872" in disposals
    # Disposed gaps removed from gaps[]
    gap_ids = {g.get("id") for g in data.get("gaps") or []}
    assert "US_SCH_ABSENT" not in gap_ids
    assert "VONA_GUIDANCE_SILENT" not in gap_ids

    gap_report = Path(REPO / data["gap_report"])
    assert gap_report.is_file()
    report_text = gap_report.read_text(encoding="utf-8")
    assert "None" in report_text or "0" in report_text or "empty" in report_text.lower()


@pytest.mark.parametrize(
    "rule_id,status",
    [
        ("VONA_GUIDANCE_SILENT", "N/A"),
        ("US_SCH_ABSENT", "N/A"),
    ],
)
def test_tc_ev037_fullstack_status(rule_id: str, status: str) -> None:
    data = load_map()
    row = next(r for r in data["full_stack_rules"] if r["rule_id"] == rule_id)
    assert row["status"] == status
