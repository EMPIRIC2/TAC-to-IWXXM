"""TC-EVYFC-008 — M4 AIRMET/VAA/TCA matrix row lock (#1230)."""

from __future__ import annotations

import re
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
_MATRIX = _REPO / "docs" / "domain" / "overlays" / "product-engine-matrix.md"
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


def test_tc_evyfc_008_rows_lock() -> None:
    text = _MATRIX.read_text(encoding="utf-8")
    assert "TC-EVYFC-008" in text
    for product in ("AIRMET", "VAA", "TCA"):
        got = _parse_row(product, text)
        assert got == _FULL, f"{product}: got {got!r}"


def test_tc_evyfc_008_sots_exist() -> None:
    roots = (
        "packages/tac-decoding/src/tac_decoding/data/packs/airmet.yaml",
        "packages/tac-decoding/src/tac_decoding/data/packs/vaa.yaml",
        "packages/tac-decoding/src/tac_decoding/data/packs/tca.yaml",
        "packages/tac-validate/src/tac_validate/data/policies/annex3-airmet-quality.yaml",
        "packages/tac-validate/src/tac_validate/data/policies/annex3-vaa-quality.yaml",
        "packages/tac-validate/src/tac_validate/data/policies/annex3-tca-quality.yaml",
        "packages/tac-validate/src/tac_validate/data/detectors/airmet-core.yaml",
        "packages/tac-validate/src/tac_validate/data/detectors/vaa-core.yaml",
        "packages/tac-validate/src/tac_validate/data/detectors/tca-core.yaml",
        "packages/tac2iwxxm/src/tac2iwxxm/data/emit_maps/annex3-airmet.yaml",
        "packages/tac2iwxxm/src/tac2iwxxm/data/emit_maps/iwxxm-us-airmet.yaml",
        "packages/tac2iwxxm/src/tac2iwxxm/data/emit_maps/ca-eccc-airmet.yaml",
        "packages/tac2iwxxm/src/tac2iwxxm/data/emit_maps/annex3-vaa.yaml",
        "packages/tac2iwxxm/src/tac2iwxxm/data/emit_maps/annex3-tca.yaml",
    )
    for rel in roots:
        path = _REPO / rel
        assert path.is_file(), path
