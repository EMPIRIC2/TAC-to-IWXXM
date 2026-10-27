"""Lock convert issues for newly harvested Caribbean TAC strings.

[Corpus: product §F6] [Corpus: tests]
"""

from __future__ import annotations

import pytest
from tac2iwxxm.convert import convert

from .conftest import load_jsonl

_ROWS = load_jsonl("caribbean_tester_harvest_extra.jsonl")


def test_harvest_extra_has_multi_product_coverage() -> None:
    counts = {product: 0 for product in ("METAR", "SPECI", "TAF", "SIGMET")}
    for row in _ROWS:
        counts[str(row["product"])] += 1
    assert counts["METAR"] >= 50
    assert counts["SIGMET"] >= 20
    assert counts["TAF"] >= 5
    assert counts["SPECI"] >= 5
    assert len(_ROWS) >= 140


@pytest.mark.parametrize("row", _ROWS, ids=[str(row["id"]) for row in _ROWS])
def test_harvest_extra_convert_issues_stay_locked(row: dict[str, object]) -> None:
    tac = str(row["tac"])
    product = str(row["product"])
    bulletin_date = str(row.get("bulletin_date") or "2026-10-08")
    result = convert(tac, product=product, bulletin_date=bulletin_date)
    got = [{"code": issue.code, "message": issue.message} for issue in result.issues]
    assert got == row["issues"]
