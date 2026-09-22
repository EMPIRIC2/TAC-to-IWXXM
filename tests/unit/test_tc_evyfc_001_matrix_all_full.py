"""TC-EVYFC-001 — M5 matrix all-full program gate (#1231)."""

from __future__ import annotations

import re
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
_MATRIX = _REPO / "docs" / "domain" / "overlays" / "product-engine-matrix.md"

_PRODUCTS = ("METAR", "SPECI", "TAF", "SIGMET", "AIRMET", "VAA", "TCA")
_FULL = ("full", "full", "full", "full", "full", "full")


def _parse_row(product: str, text: str) -> tuple[str, ...]:
    pattern = rf"^\|\s*{re.escape(product)}\s\|(.+)\|\s*$"
    for line in text.splitlines():
        match = re.match(pattern, line.strip())
        if match is None:
            continue
        cells = [c.strip() for c in match.group(1).split("|")]
        normalized: list[str] = []
        for cell in cells:
            token = cell.split()[0].lower() if cell.strip() else ""
            if token.startswith("partial"):
                normalized.append("partial")
            elif token.startswith("full"):
                normalized.append("full")
            elif token.startswith("stub"):
                normalized.append("stub")
            else:
                normalized.append(token)
        return tuple(normalized)
    msg = f"missing matrix row for {product}"
    raise AssertionError(msg)


def test_tc_evyfc_001_all_full_program_gate() -> None:
    text = _MATRIX.read_text(encoding="utf-8")
    assert "TC-EVYFC-001" in text
    assert "TC-EVYFC-004" in text
    for product in _PRODUCTS:
        got = _parse_row(product, text)
        assert got == _FULL, f"{product}: got {got!r} expected {_FULL!r}"
        assert "partial" not in got
        assert "stub" not in got
