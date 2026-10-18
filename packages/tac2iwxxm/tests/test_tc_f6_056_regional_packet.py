"""TC-F6-056: each October 2026 tester report keeps today's convert result."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from tac2iwxxm.convert import convert

_FIXTURE = Path(__file__).parent / "fixtures" / "regional_tester_2026_10.jsonl"
_ROWS = [json.loads(line) for line in _FIXTURE.read_text(encoding="utf-8").splitlines() if line]


def test_packet_fixture_counts() -> None:
    counts = {product: 0 for product in ("METAR", "SPECI", "TAF", "SIGMET")}
    for row in _ROWS:
        counts[row["product"]] += 1
    assert counts == {"METAR": 600, "SPECI": 65, "TAF": 70, "SIGMET": 20}
    assert len(_ROWS) == 755


@pytest.mark.parametrize("row", _ROWS, ids=[row["id"] for row in _ROWS])
def test_packet_report_keeps_todays_convert_result(row: dict[str, object]) -> None:
    tac = str(row["tac"])
    product = str(row["product"])
    expected = row["issues"]
    result = convert(tac, product=product)
    got = [{"code": issue.code, "message": issue.message} for issue in result.issues]
    assert got == expected
