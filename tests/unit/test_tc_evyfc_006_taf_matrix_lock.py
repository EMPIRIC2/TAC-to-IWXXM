"""TC-EVYFC-006 — M4 TAF matrix row lock (#1230)."""

from __future__ import annotations

import re
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
_MATRIX = _REPO / "docs" / "domain" / "overlays" / "product-engine-matrix.md"

_TAF_EXPECTED = ("full", "full", "full", "full", "full", "full")


def _parse_row(product: str, text: str) -> tuple[str, ...]:
    pattern = rf"^\|\s*{re.escape(product)}\s*\|(.+)\|\s*$"
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


def test_tc_evyfc_006_taf_row_lock() -> None:
    text = _MATRIX.read_text(encoding="utf-8")
    assert "TC-EVYFC-006" in text
    assert "hatch_taf" in text
    assert "taf-core" in text or "taf.yaml" in text
    got = _parse_row("TAF", text)
    assert got == _TAF_EXPECTED, f"TAF: got {got!r} expected {_TAF_EXPECTED!r}"


def test_tc_evyfc_006_taf_sots_exist() -> None:
    roots = (
        _REPO
        / "packages"
        / "tac-decoding"
        / "src"
        / "tac_decoding"
        / "data"
        / "packs"
        / "taf.yaml",
        _REPO
        / "packages"
        / "tac-validate"
        / "src"
        / "tac_validate"
        / "data"
        / "policies"
        / "annex3-taf-quality.yaml",
        _REPO
        / "packages"
        / "tac-validate"
        / "src"
        / "tac_validate"
        / "data"
        / "detectors"
        / "taf-core.yaml",
        _REPO
        / "packages"
        / "tac2iwxxm"
        / "src"
        / "tac2iwxxm"
        / "data"
        / "emit_maps"
        / "annex3-taf.yaml",
    )
    for path in roots:
        assert path.is_file(), path
    policy = (
        _REPO
        / "packages"
        / "tac-validate"
        / "src"
        / "tac_validate"
        / "data"
        / "policies"
        / "annex3-taf-quality.yaml"
    ).read_text(encoding="utf-8")
    assert "taf-core" in policy
    assert "product: taf" in policy
