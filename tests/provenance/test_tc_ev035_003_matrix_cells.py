"""TC-EV035-003 — coverage matrix cell ↔ source URL."""

from __future__ import annotations

import pytest
from tests.provenance._helpers import VALID_DISPOSITIONS, load_map

PRODUCTS = [
    "METAR",
    "SPECI",
    "TAF",
    "SIGMET",
    "AIRMET",
    "VAA",
    "TCA",
    "SWXA",
    "VONA",
    "METAR_US",
]
ROLES = ["validation", "conversion", "iwxxm-validation", "bulletin"]


@pytest.mark.parametrize("product", PRODUCTS)
@pytest.mark.parametrize("role", ROLES)
def test_tc_ev035_003_matrix_cell(product: str, role: str) -> None:
    data = load_map()
    cells = {(c["product"], c["role"]): c for c in data["matrix_cells"]}
    assert (product, role) in cells, f"missing matrix cell {product}/{role}"
    cell = cells[(product, role)]
    assert cell["disposition"] in VALID_DISPOSITIONS
    if cell["disposition"] in {"ok", "paywall"}:
        assert cell.get("source_id") or cell.get("source_url"), (
            f"{product}/{role}: ok/paywall needs URL/source_id"
        )
    if cell["disposition"] in {"warn", "fail"}:
        assert cell.get("ticket") or cell.get("note"), (
            f"{product}/{role}: warn/fail needs ticket or note"
        )


def test_tc_ev035_003_vona_conversion_warn_with_ahl_cites() -> None:
    """S02.M1 — VONA conversion stays ⚠ Guidance but cites AHL/FM205."""
    data = load_map()
    cell = next(
        c
        for c in data["matrix_cells"]
        if c["product"] == "VONA" and c["role"] == "conversion"
    )
    assert cell["disposition"] == "warn"
    assert cell.get("ticket") == "#869"
    note = (cell.get("note") or "").lower()
    assert "ahl" in note or "fm205" in note
    assert cell.get("source_id") or cell.get("source_url")
